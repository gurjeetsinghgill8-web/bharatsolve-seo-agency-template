"""
BHARATSOLVE SEO AGENCY — Content Publisher UI
WordPress auto-publish with site management and batch publishing.
"""
import streamlit as st
from db.operations import (
    get_clients, get_projects, get_content, get_wp_sites, save_wp_site,
    get_wp_site, delete_wp_site, update_content_publish_status,
    get_unpublished_content, get_published_content, get_single_content
)
from agents.wordpress_agent import (
    publish_post, publish_content_piece, publish_batch_content,
    test_connection, get_site_categories
)


def show_publisher_page():
    """Render the content publisher page."""
    user_id = st.session_state["user_id"]
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">🌐 Content Publisher</h1>
        <p style="color: #888;">Auto-publish SEO content to WordPress sites</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["⚙️ WordPress Sites", "📤 Publish Content", "📋 Published History"])
    
    # ════════════════════════════════════════════
    # TAB 1: WordPress Site Management
    # ════════════════════════════════════════════
    with tab1:
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("### Your WordPress Sites")
            sites = get_wp_sites(user_id)
            
            if sites:
                for site in sites:
                    with st.container():
                        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                        masked_pass = site['password_encrypted'][:8] + "..." if len(site['password_encrypted']) > 8 else "****"
                        
                        c1.markdown(f"""
                        **{site['site_name']}**  
                        🌐 {site['url']}  
                        👤 {site['username']} / 🔑 {masked_pass}
                        """)
                        
                        if c2.button("🔍 Test", key=f"test_{site['id']}"):
                            with st.spinner("Testing connection..."):
                                result = test_connection(site['id'])
                            if result.get('success'):
                                st.success(f"✅ Connected! ({result.get('response_time_ms', 0)}ms)")
                                if result.get('recent_posts') is not None:
                                    st.info(f"📝 {result['recent_posts']} recent posts, {result.get('total_categories', 0)} categories")
                            else:
                                st.error(f"❌ {result.get('error', 'Connection failed')}")
                        
                        if c3.button("🗑️", key=f"del_{site['id']}"):
                            delete_wp_site(site['id'])
                            st.success(f"🗑️ Removed {site['site_name']}")
                            st.rerun()
                        
                        if c4.button("📋", key=f"cats_{site['id']}"):
                            cats = get_site_categories(site['id'])
                            if cats:
                                st.info(f"📂 Categories: {', '.join(c['name'] for c in cats[:10])}")
                            else:
                                st.warning("Could not fetch categories")
                        
                        st.markdown("---")
            else:
                st.info("💡 No WordPress sites configured yet. Add one below!")
        
        with col2:
            st.markdown("### ➕ Add WordPress Site")
            
            with st.form("add_wp_site"):
                site_name = st.text_input("Site Name", placeholder="e.g., My Blog")
                site_url = st.text_input("Site URL", placeholder="https://example.com")
                wp_username = st.text_input("Username", placeholder="admin")
                wp_password = st.text_input("Application Password", type="password",
                                             help="Use an Application Password (WP Admin > Users > Application Passwords)")
                xmlrpc_url = st.text_input("XML-RPC URL (optional)", 
                                            placeholder="https://example.com/xmlrpc.php")
                
                submitted = st.form_submit_button("💾 Save Site", type="primary", use_container_width=True)
                
                if submitted:
                    if site_name and site_url and wp_username and wp_password:
                        # Simple encryption for stored password (basic XOR + base64)
                        # In production, use the app's secure_vault
                        try:
                            from secure_vault import encrypt_data
                            encrypted_pass = encrypt_data(wp_password)
                        except:
                            # Fallback: basic reversible encoding
                            import base64
                            encrypted_pass = base64.b64encode(wp_password.encode()).decode()
                        
                        if not xmlrpc_url:
                            xmlrpc_url = site_url.rstrip('/') + "/xmlrpc.php"
                        
                        site_id = save_wp_site(
                            user_id=user_id,
                            site_name=site_name,
                            url=site_url.rstrip('/'),
                            username=wp_username,
                            password_encrypted=encrypted_pass,
                            xmlrpc_url=xmlrpc_url
                        )
                        st.success(f"✅ WordPress site '{site_name}' saved! (ID: {site_id})")
                        st.rerun()
                    else:
                        st.error("❌ Please fill all required fields!")
            
            st.markdown("---")
            st.markdown("""
            **💡 How to get Application Password:**
            1. Go to WP Admin → Users → Your Profile
            2. Scroll to "Application Passwords"
            3. Enter a name (e.g., "BHARATSOLVE SEO")
            4. Copy the generated password (looks like: `xxxx xxxx xxxx xxxx xxxx xxxx`)
            """)
    
    # ════════════════════════════════════════════
    # TAB 2: Publish Content
    # ════════════════════════════════════════════
    with tab2:
        sites = get_wp_sites(user_id)
        if not sites:
            st.warning("⚠️ Please add a WordPress site first in the 'WordPress Sites' tab!")
            st.stop()
        
        # Select site
        site_names = [f"{s['site_name']} ({s['url']})" for s in sites]
        selected_site_str = st.selectbox("Select WordPress Site", site_names, key="pub_site")
        selected_idx = site_names.index(selected_site_str)
        selected_site = sites[selected_idx]
        
        # Select client/project
        clients = get_clients(user_id)
        if not clients:
            st.warning("⚠️ Please add a client first!")
            st.stop()
        
        col1, col2 = st.columns(2)
        with col1:
            client_names = [c['name'] for c in clients]
            selected_client = st.selectbox("Select Client", client_names, key="pub_client")
            client = next(c for c in clients if c['name'] == selected_client)
        
        projects = get_projects(client['id'])
        if not projects:
            st.info("💡 Create a project first!")
            st.stop()
        
        with col2:
            proj_names = [p['name'] for p in projects]
            selected_project = st.selectbox("Select Project", proj_names, key="pub_proj")
            project = next(p for p in projects if p['name'] == selected_project)
            project_id = project['id']
        
        st.markdown("---")
        
        # ── Publish Section ──
        pub_col1, pub_col2 = st.columns([2, 1])
        
        with pub_col1:
            st.markdown("#### 📄 Select Content to Publish")
            
            # Show unpublished content
            unpublished = get_unpublished_content(project_id, limit=50)
            
            if unpublished:
                content_options = {
                    c['id']: f"{c['title'][:60]}... ({c.get('content_type', 'blog').title()})"
                    for c in unpublished
                }
                
                selected_ids = st.multiselect(
                    "Select content pieces to publish",
                    options=list(content_options.keys()),
                    format_func=lambda x: content_options[x],
                    default=[unpublished[0]['id']] if unpublished else []
                )
                
                if selected_ids:
                    st.markdown("**📋 Selected Content:**")
                    for cid in selected_ids:
                        c = next((c for c in unpublished if c['id'] == cid), None)
                        if c:
                            st.markdown(f"""
                            - **{c['title'][:60]}**  
                              └ Keyword: `{c.get('target_keyword', 'N/A')}` | Words: {c.get('word_count', 0)}
                            """)
            else:
                st.info("💡 All content has been published! Generate new content first.")
        
        with pub_col2:
            st.markdown("#### ⚙️ Publish Options")
            
            publish_mode = st.radio(
                "Publish Mode",
                ["🟢 Publish Live", "📝 Save as Draft"],
                index=0
            )
            publish_status = "publish" if "Live" in publish_mode else "draft"
            
            # Quick publish individual content
            st.markdown("#### 🚀 Quick Publish")
            st.markdown("*Select content above, then publish*")
            
            if st.button("▶️ Publish Selected", type="primary", use_container_width=True):
                if selected_ids:
                    with st.spinner(f"📤 Publishing {len(selected_ids)} pieces to WordPress..."):
                        if len(selected_ids) == 1:
                            result = publish_content_piece(
                                content_id=selected_ids[0],
                                site_id=selected_site['id'],
                                status=publish_status
                            )
                            results = [result]
                        else:
                            results = publish_batch_content(
                                content_ids=selected_ids,
                                site_id=selected_site['id'],
                                status=publish_status
                            )
                    
                    # Show results
                    success_count = sum(1 for r in results if r.get('success'))
                    fail_count = sum(1 for r in results if not r.get('success'))
                    
                    if success_count > 0:
                        st.success(f"✅ Published {success_count} piece(s) successfully!")
                    if fail_count > 0:
                        st.error(f"❌ {fail_count} piece(s) failed")
                    
                    for r in results:
                        if r.get('success'):
                            st.markdown(f"✅ **Published:** [View Post]({r.get('url', '#')}) 🆔 {r.get('post_id', '')}")
                        else:
                            st.markdown(f"❌ **Failed:** {r.get('error', 'Unknown error')}")
        st.markdown("---")
        
        # ── Single Content Quick Publish ──
        with st.expander("📝 Publish Single Content by ID", expanded=False):
            content_id = st.number_input("Content ID", min_value=1, step=1)
            if st.button("📤 Publish This Piece", use_container_width=True):
                if content_id:
                    with st.spinner("Publishing..."):
                        result = publish_content_piece(content_id, selected_site['id'], publish_status)
                    if result.get('success'):
                        st.success(f"✅ Published! [View Post]({result.get('url', '#')})")
                    else:
                        st.error(f"❌ {result.get('error', 'Publish failed')}")
    
    # ════════════════════════════════════════════
    # TAB 3: Published History
    # ════════════════════════════════════════════
    with tab3:
        clients = get_clients(user_id)
        if not clients:
            st.info("💡 No clients yet.")
            st.stop()
        
        col1, col2 = st.columns(2)
        with col1:
            client_names = [c['name'] for c in clients]
            selected_client = st.selectbox("Select Client", client_names, key="hist_client")
            client = next(c for c in clients if c['name'] == selected_client)
        
        projects = get_projects(client['id'])
        if projects:
            with col2:
                proj_names = [p['name'] for p in projects]
                selected_project = st.selectbox("Select Project", proj_names, key="hist_proj")
                project = next(p for p in projects if p['name'] == selected_project)
                project_id = project['id']
            
            st.markdown("---")
            
            published = get_published_content(project_id, limit=50)
            
            if published:
                st.markdown(f"### 📋 Published Content ({len(published)} pieces)")
                
                for c in published:
                    with st.expander(f"✅ {c['title'][:60]}..."):
                        st.markdown(f"""
                        **Type:** {c.get('content_type', 'blog').title()}  
                        **Keyword:** {c.get('target_keyword', 'N/A')}  
                        **Words:** {c.get('word_count', 0)}  
                        **Published:** {c.get('created_at', 'N/A')}  
                        **URL:** {c.get('published_url', 'N/A')}
                        """)
                        
                        if c.get('published_url'):
                            st.markdown(f"🔗 [Open Published Post]({c['published_url']})", unsafe_allow_html=True)
                        
                        if c.get('content'):
                            with st.expander("📄 View Content"):
                                st.markdown(c['content'], unsafe_allow_html=True)
            else:
                st.info("💡 No published content yet. Use the 'Publish Content' tab to publish!")
