"""
BHARATSOLVE SEO AGENCY — Competitor Intelligence Agent
Tracks competitor cardiologists in Delhi NCR + Meerut area.

Features:
  - Maintain competitor list with location and strengths
  - Simulate rank comparison for target keywords
  - AI-powered gap analysis (what competitors rank for that you don't)
  - Weekly improvement recommendations
  - Rating & review comparison
"""
import json
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from utils.llm_client import call_llm
from db.operations import log_agent_action

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════
CLINIC_INFO = {
    "name": "Gill Heart Clinic",
    "doctor": "Dr. Gurjeet Singh Gill",
    "location": "Mohiuddinpur, Meerut",
    "specialty": "Non-Invasive Cardiology",
    "years": 12,
    "patients": "50,000+",
    "google_rating": 4.8,
    "google_reviews": 127,
}

TARGET_LOCATIONS = ["Meerut", "Delhi NCR", "Modinagar", "Hapur", "Ghaziabad"]

DEFAULT_COMPETITORS = [
    {
        "id": 1,
        "name": "Meerut Heart Centre",
        "location": "Meerut",
        "specialty": "Interventional Cardiology",
        "estimated_reviews": 95,
        "estimated_rating": 4.4,
        "strengths": ["Angioplasty content", "Maps ranking", "Reviews count"],
        "website": "",
    },
    {
        "id": 2,
        "name": "Delhi NCR Cardiac Care",
        "location": "Delhi NCR",
        "specialty": "Cardiac Surgery",
        "estimated_reviews": 215,
        "estimated_rating": 4.6,
        "strengths": ["Blog content volume", "Domain authority", "Video content"],
        "website": "",
    },
    {
        "id": 3,
        "name": "Lifeline Heart Institute",
        "location": "Meerut Cantt",
        "specialty": "General Cardiology",
        "estimated_reviews": 142,
        "estimated_rating": 4.5,
        "strengths": ["Citation count", "Google Posts frequency", "Local backlinks"],
        "website": "",
    },
    {
        "id": 4,
        "name": "Max Heart & Vascular",
        "location": "Delhi",
        "specialty": "Multi-Specialty Cardiac",
        "estimated_reviews": 420,
        "estimated_rating": 4.7,
        "strengths": ["Brand authority", "Content depth", "Patient testimonials"],
        "website": "",
    },
]

SHARED_KEYWORDS = [
    "Cardiologist Meerut", "Heart Doctor Delhi NCR", "BP Specialist Meerut",
    "Chest Pain Doctor Near Me", "Heart Clinic Mohiuddinpur",
    "ECG Test Meerut", "2D Echo Test Meerut", "TMT Test Meerut",
    "Heart Checkup Meerut", "Cardiac Care Delhi NCR",
    "Heart Attack Treatment", "Heart Failure Specialist",
    "Cholesterol Doctor", "Diabetes Heart Specialist",
    "Angioplasty Guide", "Heart Surgery Recovery",
]

COMPETITOR_ANALYSIS_PROMPT = """तुम एक Local SEO Competitor Analyst हो।
तुम्हारा काम:
1. Local competitors के data analyze करना
2. Keyword gap analysis करना — वो keywords जो competitors rank कर रहे हैं पर आप नहीं
3. Actionable recommendations देना जो rankings improve कर सकें
4. Indian healthcare market के context में suggestions देना
5. Practical, implementable advice देना — theory नहीं

Focus areas:
- Local SEO (Google Maps, Google Business Profile)
- Content gaps (blogs, service pages)
- Review management
- Citation building
- Technical SEO improvements"""


# ═══════════════════════════════════════════════════════════════════════
# COMPETITOR DATA MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════

def get_competitors() -> List[Dict]:
    """Get the competitor list. Uses defaults if DB not available."""
    try:
        from db.operations import get_competitors as db_get_competitors
        comps = db_get_competitors()
        if comps:
            return comps
    except:
        pass
    return DEFAULT_COMPETITORS


