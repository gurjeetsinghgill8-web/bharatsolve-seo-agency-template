"""
BHARATSOLVE SEO AGENCY — Content Creation Agent
Generates SEO-optimized content with proper schema markup.
"""
import json
import time
import re
from utils.llm_client import call_llm
from db.operations import save_content, get_keywords, log_agent_action, get_project

CONTENT_SYSTEM_PROMPT = """You are writing medical content for a cardiologist's website.
Dr. Gurjeet Singh Gill (MBBS, Dip Cardiology, PGDCCP) — Gill Heart Clinic, Meerut.

ABSOLUTE RULES:
1. PROFESSIONAL TONE ONLY. NEVER use: "bhai log", "yaar", "aam baat", "prasiddh", "mashoor", "famous", "best", "#1", "guaranteed", "100%", "miracle", "magic"
2. All medical claims MUST have AHA/ACC/ESC citation
3. Write as a DOCTOR speaking to patients — respectful, accurate, compassionate
4. Hindi is OK for patient education but medical terms in English
5. NEVER use casual/slang Hinglish. Professional medical Hindi only.
6. Structure: Title > Key Facts > Symptoms > Causes > When to See Doctor > Treatment Options > Prevention > FAQ > References > Disclaimer
7. Include: "This article has been reviewed by Dr. Gurjeet Singh Gill"
8. Include: AHA Guideline reference numbers
9. NEVER claim "best doctor" or "top cardiologist" — let qualifications speak
10. If you're unsure about a medical fact, write "Consult your cardiologist" instead

FORMAT: Start with <h2> headings. Clean HTML. No markdown code blocks."""


def generate_content(project_id: int, keyword: str, content_type: str = "blog") -> dict:
    """
    Generate SEO-optimized content for a keyword.
    Returns dict with title, content, meta_title, meta_description, schema.
    """
    project = get_project(project_id)
    
    prompt = f"""
Project: {project['name'] if project else 'General'}
Target Location: {project.get('target_location', '') if project else ''}
Target Language: {project.get('target_language', 'hi') if project else ''}
Content Type: {content_type}
Primary Keyword: {keyword}

Generate complete SEO content including:
1. Catchy title (with keyword)
2. Meta title (55-60 chars)
3. Meta description (150-160 chars)
4. Full article with H1, H2, H3 structure
5. FAQ schema JSON-LD
6. Word count: 800-1500 words

Return JSON:
{{
  "title": "...",
  "meta_title": "...",
  "meta_description": "...",
  "content": "Full article with HTML headings...",
  "schema_json": {{"@context": "...", ...}},
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
    
    # CONTENT FILTER: Reject unprofessional language
    banned_words = [
        "bhai log", "bhaiyo", "yaar", "aam baat", "prasiddh", "mashoor", 
        "famous doctor", "#1", "best doctor", "top cardiologist", "miracle",
        "guaranteed cure", "100% guaranteed", "magic", "gandagi",
    ]
    content_lower = result.get("content", "").lower()
    for word in banned_words:
        if word in content_lower:
            # Regenerate with stricter prompt
            log_agent_action("content", f"Banned word '{word}' detected — regenerating")
            messages.append({"role": "user", "content": "REGENERATE with PROFESSIONAL MEDICAL TONE. No casual language. No self-promotion. Write as a qualified cardiologist."})
            response = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
            result = parse_content_response(response, keyword)
            break
    
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
    
    log_agent_action("content", f"Generated {content_type}: {result.get('title', '')[:50]}",
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
            data = json.loads(json_match.group())
            title = data.get("title", fallback_keyword)
            meta_title = data.get("meta_title", fallback_keyword[:60])
            meta_desc = data.get("meta_description", f"Learn about {fallback_keyword}.")
            content_text = data.get("content", response)
            schema = data.get("schema_json", {})
            
            # Clean content: remove JSON code blocks and markdown artifacts
            content_text = re.sub(r'```(?:json|html)?\s*', '', content_text)
            content_text = re.sub(r'```\s*$', '', content_text)
            content_text = re.sub(r'\*\*JSON Response\*\*.*?(?=<h|\Z)', '', content_text, flags=re.DOTALL)
            content_text = re.sub(r'\*\*स्कीमा.*?\*\*.*?(?=<h|\Z)', '', content_text, flags=re.DOTALL)
    except:
        pass
    
    # If content is still the full raw response, try to extract just the HTML part
    if len(content_text) > 1000 and ('{' in content_text or 'json' in content_text.lower()[:200]):
        # Try to extract H2/H3 content
        html_match = re.search(r'<h[123][^>]*>.*?</h[123]>', content_text, re.DOTALL | re.IGNORECASE)
        if html_match:
            start = content_text.find(html_match.group())
            content_text = content_text[start:] if start >= 0 else content_text
    
    # Ensure content starts with HTML
    if not content_text.strip().startswith('<'):
        content_text = f"<h2>{fallback_keyword}</h2>\n<p>{content_text[:2000]}</p>"
    
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
