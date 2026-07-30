"""
BHARATSOLVE SEO AGENCY — Auto-Review Reply Agent
Manages Google Business Profile reviews with AI-powered Hinglish replies.

Features:
  - Fetch latest Google reviews via GBP API
  - AI sentiment analysis (positive/neutral/negative)
  - Auto-generate personalized Hinglish replies
  - Auto-post replies via GBP API
  - Track reply history to avoid duplicates
  - Weekly review summary report
"""
import json
import time
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from utils.llm_client import call_llm
from db.operations import log_agent_action

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════
CLINIC_CONFIG = {
    "name": "Gill Heart Clinic",
    "doctor": "Dr. Gurjeet Singh Gill",
    "location": "Mohiuddinpur, Meerut",
    "phone": "+91-9639011155",
    "website": "https://gurjeetsinghgill8-web.github.io/gill-heart-clinic/",
}

REVIEW_REPLY_PROMPT = """You are a Medical Clinic Review Reply Assistant.
Your job:
1. Read patient reviews and understand their sentiment
2. Write natural, warm, professional Hinglish replies
3. Use the patient's name in the reply
4. Naturally mention clinic/doctor services
5. Express gratitude for positive reviews
6. Politely address concerns in negative reviews and assure improvement
7. Every reply must be unique and personalized — no copy-paste

IMPORTANT RULES:
- REPLY MUST BE IN HINGLISH (mix of Hindi + English, natural Indian style)
- 2-4 sentences max, conversational tone
- Never sound like a bot or automated response
- For negative reviews: don't be defensive, show empathy, offer to connect offline
- For positive reviews: express genuine gratitude, mention specific things they appreciated
- Always include doctor's name naturally when relevant
- Maintain medical professionalism"""


# ═══════════════════════════════════════════════════════════════════════
# GBP REVIEW API HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _get_gbp_token() -> str:
    """Get Google Business Profile token from multiple sources."""
    token = os.getenv("GOOGLE_BUSINESS_TOKEN", "")
    if not token:
        try:
            import streamlit as st
            token = st.secrets.get("GOOGLE_BUSINESS_TOKEN", "")
        except:
            pass
    return token


def _get_gbp_account() -> str:
    """Get GBP account name."""
    account = os.getenv("GOOGLE_BUSINESS_ACCOUNT", "")
    if not account:
        try:
            import streamlit as st
            account = st.secrets.get("GOOGLE_BUSINESS_ACCOUNT", "")
        except:
            pass
    return account


def _get_gbp_location() -> str:
    """Get GBP location name."""
    loc = os.getenv("GOOGLE_BUSINESS_LOCATION", "")
    if not loc:
        try:
            import streamlit as st
            loc = st.secrets.get("GOOGLE_BUSINESS_LOCATION", "")
        except:
            pass
    return loc


def _gbp_headers() -> dict:
    token = _get_gbp_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def fetch_latest_reviews(max_results: int = 10) -> List[Dict]:
    """
    Fetch latest Google reviews via GBP API.
    If API is not configured, returns simulated reviews for demo.
    """
    account = _get_gbp_account()
    location = _get_gbp_location()
    token = _get_gbp_token()
    
    if not all([account, location, token]):
        # Return simulated reviews for demo/testing
        return _get_demo_reviews()
    
    try:
        import requests
        url = (
            f"https://mybusiness.googleapis.com/v4/"
            f"accounts/{account}/locations/{location}/reviews"
            f"?pageSize={max_results}&orderBy=updateTime desc"
        )
        headers = _gbp_headers()
        resp = requests.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            reviews = data.get("reviews", [])
            
            # Format reviews
            formatted = []
            for r in reviews:
                formatted.append({
                    "review_id": r.get("reviewId", ""),
                    "reviewer": r.get("reviewer", {}).get("displayName", "Anonymous"),
                    "rating": r.get("starRating", "STAR_RATING_UNSPECIFIED"),
                    "text": r.get("comment", ""),
                    "time": r.get("updateTime", ""),
                    "has_reply": "reviewReply" in r,
                })
            return formatted
        else:
            print(f"⚠️ GBP API error: {resp.status_code}")
            return _get_demo_reviews()
    except Exception as e:
        print(f"⚠️ GBP fetch error: {e}")
        return _get_demo_reviews()