def add_competitor(name: str, location: str, specialty: str = "", 
                   strengths: list = None) -> Dict:
    """Add a new competitor to track."""
    try:
        from db.operations import add_competitor as db_add_competitor
        return db_add_competitor(name, location, specialty, strengths or [])
    except:
        new_comp = {
            "id": len(DEFAULT_COMPETITORS) + 1,
            "name": name,
            "location": location,
            "specialty": specialty,
            "estimated_reviews": 0,
            "estimated_rating": 0,
            "strengths": strengths or [],
            "website": "",
        }
        DEFAULT_COMPETITORS.append(new_comp)
        return new_comp


# ═══════════════════════════════════════════════════════════════════════
# RANK SIMULATION (for competitor comparison)
# ═══════════════════════════════════════════════════════════════════════

def simulate_competitor_ranks(competitor: Dict) -> List[Dict]:
    """
    Simulate rank positions for a competitor across shared keywords.
    In production, this would use SerpAPI or DataForSEO for real data.
    """
    import random
    import hashlib
    
    # Use competitor name as seed for consistent pseudo-random results
    seed = int(hashlib.md5(competitor["name"].encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    
    # Different competitors have different strengths
    strength_bonus = len(competitor.get("strengths", [])) * 0.5
    
    ranks = []
    for kw in SHARED_KEYWORDS:
        # Base rank depends on competitor's review count and rating (proxies for authority)
        base_rank = max(1, 15 - (competitor.get("estimated_reviews", 50) / 50) - strength_bonus)
        position = max(1, int(rng.gauss(base_rank, 3)))
        
        ranks.append({
            "keyword": kw,
            "competitor_position": min(position, 30),
            "estimated_volume": rng.randint(500, 5000),
            "in_maps_pack": position <= 3 and rng.random() > 0.3,
        })
    
    return ranks


def get_your_simulated_ranks() -> List[Dict]:
    """Get simulated rank positions for Gill Heart Clinic."""
    import random
    import hashlib
    
    seed = int(hashlib.md5(CLINIC_INFO["name"].encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    
    # Gill Clinic has good reviews and rating = better base rank
    base_rank = max(1, 12 - (CLINIC_INFO["google_reviews"] / 50))
    
    ranks = []
    for kw in SHARED_KEYWORDS:
        position = max(1, int(rng.gauss(base_rank, 2.5)))
        ranks.append({
            "keyword": kw,
            "your_position": min(position, 30),
            "in_maps_pack": position <= 3 and rng.random() > 0.2,
        })
    
    return ranks


# ═══════════════════════════════════════════════════════════════════════
# COMPARISON + GAP ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

def compare_rankings() -> Dict:
    """
    Compare your rankings vs all competitors across shared keywords.
    Returns detailed comparison data.
    """
    your_ranks = get_your_simulated_ranks()
    your_rank_map = {r["keyword"]: r for r in your_ranks}
    
    competitors = get_competitors()
    all_comparisons = []
    
    for comp in competitors:
        comp_ranks = simulate_competitor_ranks(comp)
        
        # Build comparison for this competitor
        comparison = {
            "competitor": comp["name"],
            "location": comp["location"],
            "keywords_compared": len(comp_ranks),
            "keywords_winning": 0,
            "keywords_losing": 0,
            "tied": 0,
            "gap_keywords": [],
        }
        
        for cr in comp_ranks:
            kw = cr["keyword"]
            your_pos = your_rank_map.get(kw, {}).get("your_position", 30)
            comp_pos = cr["competitor_position"]
            
            if your_pos < comp_pos:
                comparison["keywords_winning"] += 1
            elif your_pos > comp_pos:
                comparison["keywords_losing"] += 1
                if comp_pos <= 10 and your_pos > 10:
                    comparison["gap_keywords"].append({
                        "keyword": kw,
                        "competitor_rank": comp_pos,
                        "your_rank": your_pos,
                        "volume": cr["estimated_volume"],
                    })
            else:
                comparison["tied"] += 1
        
        comparison["win_rate"] = round(
            comparison["keywords_winning"] / comparison["keywords_compared"] * 100, 1
        ) if comparison["keywords_compared"] else 0
        
        all_comparisons.append(comparison)
    
    # Summary
    total_winning = sum(c["keywords_winning"] for c in all_comparisons)
    total_losing = sum(c["keywords_losing"] for c in all_comparisons)
    total_compared = sum(c["keywords_compared"] for c in all_comparisons)
    
    your_avg_position = sum(r["your_position"] for r in your_ranks) / len(your_ranks) if your_ranks else 0
    
    return {
        "generated_at": datetime.now().isoformat(),
        "your_clinic": CLINIC_INFO["name"],
        "your_avg_position": round(your_avg_position, 1),
        "your_maps_pack_count": sum(1 for r in your_ranks if r.get("in_maps_pack")),
        "your_total_keywords": len(your_ranks),
        "competitors_analyzed": len(competitors),
        "summary": {
            "total_keywords": total_compared,
            "keywords_winning": total_winning,
            "keywords_losing": total_losing,
            "win_rate": round(total_winning / total_compared * 100, 1) if total_compared else 0,
        },
        "per_competitor": all_comparisons,
        "top_gap_keywords": _extract_top_gaps(all_comparisons),
    }


def _extract_top_gaps(comparisons: List[Dict]) -> List[Dict]:
    """Extract the most important gap keywords across all competitors."""
    all_gaps = []
    for comp in comparisons:
        for gap in comp.get("gap_keywords", []):
            all_gaps.append({
                **gap,
                "competitor": comp["competitor"],
            })
    
    # Sort by volume (highest first) and take top 10
    all_gaps.sort(key=lambda x: x.get("volume", 0), reverse=True)
    return all_gaps[:10]


def generate_gap_analysis() -> Dict:
    """
    Use AI to analyze the gap and generate actionable recommendations.
    """
    comparison_data = compare_rankings()
    
    # Build a prompt for AI analysis
    gaps_text = "\n".join([
        f"- {g['keyword']}: Competitor rank #{g['competitor_rank']}, Your rank #{g['your_rank']} "
        f"(Competitor: {g['competitor']}, Volume: {g['volume']})"
        for g in comparison_data.get("top_gap_keywords", [])[:5]
    ])
    
    prompt = f"""Analyze the competitive landscape for a cardiology clinic in Meerut/Delhi NCR:

Your Clinic: {CLINIC_INFO['name']} by {CLINIC_INFO['doctor']}
Your Avg Rank: #{comparison_data['your_avg_position']}
Win Rate vs Competitors: {comparison_data['summary']['win_rate']}%
Keywords You're Losing: {comparison_data['summary']['keywords_losing']}

Top Gap Keywords (Competitors beating you):
{gaps_text}

Competitor Overview:
{json.dumps([{
    'name': c['competitor'], 
    'location': c['location'],
    'win_rate_against_them': c['win_rate']
} for c in comparison_data['per_competitor']], indent=2)}

Generate a CONCISE Competitive Intelligence Report with:
1. Your current standing (1-2 lines)
2. Top 3 most critical gap keywords to target first
3. 5 specific, actionable recommendations to improve rankings
4. Priority order (what to do first, second, third)

Return as JSON:
{{
  "standing": "...",
  "critical_gaps": [{{"keyword": "...", "action": "..."}}],
  "action_items": [{{"priority": 1, "action": "...", "expected_impact": "high/medium/low", "effort": "low/medium/high"}}],
  "weekly_goal": "..."
}}"""

    messages = [
        {"role": "system", "content": COMPETITOR_ANALYSIS_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    start = time.time()
    response = call_llm(messages, provider="gemini", model="gemini-2.0-flash")
    elapsed = int((time.time() - start) * 1000)
    
    # Parse JSON
    try:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            ai_analysis = json.loads(json_match.group())
            result = {**comparison_data, "ai_analysis": ai_analysis}
            log_agent_action("competitor_agent", f"Generated gap analysis — {len(ai_analysis.get('action_items', []))} recommendations",
                           response_time_ms=elapsed)
            return result
    except:
        pass
    
    # Fallback
    result = {
        **comparison_data,
        "ai_analysis": {
            "standing": f"Your clinic ranks #{comparison_data['your_avg_position']} on average across {len(SHARED_KEYWORDS)} keywords with a {comparison_data['summary']['win_rate']}% win rate against {len(comparison_data['per_competitor'])} competitors.",
            "critical_gaps": comparison_data.get("top_gap_keywords", [])[:3],
            "action_items": [
                {"priority": 1, "action": "Create dedicated service pages for top gap keywords", "expected_impact": "high", "effort": "medium"},
                {"priority": 2, "action": "Post 3x weekly on Google Business Profile with location-optimized content", "expected_impact": "high", "effort": "low"},
                {"priority": 3, "action": "Build 10 local citations on medical directories (Practo, Lybrate, JustDial)", "expected_impact": "medium", "effort": "low"},
                {"priority": 4, "action": "Launch a weekly heart health blog targeting long-tail local keywords", "expected_impact": "high", "effort": "medium"},
                {"priority": 5, "action": "Get 5 new Google reviews per week — directly impacts Maps pack ranking", "expected_impact": "high", "effort": "low"},
            ],
            "weekly_goal": f"Close the gap on {len(comparison_data.get('top_gap_keywords', []))} keywords and improve Maps pack presence from {comparison_data['your_maps_pack_count']}/{comparison_data['your_total_keywords']} to {comparison_data['your_maps_pack_count'] + 3}/{comparison_data['your_total_keywords']}",
        }
    }
    
    log_agent_action("competitor_agent", "Generated gap analysis (fallback)", response_time_ms=elapsed)
    return result


# ═══════════════════════════════════════════════════════════════════════
# COMPETITOR REVIEW COMPARISON
# ═══════════════════════════════════════════════════════════════════════

def compare_reviews() -> Dict:
    """Compare your Google reviews/rating vs competitors."""
    competitors = get_competitors()
    
    comp_summary = []
    for c in competitors:
        comp_summary.append({
            "name": c["name"],
            "location": c["location"],
            "rating": c.get("estimated_rating", 0),
            "reviews": c.get("estimated_reviews", 0),
        })
    
    # Sort by rating
    comp_summary.sort(key=lambda x: x["rating"], reverse=True)
    
    your_rank = 1
    for i, c in enumerate(comp_summary):
        if CLINIC_INFO["google_rating"] < c["rating"]:
            your_rank = i + 2
    
    return {
        "your_clinic": {
            "name": CLINIC_INFO["name"],
            "rating": CLINIC_INFO["google_rating"],
            "reviews": CLINIC_INFO["google_reviews"],
            "rank": your_rank,
        },
        "competitors": comp_summary,
        "total_compared": len(competitors) + 1,
        "recommendation": _get_review_recommendation(your_rank, CLINIC_INFO["google_reviews"], 
                                                       max(c.get("estimated_reviews", 0) for c in competitors)),
    }


def _get_review_recommendation(your_rank: int, your_reviews: int, top_reviews: int) -> str:
    """Generate review-based recommendations."""
    if your_rank == 1:
        return "🏆 You lead in reviews! Maintain this advantage by consistently asking satisfied patients for reviews."
    
    gap = top_reviews - your_reviews
    if gap > 100:
        return f"⚠️ Competitors have {gap}+ more reviews. Goal: Get 10 new reviews per week. Ask every patient after consultation."
    elif gap > 50:
        return f"📈 {gap} review gap. Use WhatsApp + SMS reminders to request reviews from recent patients."
    else:
        return f"👍 Close gap ({gap} reviews). 5 more reviews per week will put you at #1."


# ═══════════════════════════════════════════════════════════════════════
# SCHEDULER TASK
# ═══════════════════════════════════════════════════════════════════════

def competitor_scan_task():
    """
    Automated competitor scan — runs analysis and logs results.
    Designed to be called by the scheduler every 48 hours.
    """
    print("🔍 Competitor Scan: Analyzing Delhi NCR + Meerut competitors...")
    
    result = generate_gap_analysis()
    
    summary = result.get("summary", {})
    ai = result.get("ai_analysis", {})
    
    print(f"🔍 Win Rate: {summary.get('win_rate', 0)}%")
    print(f"🔍 Top Gap Keywords: {len(result.get('top_gap_keywords', []))}")
    
    if ai.get("weekly_goal"):
        print(f"🔍 Weekly Goal: {ai['weekly_goal']}")
    
    log_agent_action("competitor_agent", 
                    f"Scan complete: {summary.get('win_rate', 0)}% win rate, "
                    f"{len(result.get('top_gap_keywords', []))} gaps found")
    
    return result
