"""
BHARATSOLVE SEO AGENCY — GitHub Pages Auto-Blog Publisher
Publishes AI-generated heart health blogs to the Gill Heart Clinic static website.

Flow:
  1. Generate SEO blog content via Gemini LLM
  2. Create HTML file with clinic's styling
  3. Push to GitHub Pages repo via GitHub REST API
  4. Update blog index on the static site

Repo: gurjeetsinghgill8-web/gill-heart-clinic
"""
import os
import json
import base64
import time
import re
import requests
from datetime import datetime
from typing import Dict, Optional

from utils.llm_client import call_llm
from db.operations import save_content, log_agent_action

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════
DEFAULT_CONFIG = {
    "github_token": "YOUR_GITHUB_TOKEN",  # Set via env var GITHUB_TOKEN
    "github_repo": "gurjeetsinghgill8-web/gill-heart-clinic",
    "github_branch": "gh-pages",
    "blog_folder": "blogs",
    "website_url": "https://gurjeetsinghgill8-web.github.io/gill-heart-clinic/",
    "clinic_name": "Gill Heart Clinic",
    "doctor_name": "Dr. Gurjeet Singh Gill",
    "doctor_qualifications": "MBBS, Diploma Cardiology (UN Mehta), PGDCCP, AI in Healthcare (IIT Kanpur)",
    "clinic_address": "Mohiuddinpur, Meerut, Uttar Pradesh",
    "clinic_phone": "+91-9639011155",
    "target_locations": ["Meerut", "Delhi NCR", "Mohiuddinpur"],
}

BLOG_SYSTEM_PROMPT = """You are a medical content writer for a cardiologist.
CRITICAL RULES:
1. ALL medical claims MUST cite guidelines: AHA (American Heart Association), ACC, ESC, or WHO
2. NEVER use casual/fake terms — use proper medical terminology
3. Every blog MUST include a "References" section with real guideline citations
4. Include prominent disclaimer: "This is general information. Consult Dr. Gill before following any advice."
5. Professional tone — you represent Dr. Gurjeet Singh Gill, a qualified cardiologist
6. Indian context is OK, but medical facts must be evidence-based
7. Format: Professional Hinglish (Hindi terms OK, but medical terms in English)
8. MUST include at the end: "Reviewed by: [Pending Doctor Review]"

Format: HTML article with:
- Professional medical title (not clickbait)
- "Medical References" section at bottom with AHA/ACC/ESC guideline citations
- FAQ section answering real patient questions accurately
- Medical disclaimer
- CTA for appointment booking"""

