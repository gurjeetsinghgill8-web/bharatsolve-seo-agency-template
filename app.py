"""
BHARATSOLVE SEO AGENCY
🚀 Single Person SEO Agency — AI Fully Automated
Main Application Entry Point
Compatible with: Local PC, Streamlit Cloud, Docker
"""
import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Load environment variables (local dev) + Streamlit secrets (cloud)
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── PWA / Streamlit Cloud detection ──
IS_STREAMLIT_CLOUD = os.environ.get('STREAMLIT_RUNNER_ID') is not None

# Import UI modules
from ui.auth import login_page, check_auth, logout
from ui.dashboard import show_dashboard
from ui.clients import show_clients_page
from ui.keywords import show_keywords_page
from ui.content import show_content_page
from ui.rankings import show_rankings_page
from ui.social import show_social_page
from ui.email import show_email_page
from ui.reports import show_reports_page
from ui.settings import show_settings_page
from ui.publisher import show_publisher_page
from ui.google_business import show_google_business_page
from ui.scheduler import show_scheduler_page
from ui.backup import show_backup_page

# Import DB init
from db.schema import init_db

# ── Page Config ──
st.set_page_config(
    page_title="BHARATSOLVE SEO AGENCY",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': '🚀 BHARATSOLVE SEO AGENCY v1.0 — Single Person AI SEO Agency'
    }
)

# ── PWA Meta Tags (for installable app) ──
# Note: On Streamlit Cloud, /static/ is served via the app's root
st.markdown("""
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="BHARATSOLVE SEO">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0077b6">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="manifest" crossorigin="use-credentials" href="/app/static/manifest.json">
<link rel="apple-touch-icon" href="/app/static/icon.svg">
""", unsafe_allow_html=True)

# ── Service Worker Registration (for offline support) ──
st.markdown("""
<script>
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/app/static/sw.js').then(
            function(registration) { console.log('SW registered'); },
            function(err) { console.log('SW failed:', err); }
        );
    });
}

// Before install prompt handler
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    console.log('PWA install prompt available');
});
</script>
""", unsafe_allow_html=True)

