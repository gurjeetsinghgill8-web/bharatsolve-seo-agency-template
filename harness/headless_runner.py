"""
BHARATSOLVE SEO AGENCY — Headless Autonomous SEO Runner
🏥 Dr. Gurjeet Singh Gill — Gill Heart Clinic (Meerut & Delhi NCR)

This script can be run standalone via:
  1. python harness/headless_runner.py                 (review mode — default)
  2. python harness/headless_runner.py --mode publish  (auto-publish immediately)
  3. GitHub Actions Cron (.github/workflows/auto_seo.yml)
  4. Windows Task Scheduler / batch file
  5. Streamlit UI 1-Click Master Run

MODES
-----
  review  (DEFAULT): Generate blog → save as PENDING draft → send to Dr. Gill on
                     Telegram for review. Nothing goes live until he approves.
  publish          : Generate blog → publish live immediately → Telegram confirmation.

SAFETY: if Telegram is not configured, "review" mode automatically degrades to
        "publish" so the website keeps updating instead of silently doing nothing.
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from db.schema import init_db
from db.operations import log_agent_action, get_content_pieces
from agents.github_publisher import (
    generate_heart_blog,
    publish_blog_to_github,
    update_master_blog_index,
    update_homepage_articles,
    publish_ai_geo_blueprint,
    _get_github_token,
    check_repo_connection,
    DEFAULT_CONFIG,
)
from agents.local_search_engine import LOCAL_SEARCH_QUERIES
from utils.llm_client import get_api_key


def _safe_print(text: str):
    """Safely print text avoiding UnicodeEncodeError on Windows terminals."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))


def _get_pending_topics() -> list:
    """
    Titles + topics of drafts already waiting for review.

    Needed because review-mode drafts are NOT in the published DB yet, so without
    this the runner would pick the same topic again every single day.
    """
    try:
        from agents.draft_review import list_pending_drafts
        drafts = list_pending_drafts(limit=50)
        out = []
        for d in drafts:
            if d.get("title"):
                out.append(str(d["title"]).lower())
            if d.get("topic"):
                out.append(str(d["topic"]).lower())
        return out
    except Exception:
        return []


def pick_next_target_query() -> dict:
    """Find the next high-priority query from LOCAL_SEARCH_QUERIES that hasn't been published yet."""
    # Get all published titles from DB
    try:
        pieces = get_content_pieces(project_id=1, limit=500)
        published_titles = [p.get('title', '').lower() for p in pieces]
        published_keywords = [p.get('target_keyword', '').lower() for p in pieces if p.get('target_keyword')]
    except Exception:
        published_titles = []
        published_keywords = []

    # Also skip anything already sitting in the review queue.
    pending = _get_pending_topics()

    all_queries = []
    # Priority order
    categories = ["direct_doctor", "emergency_local", "symptoms", "tests_procedures", "conditions", "lifestyle"]
    for cat in categories:
        for q in LOCAL_SEARCH_QUERIES.get(cat, []):
            all_queries.append({"category": cat, **q})

    # Pick first query that is not yet published AND not pending review
    for item in all_queries:
        q_text = item["query"].lower()
        already_done = (
            any(q_text in title for title in published_titles)
            or any(q_text in kw for kw in published_keywords)
            or any(q_text in p for p in pending)
        )
        if not already_done:
            return item

    # Fallback to random if all have been attempted
    import random
    return random.choice(all_queries)


