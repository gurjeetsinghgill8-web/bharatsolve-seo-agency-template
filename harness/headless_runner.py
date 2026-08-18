"""
BHARATSOLVE SEO AGENCY — Headless Autonomous SEO Runner
🏥 Dr. Gurjeet Singh Gill — Gill Heart Clinic (Meerut & Delhi NCR)

This script can be run standalone via:
  1. python harness/headless_runner.py
  2. GitHub Actions Cron (.github/workflows/auto_seo.yml)
  3. Windows Task Scheduler / batch file
  4. Streamlit UI 1-Click Master Run

Performs:
  1. Dynamic Keyword & Intent Selection (picks unwritten query)
  2. Medical Content Generation (100% NMC & GEO compliant via Gemini/Groq)
  3. Direct GitHub Pages Push (blogs/{slug}.html)
  4. Master Catalog, index.html, sitemap.xml & llms.txt Sync
  5. Local DB Record Save + Status Logging
"""
import os
import sys
import json
import time
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from db.schema import init_db
from db.operations import log_agent_action, get_content_pieces, save_content
from agents.github_publisher import (
    auto_blog_task,
    update_master_blog_index,
    update_homepage_articles,
    publish_ai_geo_blueprint,
    _get_github_token,
    check_repo_connection
)
from agents.local_search_engine import LOCAL_SEARCH_QUERIES
from utils.llm_client import get_api_key


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

    all_queries = []
    # Priority order
    categories = ["direct_doctor", "emergency_local", "symptoms", "tests_procedures", "conditions", "lifestyle"]
    for cat in categories:
        for q in LOCAL_SEARCH_QUERIES.get(cat, []):
            all_queries.append({"category": cat, **q})

    # Pick first query that is not yet published
    for item in all_queries:
        q_text = item["query"].lower()
        already_done = any(q_text in title for title in published_titles) or any(q_text in kw for kw in published_keywords)
        if not already_done:
            return item

    # Fallback to random if all have been attempted
    import random
    return random.choice(all_queries)


def run_clinic_turbo_cycle(force_topic: str = None, language: str = "Hinglish") -> dict:
    """
    Execute the entire automated SEO cycle end-to-end.
    Returns detailed execution result dict.
    """
    init_db()
    start_time = time.time()
    print(f"\n{'='*60}")
    print(f"🚀 BHARATSOLVE GILL CLINIC AUTO-SEO ENGINE — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # Step 1: Query selection
    if force_topic:
        query_info = {"query": force_topic, "category": "custom", "intent": "high"}
    else:
        query_info = pick_next_target_query()
    
    topic = query_info["query"]
    print(f"🎯 Target Search Query: '{topic}' (Category: {query_info.get('category')})")

    # Step 2: Check API keys
    gemini_key = get_api_key("gemini")
    groq_key = get_api_key("groq")
    github_tok = _get_github_token()

    print(f"🔑 API Status -> Gemini: {'✅ Configured' if gemini_key else '❌ Missing'}, Groq: {'✅ Configured' if groq_key else '❌ Missing'}, GitHub: {'✅ Configured' if github_tok else '❌ Missing'}")

    # Step 3: Run auto blog generation & publish
    print(f"📝 Generating NMC-compliant article in {language}...")
    try:
        result = auto_blog_task(topic=topic, target_location="Meerut, Delhi NCR", auto_publish=True, language=language)
    except Exception as e:
        err_msg = f"Auto blog task exception: {e}"
        print(f"❌ Error: {err_msg}")
        log_agent_action("auto_pilot", err_msg, status="error", error_message=str(e))
        return {"status": "error", "error": err_msg, "topic": topic}

    # Step 4: Rebuild website master catalogs & AI Blueprints
    if result.get("status") == "published":
        print(f"🌐 Published Live URL: {result.get('published_url')}")
        try:
            print("🔄 Updating Master Index, Homepage Articles & AI GEO Blueprints...")
            update_master_blog_index()
            update_homepage_articles()
            publish_ai_geo_blueprint()
            print("✅ Master catalog and AI search blueprints (/llms.txt, robots.txt, sitemap.xml) updated!")
        except Exception as update_err:
            print(f"⚠️ Catalog update warning: {update_err}")

    elapsed_s = round(time.time() - start_time, 2)
    print(f"⏱️ Cycle completed in {elapsed_s}s — Final Status: {result.get('status')}")
    print(f"{'='*60}\n")
    
    result["elapsed_seconds"] = elapsed_s
    result["query_info"] = query_info
    return result


if __name__ == "__main__":
    res = run_clinic_turbo_cycle()
    print(json.dumps(res, indent=2, default=str))
