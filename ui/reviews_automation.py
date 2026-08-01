"""
BHARATSOLVE SEO AGENCY — Google Business Profile Review Auto-Reply Engine
Generates compliant, professional patient review replies in Hindi & English
with 1-click WhatsApp & Telegram share links!
"""

import streamlit as st
import urllib.parse
from utils.llm_client import call_llm
from utils.share_links import get_whatsapp_share_url, get_telegram_share_url

SAMPLE_REVIEWS = [
    {"reviewer": "Ramesh Verma", "rating": 5, "text": "Dr. Gill is very patient and polite. Recommended Jan Aushadhi generic medicine which saved me huge money!", "date": "2 days ago"},
    {"reviewer": "Anita Singh", "rating": 5, "text": "Best heart doctor in Meerut! Fees is very reasonable and diet counseling was very helpful.", "date": "1 week ago"},
    {"reviewer": "Sanjay Sharma", "rating": 4, "text": "Very clean clinic and good doctor advice. Did minimal tests.", "date": "2 weeks ago"}
]


def render_reviews_automation():
    st.markdown("### ⭐ Google Business Profile Review Auto-Reply Engine")
    st.markdown("Automated patient review response generator with 1-click WhatsApp/Telegram sharing.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 💬 Patient Review Input")
        reviewer_name = st.text_input("Reviewer Name", value="Patient Name", key="rev_name")
        star_rating = st.slider("Star Rating", 1, 5, 5, key="rev_rating")
        review_text = st.text_area("Patient Review Text", 
                                   value="Dr. Gill is an excellent doctor. He explained everything nicely, gave diet advice, and recommended affordable Jan Aushadhi generic medicines.", 
                                   height=120, key="rev_text")
        
        reply_lang = st.radio("Reply Language", ["Hinglish / Hindi", "English"], horizontal=True, key="rev_lang")
        
        gen_reply_btn = st.button("🤖 Generate Professional Reply", type="primary", use_container_width=True, key="gen_reply_btn")

    if gen_reply_btn or st.session_state.get("last_review_reply"):
        if gen_reply_btn:
            prompt = f"""
Write a polite, professional doctor's reply to a Google Business Profile review for Gill Heart Clinic, Meerut.
Doctor: Dr. Gurjeet Singh Gill, Cardiac Physician
Reviewer: {reviewer_name}
Rating: {star_rating} stars
Review: "{review_text}"
Reply Language: {reply_lang}

Rules:
1. Thank the patient warmly.
2. Reiterate Dr. Gill's commitment to quality preventive cardiac care, diet counseling, and patient affordability.
3. Professional medical tone. Keep under 100 words.
"""
            messages = [
                {"role": "system", "content": "You are a professional medical clinic manager writing Google review replies."},
                {"role": "user", "content": prompt}
            ]
            try:
                reply_text = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
                st.session_state["last_review_reply"] = reply_text
            except Exception as e:
                reply_text = f"Thank you {reviewer_name} for your trust in Gill Heart Clinic! We wish you continuous good heart health."
                st.session_state["last_review_reply"] = reply_text
        
        reply = st.session_state.get("last_review_reply", "")
        
        with col2:
            st.markdown("#### ✅ Generated Doctor's Reply")
            edited_reply = st.text_area("Review Reply (Edit if needed)", value=reply, height=140, key="edit_rev_reply")
            
            st.markdown("##### 📱 1-Click Direct Share Links")
            wa_msg = f"⭐ *Google Review Reply for {reviewer_name}*\n\nReview: \"{review_text}\"\n\n*Dr. Gill's Reply*:\n{edited_reply}"
            
            wa_url = get_whatsapp_share_url(wa_msg)
            tg_url = get_telegram_share_url(wa_msg)
            
            col_wa, col_tg = st.columns(2)
            with col_wa:
                st.markdown(f'''
                <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                    <div style="background:#25D366; color:white; font-weight:bold; text-align:center; 
                                padding:0.6rem; border-radius:10px; font-size:0.9rem;">
                        📱 Send to WhatsApp
                    </div>
                </a>
                ''', unsafe_allow_html=True)
            
            with col_tg:
                st.markdown(f'''
                <a href="{tg_url}" target="_blank" style="text-decoration:none;">
                    <div style="background:#0088cc; color:white; font-weight:bold; text-align:center; 
                                padding:0.6rem; border-radius:10px; font-size:0.9rem;">
                        ✈️ Send to Telegram
                    </div>
                </a>
                ''', unsafe_allow_html=True)
