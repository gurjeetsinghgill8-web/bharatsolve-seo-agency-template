"""
BHARATSOLVE SEO AGENCY — Content Creation Agent
Generates SEO-optimized content with proper schema markup.
"""
import json
import time
import re
from utils.llm_client import call_llm
from db.operations import save_content, get_keywords, log_agent_action, get_project

CONTENT_SYSTEM_PROMPT = """You are writing for Dr. Gurjeet Singh Gill — Cardiac Physician, Non-Invasive Cardiology.
Gill Heart Clinic, Mohiuddinpur, Meerut.

DR. GILL'S 5 CORE PATIENT ATTRACTION PILLARS (Highlight naturally in every article):
1. AFFORDABLE MEDICINES: Patient-first advice recommending quality generic medicines from PM Jan Aushadhi Kendras (Pradhan Mantri Bhartiya Janaushadhi Kendras) to keep medicine costs ultra-low.
2. LOW OPD FEES: Highly affordable consultation fees compared to expensive corporate hospitals.
3. PERSONALIZED LIFESTYLE & DIET COUNSELING: Detailed discussions on Indian heart-healthy diet, safe exercise, and lifestyle planning.
4. MINIMAL MEDICINES PRESCRIBED: Prescribes only essential, minimal necessary medications (no over-prescription).
5. CLINICAL JUDGEMENT FIRST: Expert clinical assessment prioritized, avoiding unnecessary expensive hospital tests.

CRITICAL LEGAL & MEDICAL ETHICS RULES (NMC Regulations):
1. STRICT LEGAL COMPLIANCE: NEVER use superlative / boastful claims like "Best Doctor", "Best Cardiologist", "No. 1", "सर्वश्रेष्ठ", "नंबर 1". NMC Regulations strictly prohibit self-promotional superlatives.
2. Use ethical, professional medical terms: "Experienced Cardiac Physician", "Comprehensive Heart Care", "अनुभवी कार्डिएक फिजिशियन", "हृदय स्वास्थ्य विशेषज्ञ".
3. Dr. Gill is a CARDIAC PHYSICIAN — NEVER call him "cardiologist" or "renowned cardiologist".
4. NEVER mention test prices (₹), costs, or fees for any procedure.
5. NEVER claim ECG/2D Echo/TMT is done AT the clinic. Write: "consult a cardiac center for these tests".
6. Services: Consultation, Clinical Assessment, Preventive Cardiology, Heart Health Counseling, Lifestyle Modification.
7. Professional tone. Cite AHA/ACC/ESC guidelines.
8. Structure: Title > Key Facts > Symptoms > Causes > When to See Doctor > Low-Cost Prevention & Diet Tips > FAQ > References.
9. Include: "This article has been reviewed by Dr. Gurjeet Singh Gill, Cardiac Physician".
10. RESPECT USER LANGUAGE SELECTION STRICTLY (Hindi, English, or Hinglish)."""


