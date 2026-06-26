"""
BHARATSOLVE SEO AGENCY — Social Media UI
Create, schedule, publish, and manage social media posts.
Now with REAL platform posting via social_connectors.
"""
import streamlit as st
from datetime import datetime, timedelta
from db.operations import get_clients, get_projects, get_scheduled_posts
from agents.social_agent import (
    create_social_post, generate_content_calendar,
    test_platform_connections, get_connection_status
)
from utils.social_connectors import get_available_platforms, get_connector


def show_social_page():
    """Render social media management page."""
    user_id = st.session_state["user_id"]
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">📱 Social Media Manager</h1>
        <p style="color: #888;">AI-Powered Content for All Platforms — Auto-Publishing Enabled</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Connection Status ──
    with st.expander("🔌 Platform Connections", expanded=False):
        st.markdown("**Check which platforms are connected and ready to post**")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        platforms = [
            ("facebook", "📘", "Facebook"),
            ("instagram", "📸", "Instagram"),
            ("telegram", "✈️", "Telegram"),
            ("email", "📧", "Email"),
            ("google_business", "📍", "Google Biz"),
        ]
        
        for i, (plat, icon, name) in enumerate(platforms):
            with [col1, col2, col3, col4, col5][i]:
                status = get_connection_status(plat)
                is_ok = status.get("status") == "ok"
                st.markdown(f"""
                <div style="background: {'rgba(0,200,100,0.1)' if is_ok else 'rgba(255,100,100,0.1)'}; 
                            border-radius: 10px; padding: 1rem; text-align: center;
                            border: 1px solid {'#43e97b' if is_ok else '#ff6b6b'};">
                    <h2 style="margin: 0;">{icon}</h2>
                    <p style="font-size: 0.8rem; color: #333; margin: 0.3rem 0;"><strong>{name}</strong></p>
                    <p style="font-size: 0.7rem; color: {'green' if is_ok else 'red'}; margin: 0;">
                        {'✅ Connected' if is_ok else '❌ Not Set'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("🔄 Test All Connections", use_container_width=True):
            with st.spinner("Testing all platforms..."):
                results = test_platform_connections()
            for platform, result in results.items():
                if result.get("status") == "ok":
                    st.success(result.get("message", f"✅ {platform} OK"))
                else:
                    st.warning(result.get("message", f"⚠️ {platform} not configured"))
    
    clients = get_clients(user_id)
    if not clients:
        st.warning("⚠️ Please add a client first!")
        return
    
    # Select client and project
    col1, col2 = st.columns(2)
    with col1:
        client_names = [c['name'] for c in clients]
        selected_client = st.selectbox("Select Client", client_names, key="social_client")
        client = next(c for c in clients if c['name'] == selected_client)
    
    projects = get_projects(client['id'])
    if not projects:
        st.info("💡 Create a project first!")
        return
    
    with col2:
        proj_names = [p['name'] for p in projects]
        selected_project = st.selectbox("Select Project", proj_names, key="social_proj")
        project = next(p for p in projects if p['name'] == selected_project)
        project_id = project['id']
    
    st.markdown("---")
    
    # ── Create & Publish Post ──
    with st.expander("✍️ Create & Publish Post", expanded=True):
        st.markdown("**AI generates platform-optimized content AND publishes it live**")
        
        col1, col2 = st.columns(2)
        with col1:
            platform = st.selectbox(
                "Platform",
                ["facebook", "instagram", "telegram", "email", "google_business"],
                format_func=lambda x: {
                    "facebook": "📘 Facebook Page",
                    "instagram": "📸 Instagram",
                    "telegram": "✈️ Telegram",
                    "email": "📧 Email Newsletter",
                    "google_business": "📍 Google Business Profile"
                }[x]
            )
            content_type = st.selectbox(
                "Content Type",
                ["promotional", "educational", "engaging", "offer", "update", "testimonial"]
            )
        
        with col2:
            topic = st.text_input("Topic (optional)", placeholder="e.g., New dental services launch")
            
            # Check if this platform is configured
            connector = get_connector(platform)
            is_configured = connector and any(v for v in connector._load_credentials().values() if v and len(str(v)) > 5)
            
            if is_configured:
                st.success(f"✅ {platform.replace('_', ' ').title()} connector is active — will publish live!")
            else:
                st.warning(f"⚠️ {platform.replace('_', ' ').title()} not configured. Post will be saved as draft.")
                st.caption("Configure credentials in config.json or Streamlit secrets.")
            
            auto_publish = st.checkbox("🚀 Auto-publish to platform", value=is_configured,
                                       help="Uncheck to save as draft without publishing")
        
        if st.button("🤖 Generate & Publish Post", use_container_width=True, type="primary"):
            with st.spinner("🤖 Creating and publishing post..."):
                result = create_social_post(project_id, platform, topic, content_type, auto_publish=auto_publish)
            
            if result:
                publish_status = result.get('publish_status', 'draft')
                if publish_status == 'posted':
                    st.success(f"✅ **POST PUBLISHED LIVE!** 🎉")
                elif publish_status == 'draft':
                    st.info(f"📝 Post saved as draft")
                else:
                    st.warning(f"⚠️ Post created but publishing had issues")
                
                st.markdown("### 📱 Generated Post")
                
                # Show publish status badge
                status_badge = {
                    "posted": "🟢 LIVE",
                    "draft": "🟡 DRAFT",
                    "error": "🔴 ERROR"
                }.get(publish_status, "⚪ UNKNOWN")
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.85); border-radius: 10px; padding: 1.5rem; margin: 1rem 0;
                            border: 1px solid #90e0ef; box-shadow: 0 2px 8px rgba(0,119,182,0.06);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #0077b6;">{result.get('platform_name', 'Post')}</h4>
                        <span style="background: {'#43e97b' if publish_status == 'posted' else '#ffa502' if publish_status == 'draft' else '#ff6b6b'}; 
                                     color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">
                            {status_badge}
                        </span>
                    </div>
                    <hr style="opacity: 0.2; border-color: #90e0ef;">
                    <p style="color: #333; font-size: 1.1rem;">{result.get('content', '')}</p>
                    <hr style="opacity: 0.2; border-color: #90e0ef;">
                    <p style="color: #0077b6;">{', '.join(result.get('hashtags', []))}</p>
                    <p style="color: #e07c1f;"><strong>CTA:</strong> {result.get('cta', '')}</p>
                    <p style="color: #666;"><strong>Best Time:</strong> {result.get('best_time', '')}</p>
                """, unsafe_allow_html=True)
                
                # Show post URL if published
                if result.get('post_url'):
                    st.markdown(f"""
                    <p style="color: #0077b6;"><strong>🔗 Post URL:</strong> <a href="{result['post_url']}" target="_blank">{result['post_url'][:60]}...</a></p>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Show publish message
                if result.get('publish_message'):
                    st.caption(f"ℹ️ {result['publish_message']}")
            else:
                st.error("❌ Post creation failed!")
    
    # ── Content Calendar ──
    with st.expander("📅 Generate Content Calendar", expanded=False):
        st.markdown("**AI plans a week of social media content**")
        
        days = st.slider("Days", min_value=3, max_value=14, value=7)
        
        if st.button("🗓️ Generate Calendar", use_container_width=True):
            with st.spinner("🤖 Planning content calendar..."):
                calendar = generate_content_calendar(project_id, days)
            
            if calendar:
                st.success(f"✅ Generated {len(calendar)} days of content!")
                for day in calendar:
                    platform_icon = {
                        "google_business": "📍", "facebook": "📘", 
                        "instagram": "📸", "telegram": "✈️", "email": "📧"
                    }.get(day.get('platform', ''), "📱")
                    
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.7); border-radius: 8px; padding: 0.8rem; margin: 0.3rem 0; border: 1px solid #e0f0ff;">
                        <strong style="color: #0077b6;">Day {day.get('day', '?')}</strong>
                        {platform_icon} <strong style="color: #0077b6;">{day.get('platform', 'N/A').title()}</strong>
                        <span style="color: #666;"> | {day.get('content_type', '').title()}</span>
                        <span style="color: #0077b6; float: right; font-size: 0.8rem;">🎯 {day.get('goal', '')}</span>
                        <p style="color: #555; margin: 0.3rem 0 0 0; font-size: 0.9rem;">
                            📌 {day.get('post_preview', '')[:120]}...
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("❌ Calendar generation failed!")
    
    st.markdown("---")
    
    # ── Scheduled & Published Posts ──
    st.markdown("### 📅 Post History")
    scheduled = get_scheduled_posts(project_id)
    
    if scheduled:
        tab1, tab2 = st.tabs(["📋 All Posts", "✅ Published"])
        
        with tab1:
            for post in scheduled:
                platform_icons = {
                    "google_business": "📍", "facebook": "📘", 
                    "instagram": "📸", "telegram": "✈️", "email": "📧"
                }
                icon = platform_icons.get(post['platform'], "📱")
                
                status_color = {
                    "scheduled": "#ffa502",
                    "posted": "#43e97b",
                    "published": "#43e97b",
                    "failed": "#ff6b6b",
                    "draft": "#888"
                }.get(post['status'], "#888")
                
                status_icon = {
                    "scheduled": "🟡",
                    "posted": "🟢",
                    "published": "🟢",
                    "failed": "🔴",
                    "draft": "⚪"
                }.get(post['status'], "⚪")
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.7); border-radius: 8px; padding: 0.8rem 1rem; margin: 0.4rem 0;
                            border-left: 3px solid {status_color}; box-shadow: 0 2px 6px rgba(0,119,182,0.06);">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong style="color: #333;">{icon} {post['platform'].replace('_', ' ').title()}</strong>
                            <p style="color: #555; margin: 0.3rem 0 0 0;">{post['content'][:100]}...</p>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: {status_color}; font-size: 0.9rem;">{status_icon} {post['status'].upper()}</span>
                            <br>
                            <span style="color: #666; font-size: 0.8rem;">
                                {post.get('scheduled_for', 'N/A')[:10] if post.get('scheduled_for') else ''}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with tab2:
            published = [p for p in scheduled if p['status'] in ('posted', 'published')]
            if published:
                for post in published:
                    st.markdown(f"✅ **{post['platform'].replace('_', ' ').title()}** — {post['content'][:80]}...")
            else:
                st.info("💡 No published posts yet. Create and auto-publish posts above!")
    else:
        st.info("💡 No posts yet. Create your first post above!")
