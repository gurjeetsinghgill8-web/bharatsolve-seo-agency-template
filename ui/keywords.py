"""
BHARATSOLVE SEO AGENCY — Keyword Research UI
Research, view, and manage keywords.
"""
import streamlit as st
from db.operations import get_clients, get_projects, get_keywords, get_project
from agents.keyword_agent import research_keywords, suggest_keyword_clusters


def show_keywords_page():
    """Render keyword research page."""
    user_id = st.session_state["user_id"]
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">🔑 Keyword Research</h1>
        <p style="color: #888;">AI-Powered Keyword Discovery & Analysis</p>
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
        selected_client = st.selectbox("Select Client", client_names)
        client = next(c for c in clients if c['name'] == selected_client)
    
    projects = get_projects(client['id'])
    if not projects:
        st.info("💡 Create a project for this client first!")
        return
    
    with col2:
        proj_names = [p['name'] for p in projects]
        selected_project = st.selectbox("Select Project", proj_names)
        project = next(p for p in projects if p['name'] == selected_project)
        project_id = project['id']
    
    st.markdown("---")
    
    # ── AI Keyword Research ──
    with st.expander("🤖 AI Keyword Research", expanded=False):
        st.markdown("**Let AI research keywords for your business**")
        col1, col2 = st.columns(2)
        
        with col1:
            niche = st.text_input("Niche/Business Type", value=client.get('business_type', ''), 
                                  placeholder="e.g., Dental Clinic")
        with col2:
            location = st.text_input("Target Location", value=client.get('location', ''),
                                     placeholder="e.g., Delhi")
        
        if st.button("🔍 Research Keywords", use_container_width=True, type="primary"):
            with st.spinner("🤖 AI researching keywords... This may take a moment."):
                keywords = research_keywords(project_id, niche or client.get('business_type', ''), 
                                            location or client.get('location', ''))
            
            if keywords:
                st.success(f"✅ Found {len(keywords)} keywords!")
                
                # Show results in a table
                kw_data = []
                for i, kw in enumerate(keywords, 1):
                    kw_data.append({
                        "#": i,
                        "Keyword": kw.get('keyword', ''),
                        "Volume": kw.get('search_volume', 0),
                        "Difficulty": f"{kw.get('difficulty', 0)}%",
                        "Intent": kw.get('intent', 'N/A').capitalize()
                    })
                
                st.dataframe(kw_data, use_container_width=True, hide_index=True)
            else:
                st.error("❌ No keywords found. Please check your API keys or try again.")
    
    # ── View Existing Keywords ──
    st.markdown("### 📋 Existing Keywords")
    keywords = get_keywords(project_id)
    
    if not keywords:
        st.info("💡 No keywords yet. Use AI Research above to find keywords!")
        return
    
    # Filter and sort
    col1, col2 = st.columns(2)
    with col1:
        search_kw = st.text_input("🔍 Filter keywords", placeholder="Search...")
    with col2:
        sort_by = st.selectbox("Sort by", ["Newest", "Volume (High to Low)", "Difficulty (Low to High)", "Position"])
    
    if search_kw:
        keywords = [k for k in keywords if search_kw.lower() in k['keyword'].lower()]
    
    # Sort
    if sort_by == "Volume (High to Low)":
        keywords.sort(key=lambda k: k['search_volume'], reverse=True)
    elif sort_by == "Difficulty (Low to High)":
        keywords.sort(key=lambda k: k['difficulty'])
    elif sort_by == "Position":
        keywords.sort(key=lambda k: k['current_position'] if k['current_position'] > 0 else 999)
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Keywords", len(keywords))
    with col2:
        top10 = len([k for k in keywords if 1 <= k['current_position'] <= 10])
        st.metric("Top 10 Rankings", top10)
    with col3:
        not_ranked = len([k for k in keywords if k['current_position'] == 0])
        st.metric("Not Ranked", not_ranked)
    
    # Keyword table
    for kw in keywords:
        pos = kw['current_position']
        if pos == 0:
            pos_display = "❌ N/A"
        elif pos <= 3:
            pos_display = f"🥇 #{pos}"
        elif pos <= 10:
            pos_display = f"✅ #{pos}"
        elif pos <= 30:
            pos_display = f"📈 #{pos}"
        else:
            pos_display = f"📉 #{pos}"
        
        diff_color = "green" if kw['difficulty'] < 30 else "orange" if kw['difficulty'] < 60 else "red"
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.7); border-radius: 8px; padding: 0.5rem 1rem; margin: 0.3rem 0;
                    border-left: 3px solid {color}; box-shadow: 0 2px 6px rgba(0,119,182,0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #333;">{kw['keyword']}</strong>
                    <span style="color: #666; margin-left: 1rem; font-size: 0.9rem;">
                        📊 Vol: {kw['search_volume']:,}
                    </span>
                    <span style="color: {diff_color}; margin-left: 0.5rem; font-size: 0.9rem;">
                        🎯 Diff: {kw['difficulty']}%
                    </span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 1.1rem; font-weight: bold; color: {color};">{pos_display}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Cluster analysis
    st.markdown("---")
    if st.button("🧠 Analyze Keyword Clusters", use_container_width=True):
        with st.spinner("🤖 Analyzing keyword clusters..."):
            clusters = suggest_keyword_clusters(project_id)
        
        if clusters.get('clusters'):
            for cluster in clusters['clusters']:
                st.markdown(f"""
                <div style="background: rgba(0,119,182,0.05); border-radius: 10px; padding: 1rem; margin: 0.5rem 0; border: 1px solid #90e0ef;">
                    <h3 style="color: #0077b6;">📦 {cluster.get('topic', 'Cluster')}</h3>
                    <p style="color: #555;">{cluster.get('strategy', '')}</p>
                    <p style="color: #666;">Keywords: {', '.join(cluster.get('keywords', []))}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Could not cluster keywords. Try adding more keywords first.")