# ── Global CSS — Sky Blue Light Theme ──
st.markdown("""
<style>
    /* ═══ MAIN BACKGROUND — Sky Blue Gradient ═══ */
    .stApp {
        background: linear-gradient(135deg, #e0f7ff, #b3e5ff, #e0f7ff);
    }
    
    /* ═══ SIDEBAR — Clean Light Blue ═══ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #d4edff, #b3e0ff) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #333 !important;
    }
    
    .sidebar-title {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #00b4d8;
    }
    .sidebar-title h2 {
        color: #0077b6 !important;
        font-size: 1.5rem;
        margin: 0;
    }
    .sidebar-title p {
        color: #555;
        font-size: 0.8rem;
        margin: 0;
    }
    
    /* ═══ NAVIGATION BUTTONS ═══ */
    .stSidebar .stButton button {
        background: rgba(255,255,255,0.7);
        border: 1px solid #90e0ef;
        border-radius: 10px;
        color: #333;
        text-align: left;
        padding: 0.6rem 1rem;
        margin: 0.2rem 0;
        transition: all 0.3s;
    }
    .stSidebar .stButton button:hover {
        background: #00b4d8;
        border-color: #0077b6;
        color: white !important;
    }
    
    /* ═══ TABS ═══ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: rgba(255,255,255,0.6);
        border-radius: 10px;
        padding: 0.3rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #555;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #0077b6, #00b4d8) !important;
        color: white !important;
    }
    
    /* ═══ METRIC CARDS ═══ */
    .stMetric {
        background: rgba(255,255,255,0.8);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #90e0ef;
        box-shadow: 0 2px 8px rgba(0,119,182,0.08);
    }
    .stMetric label, .stMetric [data-testid="stMetricValue"] {
        color: #333 !important;
    }
    
    /* ═══ INPUT FIELDS ═══ */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background: white !important;
        border: 1px solid #90e0ef !important;
        color: #333 !important;
        border-radius: 8px !important;
    }
    .stTextInput label, .stSelectbox label, .stTextArea label {
        color: #333 !important;
    }
    
    /* ═══ BUTTONS ═══ */
    .stButton button {
        border-radius: 10px !important;
        font-weight: bold !important;
    }
    .stButton button[kind="primary"] {
        background: linear-gradient(90deg, #0077b6, #00b4d8) !important;
        color: white !important;
        border: none !important;
    }
    
    /* ═══ DATA FRAMES ═══ */
    .stDataFrame {
        background: rgba(255,255,255,0.7);
        border-radius: 10px;
    }
    
    /* ═══ EXPANDERS ═══ */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.6);
        border-radius: 8px;
        font-weight: bold;
        color: #0077b6 !important;
    }
    
    /* ═══ ALERT BOXES ═══ */
    .stAlert {
        border-radius: 10px;
        border: none;
    }
    
    /* ═══ SCROLLBAR ═══ */
    ::-webkit-scrollbar {
        width: 6px;
        background: #d4edff;
    }
    ::-webkit-scrollbar-thumb {
        background: #00b4d8;
        border-radius: 3px;
    }
    
    /* ═══ ALL TEXT ═══ */
    * {
        color: #333;
    }
    .stMarkdown, p, span, label, li {
        color: #333 !important;
    }
    
    /* ═══ HEADERS ═══ */
    h1, h2, h3 {
        color: #0077b6 !important;
    }
    h1 {
        border-bottom: 2px solid #00b4d8;
        padding-bottom: 0.3rem;
    }
    
    /* ═══ DIVIDERS ═══ */
    hr {
        border-color: rgba(0,180,216,0.3);
    }
    
    /* ═══ CODE BLOCKS ═══ */
    code {
        background: #e8f4fd !important;
        color: #0077b6 !important;
    }
    
    /* ═══ SIDEBAR USER INFO ═══ */
    .css-1v3fvcr, .css-1wrcr25 {
        color: #333 !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Initialize database ──
init_db()

# Store cloud mode in session state for UI pages
if "_is_cloud" not in st.session_state:
    st.session_state["_is_cloud"] = IS_STREAMLIT_CLOUD


# ── Main App ──
def main():
    """Main application router."""
    
    # Check authentication
    if not check_auth():
        login_page()
        return
    
    # ── Sidebar ──
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-title">
            <h2>🚀 BHARATSOLVE</h2>
            <p>SEO Agency OS v1.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<p style='text-align: center; color: #0077b6; font-weight: bold;'>👤 {st.session_state['username']}</p>", 
                    unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        nav_items = {
            "🏠 Dashboard": "dashboard",
            "👥 Clients": "clients",
            "🔑 Keywords": "keywords",
            "📝 Content": "content",
            "📊 Rankings": "rankings",
            "📱 Social": "social",
            "📧 Email": "email",
            "🌐 Publish": "publisher",
            "🏪 Google Biz": "google_business",
            "⏰ Scheduler": "scheduler",
            "💾 Backup": "backup",
            "📈 Reports": "reports",
            "⚙️ Settings": "settings"
        }
        
        for label, page in nav_items.items():
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                st.session_state["page"] = page
        
        st.markdown("---")
        
        # Subscription info
        user_data = st.session_state.get("user_data", {})
        tier = user_data.get("subscription_tier", "freelancer")
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.8); border-radius: 10px; padding: 0.8rem; text-align: center; margin: 1rem 0; border: 1px solid #90e0ef;">
            <p style="color: #666; margin: 0; font-size: 0.8rem;">Current Plan</p>
            <p style="color: #0077b6; margin: 0; font-weight: bold;">{tier.title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Install App button (PWA)
        st.markdown("""
        <div style="text-align: center; margin: 0.5rem 0;">
            <button onclick="if(deferredPrompt) { deferredPrompt.prompt(); }" 
                    style="background: rgba(255,255,255,0.7); border: 1px solid #90e0ef; 
                           border-radius: 10px; padding: 0.4rem 1rem; color: #0077b6; 
                           cursor: pointer; font-size: 0.9rem; width: 100%;">
                📲 Install App
            </button>
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-Pilot Toggle (disabled on Streamlit Cloud)
        st.markdown("---")
        if IS_STREAMLIT_CLOUD:
            st.info("🤖 Auto-Pilot runs automatically on cloud")
        else:
            auto_pilot = st.toggle("🤖 Auto-Pilot Mode", key="auto_pilot_toggle", 
                                   value=st.session_state.get("auto_pilot_active", False))
            if auto_pilot and not st.session_state.get("auto_pilot_active", False):
                from harness.auto_pilot import run_auto_pilot
                msg = run_auto_pilot(interval_minutes=60)
                st.session_state["auto_pilot_active"] = True
                st.success(msg)
            elif not auto_pilot and st.session_state.get("auto_pilot_active", False):
                from harness.auto_pilot import stop_auto_pilot
                msg = stop_auto_pilot()
                st.session_state["auto_pilot_active"] = False
                st.info(msg)
        
        # Logout
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # ── Page Router ──
    page = st.session_state.get("page", "dashboard")
    
    if page == "dashboard":
        show_dashboard()
    elif page == "clients":
        show_clients_page()
    elif page == "keywords":
        show_keywords_page()
    elif page == "content":
        show_content_page()
    elif page == "rankings":
        show_rankings_page()
    elif page == "social":
        show_social_page()
    elif page == "email":
        show_email_page()
    elif page == "publisher":
        show_publisher_page()
    elif page == "google_business":
        show_google_business_page()
    elif page == "scheduler":
        show_scheduler_page()
    elif page == "backup":
        show_backup_page()
    elif page == "reports":
        show_reports_page()
    elif page == "settings":
        show_settings_page()


if __name__ == "__main__":
    main()
