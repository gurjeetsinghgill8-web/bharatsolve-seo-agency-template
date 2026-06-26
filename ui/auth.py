"""
BHARATSOLVE SEO AGENCY — Authentication UI
Login, registration, password management.
"""
import streamlit as st
import hashlib
from db.operations import create_user, get_user, update_subscription
from db.schema import init_db

# Initialize DB on first load
init_db()


def hash_password(password: str) -> str:
    """Simple password hashing for demo purposes."""
    return hashlib.sha256(password.encode()).hexdigest()


def check_auth() -> bool:
    """Check if user is authenticated in session."""
    return st.session_state.get("authenticated", False)


def logout():
    """Clear session state."""
    for key in ["authenticated", "username", "user_id", "user_data"]:
        if key in st.session_state:
            del st.session_state[key]


def login_page():
    """Render login/register page."""
    # Custom CSS for BharatSolve branding
    # (set_page_config is called from app.py)
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #e0f4ff, #b3e0ff, #87ceeb);
        }
        .main-title {
            text-align: center;
            padding: 2rem;
        }
        .main-title h1 {
            font-size: 3rem;
            color: #0077b6;
            text-shadow: none;
        }
        .main-title p {
            color: #555;
            font-size: 1.1rem;
        }
        .auth-card {
            background: rgba(255,255,255,0.8);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(10px);
            border: 1px solid #00b4d8;
        }
        .stTextInput input {
            background: white;
            border: 1px solid #90e0ef;
            color: #333;
            border-radius: 10px;
        }
        .stTextInput label {
            color: #333 !important;
        }
        .stButton button {
            background: linear-gradient(90deg, #0077b6, #00b4d8);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 2rem;
            font-weight: bold;
            width: 100%;
        }
        .footer {
            text-align: center;
            color: #666;
            padding: 2rem;
            font-size: 0.8rem;
        }
        /* Tab colors */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(255,255,255,0.6);
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #0077b6, #00b4d8) !important;
            color: white !important;
        }
        /* Text colors on login page */
        .stMarkdown, p, span, label {
            color: #333 !important;
        }
        h1, h2, h3 {
            color: #0077b6 !important;
        }
        .stAlert {
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.markdown("""
    <div class="main-title">
        <h1>🚀 BHARATSOLVE</h1>
        <p>Single Person SEO Agency — AI Powered 🤖</p>
        <p style="font-size: 0.9rem; color: #888;">देश का पहला AI SEO Agent जो आपकी पूरी SEO agency चलाएगा!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Auth tabs
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Register", "ℹ️ Plans"])
    
    with tab1:
        with st.container():
            st.markdown("### 👋 Welcome Back!")
            username = st.text_input("Username", key="login_user", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("🚀 Login", use_container_width=True):
                    if username and password:
                        user = get_user(username)
                        if user and user['password_hash'] == hash_password(password):
                            st.session_state["authenticated"] = True
                            st.session_state["username"] = username
                            st.session_state["user_id"] = user['id']
                            st.session_state["user_data"] = user
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password!")
                    else:
                        st.warning("⚠️ Please fill in all fields")
            with col2:
                st.markdown("")
    
    with tab2:
        with st.container():
            st.markdown("### 🆕 Create Your Account")
            col1, col2 = st.columns(2)
            
            with col1:
                new_user = st.text_input("Username", key="reg_user", placeholder="Choose a username")
                full_name = st.text_input("Full Name", key="reg_name", placeholder="Your name")
                plan = st.selectbox(
                    "Subscription Plan",
                    ["freelancer", "pro", "agency", "clinic", "lifetime"],
                    format_func=lambda x: {
                        "freelancer": "Freelancer ₹499/mo (3 clients)",
                        "pro": "Pro ₹1499/mo (10 clients)",
                        "agency": "Agency ₹4999/mo (Unlimited)",
                        "clinic": "Clinic ₹999/mo (1 client)",
                        "lifetime": "Lifetime ₹29,999 (Unlimited)"
                    }[x]
                )
            
            with col2:
                new_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Create a password")
                confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Confirm password")
                email = st.text_input("Email", key="reg_email", placeholder="your@email.com")
            
            if st.button("📝 Create Account", use_container_width=True):
                if not all([new_user, new_pass, confirm_pass]):
                    st.warning("⚠️ Please fill all required fields")
                elif new_pass != confirm_pass:
                    st.error("❌ Passwords don't match!")
                elif len(new_pass) < 4:
                    st.error("❌ Password must be at least 4 characters")
                else:
                    if create_user(new_user, hash_password(new_pass), full_name, email):
                        user = get_user(new_user)
                        if user:
                            update_subscription(new_user, plan)
                            st.success(f"✅ Account created! Welcome {new_user}! 🎉")
                            st.info("💡 Please login with your credentials")
                    else:
                        st.error("❌ Username already exists! Please choose another.")
    
    with tab3:
        with st.container():
            st.markdown("### 💎 Subscription Plans")
            
            plans_data = [
                ("🚀 Freelancer", "₹499/mo", "3 Clients", ["Keyword Research", "Content Writing", "Rank Tracking", "Social Media"]),
                ("💼 Pro", "₹1,499/mo", "10 Clients", ["All Freelancer features", "Tech SEO", "Link Building", "Clinic & Alumni"]),
                ("🏢 Agency", "₹4,999/mo", "Unlimited Clients", ["All Pro features", "White Label", "Priority Support", "All Agents"]),
                ("🏥 Clinic", "₹999/mo", "1 Client", ["Clinic-specific SEO", "Social Media", "Local SEO", "Rank Tracking"]),
                ("👑 Lifetime", "₹29,999", "Unlimited", ["Everything Unlimited", "Lifetime Access", "White Label", "Premium Support"]),
            ]
            
            for name, price, clients, features in plans_data:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin: 0.5rem 0; border: 1px solid rgba(255,255,255,0.1);">
                    <h3 style="color: #00d2ff; margin: 0;">{name}</h3>
                    <h2 style="margin: 0.2rem 0;">{price}</h2>
                    <p style="color: #888;">👥 {clients}</p>
                    <ul style="color: #ccc;">
                        {''.join(f'<li>{f}</li>' for f in features)}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="footer">
        Made with ❤️ by BharatSolve | Powered by AI 🤖
    </div>
    """, unsafe_allow_html=True)
