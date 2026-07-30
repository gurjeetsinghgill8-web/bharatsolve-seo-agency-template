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

BLOG_SYSTEM_PROMPT = """You are a Cardiology SEO Content Writer.
Your job:
1. Write high-quality, patient-friendly blogs on heart health topics
2. Maintain medical accuracy (evidence-based information)
3. Write for Indian context — Indian diet, lifestyle, and local references
4. SEO optimize with proper headings, meta tags, and FAQ schema
5. Naturally include doctor's expertise and clinic info
6. Always include medical disclaimer for readers to consult a doctor

Format: Complete HTML-ready blog post with:
- Title (H1) with location keyword
- Meta description (150-160 chars)
- Proper H2/H3 structure
- FAQ section with questions Indian patients commonly ask
- Medical disclaimer
- Call-to-action for appointment booking"""

BLOG_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="hi">
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
    <meta property="og:url" content="{website_url}blogs/{slug}.html">
    <link rel="canonical" href="{website_url}blogs/{slug}.html">
    <!-- Clinic Styles -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Playfair+Display:wght@700&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../style.css">
    <style>
        body {{ font-family: 'Poppins', 'Noto Sans Devanagari', sans-serif; background: #f8f9fa; }}
        .blog-container {{ max-width: 850px; margin: 2rem auto; padding: 2rem; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        .blog-container h1 {{ color: #d90429; font-family: 'Playfair Display', serif; font-size: 2.2rem; margin-bottom: 0.5rem; }}
        .blog-container h2 {{ color: #1a1a2e; font-size: 1.5rem; margin-top: 2rem; border-bottom: 2px solid #d90429; padding-bottom: 0.4rem; }}
        .blog-container h3 {{ color: #333; font-size: 1.2rem; margin-top: 1.5rem; }}
        .blog-container p {{ color: #444; line-height: 1.8; font-size: 1.05rem; margin: 1rem 0; }}
        .blog-meta {{ color: #888; font-size: 0.9rem; margin-bottom: 1.5rem; }}
        .doctor-card {{ background: linear-gradient(135deg, #fdf2f2, #fff5f5); border-left: 4px solid #d90429; padding: 1rem 1.5rem; border-radius: 10px; margin: 2rem 0; }}
        .doctor-card strong {{ color: #d90429; }}
        .faq-section {{ background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 2rem 0; }}
        .faq-section details {{ margin: 0.8rem 0; }}
        .faq-section summary {{ font-weight: 600; color: #d90429; cursor: pointer; }}
        .cta-box {{ background: linear-gradient(135deg, #d90429, #ef233c); color: white; padding: 1.5rem; border-radius: 12px; text-align: center; margin: 2rem 0; }}
        .cta-box a {{ color: white; font-weight: bold; text-decoration: underline; }}
        .disclaimer {{ background: #fff3cd; padding: 1rem; border-radius: 8px; font-size: 0.9rem; color: #856404; margin: 2rem 0; }}
        .back-link {{ display: inline-block; margin-bottom: 1.5rem; color: #d90429; text-decoration: none; font-weight: 500; }}
        .back-link:hover {{ text-decoration: underline; }}
{extra_css}
    </style>
    {schema_json}
</head>
<body>
    <div class="blog-container">
        <a href="{website_url}" class="back-link">← Back to {clinic_name}</a>
        <h1>{title}</h1>
        <div class="blog-meta">
            📅 Published: {date} &nbsp;|&nbsp; ✍️ By {doctor_name} &nbsp;|&nbsp; 🏥 {clinic_name}
        </div>
        {content}
        
        <div class="doctor-card">
            <strong>👨‍⚕️ About the Author:</strong> <strong>{doctor_name}</strong> — {doctor_qualifications}. 
            Practicing at <strong>{clinic_name}</strong>, {clinic_address}. With {years_experience}+ years of experience 
            and {patients_treated}+ patients treated, Dr. Gill is one of the most trusted cardiologists in Meerut & Delhi NCR.
            <br>📞 <strong>Book Appointment:</strong> <a href="tel:{clinic_phone}">{clinic_phone}</a>
        </div>
        
        <div class="cta-box">
            <h3 style="color: white; margin: 0 0 0.5rem 0;">❤️ Book Your Heart Checkup Today</h3>
            <p style="color: rgba(255,255,255,0.9); margin: 0;">
                📞 Call/WhatsApp: <a href="tel:{clinic_phone}">{clinic_phone}</a><br>
                📍 Visit: {clinic_address}<br>
                🕐 Timings: Mon-Sun, 9 AM — 7 PM (By Appointment Only)
            </p>
        </div>
        
        <div class="disclaimer">
            ⚠️ <strong>Medical Disclaimer:</strong> This article is for informational purposes only and does not 
            constitute medical advice. Always consult a qualified cardiologist for diagnosis and treatment. 
            If you experience chest pain, difficulty breathing, or other heart-related symptoms, seek immediate medical attention.
        </div>
    </div>
    
    <!-- Back to top -->
    <button onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})" 
            style="position: fixed; bottom: 20px; right: 20px; background: #d90429; color: white; 
                   border: none; border-radius: 50%; width: 45px; height: 45px; cursor: pointer; 
                   font-size: 1.2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.2); z-index: 1000;">
        ↑
    </button>
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
    
    # Build FAQ schema JSON-LD
    faq_items = blog_data.get("faq", [])
    faq_schema = ""
    if faq_items:
        faq_entities = []
        for f in faq_items:
            faq_entities.append({
                "@type": "Question",
                "name": f.get("question", ""),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f.get("answer", "")
                }
            })
        
        schema = {
            "@context": "https://schema.org",
            "@type": "MedicalArticle",
            "headline": blog_data.get("meta_title", title),
            "description": blog_data.get("meta_description", ""),
            "author": {
                "@type": "Person",
                "name": DEFAULT_CONFIG["doctor_name"]
            },
            "publisher": {
                "@type": "MedicalOrganization",
                "name": DEFAULT_CONFIG["clinic_name"],
                "address": DEFAULT_CONFIG["clinic_address"]
            },
            "datePublished": datetime.now().strftime("%Y-%m-%d"),
            "mainEntityOfPage": {
                "@type": "FAQPage",
                "mainEntity": faq_entities
            }
        }
        faq_schema = f'\n    <script type="application/ld+json">\n    {json.dumps(schema, indent=4, ensure_ascii=False)}\n    </script>'
    
    # Build extra CSS for FAQ section if needed
    extra_css = ""
    if faq_items:
        faq_html = '<div class="faq-section">\n            <h2>❓ अक्सर पूछे जाने वाले सवाल (FAQs)</h2>\n'
        for f in faq_items:
            faq_html += f'            <details>\n                <summary>{f.get("question", "")}</summary>\n                <p>{f.get("answer", "")}</p>\n            </details>\n'
        faq_html += '        </div>'
        
        # Append FAQ HTML to content
        blog_data["content"] = blog_data.get("content", "") + "\n        " + faq_html
    
    # Fill the template
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
        extra_css=extra_css,
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
