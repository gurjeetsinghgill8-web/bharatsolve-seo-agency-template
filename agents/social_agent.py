"""
BHARATSOLVE SEO AGENCY — Social Media Agent
Manages social media posts across platforms with REAL API posting.
Uses social_connectors.py for actual platform integration.
"""
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Optional

from utils.llm_client import call_llm
from utils.social_connectors import (
    get_connector, get_available_platforms, post_to_platform, test_all_connections
)
from db.operations import (
    schedule_social_post, get_scheduled_posts, log_agent_action, get_project,
    update_social_post_status
)

logger = logging.getLogger(__name__)

SOCIAL_SYSTEM_PROMPT = """तुम एक Social Media Marketing Agent हो।
तुम्हारा काम:
1. Business और platform के according engaging social media posts बनाना
2. Platform-specific content strategy देना
3. Hinglish में catchy posts लिखना
4. Emojis और hashtags include करना
5. Platform-specific formatting (character limits, image ratios, etc.)
6. सुनिश्चित करना कि post actual platform par publish ho

Platforms: Google Business Profile, Facebook, Instagram, Telegram, Email"""


def create_social_post(project_id: int, platform: str, topic: str = "", 
                       content_type: str = "promotional",
                       auto_publish: bool = True) -> dict:
    """
    Generate AND publish a social media post.
    
    auto_publish=True → tries to post to the real platform.
    auto_publish=False → saves as draft only.
    """
    project = get_project(project_id)
    
    # Check if platform connector is configured
    connector = get_connector(platform)
    connector_available = connector and any(v for v in connector._load_credentials().values() if v and len(str(v)) > 5)
    
    platform_names = {
        "google_business": "Google Business Profile",
        "facebook": "Facebook Page",
        "instagram": "Instagram",
        "telegram": "Telegram Channel",
        "email": "Email Newsletter"
    }
    
    platform_prompts = {
        "google_business": "Google Business Profile post (local SEO focused, offers/updates, 1500 chars max)",
        "facebook": "Facebook post (engaging, shareable, with CTA, 63,206 chars max)",
        "instagram": "Instagram post with caption (visual description, 2200 chars, hashtags, emojis, 30 hashtags max)",
        "telegram": "Telegram post (informative, direct, HTML formatting supported, 4096 chars max)",
        "email": "Email newsletter (subject line, body, CTA button, professional HTML)"
    }
    
    platform_style = platform_prompts.get(platform, f"{platform} post")
    platform_name = platform_names.get(platform, platform)
    
    # Extra context for the AI
    extra_context = ""
    if connector_available:
        extra_context = f"\n✅ {platform_name} connector is CONFIGURED. Post will be published LIVE."
    else:
        extra_context = f"\n⚠️ {platform_name} connector NOT configured. Post will be saved as draft."
    
    prompt = f"""
Business: {project['name'] if project else 'General Business'}
Website: {project.get('website', '') if project else ''}
Location: {project.get('target_location', '') if project else ''}
Platform: {platform_style}
Topic: {topic or (project['name'] if project else 'general update')}
Type: {content_type}{extra_context}

Generate a complete post:
- Platform-appropriate tone and length
- Emojis where suitable (2-4 relevant emojis)
- 3-5 relevant hashtags (for platforms that support them)
- Call to action
- Best posting time suggestion (in IST)
- Target audience consideration

Return JSON:
{{
  "content": "Full post content...",
  "hashtags": ["#tag1", "#tag2"],
  "best_time": "10:00 AM IST",
  "cta": "Call to action text",
  "media_suggestion": "Description of suggested image/video",
  "target_audience": "Brief audience description",
  "subject": "Email subject line (only for email)"
}}
"""
    
    messages = [
        {"role": "system", "content": SOCIAL_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    start = time.time()
    response = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
    elapsed = int((time.time() - start) * 1000)
    
    # Parse response
    result = parse_social_response(response, platform, topic)
    result["platform_name"] = platform_name
    
    # Try to publish to real platform
    publish_result = None
    if auto_publish and connector_available:
        logger.info(f"🚀 Publishing to {platform}...")
        post_content = result.get("content", "")
        post_content += "\n\n" + " ".join(result.get("hashtags", []))
        
        publish_result = post_to_platform(
            platform=platform,
            content=post_content,
            media_url=None,  # No media for now (text-only)
            subject=result.get("subject", ""),
            to_email=result.get("to_email", "")
        )
        
        result["publish_status"] = publish_result.get("status", "unknown")
        result["publish_message"] = publish_result.get("message", "")
        result["post_url"] = publish_result.get("url", "")
        
        if publish_result.get("status") == "posted":
            logger.info(f"✅ Published to {platform}: {publish_result.get('url', '')}")
        else:
            logger.warning(f"⚠️ Failed to publish to {platform}: {publish_result.get('message', '')}")
    else:
        if auto_publish:
            result["publish_status"] = "draft"
            result["publish_message"] = f"⚠️ {platform_name} not configured. Save credentials in Settings → Social Connectors."
        else:
            result["publish_status"] = "draft"
            result["publish_message"] = "Saved as draft (auto-publish disabled)"
    
    # Schedule the post (for tracking in UI)
    scheduled_time = (datetime.now() + timedelta(days=0, hours=1)).replace(
        minute=0, second=0, microsecond=0
    )
    
    post_id = schedule_social_post(
        project_id=project_id,
        platform=platform,
        content=result.get("content", response),
        scheduled_for=scheduled_time.isoformat()
    )
    
    # Update post status based on publish result
    if publish_result and publish_result.get("status") == "posted":
        from db.schema import get_connection
        conn = get_connection()
        conn.execute("UPDATE social_posts SET status = 'posted', posted_at = ? WHERE id = ?",
                     (datetime.now().isoformat(), post_id))
        conn.commit()
        conn.close()
    
    result["id"] = post_id
    result["scheduled_for"] = scheduled_time.isoformat()
    
    log_agent_action("social", f"Created {platform} post for project {project_id} | Status: {result.get('publish_status', 'draft')}",
                     response_time_ms=elapsed,
                     status="ok" if result.get("publish_status") == "posted" else "warning")
    
    return result


def parse_social_response(response: str, platform: str, topic: str) -> dict:
    """Parse LLM response into structured post dict."""
    try:
        json_match = __import__('re').search(r'\{.*\}', response, __import__('re').DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return {
                "content": data.get("content", response),
                "hashtags": data.get("hashtags", []),
                "best_time": data.get("best_time", "10:00 AM IST"),
                "cta": data.get("cta", "Learn More"),
                "media_suggestion": data.get("media_suggestion", ""),
                "target_audience": data.get("target_audience", ""),
                "subject": data.get("subject", f"Update from {topic}"),
                "to_email": data.get("to_email", ""),
                "publish_status": "draft",
                "publish_message": "",
                "post_url": ""
            }
    except:
        pass
    
    return {
        "content": response,
        "hashtags": [],
        "best_time": "10:00 AM IST",
        "cta": "Learn More",
        "media_suggestion": "",
        "target_audience": "",
        "subject": f"Update from {topic}",
        "to_email": "",
        "publish_status": "draft",
        "publish_message": "",
        "post_url": ""
    }


def generate_content_calendar(project_id: int, days: int = 7) -> list:
    """Generate a multi-day social media content calendar."""
    project = get_project(project_id)
    available = get_available_platforms()
    
    if not available:
        available = ["google_business", "facebook", "instagram", "telegram"]
    
    platforms_str = [p.replace("_", " ").title() for p in available]
    
    prompt = f"""
Business: {project['name'] if project else 'Business'}
Location: {project.get('target_location', '') if project else ''}
Days: {days}
Configured Platforms: {', '.join(platforms_str)}

Create a {days}-day social media content calendar with one post per day.
Mix across platforms. Include specific topics and content strategies.

Return JSON array:
[
  {{
    "day": 1,
    "platform": "instagram",
    "topic": "...",
    "content_type": "educational|promotional|engaging|offer|testimonial",
    "post_preview": "brief preview...",
    "goal": "engagement|awareness|conversion"
  }}
]
"""
    
    messages = [
        {"role": "system", "content": SOCIAL_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    response = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
    
    try:
        json_match = __import__('re').search(r'\[.*?\]', response, __import__('re').DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    
    return []


def test_platform_connections() -> dict:
    """Test all configured platform connections and return status."""
    results = test_all_connections()
    log_agent_action("social", "Tested all platform connections",
                     response_time_ms=0, status="ok")
    return results


def get_connection_status(platform: str) -> dict:
    """Check if a specific platform is connected."""
    connector = get_connector(platform)
    if not connector:
        return {"platform": platform, "status": "unknown", "message": "No connector available"}
    return connector.test_connection()
