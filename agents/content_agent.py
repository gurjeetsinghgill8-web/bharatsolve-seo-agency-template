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
Gill Heart Clinic, Mohiuddinpur, Meerut (Near Metro Pillar No. 1375).

CRITICAL MANDATE — ELABORATIVE & IN-DEPTH CONTENT LENGTH:
- Write comprehensive, in-depth, highly elaborative medical articles (1200 to 1800 words minimum).
- NEVER write short, brief, or superficial summaries. Provide exhaustive clinical, diagnostic, and patient guidance.

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
7. Tone: Deeply informative, empathetic, authoritative medical guidance citing ACC/AHA/ESC guidelines.
8. REQUIRED STRUCTURE:
   - 📌 Executive Summary & Key Highlights Box
   - 🩺 Clinical Symptoms, Causes & Early Warning Signs
   - 📊 Diagnostic Evaluation (Digital ECG, 2D Echo Ultrasound, TMT)
   - 💊 Evidence-Based Treatment & PM Jan Aushadhi Generic Medicine Guidance
   - 🥗 Indian Heart-Healthy Diet & Lifestyle Protocols
   - 🚨 Emergency Protocol & OPD Appointment Instructions
   - ❓ Frequently Asked Patient Questions (FAQs)
9. Include: "This article has been reviewed by Dr. Gurjeet Singh Gill, Cardiac Physician".
10. RESPECT USER LANGUAGE SELECTION STRICTLY (Hindi, English, or Hinglish).

═══ GEO (GENERATIVE ENGINE OPTIMIZATION) ENHANCEMENTS ═══

11. QUESTION-FIRST Q&A FORMAT (CRITICAL for ChatGPT/Gemini/Perplexity Ranking):
   - EVERY section MUST start with a real patient question followed by Dr. Gill's answer.
   - Format: <h3>❓ मरीज़ पूछते हैं / Patients Ask: "[real question]"</h3>
             <p>🩺 Dr. Gill's Answer: [comprehensive, authoritative answer 150-250 words]</p>
   - Example: "मरीज़ अक्सर पूछते हैं: सीने में हल्का दर्द हार्ट अटैक हो सकता है क्या? → Dr. Gill बताते हैं: हर सीने का दर्द हार्ट अटैक नहीं होता..."
   - LLMs (ChatGPT, Gemini, Claude) PREFERENTIALLY cite Q&A-formatted content because it directly matches user query patterns.
   - Make the questions sound like REAL patients talking — use conversational Hindi/English, not textbook language.

12. NAMED EXPERT & LANDMARK RESEARCH CITATIONS (Builds AI Trust & Authority):
   - Every article MUST cite at least 2-3 of:
     (a) NAMED CARDIOLOGY EXPERTS: Dr. Eugene Braunwald (father of modern cardiology), Dr. Valentin Fuster (Mount Sinai), Dr. Deepak L. Bhatt (Harvard), Dr. Salim Yusuf (PHRI), Dr. Ashok Seth (Fortis Escorts Delhi).
     (b) LANDMARK CLINICAL TRIALS: Framingham Heart Study (1948-present), SPRINT Trial (2015, NEJM), ISCHEMIA Trial (2020, NEJM), PARADIGM-HF (2014), IMPROVE-IT (2015), COURAGE Trial (2007).
     (c) STANDARD MEDICAL TEXTBOOKS: Harrison's Principles of Internal Medicine (21st Ed.), Braunwald's Heart Disease (12th Ed.), Hurst's The Heart, ESC Clinical Practice Guidelines.
   - Example: "As demonstrated in the landmark SPRINT Trial (2015, NEJM), intensive BP control (<120 mmHg) reduced cardiovascular events by 25%. Dr. Eugene Braunwald, in Braunwald's Heart Disease (12th Ed.), emphasizes..."

13. DR. GILL'S PERSONAL CLINICAL EXPERIENCE SECTION (MOST IMPORTANT for GEO — AI Prioritizes Genuine Human Experience):
   - Every article MUST include a dedicated section: <h2>🩺 Dr. Gill's Clinical Experience & Personal Patient Guidance</h2>
   - Share practical, real-world clinical observations from Dr. Gill's 12+ years of practice and 50,000+ patients treated.
   - Include anonymized patient scenarios: "Dr. Gill recalls a 45-year-old school teacher from Meerut who came with mild chest discomfort after climbing stairs. Her ECG was normal but..."
   - Add personal clinical tips and observations that only come from real experience, not textbooks.
   - This section is what ChatGPT and Google Gemini value MOST — authentic, first-hand human expertise that cannot be replicated by AI.
   - Include: "Based on Dr. Gill's clinical experience at Gill Heart Clinic, Mohiuddinpur, Meerut..."