BLOG_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta_title}</title>
    <meta name="description" content="{meta_description}">
    <meta name="keywords" content="{keywords}">
    <meta name="author" content="{doctor_name}">
    <meta property="og:title" content="{meta_title}">
    <meta property="og:description" content="{meta_description}">
    <meta property="og:type" content="article">
    <link rel="canonical" href="{website_url}blogs/{slug}.html">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; color: #333; line-height:1.8; font-size:16px; }}
        .blog-container {{ max-width: 800px; margin: 0 auto; padding: 20px; background: white; min-height:100vh; }}
        h1 {{ color: #d90429; font-size: 1.8rem; margin: 1rem 0 0.5rem; }}
        h2 {{ color: #1a1a2e; font-size: 1.3rem; margin: 2rem 0 0.5rem; border-bottom: 2px solid #d90429; padding-bottom: 0.3rem; }}
        h3 {{ color: #444; font-size: 1.1rem; margin: 1.2rem 0 0.3rem; }}
        p {{ margin: 0.8rem 0; }}
        ul, ol {{ margin: 0.5rem 0 0.5rem 1.5rem; }}
        li {{ margin: 0.3rem 0; }}
        .doctor-card {{ background: #fdf2f2; border-left: 4px solid #d90429; padding: 1rem; border-radius: 8px; margin: 2rem 0; }}
        .cta-box {{ background: #d90429; color: white; padding: 1.2rem; border-radius: 10px; text-align: center; margin: 2rem 0; }}
        .cta-box a {{ color: white; font-weight: bold; }}
        .disclaimer {{ background: #fff3cd; padding: 0.8rem; border-radius: 6px; font-size: 0.85rem; color: #856404; margin: 2rem 0; }}
        .back-link {{ color: #d90429; text-decoration: none; font-weight: 500; display:inline-block; margin-bottom:1rem; }}
        .refs {{ font-size:0.85rem; color:#666; margin-top:2rem; }}
        @media(max-width:600px) {{ .blog-container {{ padding:12px; }} h1 {{ font-size:1.4rem; }} }}
    </style>
    {schema_json}
</head>
<body>
    <div class="blog-container">
        <a href="{website_url}" class="back-link">← {clinic_name}</a>
        <h1>{title}</h1>
        <p style="color:#888;font-size:0.85rem;">Published: {date} | By {doctor_name} | {clinic_name}</p>
        {content}
        
        <div class="doctor-card">
            <strong>About the Author:</strong> {doctor_name} — {doctor_qualifications}. 
            Practicing at {clinic_name}, {clinic_address}. {years_experience}+ years of experience, {patients_treated}+ patients treated.
            <br>📞 <strong>Book Appointment:</strong> <a href="tel:{clinic_phone}">{clinic_phone}</a>
        </div>
        
        <div class="cta-box">
            <h3 style="color:white;margin:0 0 0.5rem;">Book Your Heart Checkup</h3>
            <p style="color:rgba(255,255,255,0.9);margin:0;">
                📞 <a href="tel:{clinic_phone}">{clinic_phone}</a><br>
                📍 {clinic_address}<br>
                🕐 Mon-Sun, 9 AM — 7 PM (By Appointment)
            </p>
        </div>
        
        <div class="disclaimer">
            <strong>Medical Disclaimer:</strong> This article is for informational purposes only and does not constitute medical advice. Always consult a qualified cardiologist for diagnosis and treatment. In case of emergency, call your local emergency services immediately.
        </div>
    </div>
</body>
</html>"""


# ═══════════════════════════════════════════════════════════════════════
# GITHUB API HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _get_github_token() -> str:
    """Get GitHub token from environment or Streamlit secrets."""
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        try:
            import streamlit as st
            token = st.secrets.get("GITHUB_TOKEN", "")
        except:
            pass
    return token


def _github_api(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Make a GitHub REST API call."""
    token = _get_github_token()
    if not token:
        return {"error": "GitHub token not configured. Set GITHUB_TOKEN environment variable."}
    
    url = f"https://api.github.com{endpoint}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "BHARATSOLVE-SEO-Agency"
    }
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=30)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=data, timeout=30)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, json=data, timeout=30)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        if resp.status_code in [200, 201]:
            return resp.json()
        elif resp.status_code == 204:
            return {"success": True}
        else:
            return {"error": f"GitHub API {resp.status_code}: {resp.text[:300]}"}
    except Exception as e:
        return {"error": str(e)}


def check_repo_connection() -> dict:
    """Test connection to GitHub repository."""
    repo = DEFAULT_CONFIG["github_repo"]
    result = _github_api(f"/repos/{repo}")
    if "error" in result:
        return {"connected": False, "error": result["error"]}
    return {
        "connected": True,
        "repo_name": result.get("full_name", repo),
        "default_branch": result.get("default_branch", "main"),
        "stars": result.get("stargazers_count", 0),
    }


def _push_file_to_repo(file_path: str, content: str, commit_message: str) -> dict:
    """
    Push a single file to GitHub repository.
    Creates or updates the file via GitHub Contents API.
    """
    repo = DEFAULT_CONFIG["github_repo"]
    branch = DEFAULT_CONFIG["github_branch"]
    
    # First, check if file exists (to get SHA for update)
    existing = _github_api(f"/repos/{repo}/contents/{file_path}?ref={branch}")
    
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    payload = {
        "message": commit_message,
        "content": encoded_content,
        "branch": branch,
    }
    
    if "sha" in existing:
        payload["sha"] = existing["sha"]  # Update existing file
    
    result = _github_api(f"/repos/{repo}/contents/{file_path}", method="PUT", data=payload)
    return result


# ═══════════════════════════════════════════════════════════════════════
# BLOG GENERATION + PUBLISHING
# ═══════════════════════════════════════════════════════════════════════

def generate_heart_blog(topic: str, target_location: str = "Meerut", 
                       language: str = "hinglish") -> dict:
    """
    Generate a complete heart health blog using AI.
    Simplified prompt for reliable JSON output.
    """
    prompt = f"""Write a heart health blog on: "{topic}"
Target Location: {target_location}
Language: {language} (Hinglish = natural Hindi+English mix used by Indian doctors)
Clinic: {DEFAULT_CONFIG['clinic_name']}
Doctor: {DEFAULT_CONFIG['doctor_name']}

Write a complete blog article (1000 words). Include:
- SEO title with location keyword
- Introduction for Indian patients
- 5-6 sections with subheadings
- Indian-specific diet and lifestyle advice
- Doctor mention naturally
- FAQ section with 3-4 questions
- Appointment booking CTA
- Medical disclaimer

RETURN ONLY VALID JSON. No markdown, no explanation:
{{"title":"...","meta_title":"...","meta_description":"...","keywords":"...","content":"<h2>Title</h2><p>Full article HTML here...</p><h2>FAQ</h2>...","faq":[{{"question":"...","answer":"..."}}]}}"""

    messages = [
        {"role": "system", "content": "You are a medical blog writer. Write in Hinglish (Hindi+English mix). Return ONLY valid JSON. The 'content' field must contain complete HTML article body."},
        {"role": "user", "content": prompt}
    ]
    
    start = time.time()
    response = call_llm(messages, provider="groq", model="llama-3.1-8b-instant", temperature=0.7)
    elapsed = int((time.time() - start) * 1000)
    
    # Parse JSON
    try:
        # Find JSON between { and }
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx+1]
            data = json.loads(json_str)
            content = data.get("content", "")
            
            if not content or len(content) < 300:
                # Try to extract HTML content from the raw response
                html_match = re.search(r'<h[123][^>]*>.*?</h[123]>', response, re.DOTALL | re.IGNORECASE)
                if html_match:
                    # Extract everything after the first heading
                    content_start = response.find(html_match.group())
                    content = response[content_start:] if content_start >= 0 else response
            
            if content and len(content) > 200:
                return {
                    "title": data.get("title", f"{topic} - Guide by {DEFAULT_CONFIG['doctor_name']}"),
                    "meta_title": data.get("meta_title", f"{topic} - {DEFAULT_CONFIG['clinic_name']}, {target_location}"),
                    "meta_description": data.get("meta_description", f"{topic} explained by {DEFAULT_CONFIG['doctor_name']}. Best cardiologist in {target_location}."),
                    "keywords": data.get("keywords", f"{topic}, cardiologist {target_location}"),
                    "content": content,
                    "faq": data.get("faq", []),
                    "word_count": len(content.split()),
                }
    except Exception as e:
        print(f"JSON parse error: {e}")
    
    # Last resort: use raw response as HTML if it has enough content
    if len(response) > 400:
        # Strip any non-HTML prefixes
        cleaned = re.sub(r'^.*?<h[123]', '<h', response, count=1, flags=re.DOTALL | re.IGNORECASE)
        if '<h' in cleaned and len(cleaned) > 300:
            return {
                "title": f"{topic} - {DEFAULT_CONFIG['doctor_name']}",
                "meta_title": f"{topic} - {DEFAULT_CONFIG['clinic_name']}, {target_location}",
                "meta_description": f"Expert guide on {topic.lower()} by {DEFAULT_CONFIG['doctor_name']}, {target_location}.",
                "keywords": f"{topic}, cardiologist {target_location}",
                "content": cleaned,
                "faq": [],
                "word_count": len(cleaned.split()),
            }
    
    # Absolute fallback - should never reach here
    log_agent_action("github_publisher", f"Blog generation failed for: {topic}", status="error")
    return {"title": "", "content": "", "error": "AI generation failed — please try again"}


def build_blog_html(blog_data: dict, slug: str = None) -> str:
    """
    Build a complete standalone HTML blog page from AI-generated content.
    Uses the BLOG_HTML_TEMPLATE with clinic branding.
    """
    title = blog_data.get("title", "Heart Health Blog")
    if not slug:
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:60]
    
    # Build FAQ section HTML if FAQ exists
    if blog_data.get("faq"):
        faq_html = '<div style="background:#f8f9fa;padding:1rem;border-radius:8px;margin:2rem 0;">\n<h2>Frequently Asked Questions</h2>\n'
        for f in blog_data["faq"]:
            faq_html += f'<details style="margin:0.5rem 0;"><summary style="font-weight:600;color:#d90429;cursor:pointer;">{f.get("question", "")}</summary><p>{f.get("answer", "")}</p></details>\n'
        faq_html += '</div>'
        blog_data["content"] = blog_data.get("content", "") + "\n" + faq_html
    
    # Build FAQ schema JSON-LD
    faq_items = blog_data.get("faq", [])
    faq_schema = ""
    if faq_items:
        faq_entities = [{"@type": "Question", "name": f.get("question", ""), "acceptedAnswer": {"@type": "Answer", "text": f.get("answer", "")}} for f in faq_items]
        schema = {"@context": "https://schema.org", "@type": "MedicalArticle", "headline": blog_data.get("meta_title", title), "description": blog_data.get("meta_description", ""), "author": {"@type": "Person", "name": DEFAULT_CONFIG["doctor_name"]}, "datePublished": datetime.now().strftime("%Y-%m-%d")}
        faq_schema = f'\n    <script type="application/ld+json">\n    {json.dumps(schema, indent=4, ensure_ascii=False)}\n    </script>'
    
    html = BLOG_HTML_TEMPLATE.format(
        meta_title=blog_data.get("meta_title", title),
        meta_description=blog_data.get("meta_description", ""),
        keywords=blog_data.get("keywords", ""),
        doctor_name=DEFAULT_CONFIG["doctor_name"],
        website_url=DEFAULT_CONFIG["website_url"],
        slug=slug,
        title=title,
        date=datetime.now().strftime("%d %B %Y"),
        clinic_name=DEFAULT_CONFIG["clinic_name"],
        doctor_qualifications=DEFAULT_CONFIG["doctor_qualifications"],
        clinic_address=DEFAULT_CONFIG["clinic_address"],
        clinic_phone=DEFAULT_CONFIG["clinic_phone"],
        years_experience="12",
        patients_treated="50,000",
        content=blog_data.get("content", ""),
        schema_json=faq_schema,
    )
    return html


def publish_blog_to_github(topic: str, target_location: str = "Meerut", 
                          language: str = "hinglish", auto_publish: bool = True) -> dict:
    """
    Full pipeline: Generate blog → Build HTML → Push to GitHub Pages.
    
    Args:
        topic: Blog topic
        target_location: Target city
        language: Language
        auto_publish: If True, push to GitHub. If False, just generate & return.
    
    Returns:
        dict with status, blog data, and GitHub URL if published
    """
    log_agent_action("github_publisher", f"Generating blog: {topic} [{target_location}]")
    
    # Step 1: Generate content
    blog_data = generate_heart_blog(topic, target_location, language)
    
    if not blog_data.get("content") or blog_data.get("error"):
        error_msg = blog_data.get("error", "Blog generation failed — no content returned")
        log_agent_action("github_publisher", error_msg, status="error", error_message=error_msg)
        return {"status": "error", "message": error_msg}
    
    # Step 2: Build HTML
    slug = re.sub(r'[^a-z0-9]+', '-', blog_data["title"].lower()).strip('-')[:60]
    blog_html = build_blog_html(blog_data, slug)
    
    # Step 3: Save to local DB
    try:
        save_content(
            project_id=1,
            title=blog_data["title"],
            content=blog_html,
            content_type="blog",
            target_keyword=topic,
            meta_title=blog_data.get("meta_title", ""),
            meta_description=blog_data.get("meta_description", ""),
            schema_json=json.dumps(blog_data.get("faq", [])),
            published_url=f"{DEFAULT_CONFIG['website_url']}blogs/{slug}.html" if auto_publish else ""
        )
    except Exception as e:
        log_agent_action("github_publisher", f"DB save warning: {e}", status="warning")
    
    # Step 4: Push to GitHub (if auto_publish)
    result = {
        "status": "generated",
        "title": blog_data["title"],
        "slug": slug,
        "meta_title": blog_data.get("meta_title", ""),
        "meta_description": blog_data.get("meta_description", ""),
        "word_count": blog_data.get("word_count", 0),
        "blog_html": blog_html,
        "published_url": None,
    }
    
    if auto_publish:
        file_path = f"blogs/{slug}.html"
        commit_msg = f"📝 Auto-blog: {blog_data['title'][:70]} [BHARATSOLVE AI]"
        
        push_result = _push_file_to_repo(file_path, blog_html, commit_msg)
        
        if "error" in push_result:
            result["status"] = "generated_not_published"
            result["push_error"] = push_result["error"]
            log_agent_action("github_publisher", f"Push failed: {push_result['error']}", 
                           status="error", error_message=push_result["error"])
        else:
            result["status"] = "published"
            result["published_url"] = f"{DEFAULT_CONFIG['website_url']}blogs/{slug}.html"
            log_agent_action("github_publisher", 
                           f"Published: {blog_data['title'][:50]} → {result['published_url']}",
                           response_time_ms=0)
    
    return result


def publish_batch_blogs(topics: list = None) -> list:
    """
    Publish multiple blogs at once.
    If topics is None, uses default heart health topics.
    """
    if topics is None:
        topics = [
            "Chest Pain Warning Signs",
            "High BP Control Tips",
            "ECG vs 2D Echo vs TMT Difference",
            "Diabetes and Heart Connection",
            "Cholesterol Management Tips",
        ]
    
    results = []
    for i, topic in enumerate(topics):
        location = DEFAULT_CONFIG["target_locations"][i % len(DEFAULT_CONFIG["target_locations"])]
        result = publish_blog_to_github(topic, location)
        results.append(result)
        
        if i < len(topics) - 1:
            time.sleep(2)  # Rate limiting
    
    return results


# ═══════════════════════════════════════════════════════════════════════
# AUTO-BLOG TASK (for scheduler)
# ═══════════════════════════════════════════════════════════════════════

def auto_blog_task():
    """
    Automated blog task — picks a random heart health topic and publishes daily.
    Designed to be called by the scheduler every 24 hours.
    """
    import random
    
    heart_topics = [
        "Chest Pain Warning Signs",
        "High BP Control Tips",
        "ECG vs 2D Echo vs TMT Difference",
        "Diabetes and Heart Connection",
        "Cholesterol Management Tips",
        "Heart Attack Prevention in Hindi",
        "Heart Healthy Indian Diet Plan",
        "Safe Exercises for Heart Patients",
        "Heart Failure Symptoms and Treatment",
        "Stress and Heart Health Connection",
        "Seasonal Heart Care Tips for Summer",
        "Women Heart Disease Awareness",
        "Smoking and Heart Damage",
        "Obesity and Heart Risk Factors",
        "Sleep Apnea and Heart Problems",
        "Heart Checkup — What Tests You Need",
        "BP Medicine Side Effects Management",
        "Post-Heart Attack Recovery Guide",
        "Heart Disease in Young Indians",
        "Yoga for Heart Health",
    ]
    
    topic = random.choice(heart_topics)
    location = random.choice(DEFAULT_CONFIG["target_locations"])
    
    result = publish_blog_to_github(topic, location, auto_publish=True)
    
    print(f"📝 Auto-Blog: {result.get('title', 'Unknown')} — Status: {result.get('status', 'unknown')}")
    
    return result
