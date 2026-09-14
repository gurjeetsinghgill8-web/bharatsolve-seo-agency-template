"""
BHARATSOLVE SEO AGENCY — Live Research & Multi-LLM Analytics Hub
🏥 Dr. Gurjeet Singh Gill — Gill Heart Clinic (Meerut & Delhi NCR)

NOTE: All charts in this module are SIMULATED SAMPLE DATA for strategy
planning and are clearly labeled as such in the UI (NMC compliance —
no fabricated live metrics, no "No. 1"/"Best" claims).

Real, verified facts (Grexa Google ranking report, Sep 2026):
  - Gill Heart Clinic: 5.0★ rating (4 Google reviews)
  - "cardiologist near me": top 5 in 9 of 20 nearby areas; beyond #20 in the rest

Provides graphical intelligence:
  1. Timeframe filtering: 1 Day (24h), 3 Days, 7 Days, 1 Month (30D), 6 Months (180D)
  2. Multi-LLM AI Visibility Radar (ChatGPT-4o, Google Gemini, Perplexity AI, Claude)
  3. Google Organic Search Ranking Timeline + 'Kyon Badi' algorithmic reasons
  4. Google Maps Local 3-Pack Positioning & Competitor Proximity Radar
  5. Visual Competitor Dominance Leaderboard Tower
"""
import streamlit as st
import datetime
from datetime import datetime, timedelta
import random

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def generate_timeframe_data(timeframe: str):
    """
    Generate accurate chronological timeline datasets for the selected timeframe.
    Timeframe options: '1 Day', '3 Days', '7 Days', '1 Month', '6 Months'
    """
    now = datetime.now()
    if timeframe == "1 Day":
        points = 8
        dates = [(now - timedelta(hours=i*3)).strftime("%H:00") for i in reversed(range(points))]
        x_label = "Hour (Past 24h)"
    elif timeframe == "3 Days":
        points = 6
        dates = [(now - timedelta(hours=i*12)).strftime("%d %b %H:%M") for i in reversed(range(points))]
        x_label = "Date & Time (Past 72h)"
    elif timeframe == "7 Days":
        points = 7
        dates = [(now - timedelta(days=i)).strftime("%d %b") for i in reversed(range(points))]
        x_label = "Date (Past 7 Days)"
    elif timeframe == "1 Month":
        points = 10
        dates = [(now - timedelta(days=i*3)).strftime("%d %b") for i in reversed(range(points))]
        x_label = "Date (Past 30 Days)"
    else:  # 6 Months
        points = 12
        dates = [(now - timedelta(days=i*15)).strftime("%b %Y") for i in reversed(range(points))]
        x_label = "Month (Past 6 Months)"

    # Multi-LLM Visibility Progression (%)
    llm_chatgpt = [round(40 + (54 * (i / (points - 1))), 1) for i in range(points)]
    llm_gemini  = [round(35 + (56 * (i / (points - 1))), 1) for i in range(points)]
    llm_perplexity = [round(28 + (60 * (i / (points - 1))), 1) for i in range(points)]
    llm_claude  = [round(32 + (53 * (i / (points - 1))), 1) for i in range(points)]

    # Google SERP Rank Positions (Lower is better: #1 is top)
    kw_physician_meerut = [max(1, round(9 - (8 * (i / (points - 1))))) for i in range(points)]
    kw_heart_doctor_delhi = [max(2, round(14 - (11 * (i / (points - 1))))) for i in range(points)]
    kw_bp_specialist = [max(1, round(7 - (6 * (i / (points - 1))))) for i in range(points)]
    kw_chest_pain = [max(2, round(12 - (10 * (i / (points - 1))))) for i in range(points)]
    kw_clinic_mohiuddinpur = [1 for _ in range(points)]

    return {
        "dates": dates,
        "x_label": x_label,
        "points": points,
        "llm_chatgpt": llm_chatgpt,
        "llm_gemini": llm_gemini,
        "llm_perplexity": llm_perplexity,
        "llm_claude": llm_claude,
        "kw_physician_meerut": kw_physician_meerut,
        "kw_heart_doctor_delhi": kw_heart_doctor_delhi,
        "kw_bp_specialist": kw_bp_specialist,
        "kw_chest_pain": kw_chest_pain,
        "kw_clinic_mohiuddinpur": kw_clinic_mohiuddinpur,
    }


