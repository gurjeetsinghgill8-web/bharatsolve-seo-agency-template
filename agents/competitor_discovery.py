"""
BHARATSOLVE SEO AGENCY — AI Competitor Discovery
Uses Groq AI to find real cardiologist names in Meerut/Delhi NCR area.
"""
import json
import time
import re
from typing import List, Dict
from utils.llm_client import call_llm
from db.operations import log_agent_action


def discover_competitors_ai(location: str = "Meerut", count: int = 20) -> List[Dict]:
    """
    Use AI to discover real cardiologists in a location.
    AI searches its training data for known doctor names.
    """
    prompt = f"""You have knowledge of real medical professionals in India. 
Please list {count} real, verified cardiologists and heart specialists practicing in {location} and nearby areas (within 50km radius).

Include doctors from:
- {location} city
- Nearby towns (Modinagar, Hapur, Ghaziabad, Muzaffarnagar, etc.)
- Individual practitioners (NOT big hospitals like Max/Fortis/Apollo)
- Small clinics and nursing homes

For each doctor provide:
1. Full real name with title (Dr. FirstName LastName)
2. Specific location within/near {location}
3. Sub-specialty if known (e.g., Interventional, Non-invasive, Pediatric Cardiology)

IMPORTANT:
- ONLY list doctors you are confident are REAL practicing cardiologists
- If unsure about a name, mark it with [uncertain]
- DO NOT make up names — use only names from your training data
- Prefer Indian names that are common in Uttar Pradesh/Western UP

Return as JSON list:
[
  {{"name": "Dr. Full Name", "location": "Specific Location", "specialty": "Cardiology/Sub-type", "confidence": "high/medium/low"}},
  ...
]"""

    messages = [
        {"role": "system", "content": "You are a medical directory assistant with knowledge of real Indian doctors. Only list verified real names — do not hallucinate or invent names."},
        {"role": "user", "content": prompt}
    ]
    
    start = time.time()
    response = call_llm(messages, provider="groq", model="llama-3.1-8b-instant", temperature=0.3)
    elapsed = int((time.time() - start) * 1000)
    
    # Parse JSON from response
    try:
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            doctors = json.loads(json_match.group())
            log_agent_action("competitor_discovery", f"AI found {len(doctors)} doctors in {location}")
            return doctors
    except:
        pass
    
    # Fallback: parse text lines
    doctors = []
    for line in response.split('\n'):
        line = line.strip()
        if line.startswith(('Dr.', 'Dr ', '- Dr', '* Dr', '• Dr')):
            name = re.sub(r'^[-*•\s]+', '', line).strip()
            doctors.append({"name": name, "location": location, "specialty": "Cardiology", "confidence": "low"})
    
    log_agent_action("competitor_discovery", f"Parsed {len(doctors)} doctors from text")
    return doctors


def discover_from_multiple_sources() -> Dict[str, List[Dict]]:
    """Discover competitors from multiple locations."""
    locations = ["Meerut", "Ghaziabad", "Delhi NCR near Meerut"]
    
    all_results = {}
    for loc in locations:
        try:
            doctors = discover_competitors_ai(loc, count=8)
            all_results[loc] = doctors
            time.sleep(1)  # Rate limiting
        except Exception as e:
            all_results[loc] = []
    
    return all_results


def format_for_ui(doctors: List[Dict]) -> str:
    """Format discovered doctors for the competitor editor."""
    lines = []
    for d in doctors:
        name = d.get("name", "Unknown")
        location = d.get("location", "Meerut")
        specialty = d.get("specialty", "Cardiology")
        confidence = d.get("confidence", "medium")
        
        prefix = "✅" if confidence == "high" else ("🟡" if confidence == "medium" else "❓")
        lines.append(f"{prefix} {name} — {specialty}, {location}")
    
    return "\n".join(lines)
