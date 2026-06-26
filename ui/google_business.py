"""
BHARATSOLVE SEO AGENCY — Google Business Profile Management UI
Full GBP integration: posts, reviews, insights, Q&A.
"""
import streamlit as st
import json
import os
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from db.operations import (
    get_clients, get_projects, log_agent_action, get_wp_sites
)

# ── Try importing google api client for advanced GBP API calls ──
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.oauth2.credentials import Credentials
    GOOGLE_API = True
except ImportError:
    GOOGLE_API = False


def _get_gbp_token() -> str:
    """Get Google Business Profile token from multiple sources."""
    import os
    token = os.getenv("GOOGLE_BUSINESS_TOKEN", "")
    if not token:
        try:
            import streamlit as st
            token = st.secrets.get("GOOGLE_BUSINESS_TOKEN", "")
        except:
            pass
    return token


def _get_gbp_account() -> str:
    """Get GBP account name."""
    import os
    account = os.getenv("GOOGLE_BUSINESS_ACCOUNT", "")
    if not account:
        try:
            import streamlit as st
            account = st.secrets.get("GOOGLE_BUSINESS_ACCOUNT", "")
        except:
            pass
    return account


def _get_gbp_location() -> str:
    """Get GBP location name."""
    import os
    loc = os.getenv("GOOGLE_BUSINESS_LOCATION", "")
    if not loc:
        try:
            import streamlit as st
            loc = st.secrets.get("GOOGLE_BUSINESS_LOCATION", "")
        except:
            pass
    return loc


def get_gbp_headers() -> dict:
    """Get headers for GBP API calls."""
    token = _get_gbp_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


@st.cache_data(ttl=300)
def fetch_locations() -> List[Dict]:
    """
    Fetch all GBP locations for the authenticated account.
    GET https://mybusinessaccountmanagement.googleapis.com/v1/accounts/{account}/locations
    """
    account = _get_gbp_account()
    if not account:
        return []
    
    try:
        url = f"https://mybusinessaccountmanagement.googleapis.com/v1/accounts/{account}/locations"
        headers = get_gbp_headers()
        resp = requests.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            return data.get("locations", [])
        else:
            st.error(f"❌ GBP API error: {resp.status_code} — {resp.text[:200]}")
            return []
    except Exception as e:
        st.error(f"❌ Fetch locations error: {e}")
        return []


@st.cache_data(ttl=120)
def fetch_posts(location_name: str, page_size: int = 20) -> List[Dict]:
    """
    Fetch GBP posts for a location.
    GET https://mybusiness.googleapis.com/v4/{location_name}/localPosts
    """
    if not location_name:
        return []
    
    try:
        url = f"https://mybusiness.googleapis.com/v4/{location_name}/localPosts"
        headers = get_gbp_headers()
        params = {"pageSize": min(page_size, 100)}
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            return data.get("localPosts", [])
        else:
            return []
    except:
        return []


@st.cache_data(ttl=300)
def fetch_insights(location_name: str) -> Dict:
    """
    Fetch GBP insights for a location.
    Uses the reports API: POST https://mybusiness.googleapis.com/v4/{location_name}/reportInsights
    """
    if not location_name:
        return {}
    
    try:
        url = f"https://mybusiness.googleapis.com/v4/{location_name}:reportInsights"
        headers = get_gbp_headers()
        
        # Basic metrics request
        body = {
            "basicRequest": {
                "metricRequests": [
                    {"metric": "ALL"},
                ],
                "timeRange": {
                    "startTime": (datetime.now() - timedelta(days=28)).isoformat() + "Z",
                    "endTime": datetime.now().isoformat() + "Z",
                }
            }
        }
        resp = requests.post(url, headers=headers, json=body, timeout=15)
        
        if resp.status_code == 200:
            return resp.json()
        return {}
    except:
        return {}


@st.cache_data(ttl=300)
def fetch_reviews(location_name: str) -> List[Dict]:
    """
    Fetch GBP reviews for a location.
    GET https://mybusiness.googleapis.com/v4/{location_name}/reviews
    """
    if not location_name:
        return []
    
    try:
        url = f"https://mybusiness.googleapis.com/v4/{location_name}/reviews"
        headers = get_gbp_headers()
        resp = requests.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            return data.get("reviews", [])
        return []
    except:
        return []


