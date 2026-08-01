"""
BHARATSOLVE SEO AGENCY — Multi-Location Local SEO Page Builder
Generates hyper-local landing page content targeting Meerut, Delhi NCR, Mohiuddinpur, Modinagar, and Hapur.
Includes 1-click WhatsApp/Telegram sharing.
"""

import streamlit as st
from utils.share_links import get_whatsapp_share_url, get_telegram_share_url

TARGET_CITIES = ["Meerut", "Delhi NCR", "Mohiuddinpur", "Modinagar", "Hapur"]

def render_multi_location_seo():
    st.markdown("### 🌐 Multi-Location Local SEO Engine")
    st.markdown("Expand Gill Heart Clinic's reach across Meerut, Delhi NCR, Mohiuddinpur, Modinagar, & Hapur.")

    city = st.selectbox("Select Target City / Region", TARGET_CITIES, key="multi_loc_city")
    
    st.info(f"📍 Target Location Selected: **{city}**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### 🎯 High-Intent Keywords for {city}")
        st.markdown(f"""
        - Best Heart Doctor in {city}
        - Low Cost Cardiac Care {city}
        - Blood Pressure Specialist near {city}
        - Jan Aushadhi Generic Medicine Heart Doctor {city}
        - ECG & Echo Consultation {city}
        """)
    
    with col2:
        st.markdown("#### 🚀 Action Options")
        wa_text = f"🌐 *Local SEO Expansion Page: {city}*\nTargeting keywords for {city}.\nDoctor: Dr. Gurjeet Singh Gill, Cardiac Physician."
        wa_url = get_whatsapp_share_url(wa_text)
        tg_url = get_telegram_share_url(wa_text)
        
        st.markdown(f'''
        <a href="{wa_url}" target="_blank" style="text-decoration:none;">
            <div style="background:#25D366; color:white; font-weight:bold; text-align:center; 
                        padding:0.6rem; border-radius:10px; font-size:0.9rem; margin-bottom:10px;">
                📱 Send Local Keywords to WhatsApp
            </div>
        </a>
        <a href="{tg_url}" target="_blank" style="text-decoration:none;">
            <div style="background:#0088cc; color:white; font-weight:bold; text-align:center; 
                        padding:0.6rem; border-radius:10px; font-size:0.9rem;">
                ✈️ Send Local Keywords to Telegram
            </div>
        </a>
        ''', unsafe_allow_html=True)