def _get_demo_reviews() -> List[Dict]:
    """Simulated reviews for demo/testing when GBP API is not configured."""
    return [
        {
            "review_id": "rev_001",
            "reviewer": "Rahul Sharma",
            "rating": "FIVE",
            "text": "Dr. Gill is the best cardiologist in Meerut. Very thorough checkup and explained everything clearly. Highly recommended!",
            "time": (datetime.now() - timedelta(hours=2)).isoformat(),
            "has_reply": False,
        },
        {
            "review_id": "rev_002",
            "reviewer": "Priya Verma",
            "rating": "FIVE",
            "text": "My father's heart treatment was excellent. The clinic is well-equipped and the doctor is very caring. Thank you Dr. Gill!",
            "time": (datetime.now() - timedelta(days=1)).isoformat(),
            "has_reply": False,
        },
        {
            "review_id": "rev_003",
            "reviewer": "Amit Kumar",
            "rating": "FOUR",
            "text": "Good experience with ECG and consultation. Waiting time could be improved but overall satisfied with the treatment.",
            "time": (datetime.now() - timedelta(days=2)).isoformat(),
            "has_reply": False,
        },
        {
            "review_id": "rev_004",
            "reviewer": "Sunita Devi",
            "rating": "FIVE",
            "text": "Best heart doctor in Mohiuddinpur area. Affordable fees and excellent care. The staff is also very helpful.",
            "time": (datetime.now() - timedelta(days=3)).isoformat(),
            "has_reply": False,
        },
        {
            "review_id": "rev_005",
            "reviewer": "Vikram Singh",
            "rating": "THREE",
            "text": "Doctor is good but parking is a problem. The ECG report was given on time. Treatment quality is satisfactory.",
            "time": (datetime.now() - timedelta(days=5)).isoformat(),
            "has_reply": False,
        },
    ]


def _star_rating(rating_str: str) -> int:
    """Convert GBP star rating string to integer."""
    mapping = {
        "STAR_RATING_UNSPECIFIED": 0,
        "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5,
    }
    # Handle both string formats and numeric
    if isinstance(rating_str, (int, float)):
        return int(rating_str)
    return mapping.get(str(rating_str).upper(), 0)


# ═══════════════════════════════════════════════════════════════════════
# SENTIMENT ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

def analyze_sentiment(review_text: str, rating: int) -> str:
    """Analyze review sentiment based on rating and text content."""
    if rating >= 5:
        return "positive"
    elif rating >= 4:
        # Check text for mixed signals
        negative_words = ["bad", "poor", "worst", "terrible", "disappointed", 
                         "problem", "issue", "waiting", "delay", "rude"]
        if any(w in review_text.lower() for w in negative_words):
            return "neutral"
        return "positive"
    elif rating == 3:
        return "neutral"
    else:
        return "negative"


# ═══════════════════════════════════════════════════════════════════════
# AI REPLY GENERATION
# ═══════════════════════════════════════════════════════════════════════