"""

def generate_content(project_id: int, keyword: str, content_type: str = "blog", language: str = "hi") -> dict:
    """
    Generate SEO-optimized content for a keyword.
    Returns dict with title, content, meta_title, meta_description, schema.
    """
    project = get_project(project_id)
    
    # Map language string (handles both Devanagari "हिंदी" and English "Hindi")
    # IMPORTANT: Check "hinglish" FIRST before "english" — "english" is a substring of "hinglish"!
    lang_str = str(language).lower().strip()
    if "hinglish" in lang_str:
        target_lang_instruction = "HINGLISH (Easy-to-understand Hindi using Roman English script)."
    elif "हिंदी" in lang_str or "hindi" in lang_str or lang_str == "hi":
        target_lang_instruction = "PURE HINDI IN DEVANAGARI SCRIPT (शुद्ध देवनागरी हिंदी लिपि में लिखें - जैसे: 'सीने में दर्द के लक्षण', 'हृदय स्वास्थ्य' - NOT Roman script). DO NOT USE CASUAL WORDS LIKE 'Bhai' OR 'Yaar'."
    elif "english" in lang_str or lang_str == "en":
        target_lang_instruction = "PURE ENGLISH (Professional medical English text)."
    else:
        target_lang_instruction = "HINGLISH (Easy-to-understand Hindi using Roman English script)."
    
    prompt = f"""
Project: {project['name'] if project else 'General'}
Target Location: {project.get('target_location', '') if project else ''}
TARGET LANGUAGE: {target_lang_instruction}
Content Type: {content_type}
Primary Keyword: {keyword}

	═══ CRITICAL MANDATES ═══
	
	1. PRIMARY LANGUAGE: WRITE THE ENTIRE ARTICLE IN THE TARGET LANGUAGE SPECIFIED ABOVE.
	   - If TARGET LANGUAGE is PURE ENGLISH: Write the complete article in professional medical English ONLY. Do NOT include Hindi sections.
	   - If TARGET LANGUAGE is PURE HINDI: Write the complete article in Devanagari Hindi script ONLY. Do NOT include Roman/English sections.
	   - If TARGET LANGUAGE is HINGLISH: Write the complete article in Hinglish (Romanized Hindi using English letters).

2. QUESTION-FIRST Q&A FORMAT (GEO — ChatGPT/Gemini/Perplexity Optimization):
   Structure EVERY section as: Patient Question → Dr. Gill's Answer.
   Format: <h3>❓ मरीज़ पूछते हैं / Patients Ask: "[real conversational question]"</h3>
           <p>🩺 <strong>Dr. Gill's Answer:</strong> [comprehensive, authoritative 150-250 word answer]</p>
   Make questions sound like REAL patients — use natural conversational language, not textbook style.

3. CREDIBILITY REQUIREMENT — NAMED EXPERTS & LANDMARK TRIALS:
   Cite at least 2-3 named experts (Dr. Eugene Braunwald, Dr. Valentin Fuster, Dr. Deepak L. Bhatt),
   landmark trials (Framingham Heart Study, SPRINT Trial 2015, ISCHEMIA Trial 2020, PARADIGM-HF),
   or standard textbooks (Harrison's Principles, Braunwald's Heart Disease, ESC Guidelines).

4. PERSONAL CLINICAL EXPERIENCE SECTION:
   MUST include a dedicated section: <h2>🩺 Dr. Gill's Clinical Experience & Personal Patient Guidance</h2>
   Share anonymized patient scenarios from Dr. Gill's 12+ years at Gill Heart Clinic, Mohiuddinpur, Meerut.
   Example: "Dr. Gill recalls a 45-year-old Meerut teacher who..."
   Add personal tips that only come from real clinical experience — this is what AI search engines value most!

5. CONTENT FORMAT VARIETY (choose the format that best fits this topic):
   (a) Q&A Deep-Dive — Series of real patient questions with Dr. Gill's detailed answers (DEFAULT, recommended for AI ranking)
   (b) Patient Story First — Start with an engaging anonymized patient story, then explain the medical science
   (c) Myth Buster — List 5-7 common myths about this topic that Dr. Gill frequently corrects, debunk each
   (d) Doctor-Patient Conversation — Write as a realistic clinic dialogue between Dr. Gill and a patient

Dr. Gurjeet Singh Gill is a CARDIAC PHYSICIAN (NEVER cardiologist).

	Generate complete GEO-optimized content in the TARGET LANGUAGE including:
	1. Catchy title in the target language — make it question-based when possible, e.g., "Chest Pain: Heart Attack or Gas?"
	2. Meta title (55-60 chars) — include primary keyword + location
	3. Meta description (150-160 chars) — conversational, question-based, compelling
	4. Full Q&A-first article body HTML in the target language
	5. FAQ schema JSON-LD with at least 5 real patient questions
	6. Word count: 1200-1800 words minimum (comprehensive, in-depth)
	
	Return JSON format:
	{{
	  "title": "...",
	  "meta_title": "...",
	  "meta_description": "...",
	  "content": "<h2>...</h2>...<h2>🩺 Dr. Gill's Clinical Experience</h2>...",
	  "schema_json": {{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [...]}},
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
