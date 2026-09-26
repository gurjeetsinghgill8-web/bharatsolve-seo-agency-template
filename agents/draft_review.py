"""
BHARATSOLVE SEO AGENCY — Draft Review Store
🏥 Dr. Gurjeet Singh Gill — Gill Heart Clinic

Stores AI-generated blog drafts as JSON files in the WEBSITE repository
(``pending_drafts/``) until Dr. Gill approves or rejects them.

WHY GITHUB AND NOT SQLITE?
    The daily cron runs on GitHub Actions with a throwaway checkout, while the
    Streamlit app runs on Streamlit Cloud with its own ephemeral ``/tmp`` DB.
    They share no database. The website repository IS shared, so it is used as
    the hand-off store: cron writes a draft → Telegram notifies Dr. Gill →
    the app reads the draft → Dr. Gill approves → the app publishes it.

Flow:
    generate → save_pending_draft() → Telegram → approve_and_publish_draft()
                                              ↘ reject_pending_draft()
"""
import base64
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional

from agents.github_publisher import (
    DEFAULT_CONFIG,
    _github_api,
    _push_file_to_repo,
    build_blog_html,
    update_master_blog_index,
    update_homepage_articles,
    publish_ai_geo_blueprint,
)
from db.operations import save_content, log_agent_action

PENDING_FOLDER = "pending_drafts"


# ═══════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _slugify(text: str, fallback: str = "") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")[:60]
    return slug or fallback or f"draft-{int(time.time())}"


def _repo_path(slug: str) -> str:
    return f"{PENDING_FOLDER}/{slug}.json"


def _decode_file(res: dict) -> Optional[dict]:
    """Decode a GitHub contents-API response into a dict."""
    if not isinstance(res, dict) or "content" not in res:
        return None
    try:
        raw = base64.b64decode(res["content"]).decode("utf-8", errors="ignore")
        return json.loads(raw)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════
# WRITE
# ═══════════════════════════════════════════════════════════════════════

def save_pending_draft(
    title: str,
    content: str,
    topic: str = "",
    language: str = "Hinglish",
    meta_title: str = "",
    meta_description: str = "",
    keywords: str = "",
    faq: Optional[list] = None,
    slug: Optional[str] = None,
    source: str = "auto_pilot",
) -> Dict:
    """
    Save a blog draft to ``pending_drafts/{slug}.json`` in the website repo.

    Returns {"success": True, "slug": ..., "draft": {...}} or {"success": False, "error": ...}
    """
    slug = slug or _slugify(title)
    draft = {
        "slug": slug,
        "title": title,
        "topic": topic,
        "language": language,
        "meta_title": meta_title or f"{title} — Dr. Gurjeet Singh Gill",
        "meta_description": meta_description or f"{title} — expert heart health guide by Dr. Gurjeet Singh Gill, Cardiac Physician.",
        "keywords": keywords or title,
        "content": content,
        "faq": faq or [],
        "word_count": len(str(content).split()),
        "created_at": datetime.now().isoformat(),
        "source": source,
        "status": "pending_review",
        "review_note": "",
    }

    result = _push_file_to_repo(
        _repo_path(slug),
        json.dumps(draft, ensure_ascii=False, indent=2),
        f"📥 New blog draft for review: {title[:60]} [BHARATSOLVE AI]",
    )

    if isinstance(result, dict) and "error" in result:
        log_agent_action("draft_review", f"Draft save failed: {result['error']}",
                         status="error", error_message=result["error"])
        return {"success": False, "error": result["error"], "draft": draft}

    log_agent_action("draft_review", f"Draft saved for review: {title[:50]}")
    return {"success": True, "slug": slug, "draft": draft}


# ═══════════════════════════════════════════════════════════════════════
# READ
# ═══════════════════════════════════════════════════════════════════════

def list_pending_drafts(limit: int = 20) -> List[Dict]:
    """List all pending drafts (newest first). Returns [] on any error."""
    repo = DEFAULT_CONFIG["github_repo"]
    branch = DEFAULT_CONFIG["github_branch"]

    listing = _github_api(f"/repos/{repo}/contents/{PENDING_FOLDER}?ref={branch}")
    if not isinstance(listing, list):
        return []

    drafts: List[Dict] = []
    for item in listing[:limit]:
        name = item.get("name", "")
        if not name.endswith(".json"):
            continue
        slug = name[:-5]
        draft = get_pending_draft(slug)
        if draft:
            drafts.append(draft)

    drafts.sort(key=lambda d: d.get("created_at", ""), reverse=True)
    return drafts


def get_pending_draft(slug: str) -> Optional[Dict]:
    """Fetch one pending draft by slug. Returns None if missing."""
    repo = DEFAULT_CONFIG["github_repo"]
    branch = DEFAULT_CONFIG["github_branch"]
    res = _github_api(f"/repos/{repo}/contents/{_repo_path(slug)}?ref={branch}")
    return _decode_file(res)


def pending_draft_count() -> int:
    """Cheap count of pending drafts (for dashboard badges)."""
    repo = DEFAULT_CONFIG["github_repo"]
    branch = DEFAULT_CONFIG["github_branch"]
    listing = _github_api(f"/repos/{repo}/contents/{PENDING_FOLDER}?ref={branch}")
    if not isinstance(listing, list):
        return 0
    return len([i for i in listing if str(i.get("name", "")).endswith(".json")])


