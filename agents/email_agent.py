"""
BHARATSOLVE SEO AGENCY — Email Marketing Agent
Automated email campaigns, newsletters, and client reports via SMTP/SendGrid.
"""
import json
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from utils.llm_client import call_llm
from utils.social_connectors import EmailConnector
from db.operations import (
    get_clients, get_projects, get_keywords, get_dashboard_stats,
    get_agent_logs, log_agent_action, get_all_projects
)

logger = logging.getLogger(__name__)

EMAIL_SYSTEM_PROMPT = """तुम एक Email Marketing Agent हो।
तुम्हारा काम:
1. Professional email newsletters बनाना
2. Client report emails generate करना
3. SEO progress updates email में भेजना
4. Marketing campaign emails लिखना
5. Hinglish और English दोनों में emails लिखना

हमेशा professional tone में emails लिखो।"""


def send_email(to_email: str, subject: str, content: str, cc: str = "") -> Dict[str, Any]:
    """
    Send an email using the EmailConnector.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        content: Email body (will be wrapped in HTML template)
        cc: Comma-separated CC recipients
    
    Returns:
        Dict with status, message, etc.
    """
    connector = EmailConnector()
    result = connector.post(content, to_email=to_email, subject=subject, cc=cc)
    
    log_agent_action("email", f"Sent email to {to_email}: {subject[:50]}",
                     status="ok" if result.get("status") == "posted" else "error")
    
    return result