def render_live_research_hub(user_id=None, project_id=0):
    """Render the full interactive Analytics & Multi-LLM Radar Hub."""
    with st.container():
        st.markdown('<div class="gill-section">', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:1rem;">
            <div>
                <h3 style="margin:0; color:#0077b6;">📊 Search & Multi-LLM Intelligence Command (Simulation)</h3>
                <p style="margin:0.2rem 0; color:#666; font-size:0.9rem;">
                    Timeline tracking across <strong>ChatGPT Search, Google Gemini, Perplexity AI, Claude, Google SERP & Google Maps</strong>.
                </p>
            </div>
            <div style="background:#fff9e6; border:1px solid #f0b429; padding:4px 10px; border-radius:20px; font-size:0.82rem; color:#b45309; font-weight:bold;">
                🟡 SAMPLE DATA MODE (Simulation)
            </div>
        </div>
        <div style="background:#fff8e6; border:1px solid #f0b429; border-radius:10px; padding:0.6rem 1rem; margin-bottom:0.8rem; font-size:0.85rem; color:#7c5a10;">
            ⚠️ <strong>NMC Compliance Notice:</strong> Charts below use <strong>simulated sample data</strong> for strategy planning — not live Google metrics.
            Verified live facts: <strong>5.0★ (4 Google reviews)</strong> · "cardiologist near me" ranks <strong>top 5 in 9 of 20</strong> nearby areas (Grexa report, Sep 2026).
        </div>
        """, unsafe_allow_html=True)

        # ── 1. TIMEFRAME SELECTOR ──
        col_tf1, col_tf2 = st.columns([1.5, 3.5])
        with col_tf1:
            timeframe = st.radio(
                "📅 Select Tracking Timeframe:",
                ["1 Day", "3 Days", "7 Days", "1 Month", "6 Months"],
                index=2, # Default to 7 Days
                horizontal=True,
                key="analytics_timeframe_selector"
            )
        
        with col_tf2:
            st.markdown(f"""
            <div style="background:#f8fdff; border:1px solid #b3e5ff; border-radius:10px; padding:0.6rem 1rem; margin-top:1.2rem;">
                <p style="margin:0; font-size:0.85rem; color:#333;">
                    🔍 <strong>Active Scope ({timeframe}):</strong> Analyzing Google SERP, Local Maps Pack, 4 Major LLM Citation Graphs & Competitor Gaps in Meerut & Delhi NCR.
                </p>
            </div>
            """, unsafe_allow_html=True)

        data = generate_timeframe_data(timeframe)
        st.markdown("<br>", unsafe_allow_html=True)

        # ── 2. COMPETITOR DOMINANCE TOWER (PODIUM & GAP ANALYSIS) ──
        st.markdown("### 🏆 Competitor Dominance Leaderboard Tower (Meerut & Delhi NCR)")
        st.markdown("Simulated SEO-authority comparison of **Dr. Gurjeet Singh Gill (Gill Heart Clinic)** with regional competitors. Scores are planning estimates — refresh with live rank data for real numbers.")

        competitors_tower = [
            {"name": "Dr. Gurjeet Singh Gill (Gill Heart Clinic)", "score": 62, "rank_badge": "📊 Baseline (sample)", "color": "#00b4d8", "maps_pos": "Top 5 in 9/20 areas", "reviews": "4 (5.0★ live)", "geo_ai": "N/A", "status": "Improving"},
            {"name": "Dr. Sanjeev Kumar Bansal (Shastri Nagar)", "score": 78, "rank_badge": "🥈 Sample", "color": "#74b9ff", "maps_pos": "Sample", "reviews": "94 est. (4.5★)", "geo_ai": "Sample", "status": "Sample"},
            {"name": "Dr. Hari Mohan Choudhary (Meerut)", "score": 72, "rank_badge": "🥉 Sample", "color": "#a29bfe", "maps_pos": "Sample", "reviews": "68 est. (4.3★)", "geo_ai": "Sample", "status": "Sample"},
            {"name": "Dr. Mamtesh Gupta (Meerut)", "score": 68, "rank_badge": "4️⃣ Sample", "color": "#dfe6e9", "maps_pos": "Sample", "reviews": "52 est. (4.2★)", "geo_ai": "Sample", "status": "Sample"},
            {"name": "Dr. Rajeev Agarwal (Meerut)", "score": 64, "rank_badge": "5️⃣ Sample", "color": "#b2bec3", "maps_pos": "Sample", "reviews": "43 est. (4.1★)", "geo_ai": "Sample", "status": "Sample"}
        ]

        if PLOTLY_AVAILABLE:
            fig_tower = go.Figure()
            comp_names = [c["name"] for c in reversed(competitors_tower)]
            comp_scores = [c["score"] for c in reversed(competitors_tower)]
            comp_colors = [c["color"] for c in reversed(competitors_tower)]

            fig_tower.add_trace(go.Bar(
                y=comp_names,
                x=comp_scores,
                orientation='h',
                marker=dict(
                    color=comp_colors,
                    line=dict(color='#0077b6', width=1.5)
                ),
                text=[f"<b>{score}/100</b>" for score in comp_scores],
                textposition='auto',
                hoverinfo='text',
                hovertext=[f"{c['name']}<br>Score: {c['score']}/100<br>Status: {c['rank_badge']}" for c in reversed(competitors_tower)]
            ))
            fig_tower.update_layout(
                title=f"<b>🏆 Regional Authority Tower — Dr. Gill vs Top Competitors ({timeframe})</b>",
                xaxis=dict(title="Overall SEO & AI Citation Score (0 - 100)", range=[0, 105]),
                yaxis=dict(autorange="reversed"),
                margin=dict(l=20, r=20, t=40, b=20),
                height=280,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(240,249,255,0.4)",
            )
            st.plotly_chart(fig_tower, use_container_width=True)

        # Tower Detail Comparison Table
        col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns([2.5, 1.2, 1.2, 1.4, 1.2])
        col_c1.markdown("**Doctor / Clinic**")
        col_c2.markdown("**Score**")
        col_c3.markdown("**Maps Rank**")
        col_c4.markdown("**Verified Reviews**")
        col_c5.markdown("**AI GEO Cite**")

        for c in competitors_tower:
            is_gill = "Gill" in c["name"]
            bg = "#e8f4fd" if is_gill else "#ffffff"
            border = "2px solid #00b4d8" if is_gill else "1px solid #e0f0ff"
            st.markdown(f"""
            <div style="background:{bg}; border:{border}; border-radius:8px; padding:0.4rem 0.8rem; margin:0.25rem 0; display:flex; justify-content:space-between; align-items:center; font-size:0.88rem;">
                <div style="flex:2.5; font-weight:{'bold' if is_gill else 'normal'}; color:{'#0077b6' if is_gill else '#333'};">
                    {c['name']}
                </div>
                <div style="flex:1.2; font-weight:bold; color:{'#27ae60' if is_gill else '#555'};">
                    {c['score']}/100 ({c['rank_badge']})
                </div>
                <div style="flex:1.2; color:#333;">{c['maps_pos']}</div>
                <div style="flex:1.4; color:#333;">⭐ {c['reviews']}</div>
                <div style="flex:1.2; font-weight:bold; color:#0077b6;">{c['geo_ai']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── 3. MULTI-LLM AI SEARCH VISIBILITY RADAR ──
        st.markdown(f"### 🤖 Multi-LLM AI Search Engine Radar ({timeframe})")
        st.markdown("Simulated sample trend of patient queries where Dr. Gurjeet Singh Gill is cited in **ChatGPT-4o, Google Gemini, Perplexity AI, and Claude** — planning estimate only, not live measurement.")

        col_llm_chart, col_llm_insights = st.columns([1.6, 1.1])

        with col_llm_chart:
            if PLOTLY_AVAILABLE:
                fig_llm = go.Figure()
                fig_llm.add_trace(go.Scatter(x=data["dates"], y=data["llm_chatgpt"], mode='lines+markers', name='ChatGPT Search (GPT-4o)', line=dict(color='#10a37f', width=3)))
                fig_llm.add_trace(go.Scatter(x=data["dates"], y=data["llm_gemini"], mode='lines+markers', name='Google Gemini', line=dict(color='#4285f4', width=3)))
                fig_llm.add_trace(go.Scatter(x=data["dates"], y=data["llm_perplexity"], mode='lines+markers', name='Perplexity AI', line=dict(color='#00b4d8', width=3, dash='dash')))
                fig_llm.add_trace(go.Scatter(x=data["dates"], y=data["llm_claude"], mode='lines+markers', name='Anthropic Claude', line=dict(color='#d97706', width=2)))

                fig_llm.update_layout(
                    title=f"<b>AI Search Engine Citation Index (%) — {timeframe} Timeline</b>",
                    xaxis_title=data["x_label"],
                    yaxis_title="Citation & Recommendation Rate (%)",
                    yaxis=dict(range=[20, 100]),
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=320,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(240,249,255,0.4)",
                )
                st.plotly_chart(fig_llm, use_container_width=True)

        with col_llm_insights:
            st.markdown(f"""
            <div style="background:#f0f9ff; border:1px solid #00b4d8; border-radius:12px; padding:1rem; height:100%;">
                <h5 style="color:#0077b6; margin:0 0 0.5rem 0;">💡 LLM Visibility Breakdown ({timeframe}):</h5>
                <p style="font-size:0.85rem; margin:0.3rem 0;">
                    🟢 <strong>ChatGPT-4o Search: {data['llm_chatgpt'][-1]}%</strong> (Started at {data['llm_chatgpt'][0]}% → <strong>+{round(data['llm_chatgpt'][-1] - data['llm_chatgpt'][0], 1)}%</strong>)<br>
                    <span style="color:#666; font-size:0.8rem;">Reason: <code>/llms.txt</code> indexing + MedicalBusiness schema.</span>
                </p>
                <hr style="margin:0.4rem 0;">
                <p style="font-size:0.85rem; margin:0.3rem 0;">
                    🟢 <strong>Google Gemini: {data['llm_gemini'][-1]}%</strong> (Started at {data['llm_gemini'][0]}% → <strong>+{round(data['llm_gemini'][-1] - data['llm_gemini'][0], 1)}%</strong>)<br>
                    <span style="color:#666; font-size:0.8rem;">Reason: Google-Extended crawler allowed + Physician JSON-LD.</span>
                </p>
                <hr style="margin:0.4rem 0;">
                <p style="font-size:0.85rem; margin:0.3rem 0;">
                    🟢 <strong>Perplexity AI: {data['llm_perplexity'][-1]}%</strong> (Started at {data['llm_perplexity'][0]}% → <strong>+{round(data['llm_perplexity'][-1] - data['llm_perplexity'][0], 1)}%</strong>)<br>
                    <span style="color:#666; font-size:0.8rem;">Reason: AHA/ACC guideline & landmark trial citations.</span>
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── 4. GOOGLE ORGANIC SERP RANKINGS TIMELINE & "KYON BADI" ──
        st.markdown(f"### 📈 Google Organic Keyword Positions Timeline ({timeframe}) — Simulated")
        st.markdown("Sample position movement for strategy tracking (Position #1 is top of page 1). Not live Google data.")

        col_serp_chart, col_serp_reasons = st.columns([1.6, 1.1])

        with col_serp_chart:
            if PLOTLY_AVAILABLE:
                fig_serp = go.Figure()
                fig_serp.add_trace(go.Scatter(x=data["dates"], y=data["kw_physician_meerut"], mode='lines+markers', name='Cardiac Physician Meerut', line=dict(color='#2ecc71', width=3)))
                fig_serp.add_trace(go.Scatter(x=data["dates"], y=data["kw_heart_doctor_delhi"], mode='lines+markers', name='Heart Doctor Delhi NCR', line=dict(color='#e74c3c', width=3)))
                fig_serp.add_trace(go.Scatter(x=data["dates"], y=data["kw_bp_specialist"], mode='lines+markers', name='BP Specialist Meerut', line=dict(color='#9b59b6', width=2)))
                fig_serp.add_trace(go.Scatter(x=data["dates"], y=data["kw_chest_pain"], mode='lines+markers', name='Chest Pain Doctor Near Me', line=dict(color='#f39c12', width=2, dash='dot')))
                fig_serp.add_trace(go.Scatter(x=data["dates"], y=data["kw_clinic_mohiuddinpur"], mode='lines+markers', name='Heart Clinic Mohiuddinpur', line=dict(color='#0077b6', width=3)))

                fig_serp.update_layout(
                    title=f"<b>Keyword Google Search Positions ({timeframe}) — Closer to #1 is Top</b>",
                    xaxis_title=data["x_label"],
                    yaxis_title="Google Search Rank (#1 is First)",
                    yaxis=dict(autorange="reversed", range=[15, 0.5]),
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=320,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(240,249,255,0.4)",
                )
                st.plotly_chart(fig_serp, use_container_width=True)

        with col_serp_reasons:
            st.markdown(f"""
            <div style="background:#fff9f0; border:1px solid #f39c12; border-radius:12px; padding:1rem; height:100%;">
                <h5 style="color:#d35400; margin:0 0 0.5rem 0;">🎯 Kyon Badi Rankings? (Algorithmic Strategy Notes — sample):</h5>
                <ul style="font-size:0.85rem; color:#444; padding-left:1.1rem; margin:0;">
                    <li style="margin-bottom:0.4rem;"><strong>'Cardiac Physician Meerut':</strong> Fresh Q&A blog on diagnostic ECG/Echo published & linked to homepage.</li>
                    <li style="margin-bottom:0.4rem;"><strong>'Heart Doctor Delhi NCR':</strong> Added catchments (Ghaziabad, Modinagar, Hapur) in geo-schema.</li>
                    <li style="margin-bottom:0.4rem;"><strong>'BP Specialist Meerut':</strong> High search-intent article on hypertension & Indian diet charts.</li>
                    <li style="margin-bottom:0.4rem;"><strong>'Chest Pain Near Me':</strong> Urgent-symptom Q&A schema indexed in mobile rich snippets.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── 5. GOOGLE MAPS LOCAL 3-PACK PROXIMITY RADAR ──
        st.markdown(f"### 🗺️ Google Maps Local Radar — Latest Verified Report (Grexa, Sep 2026)")
        st.markdown("Real data from the latest Google ranking report for **'cardiologist near me'** — scanned across 20 nearby areas around Gill Heart Clinic.")

        maps_data = [
            {"locality": "Mohiuddinpur (Clinic Center)", "maps_rank": "📍 Baseline", "distance": "0 km", "competitors_behind": "Gill Heart Clinic location"},
            {"locality": "Nearby areas (of 20 scanned)", "maps_rank": "Top 5 in 9 areas", "distance": "Good visibility", "competitors_behind": "Grexa ranking grid"},
            {"locality": "Remaining nearby areas", "maps_rank": "Beyond #20", "distance": "Improvement target", "competitors_behind": "1 competitor ranks higher"},
        ]

        col_m1, col_m2 = st.columns(2)
        for idx, m in enumerate(maps_data):
            target_col = col_m1 if idx % 2 == 0 else col_m2
            with target_col:
                st.markdown(f"""
                <div style="background:white; border:1px solid #d4edff; border-left:4px solid #00b4d8; border-radius:10px; padding:0.8rem; margin:0.3rem 0; box-shadow:0 2px 8px rgba(0,119,182,0.06);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:bold; color:#0077b6;">📍 {m['locality']}</span>
                        <span style="background:#eef9f1; color:#27ae60; padding:2px 8px; border-radius:12px; font-weight:bold; font-size:0.8rem;">
                            {m['maps_rank']}
                        </span>
                    </div>
                    <p style="margin:0.3rem 0 0 0; font-size:0.82rem; color:#555;">
                        📏 Radius: <strong>{m['distance']}</strong> &nbsp;|&nbsp; 👥 Trailing: {m['competitors_behind']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
