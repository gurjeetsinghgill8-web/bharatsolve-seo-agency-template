"""
BHARATSOLVE SEO AGENCY — Social Media Platform Connectors
Actual API integrations for posting to social platforms.
Supports: Instagram, Facebook, Telegram, Email (SMTP), Google Business Profile

Architecture:
  Each platform has a connect() and post() method.
  Connectors store credentials in config.json (encrypted in production).
  Status is logged to DB for tracking.
"""
import os
import json
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Config Loading ──

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

def _load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# ── Base Connector ──

class BaseConnector:
    """Base class for all social platform connectors."""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.config = _load_config()
        self._connected = False
        self._creds = self._load_credentials()
    
    def _load_credentials(self) -> dict:
        """Load platform-specific credentials from config/streamlit secrets."""
        secrets = {}
        
        # Try Streamlit secrets first (cloud mode)
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                prefix = self.platform_name.upper()
                for key in st.secrets:
                    if key.startswith(prefix) or key.startswith(f"SOCIAL_{prefix}"):
                        secrets[key] = st.secrets[key]
        except:
            pass
        
        # Try config.json
        social_config = self.config.get("social_platforms_config", {}).get(self.platform_name, {})
        secrets.update(social_config)
        
        # Try environment variables
        for env_key in [f"{self.platform_name.upper()}_TOKEN", f"{self.platform_name.upper()}_API_KEY",
                        f"SOCIAL_{self.platform_name.upper()}_TOKEN"]:
            val = os.getenv(env_key)
            if val:
                secrets[env_key] = val
        
        return secrets
    
    def connect(self) -> bool:
        """Connect to the platform. Returns True if successful."""
        raise NotImplementedError
    
    def post(self, content: str, media_url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Post content to the platform. Returns result dict."""
        raise NotImplementedError
    
    def test_connection(self) -> Dict[str, Any]:
        """Test if credentials work. Returns {'status': 'ok'|'error', 'message': '...'}"""
        try:
            success = self.connect()
            if success:
                return {"status": "ok", "message": f"✅ {self.platform_name} connected successfully"}
            return {"status": "error", "message": f"❌ {self.platform_name} connection failed"}
        except Exception as e:
            return {"status": "error", "message": f"❌ {self.platform_name}: {str(e)[:100]}"}


# ── Facebook Page Connector ──

class FacebookConnector(BaseConnector):
    """
    Facebook Page posting via Graph API v19.0+
    Requires: Facebook Page Access Token (long-lived)
    """
    
    def __init__(self):
        super().__init__("facebook")
        self.page_id = None
        self.access_token = None
        self.api_version = "v19.0"
    
    def _load_credentials(self) -> dict:
        creds = super()._load_credentials()
        # Also check specific keys
        self.access_token = (creds.get("FACEBOOK_ACCESS_TOKEN") or 
                             creds.get("facebook_access_token") or 
                             os.getenv("FACEBOOK_ACCESS_TOKEN", ""))
        self.page_id = (creds.get("FACEBOOK_PAGE_ID") or 
                        creds.get("facebook_page_id") or 
                        os.getenv("FACEBOOK_PAGE_ID", ""))
        return creds
    
    def connect(self) -> bool:
        """Verify Facebook Page access token works."""
        if not self.access_token or not self.page_id:
            logger.warning("Facebook: Missing access_token or page_id")
            return False
        
        import requests
        url = f"https://graph.facebook.com/{self.api_version}/{self.page_id}"
        params = {"access_token": self.access_token, "fields": "id,name"}
        
        try:
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            if "id" in data:
                self._connected = True
                logger.info(f"Facebook: Connected to page {data.get('name')}")
                return True
            logger.warning(f"Facebook connection failed: {data.get('error', {}).get('message', 'Unknown')}")
            return False
        except Exception as e:
            logger.error(f"Facebook connection error: {e}")
            return False
    
    def post(self, content: str, media_url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Post to Facebook Page feed."""
        if not self._connected and not self.connect():
            return {"status": "error", "message": "Facebook: Not connected"}
        
        import requests
        url = f"https://graph.facebook.com/{self.api_version}/{self.page_id}/feed"
        
        post_data = {
            "message": content,
            "access_token": self.access_token
        }
        
        # If media URL provided, attach it
        if media_url:
            # First upload photo, then post
            photo_url = f"https://graph.facebook.com/{self.api_version}/{self.page_id}/photos"
            photo_data = {
                "url": media_url,
                "caption": content[:2000],
                "access_token": self.access_token
            }
            try:
                photo_resp = requests.post(photo_url, data=photo_data, timeout=30)
                if photo_resp.status_code == 200:
                    return {
                        "status": "posted",
                        "platform": "facebook",
                        "post_id": photo_resp.json().get("id", ""),
                        "url": f"https://facebook.com/{photo_resp.json().get('id', '')}",
                        "posted_at": datetime.now().isoformat()
                    }
            except Exception as e:
                logger.error(f"Facebook photo post error: {e}")
                # Fall through to text-only post
        
        try:
            resp = requests.post(url, data=post_data, timeout=30)
            result = resp.json()
            
            if "id" in result:
                return {
                    "status": "posted",
                    "platform": "facebook",
                    "post_id": result["id"],
                    "url": f"https://facebook.com/{self.page_id}/posts/{result['id']}",
                    "posted_at": datetime.now().isoformat()
                }
            else:
                error_msg = result.get("error", {}).get("message", "Unknown error")
                return {"status": "error", "message": f"Facebook: {error_msg}"}
        except Exception as e:
            return {"status": "error", "message": f"Facebook API error: {str(e)[:100]}"}


# ── Instagram Connector (via Graph API) ──

class InstagramConnector(BaseConnector):
    """
    Instagram posting via Facebook Graph API.
    Requires: Facebook Page connected to Instagram, plus Instagram Business Account ID.
    """
    
    def __init__(self):
        super().__init__("instagram")
        self.instagram_business_id = None
        self.access_token = None
        self.api_version = "v19.0"
    
    def _load_credentials(self) -> dict:
        creds = super()._load_credentials()
        self.access_token = (creds.get("FACEBOOK_ACCESS_TOKEN") or 
                             creds.get("instagram_access_token") or
                             os.getenv("FACEBOOK_ACCESS_TOKEN", ""))
        self.instagram_business_id = (creds.get("INSTAGRAM_BUSINESS_ID") or 
                                      creds.get("instagram_business_id") or
                                      os.getenv("INSTAGRAM_BUSINESS_ID", ""))
        return creds
    
    def connect(self) -> bool:
        if not self.access_token or not self.instagram_business_id:
            logger.warning("Instagram: Missing access_token or business_id")
            return False
        
        import requests
        url = f"https://graph.facebook.com/{self.api_version}/{self.instagram_business_id}"
        params = {"access_token": self.access_token, "fields": "id,name,username"}
        
        try:
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            if "id" in data:
                self._connected = True
                logger.info(f"Instagram: Connected to @{data.get('username')}")
                return True
            logger.warning(f"Instagram connection failed: {data.get('error', {}).get('message', 'Unknown')}")
            return False
        except Exception as e:
            logger.error(f"Instagram connection error: {e}")
            return False
    
    def post(self, content: str, media_url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Post to Instagram Feed.
        Instagram requires an image/video (cannot post text-only to feed).
        For text-only: post to Instagram Stories or use caption-only as comment.
        """
        if not self._connected and not self.connect():
            return {"status": "error", "message": "Instagram: Not connected"}
        
        import requests
        
        if not media_url:
            # Instagram requires media for feed posts
            # Fallback: return as draft/scheduled with note
            return {
                "status": "draft",
                "platform": "instagram",
                "message": "Instagram needs an image. Post saved as draft.",
                "content": content,
                "posted_at": datetime.now().isoformat()
            }
        
        # Step 1: Create media container
        create_url = f"https://graph.facebook.com/{self.api_version}/{self.instagram_business_id}/media"
        create_data = {
            "image_url": media_url,
            "caption": content[:2200],  # Instagram caption limit
            "access_token": self.access_token
        }
        
        try:
            # Create media container
            create_resp = requests.post(create_url, data=create_data, timeout=30)
            create_result = create_resp.json()
            
            if "id" not in create_result:
                error = create_result.get("error", {}).get("message", "Unknown")
                return {"status": "error", "message": f"Instagram: {error}"}
            
            container_id = create_result["id"]
            
            # Step 2: Publish the container
            time.sleep(3)  # Wait for media processing
            publish_url = f"https://graph.facebook.com/{self.api_version}/{self.instagram_business_id}/media_publish"
            publish_data = {
                "creation_id": container_id,
                "access_token": self.access_token
            }
            
            publish_resp = requests.post(publish_url, data=publish_data, timeout=30)
            publish_result = publish_resp.json()
            
            if "id" in publish_result:
                return {
                    "status": "posted",
                    "platform": "instagram",
                    "post_id": publish_result["id"],
                    "url": f"https://instagram.com/p/{publish_result['id']}/",
                    "posted_at": datetime.now().isoformat()
                }
            else:
                error = publish_result.get("error", {}).get("message", "Unknown")
                return {"status": "error", "message": f"Instagram publish: {error}"}
        
        except Exception as e:
            return {"status": "error", "message": f"Instagram API error: {str(e)[:100]}"}


# ── Telegram Bot Connector ──

class TelegramConnector(BaseConnector):
    """
    Telegram channel/group posting via Bot API.
    Requires: Bot Token from @BotFather + Channel/Chat ID.
    """
    
    def __init__(self):
        super().__init__("telegram")
        self.bot_token = None
        self.chat_id = None
        self.api_base = "https://api.telegram.org/bot"
    
    def _load_credentials(self) -> dict:
        creds = super()._load_credentials()
        self.bot_token = (creds.get("TELEGRAM_BOT_TOKEN") or 
                          creds.get("telegram_bot_token") or 
                          os.getenv("TELEGRAM_BOT_TOKEN", ""))
        self.chat_id = (creds.get("TELEGRAM_CHAT_ID") or 
                        creds.get("telegram_chat_id") or 
                        os.getenv("TELEGRAM_CHAT_ID", ""))
        return creds
    
    def connect(self) -> bool:
        """Verify bot token by calling getMe."""
        if not self.bot_token:
            logger.warning("Telegram: Missing bot_token")
            return False
        
        import requests
        url = f"{self.api_base}{self.bot_token}/getMe"
        
        try:
            resp = requests.get(url, timeout=15)
            data = resp.json()
            if data.get("ok"):
                bot_name = data.get("result", {}).get("first_name", "Unknown")
                self._connected = True
                logger.info(f"Telegram: Connected to bot @{data.get('result', {}).get('username')}")
                return True
            logger.warning(f"Telegram connection failed: {data.get('description', 'Unknown')}")
            return False
        except Exception as e:
            logger.error(f"Telegram connection error: {e}")
            return False
    
    def post(self, content: str, media_url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Send message to Telegram channel/group."""
        if not self._connected and not self.connect():
            return {"status": "error", "message": "Telegram: Not connected"}
        
        if not self.chat_id:
            return {"status": "error", "message": "Telegram: No chat_id configured"}
        
        import requests
        
        # Parse buttons if provided
        reply_markup = kwargs.get("reply_markup")
        parse_mode = kwargs.get("parse_mode", "HTML")
        
        if media_url:
            # Send photo with caption
            url = f"{self.api_base}{self.bot_token}/sendPhoto"
            data = {
                "chat_id": self.chat_id,
                "photo": media_url,
                "caption": content[:1024],
                "parse_mode": parse_mode
            }
        else:
            # Send text message
            url = f"{self.api_base}{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": content,
                "parse_mode": parse_mode,
                "disable_web_page_preview": False
            }
        
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        
        try:
            resp = requests.post(url, data=data, timeout=30)
            result = resp.json()
            
            if result.get("ok"):
                msg_id = result.get("result", {}).get("message_id")
                return {
                    "status": "posted",
                    "platform": "telegram",
                    "post_id": str(msg_id),
                    "url": f"https://t.me/c/{self.chat_id}/{msg_id}" if self.chat_id else "",
                    "posted_at": datetime.now().isoformat()
                }
            else:
                return {"status": "error", "message": f"Telegram: {result.get('description', 'Unknown')}"}
        except Exception as e:
            return {"status": "error", "message": f"Telegram API error: {str(e)[:100]}"}


# ── Email Connector (SMTP) ──

class EmailConnector(BaseConnector):
    """
    Email sending via SMTP (Gmail, SendGrid, or custom SMTP).
    Supports: Gmail App Passwords, SendGrid API, generic SMTP.
    """
    
    def __init__(self):
        super().__init__("email")
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_user = None
        self.smtp_pass = None
        self.from_email = None
        self.from_name = "BHARATSOLVE SEO AGENCY"
        self.use_sendgrid = False
        self.sendgrid_api_key = None
    
    def _load_credentials(self) -> dict:
        creds = super()._load_credentials()
        
        # SMTP settings
        self.smtp_host = (creds.get("SMTP_HOST") or os.getenv("SMTP_HOST", "smtp.gmail.com"))
        self.smtp_port = int(creds.get("SMTP_PORT") or os.getenv("SMTP_PORT", "587"))
        self.smtp_user = (creds.get("SMTP_USER") or os.getenv("SMTP_USER", ""))
        self.smtp_pass = (creds.get("SMTP_PASS") or os.getenv("SMTP_PASS", ""))
        self.from_email = (creds.get("FROM_EMAIL") or os.getenv("FROM_EMAIL", self.smtp_user))
        
        # SendGrid alternative
        self.sendgrid_api_key = (creds.get("SENDGRID_API_KEY") or os.getenv("SENDGRID_API_KEY", ""))
        self.use_sendgrid = bool(self.sendgrid_api_key)
        
        return creds
    
    def connect(self) -> bool:
        """Test SMTP connection."""
        if self.use_sendgrid:
            # SendGrid: test via API
            import requests
            url = "https://api.sendgrid.com/v3/scopes"
            headers = {"Authorization": f"Bearer {self.sendgrid_api_key}"}
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    self._connected = True
                    logger.info("Email: Connected via SendGrid")
                    return True
            except Exception as e:
                logger.error(f"SendGrid connection error: {e}")
                return False
        
        # SMTP test
        if not self.smtp_host or not self.smtp_user or not self.smtp_pass:
            logger.warning("Email: Missing SMTP credentials")
            return False
        
        import smtplib
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.quit()
            self._connected = True
            logger.info(f"Email: Connected to {self.smtp_host}")
            return True
        except Exception as e:
            logger.error(f"Email SMTP connection error: {e}")
            return False
    
    def post(self, content: str, media_url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Send email. 
        kwargs: to_email (required), subject (optional), cc (optional)
        """
        to_email = kwargs.get("to_email", "")
        subject = kwargs.get("subject", "Update from BHARATSOLVE SEO AGENCY")
        cc = kwargs.get("cc", "")
        
        if not to_email:
            return {"status": "error", "message": "Email: No recipient (to_email required)"}
        
        if self.use_sendgrid:
            return self._send_via_sendgrid(to_email, subject, content, cc)
        else:
            return self._send_via_smtp(to_email, subject, content, cc)
    
    def _build_html_body(self, content: str) -> str:
        """Wrap content in a professional HTML email template."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: Arial, sans-serif; background: #f4f9ff; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #0077b6, #00b4d8); padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">🚀 BHARATSOLVE</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0;">SEO Agency Update</p>
                </div>
                <div style="padding: 24px; color: #333; line-height: 1.6;">
                    {content.replace(chr(10), '<br>')}
                </div>
                <div style="background: #e8f4fd; padding: 15px; text-align: center; font-size: 12px; color: #666;">
                    <p>BHARATSOLVE SEO AGENCY — Made with ❤️ in India</p>
                    <p>This is an automated email from your SEO agency system.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _send_via_smtp(self, to_email: str, subject: str, content: str, cc: str = "") -> Dict[str, Any]:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        if not self._connected and not self.connect():
            return {"status": "error", "message": "Email: SMTP not connected"}
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            if cc:
                msg["Cc"] = cc
            
            html_body = self._build_html_body(content)
            msg.attach(MIMEText(html_body, "html"))
            
            all_recipients = [to_email]
            if cc:
                all_recipients += [c.strip() for c in cc.split(",") if c.strip()]
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.sendmail(self.from_email, all_recipients, msg.as_string())
            server.quit()
            
            return {
                "status": "posted",
                "platform": "email",
                "to": to_email,
                "subject": subject,
                "posted_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "message": f"Email SMTP error: {str(e)[:100]}"}
    
    def _send_via_sendgrid(self, to_email: str, subject: str, content: str, cc: str = "") -> Dict[str, Any]:
        import requests
        url = "https://api.sendgrid.com/v3/mail/send"
        
        personalizations = [{"to": [{"email": to_email}]}]
        if cc:
            personalizations[0]["cc"] = [{"email": c.strip()} for c in cc.split(",") if c.strip()]
        
        payload = {
            "personalizations": personalizations,
            "from": {"email": self.from_email, "name": self.from_name},
            "subject": subject,
            "content": [{"type": "text/html", "value": self._build_html_body(content)}]
        }
        
        headers = {
            "Authorization": f"Bearer {self.sendgrid_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            if resp.status_code in (200, 201, 202):
                return {
                    "status": "posted",
                    "platform": "email",
                    "to": to_email,
                    "subject": subject,
                    "posted_at": datetime.now().isoformat()
                }
            else:
                return {"status": "error", "message": f"SendGrid: {resp.status_code} {resp.text[:100]}"}
        except Exception as e:
            return {"status": "error", "message": f"SendGrid API error: {str(e)[:100]}"}


# ── Google Business Profile Connector ──

class GoogleBusinessConnector(BaseConnector):
    """
    Google Business Profile API for posting updates.
    Requires: OAuth 2.0 credentials with GBP scope.
    """
    
    def __init__(self):
        super().__init__("google_business")
        self.account_name = None
        self.location_name = None
        self.access_token = None
    
    def _load_credentials(self) -> dict:
        creds = super()._load_credentials()
        self.access_token = (creds.get("GOOGLE_BUSINESS_TOKEN") or 
                             os.getenv("GOOGLE_BUSINESS_TOKEN", ""))
        self.account_name = (creds.get("GOOGLE_BUSINESS_ACCOUNT") or 
                             os.getenv("GOOGLE_BUSINESS_ACCOUNT", ""))
        self.location_name = (creds.get("GOOGLE_BUSINESS_LOCATION") or 
                              os.getenv("GOOGLE_BUSINESS_LOCATION", ""))
        return creds
    
    def connect(self) -> bool:
        if not self.access_token:
            logger.warning("Google Business: Missing access_token")
            return False
        self._connected = True  # Token-based, assume valid
        return True
    
    def post(self, content: str, media_url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Post update to Google Business Profile.
        Note: GBP API has limited posting (only certain content types allowed).
        """
        if not self._connected and not self.connect():
            return {"status": "error", "message": "Google Business: Not connected"}
        
        # GBP local post API
        import requests
        url = f"https://mybusiness.googleapis.com/v4/{self.location_name}/localPosts"
        
        post_body = {
            "summary": content[:1500],
            "languageCode": "hi",
            "topicType": kwargs.get("topic_type", "STANDARD")
        }
        
        if media_url:
            post_body["media"] = [{"mediaFormat": "PHOTO", "sourceUrl": media_url}]
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            resp = requests.post(url, json=post_body, headers=headers, timeout=30)
            if resp.status_code in (200, 201):
                data = resp.json()
                return {
                    "status": "posted",
                    "platform": "google_business",
                    "post_id": data.get("name", ""),
                    "url": f"https://business.google.com/posts/{data.get('name', '')}",
                    "posted_at": datetime.now().isoformat()
                }
            else:
                return {"status": "error", "message": f"Google Business: {resp.status_code} {resp.text[:100]}"}
        except Exception as e:
            return {"status": "error", "message": f"Google Business API error: {str(e)[:100]}"}


# ── Connector Factory ──

_CONNECTORS = {
    "facebook": FacebookConnector,
    "instagram": InstagramConnector,
    "telegram": TelegramConnector,
    "email": EmailConnector,
    "google_business": GoogleBusinessConnector,
}

def get_connector(platform: str) -> Optional[BaseConnector]:
    """Get connector instance for a platform."""
    cls = _CONNECTORS.get(platform)
    if cls:
        return cls()
    return None

def get_available_platforms() -> list:
    """Return list of platforms that have credentials configured."""
    available = []
    for name, cls in _CONNECTORS.items():
        connector = cls()
        creds = connector._load_credentials()
        # Check if at least minimum credentials exist
        has_creds = False
        for val in creds.values():
            if val and len(str(val)) > 5:
                has_creds = True
                break
        if has_creds:
            available.append(name)
    return available

def post_to_platform(platform: str, content: str, media_url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Convenience function to post to any platform."""
    connector = get_connector(platform)
    if not connector:
        return {"status": "error", "message": f"Unknown platform: {platform}"}
    return connector.post(content, media_url, **kwargs)

def test_all_connections() -> Dict[str, Dict]:
    """Test all configured platform connections."""
    results = {}
    for name in _CONNECTORS:
        connector = get_connector(name)
        if connector:
            results[name] = connector.test_connection()
    return results
