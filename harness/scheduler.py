"""
BHARATSOLVE SEO AGENCY — Task Scheduler v2
Multi-mode scheduler:
  - APScheduler background threads (local dev)
  - Timestamp-based on-load runner (Streamlit Cloud compatible)
  - Manual single-run via UI button

Supports: keyword research, rank tracking, social posting, email campaigns,
          WordPress publishing, Google Business posts, content generation.
"""
import json
import os
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from db.operations import (
    get_all_projects, log_agent_action,
    get_agent_logs, get_agent_status_summary
)

logger = logging.getLogger(__name__)

# ── Cloud detection ──
_IS_CLOUD = os.environ.get('STREAMLIT_RUNNER_ID') is not None

# ── State tracking for timestamp-based cloud scheduler ──
_SCHEDULER_STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".scheduler_state.json"
)
if _IS_CLOUD:
    _SCHEDULER_STATE_FILE = "/tmp/.scheduler_state.json"

# ── APScheduler (local only) ──
_apscheduler = None
_apscheduler_running = False

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════
# SCHEDULER STATE PERSISTENCE (for cloud timestamp mode)
# ═══════════════════════════════════════════════════════════════

def _load_scheduler_state() -> Dict[str, Any]:
    """Load last-run timestamps from state file."""
    try:
        if os.path.exists(_SCHEDULER_STATE_FILE):
            with open(_SCHEDULER_STATE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}


def _save_scheduler_state(state: Dict[str, Any]):
    """Save last-run timestamps to state file."""
    try:
        with open(_SCHEDULER_STATE_FILE, 'w') as f:
            json.dump(state, f)
    except:
        pass


def _get_last_run(task_name: str) -> Optional[datetime]:
    """Get the last run time for a task."""
    state = _load_scheduler_state()
    ts = state.get(task_name)
    if ts:
        try:
            return datetime.fromisoformat(ts)
        except:
            pass
    return None


def _set_last_run(task_name: str):
    """Record the current time as the last run for a task."""
    state = _load_scheduler_state()
    state[task_name] = datetime.now().isoformat()
    _save_scheduler_state(state)


def _is_task_due(task_name: str, interval_hours: int) -> bool:
    """Check if a task is due to run again based on its interval."""
    last_run = _get_last_run(task_name)
    if last_run is None:
        return True
    return datetime.now() - last_run > timedelta(hours=interval_hours)


# ═══════════════════════════════════════════════════════════════
# TASK FUNCTIONS — Each can run independently
# ═══════════════════════════════════════════════════════════════

def run_keyword_research(project_id: Optional[int] = None):
    """Batch keyword research for all or one project."""
    from agents.keyword_agent import research_keywords
    
    projects = get_all_projects()
    if project_id:
        projects = [p for p in projects if p['id'] == project_id]
    
    results = []
    for p in projects:
        try:
            research_keywords(p['id'])
            log_agent_action("keyword", f"Scheduled research for project {p['id']}")
            results.append({"project_id": p['id'], "status": "ok"})
        except Exception as e:
            log_agent_action("keyword", f"Research failed for project {p['id']}", 
                            status="error", error_message=str(e))
            results.append({"project_id": p['id'], "status": "error", "error": str(e)})
    
    return results


def run_rank_check(project_id: Optional[int] = None, simulate: bool = True):
    """Batch rank checking for all or one project."""
    from agents.rank_agent import check_rankings
    
    projects = get_all_projects()
    if project_id:
        projects = [p for p in projects if p['id'] == project_id]
    
    results = []
    for p in projects:
        try:
            check_rankings(p['id'], simulate=simulate)
            log_agent_action("rank", f"Checked rankings for project {p['id']}")
            results.append({"project_id": p['id'], "status": "ok"})
        except Exception as e:
            log_agent_action("rank", f"Rank check failed for project {p['id']}",
                            status="error", error_message=str(e))
            results.append({"project_id": p['id'], "status": "error", "error": str(e)})
    
    return results


def run_social_posting(project_id: Optional[int] = None):
    """Post scheduled social media content."""
    from agents.social_agent import create_social_post
    
    projects = get_all_projects()
    if project_id:
        projects = [p for p in projects if p['id'] == project_id]
    
    results = []
    platforms = ["google_business", "facebook", "instagram", "telegram"]
    
    for p in projects:
        for platform in platforms:
            try:
                create_social_post(p['id'], platform, content_type="update")
                log_agent_action("social", f"Posted to {platform} for project {p['id']}")
                results.append({"project_id": p['id'], "platform": platform, "status": "ok"})
            except Exception as e:
                log_agent_action("social", f"Social post to {platform} failed",
                                status="error", error_message=str(e))
                results.append({"project_id": p['id'], "platform": platform, 
                               "status": "error", "error": str(e)})
    
    return results