def generate_content(project_id: int, keyword: str, content_type: str = "blog", language: str = "hi") -> dict:
    """
    Generate SEO-optimized content for a keyword.
    Returns dict with title, content, meta_title, meta_description, schema.
    """
    project = get_project(project_id)
    
    # Map language string (handles both Devanagari "हिंदी" and English "Hindi")
    lang_str = str(language).lower().strip()
    if "english" in lang_str or lang_str == "en":
        target_lang_instruction = "PURE ENGLISH (Professional medical English text)."
    elif "हिंदी" in lang_str or "hindi" in lang_str or lang_str == "hi":
        target_lang_instruction = "PURE HINDI IN DEVANAGARI SCRIPT (शुद्ध देवनागरी हिंदी लिपि में लिखें - जैसे: 'सीने में दर्द के लक्षण', 'हृदय स्वास्थ्य' - NOT Roman script). DO NOT USE CASUAL WORDS LIKE 'Bhai' OR 'Yaar'."
    else:
        target_lang_instruction = "HINGLISH (Easy-to-understand Hindi using Roman English script)."
    
    prompt = f"""
Project: {project['name'] if project else 'General'}
Target Location: {project.get('target_location', '') if project else ''}
TARGET LANGUAGE: {target_lang_instruction}
Content Type: {content_type}
Primary Keyword: {keyword}

CRITICAL MANDATE (DUAL-LANGUAGE REQUIREMENT): ALWAYS INCLUDE BOTH DEVANAGARI HINDI AND ENGLISH SECTIONS IN THE ARTICLE CONTENT!
Structure the article HTML as:
1. <h2>🇮🇳 मुख्य जानकारी (Devanagari Hindi Section)</h2>
   Complete article in pure Devanagari Hindi script (देवनागरी लिपि में विस्तृत जानकारी).
2. <h2>🇬🇧 Complete Medical Guide (English Section)</h2>
   Complete article in professional medical English.

Dr. Gurjeet Singh Gill is a CARDIAC PHYSICIAN (NEVER cardiologist).

Generate complete SEO content including:
1. Catchy bilingual title (Hindi + English)
2. Meta title (55-60 chars)
3. Meta description (150-160 chars)
4. Full dual-language article body HTML (both Hindi and English sections)
5. FAQ schema JSON-LD
6. Word count: 800-1500 words

Return JSON format:
{{
  "title": "...",
  "meta_title": "...",
  "meta_description": "...",
  "content": "<h2>🇮🇳 मुख्य जानकारी</h2><p>Hindi paragraph...</p><h2>🇬🇧 Complete Medical Guide</h2><p>English paragraph...</p>",
  "schema_json": {{"@context": "https://schema.org", "@type": "FAQPage"}},
  "word_count": number
}}
"""
    
    messages = [
        {"role": "system", "content": CONTENT_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    start = time.time()
    # Try Groq first (free, unlimited), fall back to Gemini
    response = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
    elapsed = int((time.time() - start) * 1000)
    
    # Parse JSON from response
    result = parse_content_response(response, keyword)
    
    # Save to database
    cid = save_content(
        project_id=project_id,
        title=result.get("title", keyword),
        content=result.get("content", ""),
        content_type=content_type,
        target_keyword=keyword,
        meta_title=result.get("meta_title", ""),
        meta_description=result.get("meta_description", ""),
        schema_json=json.dumps(result.get("schema_json", {}))
    )
    result["id"] = cid
    
    log_agent_action("content", f"Generated {content_type} [{language}]: {result.get('title', '')[:50]}",
                     response_time_ms=elapsed)
    
    return result


def parse_content_response(response: str, fallback_keyword: str) -> dict:
    """Parse LLM response into structured content dict. Extract clean HTML content."""
    
    content_text = response
    title = fallback_keyword
    meta_title = fallback_keyword[:60]
    meta_desc = f"Learn about {fallback_keyword}. Best tips and information."
    schema = {}
    
    try:
        # Find JSON block
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                title = data.get("title", fallback_keyword)
                meta_title = data.get("meta_title", fallback_keyword[:60])
                meta_desc = data.get("meta_description", f"Learn about {fallback_keyword}.")
                content_text = data.get("content", response)
                schema = data.get("schema_json", {})
            except:
                pass
    except:
        pass
    
    # Sanitize content_text to strip all JSON wrappers or code fences
    content_text = re.sub(r'```(?:json|html)?\s*', '', content_text)
    content_text = re.sub(r'```\s*$', '', content_text)
    content_text = re.sub(r'^\s*\{\s*"title".*?"content":\s*"', '', content_text, flags=re.DOTALL)
    content_text = content_text.replace('\\n', '\n').replace('\\"', '"').replace('\\/', '/')
    content_text = re.sub(r'\s*"\s*,\s*"schema_json".*$', '', content_text, flags=re.DOTALL)
    
    # If content is empty or short, fallback
    if len(content_text.strip()) < 50:
        content_text = f"<h2>{fallback_keyword}</h2>\n<p>{response[:2000]}</p>"
    
    # Ensure content starts with clean HTML heading if missing
    if not re.search(r'^\s*<h[123]', content_text, re.IGNORECASE):
        content_text = f"<h2>{title}</h2>\n" + content_text
    
    return {
        "title": title,
        "meta_title": meta_title,
        "meta_description": meta_desc,
        "content": content_text,
        "schema_json": schema,
        "word_count": len(content_text.split())
    }


def generate_batch_content(project_id: int, keywords: list = None) -> list:
    """Generate content for multiple keywords."""
    if not keywords:
        kws = get_keywords(project_id)
        keywords = [k['keyword'] for k in kws[:5]]
    
    results = []
    for kw in keywords:
        result = generate_content(project_id, kw)
        results.append(result)
    
    return results
