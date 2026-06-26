"""
BHARATSOLVE SEO AGENCY — Reports UI
Generate and view SEO reports.
"""
import streamlit as st
from datetime import datetime, timedelta
import json
import os
from db.operations import (
    get_clients, get_projects, get_keywords, 
    get_dashboard_stats, get_agent_logs,
    get_all_projects
)
from agents.rank_agent import get_ranking_insights


def show_reports_page():
    """Render reports page with PDF generation capability."""
    user_id = st.session_state["user_id"]
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">📊 Reports & Analytics</h1>
        <p style="color: #888;">Generate Professional SEO Reports</p>
    </div>
    """, unsafe_allow_html=True)
    
    clients = get_clients(user_id)
    if not clients:
        st.warning("⚠️ Please add clients first!")
        return
    
    # ── Quick Stats ──
    stats = get_dashboard_stats(user_id)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Clients", stats['active_clients'])
    with col2:
        st.metric("Total Keywords", stats['total_keywords'])
    with col3:
        st.metric("Content Pieces", stats['total_content'])
    
    st.markdown("---")
    
    # ── Report Generator ──
    st.markdown("### 📄 Generate Report")
    
    col1, col2 = st.columns(2)
    with col1:
        report_type = st.selectbox(
            "Report Type",
            ["quick_summary", "weekly", "monthly", "client_report"],
            format_func=lambda x: {
                "quick_summary": "⚡ Quick Summary",
                "weekly": "📅 Weekly Report",
                "monthly": "📆 Monthly Report",
                "client_report": "👥 Per-Client Report"
            }[x]
        )
    
    with col2:
        if report_type == "client_report":
            client_names = [c['name'] for c in clients]
            selected_client = st.selectbox("Select Client", client_names)
            client = next(c for c in clients if c['name'] == selected_client)
            target_id = client['id']
        else:
            target_id = None
    
    if st.button("📊 Generate Report", use_container_width=True, type="primary"):
        st.info("📄 Generating report... (PDF generation will be available with fpdf2)")
        
        # Build report data
        report_data = {
            "agency": "BHARATSOLVE SEO AGENCY",
            "generated_at": datetime.now().isoformat(),
            "report_type": report_type,
            "stats": stats,
            "clients": []
        }
        
        for client in clients:
            client_data = {
                "name": client['name'],
                "website": client.get('website', ''),
                "location": client.get('location', ''),
                "projects": []
            }
            
            projects = get_projects(client['id'])
            for proj in projects:
                keywords = get_keywords(proj['id'])
                insights = get_ranking_insights(proj['id'])
                
                proj_data = {
                    "name": proj['name'],
                    "target_location": proj.get('target_location', ''),
                    "keywords": keywords,
                    "insights": insights
                }
                client_data["projects"].append(proj_data)
            
            report_data["clients"].append(client_data)
        
        # Show report preview
        st.markdown("### 📋 Report Preview")
        st.json(report_data)
        
        # Try to generate PDF
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 20)
            pdf.cell(0, 15, "BHARATSOLVE SEO AGENCY", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(0, 10, f"Report: {report_type.replace('_', ' ').title()}", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C", new_x="LMARGIN", new_y="NEXT")
            
            pdf.ln(10)
            
            for client in report_data['clients']:
                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(0, 10, f"Client: {client['name']}", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", 10)
                
                for proj in client['projects']:
                    pdf.cell(0, 8, f"  Project: {proj['name']}", new_x="LMARGIN", new_y="NEXT")
                    insights = proj.get('insights', {})
                    pdf.cell(0, 8, f"  Keywords: {insights.get('total_keywords', 0)} | Top 10: {insights.get('top_10_count', 0)} | Avg Rank: {insights.get('avg_position', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(5)
            
            # Save PDF
            pdf_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pdf_outputs")
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_path = os.path.join(pdf_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            pdf.output(pdf_path)
            
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "📥 Download PDF Report",
                    data=f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True
                )
            st.success(f"✅ PDF generated successfully!")
            
        except Exception as e:
            st.warning(f"⚠️ PDF generation requires fpdf2: {str(e)[:100]}")
            st.info("💡 Install fpdf2: `pip install fpdf2`")
            
            # Offer JSON download instead
            st.download_button(
                "📥 Download JSON Report",
                data=json.dumps(report_data, indent=2, default=str),
                file_name=f"seo_report_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # ── Agent Activity Log ──
    st.markdown("### 📋 Agent Activity Log")
    logs = get_agent_logs(limit=50)
    
    if logs:
        log_data = []
        for log in logs:
            log_data.append({
                "Agent": log['agent_name'],
                "Task": log['task'][:50] + "..." if len(log['task']) > 50 else log['task'],
                "Status": "✅" if log['status'] == 'ok' else "❌",
                "Time (ms)": log['response_time_ms'],
                "When": log['logged_at'][:19] if 'T' in str(log.get('logged_at', '')) else str(log.get('logged_at', ''))[:19]
            })
        
        st.dataframe(log_data, use_container_width=True, hide_index=True)
    else:
        st.info("💡 No agent activity yet. Agents will log activity as they run.")
