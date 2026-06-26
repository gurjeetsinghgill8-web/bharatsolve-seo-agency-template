"""
BHARATSOLVE SEO AGENCY — Content Management UI
Generate, view, and manage SEO content.
"""
import streamlit as st
from db.operations import get_clients, get_projects, get_content, get_keywords
from agents.content_agent import generate_content, generate_batch_content


def show_content_page():
    """Render content management page."""
    user_id = st.session_state["user_id"]
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">📝 Content Creation</h1>
        <p style="color: #888;">AI-Powered SEO Content Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    clients = get_clients(user_id)
    if not clients:
        st.warning("⚠️ Please add a client first!")
        return
    
    # Select client and project
    col1, col2 = st.columns(2)
    with col1:
        client_names = [c['name'] for c in clients]
        selected_client = st.selectbox("Select Client", client_names, key="content_client")
        client = next(c for c in clients if c['name'] == selected_client)
    
    projects = get_projects(client['id'])
    if not projects:
        st.info("💡 Create a project first!")
        return
    
    with col2:
        proj_names = [p['name'] for p in projects]
        selected_project = st.selectbox("Select Project", proj_names, key="content_proj")
        project = next(p for p in projects if p['name'] == selected_project)
        project_id = project['id']
    
    st.markdown("---")
    
    # ── Generate Content ──
    with st.expander("🤖 Generate New Content", expanded=False):
        st.markdown("**AI will create SEO-optimized content with schema markup**")
        
        col1, col2 = st.columns(2)
        with col1:
            content_type = st.selectbox(
                "Content Type",
                ["blog", "article", "service_page", "landing_page", "product_description"],
                format_func=lambda x: x.replace('_', ' ').title()
            )
        
        with col2:
            # Get existing keywords or let user type
            keywords = get_keywords(project_id)
            kw_options = [k['keyword'] for k in keywords]
            
            use_existing = st.checkbox("Use existing keyword", value=bool(kw_options))
            if use_existing and kw_options:
                target_keyword = st.selectbox("Select Keyword", kw_options)
            else:
                target_keyword = st.text_input("Enter Keyword / Topic", 
                                                placeholder="e.g., Best dental clinic in Delhi")
        
        if st.button("🚀 Generate Content", use_container_width=True, type="primary"):
            if target_keyword:
                with st.spinner("🤖 AI writing content... This takes 30-60 seconds..."):
                    result = generate_content(project_id, target_keyword, content_type)
                
                if result and result.get('content'):
                    st.success(f"✅ Content generated! (ID: {result.get('id', 'N/A')})")
                    
                    # Store for viewing
                    st.session_state['last_content'] = result
                    st.rerun()
                else:
                    st.error("❌ Content generation failed. Check API keys.")
            else:
                st.warning("⚠️ Please enter a keyword or topic!")
    
    # ── Batch Generate ──
    with st.expander("📦 Batch Generate (Multiple Keywords)", expanded=False):
        st.markdown("Generate content for top keywords in one go")
        
        keywords = get_keywords(project_id)
        if keywords:
            selected_kws = st.multiselect(
                "Select keywords to generate content for",
                [k['keyword'] for k in keywords[:10]],
                default=[k['keyword'] for k in keywords[:3]]
            )
            
            if st.button("📦 Generate Batch", use_container_width=True):
                if selected_kws:
                    with st.spinner(f"🤖 Generating content for {len(selected_kws)} keywords..."):
                        results = generate_batch_content(project_id, selected_kws)
                    st.success(f"✅ Generated {len(results)} content pieces!")
                else:
                    st.warning("⚠️ Select at least one keyword!")
        else:
            st.info("💡 No keywords yet. Add keywords first!")
    
    st.markdown("---")
    
    # ── View Generated Content ──
    st.markdown("### 📚 Content Library")
    
    # Show last generated content if available
    if 'last_content' in st.session_state and st.session_state['last_content']:
        result = st.session_state['last_content']
        with st.expander(f"📄 {result.get('title', 'Untitled')} (Just Generated)", expanded=True):
            st.markdown(f"**📌 Meta Title:** {result.get('meta_title', 'N/A')}")
            st.markdown(f"**📝 Meta Description:** {result.get('meta_description', 'N/A')}")
            st.markdown(f"**📊 Word Count:** {result.get('word_count', 0)}")
            st.markdown("---")
            st.markdown(result.get('content', ''), unsafe_allow_html=True)
            
            if result.get('schema_json'):
                with st.expander("🔍 Schema JSON-LD"):
                    st.json(result['schema_json'])
    
    # All content
    content_list = get_content(project_id, limit=20)
    
    if content_list:
        # Filter
        content_types = list(set(c['content_type'] for c in content_list if c['content_type']))
        filter_type = st.selectbox("Filter by type", ["All"] + content_types)
        
        if filter_type != "All":
            content_list = [c for c in content_list if c['content_type'] == filter_type]
        
        for c in content_list:
            with st.expander(f"📄 {c['title'][:60]}... ({c.get('content_type', 'blog').title()})"):
                st.markdown(f"""
                **Status:** {c.get('status', 'draft').upper()}
                **Words:** {c.get('word_count', 0)}
                **Keyword:** {c.get('target_keyword', 'N/A')}
                **Created:** {c.get('created_at', 'N/A')}
                """)
                
                if c.get('meta_title'):
                    st.markdown(f"**Meta Title:** {c['meta_title']}")
                if c.get('meta_description'):
                    st.markdown(f"**Meta Desc:** {c['meta_description']}")
                
                if c.get('content'):
                    st.markdown("---")
                    st.markdown(c['content'], unsafe_allow_html=True)
                
                if c.get('schema_json') and c['schema_json'] != '{}':
                    with st.expander("🔍 Schema Markup"):
                        try:
                            st.json(eval(c['schema_json']) if isinstance(c['schema_json'], str) else c['schema_json'])
                        except:
                            st.code(c['schema_json'])
    else:
        st.info("💡 No content yet. Generate your first piece above!")
