"""
BHARATSOLVE SEO AGENCY — Auto-Pilot Mode v2
Self-healing autonomous agent runner.

Modes:
  1. Local: Background thread loop with APScheduler
  2. Streamlit Cloud: Timestamp-based task runner (runs on page load)
  3. Manual: Single-run via UI button

Integrates with enhanced scheduler (scheduler.py v2) for all agent tasks.
"""
import time
import threading
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from db.operations import log_agent_action, get_agent_status_summary
from harness.scheduler import (
    run_all_agents, try_cloud_tasks, get_task_status,
    get_scheduler_mode, _IS_CLOUD
)

logger = logging.getLogger(__name__)

_auto_pilot_active = False
_auto_pilot_thread = None


def run_auto_pilot(interval_minutes: int = 60):
    """
    Start auto-pilot mode.
    
    - Local: Runs all agents in a background loop with self-healing.
    - Cloud: Checks due tasks via timestamp-based scheduler.
    
    Args:
        interval_minutes: How often to run the full cycle (local only).
    """
    global _auto_pilot_active, _auto_pilot_thread
    
    if _auto_pilot_active:
        return "Auto-pilot is already running"
    
    # ── Cloud mode: just run due tasks and return ──
    if _IS_CLOUD:
        ran = try_cloud_tasks()
        if ran:
            return f"✅ Cloud auto-pilot ran: {', '.join(ran)}"
        else:
            return "⏰ Cloud auto-pilot checked — no tasks due yet"
    
    # ── Local mode: background thread loop ──
    _auto_pilot_active = True
    
    def _loop():
        cycle = 0
        while _auto_pilot_active:
            cycle += 1
            print(f"\n{'='*50}")
            print(f"🔄 Auto-Pilot Cycle {cycle} at {datetime.now().isoformat()}")
            print(f"{'='*50}")
            
            try:
                run_all_agents()
                log_agent_action("auto_pilot", f"Completed cycle {cycle}", response_time_ms=0)
            except Exception as e:
                log_agent_action("auto_pilot", f"Cycle {cycle} failed", 
                                status="error", error_message=str(e))
                print(f"❌ Cycle {cycle} failed: {e}")
            
            # Check agent health
            statuses = get_agent_status_summary()
            for s in statuses:
                if s['status'] == 'error':
                    print(f"⚠️ Agent {s['agent_name']} error: {s.get('error_message', '')[:100]}")
            
            # Wait between cycles (check every 10s if we should stop)
            for _ in range(interval_minutes * 6):
                if not _auto_pilot_active:
                    break
                time.sleep(10)
    
    _auto_pilot_thread = threading.Thread(target=_loop, daemon=True)
    _auto_pilot_thread.start()
    
    return f"✅ Auto-pilot started! Running every {interval_minutes} minutes."


def stop_auto_pilot():
    """Stop auto-pilot mode (local only)."""
    global _auto_pilot_active
    _auto_pilot_active = False
    log_agent_action("auto_pilot", "Auto-pilot stopped")
    return "⏹️ Auto-pilot stopped."


def is_auto_pilot_running() -> bool:
    """Check if auto-pilot is currently running."""
    return _auto_pilot_active


def get_auto_pilot_status() -> Dict[str, Any]:
    """Get detailed status of auto-pilot system."""
    return {
        "mode": get_scheduler_mode(),
        "is_cloud": _IS_CLOUD,
        "is_running": _auto_pilot_active if not _IS_CLOUD else "cloud_mode",
        "task_statuses": get_task_status(),
        "last_agent_statuses": get_agent_status_summary(),
    }
