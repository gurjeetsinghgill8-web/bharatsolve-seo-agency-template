"""
BHARATSOLVE SEO AGENCY — Settings UI
API keys, subscription, config management.
"""
import streamlit as st
import os
import json
from datetime import datetime
from db.operations import get_user, update_subscription
from db.schema import init_db


def show_settings_page():
    """Render settings page."""
    user_id = st.session_state["user_id"]
    username = st.session_state["username"]
    user_data = st.session_state.get("user_data", {})
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">⚙️ Settings</h1>
        <p style="color: #888;">Manage Your SEO Agency Configuration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ── User Profile ──
    with st.expander("👤 Profile", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Username:** {username}")
            st.markdown(f"**Full Name:** {user_data.get('full_name', 'N/A')}")
            st.markdown(f"**Email:** {user_data.get('email', 'N/A')}")
        with col2:
            st.markdown(f"**Plan:** {user_data.get('subscription_tier', 'freelancer').title()}")
            st.markdown(f"**Admin:** {'Yes' if user_data.get('is_admin') else 'No'}")
            st.markdown(f"**Since:** {user_data.get('created_at', 'N/A')[:10] if user_data.get('created_at') else 'N/A'}")
    
    # ── API Keys ──
    with st.expander("🔑 API Keys", expanded=True):
        is_cloud = st.session_state.get("_is_cloud", os.environ.get('STREAMLIT_RUNNER_ID') is not None)
        
        if is_cloud:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin: 1rem 0;
                        border: 1px solid rgba(0,200,100,0.3);">
                <strong>☁️ Streamlit Cloud Mode</strong><br>
                API keys are set via <strong>Streamlit Secrets</strong> (Settings → Secrets).
                <br>Go to your app dashboard → Settings → Secrets → Add your keys.
            </div>
            """, unsafe_allow_html=True)
            st.info("💡 Keys are already set if the app is working. Edit them in Streamlit Cloud dashboard.")
        else:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin: 1rem 0;
                        border: 1px solid rgba(255,210,0,0.3);">
                <strong>⚠️ Important:</strong> API keys are stored in <code>.env</code> file on disk.
                Get your free API keys from:
                <br>• <a href="https://console.groq.com" target="_blank">Groq</a> (Free, fast LLM)
                <br>• <a href="https://aistudio.google.com" target="_blank">Google AI Studio</a> (Free Gemini)
                <br>• <a href="https://platform.openai.com" target="_blank">OpenAI</a>
                <br>• <a href="https://platform.deepseek.com" target="_blank">DeepSeek</a>
            </div>
            """, unsafe_allow_html=True)
        
        # Only show .env editor when running locally
        if not is_cloud:
            # Read current .env
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
            env_vars = {}
            if os.path.exists(env_path):
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split('=', 1)
                            if len(parts) == 2:
                                env_vars[parts[0]] = parts[1].strip().strip('"').strip("'")
            
            with st.form("api_keys_form"):
                groq_key = st.text_input("GROQ_API_KEY", value=env_vars.get("GROQ_API_KEY", ""), 
                                         type="password", placeholder="gsk_...")
                gemini_key = st.text_input("GEMINI_API_KEY", value=env_vars.get("GEMINI_API_KEY", ""),
                                           type="password", placeholder="AIza...")
                openai_key = st.text_input("OPENAI_API_KEY", value=env_vars.get("OPENAI_API_KEY", ""),
                                           type="password", placeholder="sk-...")
                deepseek_key = st.text_input("DEEPSEEK_API_KEY", value=env_vars.get("DEEPSEEK_API_KEY", ""),
                                             type="password", placeholder="sk-...")
                
                if st.form_submit_button("💾 Save API Keys", use_container_width=True):
                    # Update .env file
                    env_content = """# BHARATSOLVE SEO AGENCY - API Keys
# अपनी API keys यहाँ डालें
GROQ_API_KEY={groq}
GEMINI_API_KEY={gemini}
OPENAI_API_KEY={openai}
DEEPSEEK_API_KEY={deepseek}
CLAUDE_API_KEY=
"""
                    env_content = env_content.format(
                        groq=groq_key or "",
                        gemini=gemini_key or "",
                        openai=openai_key or "",
                        deepseek=deepseek_key or ""
                    )
                    
                    with open(env_path, 'w') as f:
                        f.write(env_content)
                    
                    # Reload env
                    with open(env_path) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                parts = line.split('=', 1)
                                if len(parts) == 2 and parts[1]:
                                    os.environ[parts[0]] = parts[1]
                    
                    st.success("✅ API Keys saved! Restart app if needed.")
    
    # ── Subscription ──
    with st.expander("💎 Subscription Plan", expanded=False):
        st.markdown("**Current Plan:** " + user_data.get('subscription_tier', 'freelancer').title())
        
        plans = {
            "freelancer": "Freelancer ₹499/mo - 3 clients",
            "pro": "Pro ₹1,499/mo - 10 clients",
            "agency": "Agency ₹4,999/mo - Unlimited clients",
            "clinic": "Clinic ₹999/mo - 1 client",
            "lifetime": "Lifetime ₹29,999 - Unlimited"
        }
        
        new_plan = st.selectbox(
            "Upgrade Plan",
            list(plans.keys()),
            index=list(plans.keys()).index(user_data.get('subscription_tier', 'freelancer')),
            format_func=lambda x: plans[x]
        )
        
        if st.button("🔄 Update Plan", use_container_width=True):
            update_subscription(username, new_plan)
            st.success(f"✅ Plan updated to {new_plan.title()}!")
            st.rerun()
    
    # ── System Info ──
    with st.expander("ℹ️ System Information", expanded=False):
        st.markdown("**BHARATSOLVE SEO AGENCY v1.0.0**")
        st.markdown("**Tech Stack:** Python, Streamlit, SQLite, LLM Agents")
        st.markdown("**Agents Available:** Manager, Keyword, Content, Rank, Social")
        st.markdown(f"**Database:** seo_agency.db")
        st.markdown(f"**Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Config display
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
            st.json(config)
    
    st.markdown("---")
    
    # ── Danger Zone ──
    with st.expander("⚠️ Danger Zone", expanded=False):
        st.warning("These actions are irreversible!")
        
        if st.button("🗑️ Reset All Data (Delete Database)", use_container_width=True):
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "seo_agency.db")
            if os.path.exists(db_path):
                os.remove(db_path)
                st.success("✅ Database deleted. App will recreate on next load.")
                st.rerun()
            else:
                st.info("No database found.")