def generate_ai_reply(review: Dict) -> str:
    """
    Generate a personalized Hinglish reply to a Google review using AI.
    
    Args:
        review: Dict with 'reviewer', 'rating', 'text', 'sentiment'
    
    Returns:
        AI-generated reply string in Hinglish
    """
    reviewer = review.get("reviewer", "Patient")
    rating_val = _star_rating(review.get("rating", 0))
    review_text = review.get("text", "")
    sentiment = review.get("sentiment", analyze_sentiment(review_text, rating_val))
    
    stars = "⭐" * rating_val
    
    prompt = f"""Review by: {reviewer}
Rating: {stars} ({rating_val}/5)
Patient's Review: "{review_text}"
Sentiment: {sentiment}

Dr. {CLINIC_CONFIG['doctor'].split()[-2]} {CLINIC_CONFIG['doctor'].split()[-1]} at {CLINIC_CONFIG['name']}, {CLINIC_CONFIG['location']}

Write a short, warm, natural Hinglish reply (2-4 sentences):
- Address the reviewer by name: {reviewer.split()[0]} ji
- Reference something specific from their review
- For positive reviews: express genuine gratitude, mention we're here for their heart health
- For neutral reviews: thank them, acknowledge feedback, assure improvement
- For negative reviews: apologize politely, show empathy, invite them to contact us directly
- Natural Hinglish: mix Hindi + English like real Indians talk
- DO NOT sound robotic or templated
- Must be unique and personal

Reply (Hinglish only, no English translation needed):"""

    messages = [
        {"role": "system", "content": REVIEW_REPLY_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    start = time.time()
    reply = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
    elapsed = int((time.time() - start) * 1000)
    
    # Clean up the reply
    reply = reply.strip().strip('"').strip("'")
    # Remove any "Reply:" or "Response:" prefixes
    reply = re.sub(r'^(Reply|Response|उत्तर)[:\s-]+', '', reply, flags=re.IGNORECASE).strip()
    
    return reply


def _generate_fallback_reply(review: Dict) -> str:
    """Generate a template-based reply when AI is unavailable."""
    reviewer = review.get("reviewer", "Patient").split()[0]
    rating_val = _star_rating(review.get("rating", 0))
    
    if rating_val >= 4:
        replies = [
            f"धन्यवाद {reviewer} जी! 🙏 आपके कीमती feedback के लिए बहुत-बहुत शुक्रिया। आपका heart health हमारी priority है। हमारी clinic में आपका हमेशा स्वागत है! ❤️",
            f"Thank you so much {reviewer} ji for your wonderful review! 😊 We're committed to providing the best cardiac care in Meerut. Stay heart-healthy! 💪",
            f"बहुत-बहुत धन्यवाद {reviewer} जी! 🙏 आपके review ने हमारा दिन बना दिया। आपके और आपके परिवार के अच्छे health के लिए हम हमेशा available हैं। ❤️",
        ]
    elif rating_val == 3:
        replies = [
            f"Thank you {reviewer} ji for your honest feedback. 🙏 We've noted your suggestions and will definitely work on improving. Your satisfaction is important to us. Please feel free to reach out anytime!",
            f"धन्यवाद {reviewer} जी आपके feedback के लिए। हम आपकी बातों पर ज़रूर ध्यान देंगे और अपनी services को और बेहतर बनाएंगे। आपका स्वास्थ्य हमारी प्राथमिकता है।",
        ]
    else:
        replies = [
            f"Dear {reviewer} ji, we're sorry to hear about your experience. 🙏 Patient satisfaction is very important to us. Please call us at {CLINIC_CONFIG['phone']} — Dr. Gill would like to personally address your concerns. Your heart health matters to us.",
            f"{reviewer} जी, हमें आपकी परेशानी का बहुत दुख हुआ। 🙏 कृपया हमें {CLINIC_CONFIG['phone']} पर call करें ताकि हम आपकी समस्या का समाधान कर सकें। आपका स्वास्थ्य और satisfaction हमारी priority है।",
        ]
    
    import random
    return random.choice(replies)


# ═══════════════════════════════════════════════════════════════════════
# MAIN: Process reviews and generate replies
# ═══════════════════════════════════════════════════════════════════════

def process_reviews(max_reviews: int = 10) -> List[Dict]:
    """
    Fetch latest reviews, analyze sentiment, and generate AI replies.
    Does NOT auto-post replies (use auto_reply_to_reviews for that).
    
    Returns:
        List of reviews with AI replies attached
    """
    reviews = fetch_latest_reviews(max_reviews)
    
    processed = []
    for review in reviews:
        rating_val = _star_rating(review.get("rating", 0))
        sentiment = analyze_sentiment(review.get("text", ""), rating_val)
        
        review["rating_num"] = rating_val
        review["sentiment"] = sentiment
        
        # Generate AI reply for unreplied reviews
        if not review.get("has_reply", False):
            try:
                ai_reply = generate_ai_reply(review)
                review["ai_reply"] = ai_reply
            except Exception as e:
                review["ai_reply"] = _generate_fallback_reply(review)
                review["ai_error"] = str(e)
        else:
            review["ai_reply"] = None  # Already has a reply
        
        processed.append(review)
    
    log_agent_action("review_agent", f"Processed {len(processed)} reviews")
    
    return processed


def post_reply_to_review(review_id: str, reply_text: str) -> Dict:
    """
    Post a reply to a Google review via GBP API.
    
    Args:
        review_id: Google review ID
        reply_text: Reply text to post
    
    Returns:
        Dict with success/error status
    """
    account = _get_gbp_account()
    location = _get_gbp_location()
    token = _get_gbp_token()
    
    if not all([account, location, token]):
        return {"success": False, "error": "GBP API not configured. Set GOOGLE_BUSINESS_TOKEN, GOOGLE_BUSINESS_ACCOUNT, GOOGLE_BUSINESS_LOCATION in environment."}
    
    try:
        import requests
        url = (
            f"https://mybusiness.googleapis.com/v4/"
            f"accounts/{account}/locations/{location}/reviews/{review_id}/reply"
        )
        headers = _gbp_headers()
        body = {"comment": reply_text}
        
        resp = requests.put(url, headers=headers, json=body, timeout=15)
        
        if resp.status_code == 200:
            log_agent_action("review_agent", f"Reply posted to review {review_id}")
            return {"success": True, "review_id": review_id}
        else:
            error_msg = f"GBP API error {resp.status_code}: {resp.text[:200]}"
            log_agent_action("review_agent", error_msg, status="error", error_message=error_msg)
            return {"success": False, "error": error_msg}
    except Exception as e:
        log_agent_action("review_agent", f"Reply failed: {e}", status="error", error_message=str(e))
        return {"success": False, "error": str(e)}


def auto_reply_to_reviews(max_reviews: int = 5) -> Dict:
    """
    Complete auto-reply pipeline: 
    Fetch reviews → Generate AI replies → Post to Google.
    
    Returns:
        Summary dict with results
    """
    log_agent_action("review_agent", "Starting auto-reply cycle")
    
    reviews = process_reviews(max_reviews)
    
    replied = 0
    skipped = 0
    errors = 0
    
    for review in reviews:
        if review.get("has_reply", False):
            skipped += 1
            continue
        
        ai_reply = review.get("ai_reply")
        if not ai_reply:
            skipped += 1
            continue
        
        result = post_reply_to_review(review["review_id"], ai_reply)
        
        if result.get("success"):
            replied += 1
            print(f"✅ Replied to {review['reviewer']}: {ai_reply[:80]}...")
        else:
            errors += 1
            print(f"❌ Failed reply to {review['reviewer']}: {result.get('error', '')}")
    
    summary = {
        "total": len(reviews),
        "replied": replied,
        "skipped": skipped,
        "errors": errors,
        "timestamp": datetime.now().isoformat(),
    }
    
    log_agent_action("review_agent", 
                    f"Auto-reply complete: {replied} sent, {skipped} skipped, {errors} errors")
    
    return summary


def generate_review_report() -> Dict:
    """
    Generate a weekly review summary report.
    """
    reviews = fetch_latest_reviews(20)
    
    if not reviews:
        return {"error": "No reviews found"}
    
    total = len(reviews)
    ratings = [_star_rating(r.get("rating", 0)) for r in reviews]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    positive = [r for r in reviews if analyze_sentiment(r.get("text", ""), _star_rating(r.get("rating", 0))) == "positive"]
    neutral = [r for r in reviews if analyze_sentiment(r.get("text", ""), _star_rating(r.get("rating", 0))) == "neutral"]
    negative = [r for r in reviews if analyze_sentiment(r.get("text", ""), _star_rating(r.get("rating", 0))) == "negative"]
    unreplied = [r for r in reviews if not r.get("has_reply", False)]
    
    report = {
        "clinic": CLINIC_CONFIG["name"],
        "generated_at": datetime.now().isoformat(),
        "period": "Last 7 days",
        "total_reviews": total,
        "average_rating": round(avg_rating, 1),
        "sentiment_breakdown": {
            "positive": len(positive),
            "neutral": len(neutral),
            "negative": len(negative),
            "positive_pct": round(len(positive) / total * 100, 1) if total else 0,
        },
        "unreplied_reviews": len(unreplied),
        "reply_rate": round((total - len(unreplied)) / total * 100, 1) if total else 0,
        "top_reviewers": [],
        "recommendations": [],
    }
    
    # AI-generated recommendations
    if len(unreplied) > 0:
        report["recommendations"].append(f"⚡ {len(unreplied)} reviews pending reply — use auto-reply or reply manually")
    if avg_rating < 4.0:
        report["recommendations"].append("📈 Rating below 4.0 — focus on patient experience improvements")
    if len(negative) > 0:
        report["recommendations"].append(f"⚠️ {len(negative)} negative reviews — address concerns proactively")
    if report["reply_rate"] < 80:
        report["recommendations"].append("💬 Reply rate below 80% — aim to reply to every review within 24 hours")
    
    log_agent_action("review_agent", f"Generated review report: {avg_rating}★ avg, {total} reviews")
    
    return report


# ═══════════════════════════════════════════════════════════════════════
# SCHEDULER TASK
# ═══════════════════════════════════════════════════════════════════════

def auto_review_task():
    """
    Automated review task — checks for new reviews and auto-replies.
    Designed to be called by the scheduler every 6 hours.
    """
    print("💬 Auto-Review Task: Checking for new Google reviews...")
    result = auto_reply_to_reviews(max_reviews=5)
    print(f"💬 Result: {result['replied']} replied, {result['skipped']} skipped, {result['errors']} errors")
    return result