# ═══════════════════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════════════════

def delete_pending_draft(slug: str, commit_message: str = "") -> Dict:
    """Remove a pending draft file from the website repo."""
    repo = DEFAULT_CONFIG["github_repo"]
    branch = DEFAULT_CONFIG["github_branch"]
    path = _repo_path(slug)

    existing = _github_api(f"/repos/{repo}/contents/{path}?ref={branch}")
    if not isinstance(existing, dict) or "sha" not in existing:
        return {"success": False, "error": f"Pending draft '{slug}' not found"}

    res = _github_api(
        f"/repos/{repo}/contents/{path}",
        method="DELETE",
        data={
            "message": commit_message or f"🗑️ Remove pending draft: {slug} [BHARATSOLVE AI]",
            "sha": existing["sha"],
            "branch": branch,
        },
    )
    if isinstance(res, dict) and "error" in res:
        return {"success": False, "error": res["error"]}
    return {"success": True}


# ═══════════════════════════════════════════════════════════════════════
# APPROVE → PUBLISH
# ═══════════════════════════════════════════════════════════════════════

def approve_and_publish_draft(
    slug: str,
    edited_title: Optional[str] = None,
    edited_content: Optional[str] = None,
) -> Dict:
    """
    Publish a reviewed draft live to the website.

    Dr. Gill may optionally pass an edited title/content — whatever is approved
    is exactly what gets published.

    Steps:
      1. Read pending draft
      2. Build final blog HTML
      3. Push blogs/{slug}.html to the live branch
      4. Delete the pending draft
      5. Rebuild catalog + homepage + sitemap + llms.txt
      6. Save to local DB
      7. Telegram confirmation
    """
    draft = get_pending_draft(slug)
    if not draft:
        return {"success": False, "error": f"Pending draft '{slug}' not found"}

    title = (edited_title or draft.get("title") or "").strip()
    content = (edited_content or draft.get("content") or "").strip()
    if not title or not content:
        return {"success": False, "error": "Draft is missing title or content"}

    blog_data = {
        "title": title,
        "meta_title": draft.get("meta_title") or f"{title} — Dr. Gurjeet Singh Gill",
        "meta_description": draft.get("meta_description") or f"Expert guide on {title} by Dr. Gurjeet Singh Gill.",
        "keywords": draft.get("keywords") or title,
        "content": content,
        "faq": draft.get("faq") or [],
    }

    blog_html = build_blog_html(blog_data, slug)
    file_path = f"blogs/{slug}.html"
    published_url = f"{DEFAULT_CONFIG['website_url']}blogs/{slug}.html"

    push = _push_file_to_repo(
        file_path, blog_html,
        f"✅ Publish reviewed blog: {title[:60]} [Dr. Gill Approved]",
    )
    if isinstance(push, dict) and "error" in push:
        log_agent_action("draft_review", f"Publish failed: {push['error']}",
                         status="error", error_message=push["error"])
        return {"success": False, "error": push["error"]}

    # Draft is consumed — remove it so it doesn't reappear for review.
    delete_pending_draft(slug, f"✅ Published approved draft: {slug} [BHARATSOLVE AI]")

    # Rebuild catalogs (non-fatal if these fail).
    catalog_warnings = []
    for step_name, step_fn in (
        ("master index", update_master_blog_index),
        ("homepage", update_homepage_articles),
        ("ai blueprint", publish_ai_geo_blueprint),
    ):
        try:
            step_fn()
        except Exception as e:
            catalog_warnings.append(f"{step_name}: {e}")

    # Local DB record.
    try:
        save_content(
            project_id=1,
            title=title,
            content=blog_html,
            content_type="blog",
            target_keyword=draft.get("topic", title),
            meta_title=blog_data["meta_title"],
            meta_description=blog_data["meta_description"],
            schema_json=json.dumps(blog_data["faq"], ensure_ascii=False),
            published_url=published_url,
        )
    except Exception as e:
        catalog_warnings.append(f"db: {e}")

    log_agent_action("draft_review", f"Approved & published: {title[:50]} → {published_url}")

    # Telegram confirmation (best-effort).
    try:
        from utils.telegram_notifier import send_publish_confirmation
        send_publish_confirmation({"title": title}, published_url)
    except Exception:
        pass

    return {
        "success": True,
        "slug": slug,
        "title": title,
        "published_url": published_url,
        "warnings": catalog_warnings,
    }


# ═══════════════════════════════════════════════════════════════════════
# REJECT
# ═══════════════════════════════════════════════════════════════════════

def reject_pending_draft(slug: str, reason: str = "") -> Dict:
    """Discard a draft without publishing it."""
    draft = get_pending_draft(slug)
    title = (draft or {}).get("title", slug)

    res = delete_pending_draft(slug, f"❌ Rejected draft: {slug} [BHARATSOLVE AI]")
    if not res.get("success"):
        return {"success": False, "error": res.get("error", "Delete failed")}

    log_agent_action("draft_review", f"Draft rejected: {title[:50]}{' — ' + reason if reason else ''}")

    try:
        from utils.telegram_notifier import send_status_alert
        send_status_alert(
            "Blog draft reject kar diya",
            f"'{title[:80]}' publish nahi hoga.{chr(10) + 'Reason: ' + reason if reason else ''}",
            ok=False,
        )
    except Exception:
        pass

    return {"success": True, "slug": slug, "title": title}