def run_email_campaigns():
    """Run scheduled email campaigns (weekly digest, newsletters)."""
    from agents.email_agent import send_weekly_digest
    
    projects = get_all_projects()
    # Get unique user IDs
    user_ids = set(p.get('user_id', 0) for p in projects if p.get('user_id'))
    
    results = []
    for uid in user_ids:
        try:
            send_weekly_digest(uid)
            log_agent_action("email", f"Weekly digest sent to user {uid}")
            results.append({"user_id": uid, "status": "ok"})
        except Exception as e:
            log_agent_action("email", f"Digest failed for user {uid}",
                            status="error", error_message=str(e))
            results.append({"user_id": uid, "status": "error", "error": str(e)})
    
    return results


def run_wordpress_publish():
    """Auto-publish draft content to WordPress."""
    try:
        from agents.wordpress_agent import publish_content_piece
        from db.operations import get_unpublished_content, get_wp_sites, get_single_content
        
        sites = get_wp_sites()
        if not sites:
            return []
        
        results = []
        for site in sites:
            # Get unpublished content for each site (try all projects)
            projects = get_all_projects()
            for p in projects[:3]:  # Limit to 3 projects to avoid overload
                unpublished = get_unpublished_content(p['id'], limit=5)
                for content in unpublished[:2]:  # Max 2 per project per run
                    try:
                        result = publish_content_piece(
                            content_id=content['id'],
                            site_id=site['id'],
                            status="draft"  # Save as draft, review before live
                        )
                        if result.get('success'):
                            log_agent_action("wordpress", 
                                f"Auto-published '{content.get('title', '')[:30]}' to {site['site_name']}")
                        results.append({"content_id": content['id'], "status": result.get('success')})
                    except Exception as e:
                        log_agent_action("wordpress", "Auto-publish failed", 
                                        status="error", error_message=str(e))
        
        return results
    except Exception as e:
        logger.error(f"WordPress auto-publish error: {e}")
        return []


def run_gbp_posting():
    """Auto-post to Google Business Profile."""
    try:
        from utils.social_connectors import get_connector
        
        connector = get_connector("google_business")
        if not connector or not connector.connect():
            return []
        
        projects = get_all_projects()
        results = []
        
        for p in projects[:5]:
            try:
                # Create a business update post
                from agents.social_agent import create_social_post
                create_social_post(p['id'], "google_business", content_type="update")
                log_agent_action("google_business", f"GBP auto-post for project {p['id']}")
                results.append({"project_id": p['id'], "status": "ok"})
            except Exception as e:
                results.append({"project_id": p['id'], "status": "error", "error": str(e)})
        
        return results
    except Exception as e:
        logger.error(f"GBP auto-post error: {e}")
        return []


def run_all_agents():
    """Run ALL agents once (comprehensive run)."""
    print(f"🚀 Running all agents at {datetime.now().isoformat()}")
    
    all_results = {}
    
    # Keyword research
    all_results['keyword'] = run_keyword_research()
    
    # Rank checking
    all_results['rank'] = run_rank_check(simulate=True)
    
    # Social posting (first platform only to avoid rate limits)
    try:
        from agents.social_agent import create_social_post
        projects = get_all_projects()
        for p in projects:
            try:
                create_social_post(p['id'], "google_business", content_type="update")
            except:
                pass
        all_results['social'] = "ok"
    except:
        all_results['social'] = "skipped"
    
    # Email digests (only if configured)
    try:
        all_results['email'] = run_email_campaigns()
    except:
        all_results['email'] = "skipped"
    
    # WordPress auto-publish
    try:
        all_results['wordpress'] = run_wordpress_publish()
    except:
        all_results['wordpress'] = "skipped"
    
    # Cloud backup
    try:
        from utils.cloud_backup import auto_backup
        backup_result = auto_backup()
        all_results['backup'] = "ok" if backup_result.get('success') else "failed"
    except:
        all_results['backup'] = "skipped"
    
    print(f"✅ All agents completed at {datetime.now().isoformat()}")
    log_agent_action("scheduler", "run_all_agents completed", status="ok")
    
    return all_results


# ═══════════════════════════════════════════════════════════════
# SCHEDULER CONTROLLERS
# ═══════════════════════════════════════════════════════════════

