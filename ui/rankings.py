"""
BHARATSOLVE SEO AGENCY — Rankings Page UI
Track, monitor, and analyze keyword rankings.
Now with Google Search Console real data support.
"""
import streamlit as st
from datetime import datetime
from db.operations import get_clients, get_projects, get_keywords, get_rankings_history
from agents.rank_agent import (
    check_rankings, get_ranking_insights, get_gsc_client, sync_with_gsc
)


def show_rankings_page():
    """Render rankings tracking page."""
    user_id = st.session_state["user_id"]
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">📊 Rank Tracker</h1>
        <p style="color: #888;">Real Keyword Rankings — Powered by Google Search Console</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Data Source Status ──
    gsc = get_gsc_client()
    if gsc.is_configured():
        st.success("✅ Connected to Google Search Console — getting REAL ranking data")
    else:
        st.warning("⚠️ Google Search Console not configured. Rankings are simulated.")
        with st.expander("🔧 Configure Google Search Console"):
            st.markdown("""
            **To get real ranking data:**
            1. Go to [Google Search Console](https://search.google.com/search-console)
            2. Add & verify your website
            3. Create a **Service Account** in [Google Cloud Console](https://console.cloud.google.com)
            4. Add the service account email as an owner in GSC
            5. Download the JSON key
            6. Set these Streamlit secrets:
            ```toml
            GSC_SITE_URL = "sc-domain:example.com"  # or https://example.com
            GSC_CREDENTIALS_JSON = '{...}'  # Full service account JSON
            ```
            """)
    
    clients = get_clients(user_id)
    if not clients:
        st.warning("⚠️ Please add a client first!")
        return
    
    # Select client and project
    col1, col2 = st.columns(2)
    with col1:
        client_names = [c['name'] for c in clients]
        selected_client = st.selectbox("Select Client", client_names, key="rank_client")
        client = next(c for c in clients if c['name'] == selected_client)
    
    projects = get_projects(client['id'])
    if not projects:
        st.info("💡 Create a project first!")
        return
    
    with col2:
        proj_names = [p['name'] for p in projects]
        selected_project = st.selectbox("Select Project", proj_names, key="rank_proj")
        project = next(p for p in projects if p['name'] == selected_project)
        project_id = project['id']
    
    st.markdown("---")
    
    # ── Actions Row ──
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.markdown("### 🎯 Current Rankings")
    with col2:
        if st.button("🔄 Check Rankings Now", use_container_width=True, type="primary"):
            with st.spinner("🤖 Checking rankings..."):
                results = check_rankings(project_id, simulate=not gsc.is_configured())
            if results:
                source = results[0].get('source', 'unknown') if results else 'unknown'
                st.success(f"✅ Checked {len(results)} keywords via {source.upper()}!")
                st.rerun()
            else:
                st.warning("⚠️ No keywords to check!")
    with col3:
        if gsc.is_configured():
            if st.button("📥 Sync from GSC", use_container_width=True):
                with st.spinner("Syncing with Google Search Console..."):
                    result = sync_with_gsc(project_id)
                if result.get("status") == "ok":
                    st.success(result.get("message", "Sync complete!"))
                    if result.get("new_keywords_added"):
                        st.info(f"New keywords: {', '.join(result['new_keywords_added'][:5])}")
                    st.rerun()
                else:
                    st.error(result.get("message", "Sync failed"))
    
    keywords = get_keywords(project_id)
    if not keywords:
        st.info("💡 No keywords yet. Add keywords from the Keyword Research page!")
        return
    
    # ── AI Insights ──
    insights = get_ranking_insights(project_id)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Keywords", insights['total_keywords'])
    with col2:
        st.metric("🥇 Top 10", insights['top_10_count'])
    with col3:
        st.metric("📈 Top 30", insights['top_30_count'])
    with col4:
        st.metric("Avg Position", insights.get('avg_position', 'N/A'))
    
    # Data source badge
    st.caption(f"📡 Data source: {insights.get('data_source', 'Unknown')}")
    
    # Suggestions
    if insights.get('suggestions'):
        for s in insights['suggestions']:
            st.info(f"💡 {s}")
    
    # ── Rankings Table ──
    st.markdown("### 📋 Keyword Rankings")
    
    ranked_keywords = [k for k in keywords if k['current_position'] > 0]
    unranked_keywords = [k for k in keywords if k['current_position'] == 0]
    
    tab1, tab2, tab3 = st.tabs(["📊 All Rankings", "🏆 Top Performers", "❌ Not Ranked"])
    
    with tab1:
        if ranked_keywords:
            ranked_keywords.sort(key=lambda k: k['current_position'])
            
            for kw in ranked_keywords:
                pos = kw['current_position']
                if pos <= 3:
                    rank_icon = "🥇"
                    color = "#00d2ff"
                elif pos <= 10:
                    rank_icon = "✅"
                    color = "#43e97b"
                elif pos <= 30:
                    rank_icon = "📈"
                    color = "#ffa502"
                else:
                    rank_icon = "📉"
                    color = "#ff6b6b"
                
                best = kw['best_position'] if kw['best_position'] > 0 else pos
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.7); border-radius: 8px; padding: 0.5rem 1rem; margin: 0.3rem 0;
                            border-left: 3px solid {color}; box-shadow: 0 2px 6px rgba(0,119,182,0.06);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #333;">{rank_icon} {kw['keyword']}</strong>
                            <span style="color: #666; margin-left: 1rem; font-size: 0.85rem;">
                                Vol: {kw['search_volume']:,} | Diff: {kw['difficulty']}%
                            </span>
                        </div>
                        <div>
                            <span style="font-size: 1.2rem; font-weight: bold; color: {color};">#{pos}</span>
                            <span style="color: #888; font-size: 0.8rem; margin-left: 0.5rem;">
                                Best: #{best}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 Run a rank check to see results!")
    
    with tab2:
        top10 = [k for k in ranked_keywords if k['current_position'] <= 10]
        if top10:
            for kw in sorted(top10, key=lambda k: k['current_position']):
                st.markdown(f"""
                <div style="background: rgba(0,200,100,0.05); border-radius: 5px; padding: 0.3rem 0.8rem; margin: 0.2rem 0; border: 1px solid #90e0ef;">
                    🏆 <strong>#{kw['current_position']}</strong> — {kw['keyword']}
                    <span style="color: #666; margin-left: 1rem;">Vol: {kw['search_volume']:,}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 No keywords in Top 10 yet. Keep working on SEO!")
    
    with tab3:
        if unranked_keywords:
            for kw in sorted(unranked_keywords, key=lambda k: k['difficulty'], reverse=True):
                st.markdown(f"""
                <div style="background: rgba(255,100,100,0.05); border-radius: 5px; padding: 0.3rem 0.8rem; margin: 0.2rem 0; border: 1px solid #ffcccc;">
                    ❌ <strong>{kw['keyword']}</strong> — {kw.get('difficulty', 0)}% difficulty
                    <span style="color: #666; margin-left: 1rem;">Vol: {kw['search_volume']:,}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("✅ All keywords are ranking!")
    
    # ── Ranking History ──
    st.markdown("---")
    st.markdown("### 📈 Ranking History (Last 30 Days)")
    
    kw_names = [k['keyword'] for k in keywords]
    if kw_names:
        selected_kw = st.selectbox("Select keyword to view history", kw_names)
        selected_kw_obj = next(k for k in keywords if k['keyword'] == selected_kw)
        
        history = get_rankings_history(selected_kw_obj['id'], days=30)
        
        if history:
            chart_data = {
                "dates": [h['checked_at'][:10] for h in history],
                "positions": [h['position'] for h in history]
            }
            st.line_chart(chart_data, x="dates", y="positions", use_container_width=True)
            st.caption("📉 Lower = better ranking (1 is #1 position)")
            
            # Show trend
            if len(history) >= 2:
                first = history[0]['position']
                last = history[-1]['position']
                change = first - last
                if change > 0:
                    st.success(f"📈 Improved by {change} position(s) over {len(history)} checks")
                elif change < 0:
                    st.warning(f"📉 Declined by {abs(change)} position(s)")
                else:
                    st.info("➡️ No change in position")
        else:
            st.info("📊 No history yet. Check rankings regularly to build history!")
