"""
BHARATSOLVE SEO AGENCY — Manager Agent
Orchestrates all agents, handles user chat, and delegates tasks.
"""
import json
import time
from datetime import datetime
from utils.llm_client import call_llm, parse_model_string
from db.operations import (
    get_all_projects, get_keywords, get_dashboard_stats,
    get_agent_status_summary, log_agent_action
)

MANAGER_SYSTEM_PROMPT = """तुम BHARATSOLVE SEO AGENCY के Manager Agent हो।
तुम्हारा काम:
1. User की बात समझना और सही agent को task देना
2. SEO strategy सुझाना
3. सभी agents की performance monitor करना
4. Hinglish में reply देना (Hindi + English mix)

Available agents: keyword, content, rank, social, tech, link, clinic, alumni

तुम्हारे पास इनकी जानकारी है:
- सभी projects और उनके keywords
- Rankings और content status
- Agent logs और performance

हमेशा concise और helpful reply दो।"""


def get_manager_response(user_message: str, user_id: int) -> dict:
    """Process user message and return manager response with optional agent task."""
    stats = get_dashboard_stats(user_id)
    agent_status = get_agent_status_summary()
    
    context = f"""
User ID: {user_id}
Dashboard Stats: {json.dumps(stats)}
Agent Status: {json.dumps(agent_status)}

User Message: {user_message}
"""
    
    messages = [
        {"role": "system", "content": MANAGER_SYSTEM_PROMPT},
        {"role": "user", "content": context + "\n\nAppropriate response (Hinglish mein):"}
    ]
    
    start = time.time()
    response = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
    elapsed = int((time.time() - start) * 1000)
    
    log_agent_action("manager", f"Responded to: {user_message[:50]}", 
                     response_time_ms=elapsed)
    
    return {
        "response": response,
        "agent_status": agent_status,
        "stats": stats
    }


def analyze_user_intent(message: str) -> dict:
    """Determine which agent should handle the task."""
    messages = [
        {"role": "system", "content": """तुम एक Intent Classifier हो। 
User message को पढ़कर बताओ कि किस agent को task देना चाहिए।

Return ONLY JSON:
{"agent": "keyword|content|rank|social|manager", "task": "brief description", "priority": "high|medium|low"}

Rules:
- keyword: नए keywords चाहिए, keyword research, keyword ideas
- content: blog post, article, content write, लेख लिखो
- rank: ranking check करो, position check, rank tracker
- social: social media post, FB/Insta पर post करो
- manager: general chat, strategy, doubt, help"""},
        {"role": "user", "content": message}
    ]
    
    try:
        response = call_llm(messages, provider="groq", model="llama-3.1-8b-instant", temperature=0.3)
        # Try to extract JSON
        json_match = __import__('re').search(r'\{.*\}', response, __import__('re').DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"agent": "manager", "task": "general", "priority": "medium"}
    except:
        return {"agent": "manager", "task": "general", "priority": "medium"}