def start_apscheduler():
    """
    Start APScheduler (local development only).
    Uses interval-based scheduling for all agent tasks.
    """
    global _apscheduler, _apscheduler_running
    
    if not APSCHEDULER_AVAILABLE:
        print("⚠️ APScheduler not installed. Install with: pip install apscheduler")
        return False
    
    if _apscheduler_running:
        return True
    
    _apscheduler = BackgroundScheduler()
    
    # ── Agent schedules (from config if available) ──
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "config.json")) as f:
            config = json.load(f)
        agents_config = config.get("agents", {})
    except:
        agents_config = {}
    
    # Keyword research — every 24h
    kw_interval = agents_config.get("keyword", {}).get("interval_hours", 24)
    _apscheduler.add_job(run_keyword_research, 'interval', hours=kw_interval,
                         id='keyword_research', replace_existing=True)
    
    # Rank check — every 6h
    rk_interval = agents_config.get("rank", {}).get("interval_hours", 6)
    _apscheduler.add_job(lambda: run_rank_check(simulate=True), 'interval', hours=rk_interval,
                         id='rank_check', replace_existing=True)
    
    # Social posts — every 8h
    _apscheduler.add_job(run_social_posting, 'interval', hours=8,
                         id='social_posts', replace_existing=True)
    
    # Email campaigns — daily
    _apscheduler.add_job(run_email_campaigns, 'interval', hours=24,
                         id='email_campaigns', replace_existing=True)
    
    # WordPress auto-publish — every 12h
    _apscheduler.add_job(run_wordpress_publish, 'interval', hours=12,
                         id='wp_publish', replace_existing=True)
    
    # Daily full run at 3 AM
    _apscheduler.add_job(run_all_agents, 'cron', hour=3, minute=0,
                         id='daily_full_run', replace_existing=True)
    
    _apscheduler.start()
    _apscheduler_running = True
    print("✅ APScheduler started — all agent tasks scheduled")
    return True


def stop_apscheduler():
    """Stop APScheduler."""
    global _apscheduler, _apscheduler_running
    if _apscheduler and _apscheduler_running:
        _apscheduler.shutdown(wait=False)
        _apscheduler_running = False
        print("⏹️ APScheduler stopped")


def try_cloud_tasks():
    """
    Run due tasks on Streamlit Cloud.
    Called on each page load — checks if tasks are due via timestamps.
    Lightweight: only runs if interval has elapsed.
    """
    if not _IS_CLOUD:
        return []
    
    ran_tasks = []
    
    # ── Check each task ──
    task_schedule = [
        ("rank_check", 6, lambda: run_rank_check(simulate=True)),
        ("keyword_research", 24, run_keyword_research),
        ("social_posting", 8, run_social_posting),
        ("email_digest", 24, run_email_campaigns),
        ("wp_auto_publish", 12, run_wordpress_publish),
    ]
    
    for task_name, interval_hours, task_fn in task_schedule:
        if _is_task_due(task_name, interval_hours):
            try:
                print(f"⏰ Cloud scheduler: Running {task_name} (due every {interval_hours}h)")
                task_fn()
                _set_last_run(task_name)
                ran_tasks.append(task_name)
            except Exception as e:
                logger.error(f"Cloud scheduler: {task_name} failed: {e}")
    
    if ran_tasks:
        print(f"✅ Cloud scheduler ran: {', '.join(ran_tasks)}")
    
    return ran_tasks


def get_task_status() -> List[Dict]:
    """Get status of all scheduled tasks and their last run times."""
    tasks = [
        "rank_check", "keyword_research", "social_posting",
        "email_digest", "wp_auto_publish"
    ]
    
    statuses = []
    for task in tasks:
        last_run = _get_last_run(task)
        statuses.append({
            "task": task,
            "display_name": task.replace('_', ' ').title(),
            "last_run": last_run.isoformat() if last_run else "Never",
            "last_run_ago": str(datetime.now() - last_run).split('.')[0] + " ago" 
                           if last_run else "—"
        })
    
    return statuses


def get_scheduler_mode() -> str:
    """Return the current scheduler mode."""
    if _IS_CLOUD:
        return "cloud_timestamp"
    elif APSCHEDULER_AVAILABLE:
        return "apscheduler"
    else:
        return "manual_only"


# ── Auto-start on import (local only) ──
if not _IS_CLOUD and APSCHEDULER_AVAILABLE:
    start_apscheduler()
