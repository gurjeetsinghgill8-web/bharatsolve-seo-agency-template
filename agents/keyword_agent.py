"""
BHARATSOLVE SEO AGENCY — Keyword Research Agent
Discovers and analyzes keywords for projects.
"""
import json
import time
from utils.llm_client import call_llm
from db.operations import add_keyword, get_keywords, log_agent_action, get_project
import re

KEYWORD_SYSTEM_PROMPT = """तुम एक SEO Keyword Research Agent हो।
तुम्हारा काम:
1. Business type और location के आधार पर relevant keywords suggest करना
2. Search volume और difficulty estimate करना (1-100 scale)
3. Hinglish में explain करना
4. Keywords को priority के साथ group करना

Return JSON format for each keyword:
{"keyword": "...", "search_volume": 0-10000, "difficulty": 0-100, "intent": "informational|commercial|transactional|navigational"}"""


def research_keywords(project_id: int, niche: str = "", location: str = "") -> list:
    """
    Research and return keywords for a project.
    Returns list of keyword dicts.
    """
    project = get_project(project_id)
    if not project:
        return []
    
    niche = niche or project.get("name", "")
    location = location or project.get("target_location", "")
    
    prompt = f"""
Project: {niche}
Location: {location}
Language Target: {project.get('target_language', 'hi')}

Generate 15-20 relevant SEO keywords in the following JSON format:
[
  {{"keyword": "...", "search_volume": number, "difficulty": number, "intent": "..."}}
]

Focus on:
- Local SEO keywords (if location given)
- Long-tail keywords (high conversion)
- Question-based keywords
- Competitor keywords in this niche
"""
    
    messages = [
        {"role": "system", "content": KEYWORD_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    start = time.time()
    response = call_llm(messages, provider="gemini", model="gemini-2.0-flash")
    elapsed = int((time.time() - start) * 1000)
    
    # Parse JSON from response
    keywords = []
    try:
        json_match = re.search(r'\[.*?\]', response, re.DOTALL)
        if json_match:
            keywords = json.loads(json_match.group())
    except:
        # Fallback: line-by-line parse
        for line in response.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                keywords.append({"keyword": line, "search_volume": 0, "difficulty": 0})
    
    # Save to database
    saved = []
    for kw in keywords[:20]:  # Max 20
        kw_data = add_keyword(
            project_id=project_id,
            keyword=kw.get("keyword", ""),
            target_url="",
            search_volume=kw.get("search_volume", 0),
            difficulty=kw.get("difficulty", 0)
        )
        saved.append(kw_data)
    
    log_agent_action("keyword", f"Researched {len(saved)} keywords for project {project_id}",
                     response_time_ms=elapsed)
    
    return keywords[:20]


def suggest_keyword_clusters(project_id: int) -> dict:
    """Group existing keywords into topical clusters."""
    keywords = get_keywords(project_id)
    
    if not keywords:
        return {"clusters": [], "message": "No keywords found for clustering"}
    
    kw_text = "\n".join([f"- {k['keyword']} (vol:{k['search_volume']}, diff:{k['difficulty']})" for k in keywords[:30]])
    
    messages = [
        {"role": "system", "content": "Group these keywords into topical clusters. Return JSON: {\"clusters\": [{\"topic\": \"...\", \"keywords\": [...], \"strategy\": \"...\"}]}"},
        {"role": "user", "content": kw_text}
    ]
    
    response = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
    
    try:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    
    return {"clusters": [], "message": "Could not cluster keywords"}
