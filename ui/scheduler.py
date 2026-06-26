"""
BHARATSOLVE SEO AGENCY — Scheduler Management UI
View task status, manually trigger agents, configure schedules.
Works on both local and Streamlit Cloud.
"""
import streamlit as st
import os
from datetime import datetime

from harness.scheduler import (
    run_keyword_research, run_rank_check, run_social_posting,
    run_email_campaigns, run_wordpress_publish, run_all_agents,
    try_cloud_tasks, get_task_status, get_scheduler_mode,
    APSCHEDULER_AVAILABLE
)
from harness.auto_pilot import (
    run_auto_pilot, stop_auto_pilot, is_auto_pilot_running,
    get_auto_pilot_status
)
from db.operations import get_agent_logs, get_agent_status_summary


def show_scheduler_page():
    """Render the scheduler management page."""
    user_id = st.session_state["user_id"]
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">⏰ Scheduler & Automations</h1>
        <p style="color: #888;">Manage background tasks, auto-pilot, and agent scheduling</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Mode indicator ──
    mode = get_scheduler_mode()
    is_cloud = os.environ.get('STREAMLIT_RUNNER_ID') is not None
    
    mode_labels = {
        "apscheduler": "🖥️ **Local Mode** — APScheduler running with background threads",
        "cloud_timestamp": "☁️ **Streamlit Cloud Mode** — Timestamp-based task runner (runs on page load)",
        "manual_only": "⚠️ **Manual Only** — Install APScheduler for automatic scheduling"
    }
    
    st.info(mode_labels.get(mode, f"Mode: {mode}"))
    
    st.markdown("---")
    
    # ════════════════════════════════════════
    # TAB LAYOUT
    # ════════════════════════════════════════
    tab1, tab2, tab3 = st.tabs(["🤖 Run Agents", "📋 Task Status", "📜 Agent Logs"])
    
    # ════════════════════════════════════════
    # TAB 1: Run Agents
    # ════════════════════════════════════════
    with tab1:
        st.markdown("### 🚀 Manual Agent Triggers")
        st.markdown("Click a button to run an agent immediately.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🔑 Keyword Research**")
            if st.button("Run Keyword Research", use_container_width=True, key="run_kw"):
                with st.spinner("Running keyword research..."):
                    results = run_keyword_research()
                st.success(f"✅ Done! Processed {len(results)} projects")
                for r in results[:5]:
                    emoji = "✅" if r['status'] == 'ok' else '❌'
                    st.markdown(f"{emoji} Project {r['project_id']}")
            
            st.markdown("**📊 Rank Tracking**")
            if st.button("Run Rank Check", use_container_width=True, key="run_rank"):
                with st.spinner("Checking rankings..."):
                    results = run_rank_check(simulate=True)
                st.success(f"✅ Done! Checked {len(results)} projects")
        
        with col2:
            st.markdown("**📱 Social Posts**")
            if st.button("Run Social Posting", use_container_width=True, key="run_social"):
                with st.spinner("Posting to social platforms..."):
                    results = run_social_posting()
                st.success(f"✅ Done! {len(results)} posts attempted")
            
            st.markdown("**📧 Email Campaigns**")
            if st.button("Run Email Campaigns", use_container_width=True, key="run_email"):
                with st.spinner("Sending email campaigns..."):
                    results = run_email_campaigns()
                st.success(f"✅ Done! {len(results)} campaigns triggered")
        
        with col3:
            st.markdown("**🌐 WordPress Publish**")
            if st.button("Run WP Auto-Publish", use_container_width=True, key="run_wp"):
                with st.spinner("Publishing to WordPress..."):
                    results = run_wordpress_publish()
                st.success(f"✅ Done! {len(results)} content pieces processed")
            
            st.markdown("**🔄 All Agents**")
            if st.button("🔥 Run ALL Agents", type="primary", use_container_width=True, key="run_all"):
                with st.spinner("Running all agents..."):
                    results = run_all_agents()
                st.success("✅ All agents completed!")
                for agent, result in results.items():
                    status = "✅" if result and result != "skipped" else "⏭️"
                    st.markdown(f"{status} {agent}: {str(result)[:50]}")
        
        st.markdown("---")
        
        # ── Auto-Pilot Section ──
        st.markdown("### 🤖 Auto-Pilot")
        
        auto_status = get_auto_pilot_status()
        
        if not is_cloud:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("▶️ Start Auto-Pilot", type="primary", use_container_width=True):
                    msg = run_auto_pilot(60)
                    st.success(msg)
            
            with col2:
                if st.button("⏹️ Stop Auto-Pilot", use_container_width=True):
                    msg = stop_auto_pilot()
                    st.info(msg)
            
            with col3:
                is_running = is_auto_pilot_running()
                st.markdown(f"**Status:** {'🟢 Running' if is_running else '🔴 Stopped'}")
        else:
            st.info("☁️ On Streamlit Cloud, auto-pilot runs automatically on page loads.")
            if st.button("🔄 Check & Run Due Tasks", use_container_width=True):
                ran = try_cloud_tasks()
                if ran:
                    st.success(f"✅ Ran: {', '.join(ran)}")
                else:
                    st.info("⏰ No tasks due yet")
        
        st.markdown(f"**Scheduler Mode:** {mode}")
        st.markdown(f"**APScheduler Available:** {'✅ Yes' if APSCHEDULER_AVAILABLE else '❌ No'}")
    
    # ════════════════════════════════════════
    # TAB 2: Task Status
    # ════════════════════════════════════════
    with tab2:
        st.markdown("### 📊 Scheduled Task Status")
        
        task_statuses = get_task_status()
        
        if task_statuses:
            for task in task_statuses:
                with st.container():
                    c1, c2, c3 = st.columns([2, 2, 2])
                    c1.markdown(f"**{task['display_name']}**")
                    c2.markdown(f"🕐 Last: {task.get('last_run_ago', '—')}")
                    c3.markdown(f"📅 {task.get('last_run', '—')[:19]}")
                    st.markdown("---")
        else:
            st.info("💡 No task history yet. Run some tasks first!")
        
        st.markdown("---")
        
        # Agent health summary
        st.markdown("### 💚 Agent Health")
        health = get_agent_status_summary()
        
        if health:
            for h in health:
                emoji = "✅" if h['status'] == 'ok' else '❌'
                st.markdown(f"{emoji} **{h['agent_name']}**: {h['status']} "
                           f"({h.get('response_time_ms', 0)}ms) — {h.get('logged_at', '')[:19]}")
        else:
            st.info("💡 No agent activity yet.")
    
    # ════════════════════════════════════════
    # TAB 3: Agent Logs
    # ════════════════════════════════════════
    with tab3:
        st.markdown("### 📜 Recent Agent Activity")
        
        logs = get_agent_logs(limit=100)
        
        if logs:
            # Filter
            agent_names = list(set(l['agent_name'] for l in logs))
            filter_agent = st.selectbox("Filter by Agent", ["All"] + sorted(agent_names))
            
            if filter_agent != "All":
                logs = [l for l in logs if l['agent_name'] == filter_agent]
            
            for log in logs:
                emoji = "✅" if log['status'] == 'ok' else ('❌' if log['status'] == 'error' else '⚠️')
                st.markdown(f"""
                {emoji} **{log['agent_name']}** — {log.get('task', '')[:60]}  
                └ Status: {log['status']} | {log.get('response_time_ms', 0)}ms | {log.get('logged_at', '')[:19]}
                """)
                
                if log.get('error_message'):
                    st.markdown(f"  └ ❌ Error: {log['error_message'][:100]}")
        else:
            st.info("💡 No agent logs yet. Run some agents to see activity here.")