def run_clinic_turbo_cycle(force_topic: str = None, language: str = "Hinglish",
                           mode: str = "review") -> dict:
    """
    Execute the entire automated SEO cycle end-to-end.

    Args:
        force_topic: optional topic override
        language: Hinglish / Hindi / English
        mode: "review" (draft → Telegram → approval) or "publish" (go live now)

    Returns detailed execution result dict.
    """
    init_db()
    start_time = time.time()
    _safe_print(f"\n{'='*60}")
    _safe_print(f"🚀 BHARATSOLVE GILL CLINIC AUTO-SEO ENGINE — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    _safe_print(f"{'='*60}")

    # ── Resolve effective mode (degrade safely if Telegram is unavailable) ──
    telegram_ready = False
    try:
        from utils.telegram_notifier import is_telegram_configured
        telegram_ready = is_telegram_configured()
    except Exception as e:
        _safe_print(f"⚠️ Telegram module unavailable: {e}")

    effective_mode = mode
    if mode == "review" and not telegram_ready:
        effective_mode = "publish"
        _safe_print("⚠️ Telegram configured nahi hai → 'publish' mode par fallback kar rahe hain.")
        _safe_print("   (Draft review ke liye TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID set karein.)")

    _safe_print(f"⚙️  Mode: {mode} → effective: {effective_mode}")

    # Step 1: Query selection
    if force_topic:
        query_info = {"query": force_topic, "category": "custom", "intent": "high"}
    else:
        query_info = pick_next_target_query()

    topic = query_info["query"]
    _safe_print(f"🎯 Target Search Query: '{topic}' (Category: {query_info.get('category')})")

    # Step 2: Check API keys
    gemini_key = get_api_key("gemini")
    groq_key = get_api_key("groq")
    github_tok = _get_github_token()

    _safe_print(f"🔑 API Status -> Gemini: {'✅ Configured' if gemini_key else '❌ Missing'}, Groq: {'✅ Configured' if groq_key else '❌ Missing'}, GitHub: {'✅ Configured' if github_tok else '❌ Missing'}, Telegram: {'✅ Configured' if telegram_ready else '❌ Missing'}")

    if not github_tok:
        err_msg = "GitHub token missing — website publish impossible. Set GH_PAT (Actions) or GITHUB_TOKEN (Streamlit)."
        _safe_print(f"❌ {err_msg}")
        log_agent_action("auto_pilot", err_msg, status="error", error_message=err_msg)
        return {"status": "error", "error": err_msg, "topic": topic, "mode": effective_mode}

    # ═══════════════════════════════════════════════════════════════
    # REVIEW MODE — generate, queue for approval, notify Telegram
    # ═══════════════════════════════════════════════════════════════
    if effective_mode == "review":
        _safe_print(f"📝 Generating NMC-compliant article in {language} (review mode)...")
        try:
            blog_data = generate_heart_blog(topic, "Meerut, Delhi NCR", language)
        except Exception as e:
            err_msg = f"Blog generation exception: {e}"
            _safe_print(f"❌ {err_msg}")
            log_agent_action("auto_pilot", err_msg, status="error", error_message=str(e))
            return {"status": "error", "error": err_msg, "topic": topic, "mode": effective_mode}

        if not blog_data.get("content") or blog_data.get("error"):
            err_msg = blog_data.get("error", "Blog generation failed — no content returned")
            _safe_print(f"❌ {err_msg}")
            log_agent_action("auto_pilot", err_msg, status="error", error_message=err_msg)
            return {"status": "error", "error": err_msg, "topic": topic, "mode": effective_mode}

        # Save as a pending draft in the website repo (shared between cron + app)
        try:
            from agents.draft_review import save_pending_draft
            saved = save_pending_draft(
                title=blog_data["title"],
                content=blog_data["content"],
                topic=topic,
                language=language,
                meta_title=blog_data.get("meta_title", ""),
                meta_description=blog_data.get("meta_description", ""),
                keywords=blog_data.get("keywords", ""),
                faq=blog_data.get("faq", []),
            )
        except Exception as e:
            err_msg = f"Draft save exception: {e}"
            _safe_print(f"❌ {err_msg}")
            log_agent_action("auto_pilot", err_msg, status="error", error_message=str(e))
            return {"status": "error", "error": err_msg, "topic": topic, "mode": effective_mode}

        if not saved.get("success"):
            err_msg = saved.get("error", "Draft save failed")
            _safe_print(f"❌ {err_msg}")
            log_agent_action("auto_pilot", err_msg, status="error", error_message=err_msg)
            return {"status": "error", "error": err_msg, "topic": topic, "mode": effective_mode}

        draft = saved["draft"]
        _safe_print(f"📥 Draft queued for review: {draft['slug']} ({draft['word_count']} words)")

        # Telegram notification
        tg_result = {"ok": False, "error": "not attempted"}
        try:
            from utils.telegram_notifier import send_blog_draft_for_review
            tg_result = send_blog_draft_for_review(draft)
        except Exception as e:
            tg_result = {"ok": False, "error": str(e)}

        if tg_result.get("ok"):
            _safe_print("✈️ Telegram par draft bhej diya — Dr. Gill review karein.")
        else:
            _safe_print(f"⚠️ Telegram send failed: {tg_result.get('error')}")
            log_agent_action("telegram", f"Draft notify failed: {tg_result.get('error')}",
                             status="error", error_message=str(tg_result.get("error")))

        elapsed_s = round(time.time() - start_time, 2)
        _safe_print(f"⏱️ Cycle completed in {elapsed_s}s — Status: pending_review")
        _safe_print(f"{'='*60}\n")

        log_agent_action("auto_pilot", f"Draft for review: {blog_data['title'][:50]}")

        return {
            "status": "pending_review",
            "mode": effective_mode,
            "title": blog_data["title"],
            "slug": draft["slug"],
            "word_count": draft["word_count"],
            "telegram_sent": bool(tg_result.get("ok")),
            "telegram_error": None if tg_result.get("ok") else tg_result.get("error"),
            "review_url": "Streamlit app → 📬 Pending Drafts",
            "elapsed_seconds": elapsed_s,
            "query_info": query_info,
        }

    # ═══════════════════════════════════════════════════════════════
    # PUBLISH MODE — go live immediately (original behaviour)
    # ═══════════════════════════════════════════════════════════════
    _safe_print(f"📝 Generating NMC-compliant article in {language} (publish mode)...")
    try:
        result = publish_blog_to_github(topic=topic, target_location="Meerut, Delhi NCR",
                                        auto_publish=True, language=language)
    except Exception as e:
        err_msg = f"Auto blog task exception: {e}"
        _safe_print(f"❌ Error: {err_msg}")
        log_agent_action("auto_pilot", err_msg, status="error", error_message=str(e))
        return {"status": "error", "error": err_msg, "topic": topic, "mode": effective_mode}

    # Rebuild website master catalogs & AI Blueprints
    if result.get("status") == "published":
        _safe_print(f"🌐 Published Live URL: {result.get('published_url')}")
        try:
            _safe_print("🔄 Updating Master Index, Homepage Articles & AI GEO Blueprints...")
            update_master_blog_index()
            update_homepage_articles()
            publish_ai_geo_blueprint()
            _safe_print("✅ Master catalog and AI search blueprints (/llms.txt, robots.txt, sitemap.xml) updated!")
        except Exception as update_err:
            _safe_print(f"⚠️ Catalog update warning: {update_err}")

        # Telegram confirmation (best-effort)
        if telegram_ready:
            try:
                from utils.telegram_notifier import send_publish_confirmation
                tg = send_publish_confirmation(result, result.get("published_url", ""))
                if tg.get("ok"):
                    _safe_print("✈️ Telegram par publish confirmation bhej diya.")
                else:
                    _safe_print(f"⚠️ Telegram notify failed: {tg.get('error')}")
            except Exception as e:
                _safe_print(f"⚠️ Telegram notify error: {e}")
    else:
        _safe_print(f"❌ Publish failed: {result.get('push_error') or result.get('message') or result.get('status')}")

    elapsed_s = round(time.time() - start_time, 2)
    _safe_print(f"⏱️ Cycle completed in {elapsed_s}s — Final Status: {result.get('status')}")
    _safe_print(f"{'='*60}\n")

    result["elapsed_seconds"] = elapsed_s
    result["query_info"] = query_info
    result["mode"] = effective_mode
    return result


def main():
    parser = argparse.ArgumentParser(description="BHARATSOLVE Gill Clinic autonomous SEO runner")
    parser.add_argument("--mode", choices=["review", "publish"], default="review",
                        help="review = queue draft for Telegram approval (default); publish = go live now")
    parser.add_argument("--topic", default=None, help="Force a specific topic")
    parser.add_argument("--language", default="Hinglish", help="Hinglish / Hindi / English")
    parser.add_argument("--json", action="store_true", help="Print full result as JSON")
    args = parser.parse_args()

    res = run_clinic_turbo_cycle(force_topic=args.topic, language=args.language, mode=args.mode)

    if args.json:
        print(json.dumps(res, indent=2, default=str))

    # Non-zero exit on hard failure so GitHub Actions surfaces it clearly.
    sys.exit(1 if res.get("status") == "error" else 0)


if __name__ == "__main__":
    main()