def send_client_report_email(client_id: int, user_id: int) -> Dict[str, Any]:
    """
    Generate and send a comprehensive SEO report to a client.
    
    Args:
        client_id: Client database ID
        user_id: User (agency owner) database ID
    
    Returns:
        Dict with status and details
    """
    from db.operations import get_client
    client = get_client(client_id)
    if not client:
        return {"status": "error", "message": "Client not found"}
    
    client_email = client.get("email", "")
    if not client_email:
        return {"status": "error", "message": "Client has no email address"}
    
    # Gather client data
    projects = get_projects(client_id)
    total_keywords = 0
    total_content = 0
    keywords_data = []
    
    for proj in projects:
        kws = get_keywords(proj['id'])
        total_keywords += len(kws)
        keywords_data.extend(kws)
    
    # Calculate metrics
    top_10 = len([k for k in keywords_data if 1 <= k.get('current_position', 0) <= 10])
    not_ranked = len([k for k in keywords_data if k.get('current_position', 0) == 0])
    avg_pos = 0
    ranked = [k for k in keywords_data if k.get('current_position', 0) > 0]
    if ranked:
        avg_pos = round(sum(k['current_position'] for k in ranked) / len(ranked), 1)
    
    # Generate AI email content
    prompt = f"""
Client Name: {client['name']}
Business Type: {client.get('business_type', 'N/A')}
Website: {client.get('website', 'N/A')}
Location: {client.get('location', 'N/A')}

SEO Performance:
- Total Keywords: {total_keywords}
- Top 10 Rankings: {top_10}
- Not Ranked Yet: {not_ranked}
- Average Position: {avg_pos}

Generate a professional email to this client with:
1. Friendly greeting
2. SEO performance summary in simple terms
3. Highlight achievements (e.g., "3 keywords now in top 10!")
4. Next steps / recommendations
5. Professional closing with BHARATSOLVE branding

Keep it positive, informative, and in Hinglish (Hindi + English mix).
The email should be 150-300 words.
"""
    
    messages = [
        {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    start = time.time()
    email_body = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
    elapsed = int((time.time() - start) * 1000)
    
    subject = f"📊 SEO Progress Report — {client['name']} | BHARATSOLVE"
    
    result = send_email(client_email, subject, email_body)
    result["client_name"] = client['name']
    result["metrics"] = {
        "total_keywords": total_keywords,
        "top_10": top_10,
        "avg_position": avg_pos
    }
    
    log_agent_action("email", f"Client report sent to {client['name']} ({client_email})",
                     response_time_ms=elapsed)
    
    return result


def send_newsletter(user_id: int, topic: str = "") -> Dict[str, Any]:
    """
    Generate and send an SEO tips newsletter to all clients of a user.
    
    Args:
        user_id: Agency owner ID
        topic: Optional specific topic for the newsletter
    
    Returns:
        Dict with results for each client
    """
    clients = get_clients(user_id)
    if not clients:
        return {"status": "error", "message": "No clients found"}
    
    # Generate newsletter content
    prompt = f"""
Generate a professional SEO newsletter email with these sections:
1. Subject line (catchy, SEO-related)
2. Main article: {"Topic: " + topic if topic else "General SEO tips for small businesses"}
3. Quick SEO tip of the week
4. Upcoming trends to watch
5. CTA to contact for help

Keep it in Hinglish. Professional but friendly tone. 200-400 words.
"""
    
    messages = [
        {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    start = time.time()
    newsletter_body = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
    elapsed = int((time.time() - start) * 1000)
    
    subject = f"📬 SEO Newsletter — {datetime.now().strftime('%B %Y')} | BHARATSOLVE"
    
    results = []
    for client in clients:
        client_email = client.get("email", "")
        if client_email:
            result = send_email(client_email, subject, newsletter_body)
            result["client_name"] = client['name']
            results.append(result)
    
    log_agent_action("email", f"Newsletter sent to {len(results)} clients",
                     response_time_ms=elapsed)
    
    return {
        "status": "ok",
        "total_sent": len(results),
        "results": results,
        "subject": subject
    }


def send_weekly_digest(user_id: int) -> Dict[str, Any]:
    """
    Send weekly SEO digest to the agency owner with all clients' performance.
    """
    stats = get_dashboard_stats(user_id)
    clients = get_clients(user_id)
    logs = get_agent_logs(limit=20)
    
    # Build digest content
    prompt = f"""
Weekly BHARATSOLVE SEO Agency Digest:

Active Clients: {stats.get('active_clients', 0)}
Total Keywords: {stats.get('total_keywords', 0)}
Average Rank: {stats.get('avg_rank', 'N/A')}
Total Content: {stats.get('total_content', 0)}

Recent Agent Activity (last 20 actions):
{chr(10).join([f"- {l['agent_name']}: {l['task'][:60]}" for l in logs[:10]])}

Generate a weekly digest email for the AGENCY OWNER with:
1. Weekly performance summary
2. Key achievements this week
3. Areas needing attention
4. Recommendations for next week
5. Agent performance overview

Keep it in Hinglish, professional, actionable.
"""
    
    messages = [
        {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    email_body = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
    subject = f"📊 Weekly SEO Digest — {datetime.now().strftime('%d %b %Y')}"
    
    # Send to the owner's email (from first client or env)
    owner_email = os.getenv("OWNER_EMAIL", "")
    
    if owner_email:
        result = send_email(owner_email, subject, email_body)
        log_agent_action("email", "Weekly digest sent to owner")
        return result
    
    return {"status": "error", "message": "Owner email not configured (set OWNER_EMAIL env)"}


def send_bulk_campaign(user_id: int, campaign_type: str = "promotional", 
                       custom_message: str = "") -> Dict[str, Any]:
    """
    Send a bulk email campaign to all clients.
    
    Args:
        user_id: Agency owner ID
        campaign_type: promotional, educational, offer, update
        custom_message: Optional custom message content
    """
    clients = get_clients(user_id)
    
    prompt = f"""
Create a {campaign_type} email campaign for SEO clients.
{"Custom message: " + custom_message if custom_message else "Generate a compelling marketing email."}

Keep it professional, in Hinglish. Include a clear CTA.
200-300 words.
"""
    
    messages = [
        {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    email_body = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
    subject = f"🚀 Special Update from BHARATSOLVE SEO AGENCY"
    
    results = []
    for client in clients:
        if client.get("email"):
            result = send_email(client["email"], subject, email_body)
            result["client_name"] = client['name']
            results.append(result)
    
    return {
        "status": "ok",
        "total_sent": len(results),
        "results": results,
        "subject": subject,
        "campaign_type": campaign_type
    }