def create_post(location_name: str, content: str, media_url: str = "", 
                post_type: str = "STANDARD", action_type: str = "") -> Dict:
    """
    Create a new GBP post.
    POST https://mybusiness.googleapis.com/v4/{location_name}/localPosts
    """
    if not location_name or not content:
        return {"success": False, "error": "Missing location or content"}
    
    try:
        url = f"https://mybusiness.googleapis.com/v4/{location_name}/localPosts"
        headers = get_gbp_headers()
        
        body = {
            "summary": content[:1500],
            "topicType": post_type,
        }
        
        if media_url:
            body["media"] = [{
                "mediaFormat": "PHOTO",
                "sourceUrl": media_url
            }]
        
        if action_type:
            body["callToAction"] = {
                "actionType": action_type,
                "url": ""
            }
        
        resp = requests.post(url, headers=headers, json=body, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            post_id = data.get("name", "")
            return {
                "success": True,
                "post_id": post_id,
                "url": f"https://business.google.com/posts/{post_id}",
                "created_at": data.get("createTime", "")
            }
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def reply_to_review(location_name: str, review_name: str, reply_text: str) -> Dict:
    """
    Reply to a GBP review.
    GET https://mybusiness.googleapis.com/v4/{review_name}/reply
    """
    if not location_name or not review_name or not reply_text:
        return {"success": False, "error": "Missing parameters"}
    
    try:
        url = f"https://mybusiness.googleapis.com/v4/{review_name}/reply"
        headers = get_gbp_headers()
        body = {
            "comment": reply_text[:4096]
        }
        resp = requests.get(url, headers=headers, json=body, timeout=15)
        
        if resp.status_code == 200:
            return {"success": True}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def show_google_business_page():
    """Render the Google Business Profile management page."""
    user_id = st.session_state["user_id"]
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">🏪 Google Business Profile</h1>
        <p style="color: #888;">Manage GBP posts, reviews, and insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Check configuration ──
    has_token = bool(_get_gbp_token())
    has_account = bool(_get_gbp_account())
    
    if not has_token or not has_account:
        st.warning("⚠️ **Google Business Profile not configured!**")
        
        with st.expander("🔧 Setup Guide", expanded=True):
            st.markdown("""
            ### How to connect Google Business Profile:
            
            1. **Get Access Token:**
               - Go to [Google Cloud Console](https://console.cloud.google.com/)
               - Create a project or select existing
               - Enable "Google Business Profile API"
               - Create OAuth 2.0 credentials
               - Use OAuth playground to get token with scope: `https://www.googleapis.com/auth/business.manage`
            
            2. **Get Account & Location IDs:**
               - Call: `GET https://mybusinessaccountmanagement.googleapis.com/v1/accounts`
               - Call: `GET https://mybusinessaccountmanagement.googleapis.com/v1/accounts/{account}/locations`
            
            3. **Add to your .env or Streamlit secrets:**
            ```env
            GOOGLE_BUSINESS_TOKEN=your_oauth_token
            GOOGLE_BUSINESS_ACCOUNT=accounts/123456789
            GOOGLE_BUSINESS_LOCATION=accounts/123456789/locations/987654321
            ```
            """)
        
        with st.form("gbp_creds_form"):
            st.markdown("#### Quick Config")
            token = st.text_input("Access Token", type="password", 
                                   help="Paste your OAuth 2.0 access token")
            account = st.text_input("Account Name", placeholder="accounts/123456789")
            location = st.text_input("Location Name", placeholder="accounts/.../locations/...")
            
            if st.form_submit_button("💾 Save & Test", type="primary", use_container_width=True):
                if token and account:
                    # Save to session state for this session
                    st.session_state['gbp_token'] = token
                    st.session_state['gbp_account'] = account
                    if location:
                        st.session_state['gbp_location'] = location
                    
                    # Test connection
                    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                    try:
                        url = f"https://mybusinessaccountmanagement.googleapis.com/v1/accounts/{account}"
                        resp = requests.get(url, headers=headers, timeout=10)
                        if resp.status_code == 200:
                            st.success("✅ Connected to Google Business Profile!")
                            st.rerun()
                        else:
                            st.error(f"❌ Connection failed: {resp.status_code} - {resp.text[:150]}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.error("❌ Token and Account are required!")
        return
    
    # ── Connected — show GBP dashboard ──
    account = _get_gbp_account()
    location = _get_gbp_location()
    
    # Get locations if no specific location set
    if not location:
        locations = fetch_locations()
        if locations:
            loc_names = [l.get('name', '') for l in locations]
            loc_display = [f"{l.get('locationName', 'Unknown')} - {l.get('address', {}).get('city', '')}" 
                          for l in locations]
            selected_loc = st.selectbox("Select Business Location", loc_display, key="gbp_loc_selector")
            idx = loc_display.index(selected_loc)
            location = loc_names[idx]
            st.session_state['gbp_location'] = location
    
    if not location:
        st.error("❌ No locations found. Check your GBP account permissions.")
        return
    
    # ── Dashboard Metrics ──
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    insights = fetch_insights(location)
    
    with metrics_col1:
        st.metric("📊 Profile Views", insights.get("metrics", {}).get("profileView", {}).get("total", "—"))
    with metrics_col2:
        st.metric("🔍 Search Views", insights.get("metrics", {}).get("searchView", {}).get("total", "—"))
    with metrics_col3:
        # Count posts
        posts = fetch_posts(location)
        st.metric("📝 Posts", len(posts))
    with metrics_col4:
        reviews = fetch_reviews(location)
        avg_rating = "—"
        if reviews:
            ratings = [r.get('starRating', 0) for r in reviews if r.get('starRating')]
            if ratings:
                avg_rating = round(sum(ratings) / len(ratings), 1)
        st.metric("⭐ Avg Rating", avg_rating)
    
    st.markdown("---")
    
    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Posts", "⭐ Reviews", "📊 Insights", "⚙️ Settings"])
    
    # ════════════════════════════════════════
    # TAB 1: Posts
    # ════════════════════════════════════════
    with tab1:
        st.markdown("### ✍️ Create Post")
        
        with st.form("gbp_create_post"):
            post_content = st.text_area("Post Content", max_chars=1500,
                                         placeholder="Share an update, offer, or event...",
                                         height=120)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                post_type = st.selectbox("Post Type", 
                    ["STANDARD", "OFFER", "EVENT", "PRODUCT"],
                    format_func=lambda x: x.title())
            with col2:
                media_url = st.text_input("Media URL (optional)", 
                                           placeholder="https://example.com/image.jpg")
            with col3:
                action_type = st.selectbox("Call to Action (optional)",
                    ["", "BOOK", "CALL", "LEARN_MORE", "SIGN_UP", "SHOP"],
                    format_func=lambda x: x.replace('_', ' ').title() if x else "None")
            
            if st.form_submit_button("🚀 Publish to GBP", type="primary", use_container_width=True):
                if post_content:
                    with st.spinner("Publishing to Google Business Profile..."):
                        result = create_post(location, post_content, media_url, post_type, action_type)
                    
                    if result.get('success'):
                        st.success(f"✅ Post published! [View]({result.get('url', '#')})")
                        log_agent_action('google_business', f"GBP post created: {result.get('post_id', '')}")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('error', 'Publish failed')}")
                else:
                    st.warning("⚠️ Please enter post content!")
        
        st.markdown("---")
        st.markdown("### 📋 Recent Posts")
        
        posts = fetch_posts(location)
        if posts:
            for post in posts:
                with st.container():
                    st.markdown(f"""
                    **{post.get('summary', 'No content')[:200]}**
                    └ 🆔 {post.get('name', '').split('/')[-1][:20]}... 
                    └ 🏷️ {post.get('topicType', 'STANDARD').title()}
                    └ 📅 {post.get('createTime', '')[:10]}
                    """)
                    
                    # Show media if any
                    media = post.get('media', [])
                    if media:
                        for m in media:
                            if m.get('sourceUrl'):
                                st.image(m['sourceUrl'], width=200)
                    
                    # Call to action
                    cta = post.get('callToAction')
                    if cta:
                        st.markdown(f"🔗 [{cta.get('actionType', '').replace('_', ' ').title()}]({cta.get('url', '#')})")
                    
                    st.markdown("---")
        else:
            st.info("💡 No posts yet. Create your first post above!")
    
    # ════════════════════════════════════════
    # TAB 2: Reviews
    # ════════════════════════════════════════
    with tab2:
        st.markdown("### ⭐ Customer Reviews")
        
        reviews = fetch_reviews(location)
        
        if reviews:
            # Summary stats
            ratings = [r.get('starRating', 0) for r in reviews if r.get('starRating')]
            if ratings:
                avg = sum(ratings) / len(ratings)
                st.markdown(f"""
                **Average Rating:** {'⭐' * int(round(avg))} ({avg:.1f}/5.0)
                **Total Reviews:** {len(reviews)}
                """)
            
            for review in reviews[:10]:
                star = review.get('starRating', 0)
                stars = '⭐' * (int(star) if isinstance(star, int) else 0)
                
                with st.expander(f"{stars} — {review.get('reviewer', {}).get('displayName', 'Anonymous')}"):
                    st.markdown(f"**Review:** {review.get('comment', '')}")
                    st.markdown(f"**Date:** {review.get('createTime', '')[:10]}")
                    
                    # Check if there's already a reply
                    reply = review.get('reviewReply', {})
                    if reply and reply.get('comment'):
                        st.markdown(f"**Your Reply:** {reply['comment']}")
                    else:
                        with st.form(f"reply_form_{review.get('name', '')}"):
                            reply_text = st.text_area(
                                "Reply to this review",
                                key=f"reply_{review.get('name', '')}",
                                placeholder="Thank the customer and address their feedback..."
                            )
                            if st.form_submit_button("📤 Send Reply", type="primary", 
                                                      use_container_width=True):
                                if reply_text:
                                    with st.spinner("Posting reply..."):
                                        result = reply_to_review(
                                            location, 
                                            f"{review.get('name')}/reply",
                                            reply_text
                                        )
                                    if result.get('success'):
                                        st.success("✅ Reply posted!")
                                        st.cache_data.clear()
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {result.get('error', 'Failed')}")
                                else:
                                    st.warning("⚠️ Enter a reply!")
        else:
            st.info("💡 No reviews yet. Share your GBP link with customers!")
    
    # ════════════════════════════════════════
    # TAB 3: Insights
    # ════════════════════════════════════════
    with tab3:
        st.markdown("### 📊 Performance Insights")
        
        insights = fetch_insights(location)
        
        if insights:
            metrics = insights.get("metrics", {})
            
            # Display metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 👁️ Visibility")
                views = metrics.get("profileView", {})
                st.metric("Profile Views", 
                         views.get("total", "N/A"),
                         delta=views.get("delta", "") if isinstance(views.get("delta"), (int, float)) else None)
                
                search = metrics.get("searchView", {})
                st.metric("Search Views", 
                         search.get("total", "N/A"),
                         delta=search.get("delta", "") if isinstance(search.get("delta"), (int, float)) else None)
                
                calls = metrics.get("call", {})
                st.metric("Phone Calls", 
                         calls.get("total", "N/A"))
            
            with col2:
                st.markdown("#### 🗺️ Engagement")
                directions = metrics.get("direction", {})
                st.metric("Direction Requests",
                         directions.get("total", "N/A"))
                
                website = metrics.get("website", {})
                st.metric("Website Clicks",
                         website.get("total", "N/A"))
                
                messages = metrics.get("message", {})
                st.metric("Messages",
                         messages.get("total", "N/A"))
            
            # Raw data
            if st.checkbox("Show raw insights data"):
                st.json(insights)
        else:
            st.info("💡 Insights data not available. It may take 24-48 hours after setup.")
    
    # ════════════════════════════════════════
    # TAB 4: Settings
    # ════════════════════════════════════════
    with tab4:
        st.markdown("### ⚙️ GBP Settings")
        
        st.markdown(f"""
        **Account:** `{account}`  
        **Location:** `{location}`  
        **Token Status:** {'✅ Configured' if has_token else '❌ Missing'}  
        **API Status:** {'✅ Google API Client' if GOOGLE_API else '⚠️ Using REST API (basic)'}
        """)
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Cache cleared! Data will refresh on next load.")
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        #### Connect to Client
        
        Link a GBP location to a client for automated reporting:
        """)
        
        clients = get_clients(user_id)
        if clients:
            client_names = [c['name'] for c in clients]
            selected_client = st.selectbox("Select Client", client_names, key="gbp_client_link")
            client = next(c for c in clients if c['name'] == selected_client)
            
            if st.button("🔗 Link GBP to Client", use_container_width=True):
                from db.operations import update_client
                update_client(client['id'], google_business_url=location)
                st.success(f"✅ Linked `{location}` to client **{client['name']}**!")
        else:
            st.info("💡 Create a client first to link GBP locations.")
