"""
BHARATSOLVE SEO AGENCY — Email Marketing UI
Send newsletters, client reports, and campaign emails.
"""
import streamlit as st
import os
from datetime import datetime
from db.operations import get_clients, get_client
from agents.email_agent import (
    send_email, send_client_report_email, send_newsletter,
    send_weekly_digest, send_bulk_campaign
)
from utils.social_connectors import EmailConnector


def show_email_page():
    """Render email marketing page."""
    user_id = st.session_state["user_id"]
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">📧 Email Marketing</h1>
        <p style="color: #888;">AI-Powered Email Campaigns, Reports & Newsletters</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Email Connection Status ──
    connector = EmailConnector()
    creds = connector._load_credentials()
    has_smtp = bool(creds.get("SMTP_USER") or creds.get("SENDGRID_API_KEY"))
    
    if has_smtp:
        st.success("✅ Email connector is configured and ready to send")
    else:
        st.warning("⚠️ Email not configured. Set SMTP_HOST, SMTP_USER, SMTP_PASS or SENDGRID_API_KEY in Streamlit secrets.")
        st.info("💡 Gmail users: Use an App Password (not your regular password). Get it from https://myaccount.google.com/apppasswords")
    
    st.markdown("---")
    
    # ── Quick Send Tab ──
    tab1, tab2, tab3, tab4 = st.tabs(["✉️ Quick Send", "📊 Client Report", "📬 Newsletter", "📋 Campaign"])
    
    with tab1:
        st.markdown("### ✉️ Send Single Email")
        with st.form("quick_email"):
            col1, col2 = st.columns(2)
            with col1:
                to_email = st.text_input("To Email *", placeholder="client@email.com")
                subject = st.text_input("Subject *", placeholder="Update from BHARATSOLVE")
            with col2:
                cc_email = st.text_input("CC", placeholder="optional@email.com")
                from_name = st.text_input("From Name", value="BHARATSOLVE SEO AGENCY")
            
            content = st.text_area("Message *", height=200,
                                   placeholder="Type your email content here... Supports Hinglish!")
            
            if st.form_submit_button("📨 Send Email", use_container_width=True, type="primary"):
                if to_email and subject and content:
                    with st.spinner("📨 Sending email..."):
                        result = send_email(to_email, subject, content, cc_email)
                    
                    if result.get("status") == "posted":
                        st.success(f"✅ Email sent to {to_email}!")
                    else:
                        st.error(f"❌ Failed: {result.get('message', 'Unknown error')}")
                else:
                    st.warning("⚠️ Please fill in To, Subject, and Message")
    
    with tab2:
        st.markdown("### 📊 Send Client Report")
        st.markdown("**AI generates a personalized SEO performance report and emails it to the client**")
        
        clients = get_clients(user_id)
        if clients:
            client_names = [c['name'] for c in clients]
            selected = st.selectbox("Select Client", client_names, key="report_client")
            client = next(c for c in clients if c['name'] == selected)
            
            if st.button("📊 Generate & Email Report", use_container_width=True, type="primary"):
                with st.spinner(f"🤖 Generating report for {client['name']}..."):
                    result = send_client_report_email(client['id'], user_id)
                
                if result.get("status") == "posted" or result.get("status") == "ok":
                    st.success(f"✅ Report sent to {client.get('email', 'N/A')}!")
                    if result.get("metrics"):
                        m = result["metrics"]
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Keywords", m.get("total_keywords", 0))
                        col2.metric("Top 10", m.get("top_10", 0))
                        col3.metric("Avg Position", m.get("avg_position", "N/A"))
                else:
                    st.error(f"❌ {result.get('message', 'Send failed')}")
            
            if client.get('email'):
                st.caption(f"📧 Will send to: {client['email']}")
            else:
                st.warning("⚠️ This client has no email address. Edit client to add one.")
        else:
            st.info("💡 Add clients first to send reports")
    
    with tab3:
        st.markdown("### 📬 Send Newsletter to All Clients")
        st.markdown("**AI creates and sends a professional newsletter to all your clients**")
        
        topic = st.text_input("Newsletter Topic (optional)", 
                              placeholder="e.g., Google's latest algorithm update")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📬 Send Newsletter", use_container_width=True, type="primary"):
                with st.spinner("🤖 Creating and sending newsletter to all clients..."):
                    result = send_newsletter(user_id, topic)
                
                if result.get("status") == "ok":
                    st.success(f"✅ Newsletter sent to {result.get('total_sent', 0)} clients!")
                    if result.get("subject"):
                        st.info(f"📧 Subject: {result['subject']}")
                else:
                    st.error(f"❌ {result.get('message', 'Failed')}")
        with col2:
            if st.button("📬 Send Weekly Digest (to Owner)", use_container_width=True):
                with st.spinner("🤖 Generating weekly digest..."):
                    result = send_weekly_digest(user_id)
                
                if result.get("status") == "posted":
                    st.success("✅ Weekly digest sent to owner email!")
                else:
                    st.warning(f"⚠️ {result.get('message', 'Set OWNER_EMAIL env var')}")
    
    with tab4:
        st.markdown("### 📋 Bulk Email Campaign")
        st.markdown("**Send a promotional or educational campaign to all clients**")
        
        campaign_type = st.selectbox(
            "Campaign Type",
            ["promotional", "educational", "offer", "update"],
            format_func=lambda x: {
                "promotional": "📢 Promotional",
                "educational": "📚 Educational",
                "offer": "🎉 Special Offer",
                "update": "📋 General Update"
            }[x]
        )
        
        custom_msg = st.text_area("Custom Message (optional)", height=100,
                                   placeholder="Leave empty to let AI generate content...")
        
        clients = get_clients(user_id)
        total = len(clients)
        st.caption(f"📧 Will send to {total} client(s)")
        
        if st.button("📨 Launch Campaign", use_container_width=True, type="primary"):
            if total == 0:
                st.warning("⚠️ No clients with email addresses")
            else:
                with st.spinner(f"🤖 Creating and sending {campaign_type} campaign..."):
                    result = send_bulk_campaign(user_id, campaign_type, custom_msg)
                
                if result.get("status") == "ok":
                    st.success(f"✅ Campaign sent to {result.get('total_sent', 0)}/{total} clients!")
                    st.info(f"📧 Subject: {result.get('subject', '')}")
                    st.info(f"📋 Type: {result.get('campaign_type', '').title()}")
                else:
                    st.error(f"❌ {result.get('message', 'Campaign failed')}")
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.8rem;">
        💡 All emails are sent via configured SMTP or SendGrid. 
        Templates include professional BHARATSOLVE branding.
    </div>
    """, unsafe_allow_html=True)
