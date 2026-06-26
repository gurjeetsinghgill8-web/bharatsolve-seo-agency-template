"""
BHARATSOLVE SEO AGENCY — Content Creation Agent
Generates SEO-optimized content with proper schema markup.
"""
import json
import time
import re
from utils.llm_client import call_llm
from db.operations import save_content, get_keywords, log_agent_action, get_project

CONTENT_SYSTEM_PROMPT = """तुम एक SEO Content Writer Agent हो।
तुम्हारा काम:
1. SEO-optimized Hinglish/Hindi/English content लिखना
2. Proper heading structure (H1, H2, H3) के साथ
3. Meta title और meta description generate करना
4. FAQ schema JSON-LD include करना
5. Keyword density 1-2% maintain करना

हमेशा unique, informative, और reader-friendly content दो।"""


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
    response = call_llm(messages, provider="gemini", model="gemini-2.0-flash")
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
    
    log_agent_action("content", f"Generated {content_type}: {result.get('title', '')[:50]}",
                     response_time_ms=elapsed)
    
    return result


def parse_content_response(response: str, fallback_keyword: str) -> dict:
    """Parse LLM response into structured content dict."""
    try:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return {
                "title": data.get("title", fallback_keyword),
                "meta_title": data.get("meta_title", fallback_keyword[:60]),
                "meta_description": data.get("meta_description", fallback_keyword[:160]),
                "content": data.get("content", response),
                "schema_json": data.get("schema_json", {}),
                "word_count": data.get("word_count", len(response.split()))
            }
    except:
        pass
    
    # Fallback: use response as content
    return {
        "title": fallback_keyword,
        "meta_title": fallback_keyword[:60],
        "meta_description": f"Learn about {fallback_keyword}. Best tips and information.",
        "content": response,
        "schema_json": {},
        "word_count": len(response.split())
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
