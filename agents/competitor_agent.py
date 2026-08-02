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
    # ═══ MEERUT TOP RANKED CARDIOLOGISTS (AI Search Verified Rankings) ═══
    {"id": 1, "name": "Dr. Varad Gupta", "location": "Meerut", "hospital": "Metro Hospital and Heart Institute, Jawahar Nagar", "experience_years": 40, "specialty": "Non-Invasive & Clinical Cardiology", "estimated_reviews": 200, "estimated_rating": 4.7, "strengths": ["40+ years experience", "Metro Hospital brand", "High patient volume", "Google Maps presence"], "website": ""},
    {"id": 2, "name": "Dr. Sanjeev Saxena", "location": "Meerut", "hospital": "Metro Hospital and Heart Institute, Jawahar Nagar", "experience_years": 36, "specialty": "Interventional Cardiology", "estimated_reviews": 180, "estimated_rating": 4.6, "strengths": ["Metro Hospital brand", "Critical care expertise", "Coronary interventions"], "website": ""},
    {"id": 3, "name": "Dr. Hariraj Singh Tomar", "location": "Meerut", "hospital": "Nutema Hospital", "experience_years": 28, "specialty": "Chronic Heart Disease & Emergency Cardiology", "estimated_reviews": 160, "estimated_rating": 4.7, "strengths": ["Peer recognition", "Chronic disease management", "Emergency cardiac care"], "website": ""},
    {"id": 4, "name": "Dr. Hariom Tyagi", "location": "Meerut", "hospital": "Lokpriya Hospital", "experience_years": 26, "specialty": "Acute Coronary Syndromes", "estimated_reviews": 150, "estimated_rating": 4.7, "strengths": ["Patient communication", "Trust legacy", "Acute care"], "website": ""},
    {"id": 5, "name": "Dr. Sajal Gupta", "location": "Meerut", "hospital": "Multi-Speciality Centers / Meerut Network", "experience_years": 22, "specialty": "Preventive Cardiology & Heart Failure", "estimated_reviews": 140, "estimated_rating": 4.6, "strengths": ["Academic knowledge", "Diagnostic accuracy", "Multi-center network"], "website": ""},
    {"id": 6, "name": "Dr. Md. Talha Khan Abid", "location": "Meerut", "hospital": "KMC Hospital, Malyana", "experience_years": 20, "specialty": "Interventional Cardiology", "estimated_reviews": 130, "estimated_rating": 4.7, "strengths": ["Catheter-based procedures", "Angiography expertise"], "website": ""},
    {"id": 7, "name": "Dr. Sanjeev Kumar Bansal", "location": "Meerut", "hospital": "Lokpriya Hospital", "experience_years": 20, "specialty": "Hypertension & Lipid Disorders", "estimated_reviews": 120, "estimated_rating": 4.7, "strengths": ["Preventive counseling", "Structured treatment plans"], "website": ""},
    {"id": 8, "name": "Dr. Rakesh Morya", "location": "Meerut", "hospital": "Jaswant Rai Speciality Hospital, Mansarovar Colony", "experience_years": 18, "specialty": "Interventional Cardiology & Critical Care", "estimated_reviews": 110, "estimated_rating": 4.7, "strengths": ["Complex angioplasty", "ICU care"], "website": ""},
    {"id": 9, "name": "Dr. Abhinav Rastogi", "location": "Meerut", "hospital": "Apusnova Hospital, Mawana Road", "experience_years": 15, "specialty": "Interventional Cardiology", "estimated_reviews": 100, "estimated_rating": 4.8, "strengths": ["99% recommendation rate", "Evidence-based approach", "Bedside manner"], "website": ""},
    {"id": 10, "name": "Dr. Md. Talha Khan", "location": "Meerut", "hospital": "KMC Hospital, Malyana", "experience_years": 15, "specialty": "Cardiac Diagnostics & Emergency", "estimated_reviews": 95, "estimated_rating": 4.8, "strengths": ["99% patient approval", "Emergency response"], "website": ""},
    # ═══ MEERUT OTHER NOTABLE CARDIOLOGISTS ═══
    {"id": 11, "name": "Dr. Vishal Singh", "location": "Meerut", "hospital": "Apusnova Hospital", "experience_years": 12, "specialty": "Cardiology", "estimated_reviews": 80, "estimated_rating": 4.5, "strengths": ["Apusnova Hospital network"], "website": ""},
    {"id": 12, "name": "Dr. Amit Kumar Jain", "location": "Meerut", "hospital": "Sirohi Hospital", "experience_years": 15, "specialty": "Cardiology", "estimated_reviews": 70, "estimated_rating": 4.4, "strengths": ["Hospital affiliation"], "website": ""},
    {"id": 13, "name": "Dr. P. K. Jain", "location": "Meerut", "hospital": "Sirohi Hospital", "experience_years": 25, "specialty": "Cardiology", "estimated_reviews": 65, "estimated_rating": 4.3, "strengths": ["Senior experience"], "website": ""},
    {"id": 14, "name": "Dr. Mamtesh Gupta", "location": "Meerut", "hospital": "Dhanvantri Jeevan Rekha Hospital", "experience_years": 18, "specialty": "Cardiology", "estimated_reviews": 60, "estimated_rating": 4.4, "strengths": ["Established practice"], "website": ""},
    {"id": 15, "name": "Dr. Deepak", "location": "Meerut", "hospital": "Chhatrapati Shivaji Subharti Hospital", "experience_years": 10, "specialty": "Cardiology", "estimated_reviews": 55, "estimated_rating": 4.2, "strengths": ["Subharti medical college"], "website": ""},
    {"id": 16, "name": "Dr. Rajeev Agarwal", "location": "Meerut", "hospital": "Jaswant Rai Speciality Hospital", "experience_years": 20, "specialty": "Cardiology", "estimated_reviews": 75, "estimated_rating": 4.5, "strengths": ["Dual hospital affiliation"], "website": ""},
    {"id": 17, "name": "Dr. Chand Bhusan Pandey", "location": "Meerut", "hospital": "LLRM Medical College", "experience_years": 30, "specialty": "Cardiology", "estimated_reviews": 90, "estimated_rating": 4.3, "strengths": ["Medical college faculty", "Teaching role"], "website": ""},
    {"id": 18, "name": "Dr. Shashank Pandey", "location": "Meerut", "hospital": "LLRM Medical College", "experience_years": 15, "specialty": "Cardiology", "estimated_reviews": 50, "estimated_rating": 4.2, "strengths": ["Medical college affiliation"], "website": ""},
    {"id": 19, "name": "Dr. Dheeraj Kumar Sony", "location": "Meerut", "hospital": "LLRM Medical College", "experience_years": 12, "specialty": "Cardiology", "estimated_reviews": 45, "estimated_rating": 4.1, "strengths": ["Academic setting"], "website": ""},
    {"id": 20, "name": "Dr. Deeraj Kumar Soni", "location": "Meerut", "hospital": "IIMT Life Line Hospital", "experience_years": 10, "specialty": "Cardiology", "estimated_reviews": 40, "estimated_rating": 4.0, "strengths": ["Multi-hospital network"], "website": ""},
    {"id": 21, "name": "Dr. Vineet Bansal", "location": "Meerut", "hospital": "Navjeevan Hospital", "experience_years": 14, "specialty": "Cardiology", "estimated_reviews": 55, "estimated_rating": 4.3, "strengths": ["Independent hospital"], "website": ""},
    {"id": 22, "name": "Dr. Amit", "location": "Meerut", "hospital": "Chhatrapati Shivaji Subharti Hospital", "experience_years": 10, "specialty": "Cardiology", "estimated_reviews": 35, "estimated_rating": 4.0, "strengths": ["Subharti hospital network"], "website": ""},
    {"id": 23, "name": "Dr. Prashant Bendre", "location": "Meerut", "hospital": "Metro Hospital and Heart Institute", "experience_years": 18, "specialty": "Cardiology", "estimated_reviews": 85, "estimated_rating": 4.5, "strengths": ["Metro Hospital brand"], "website": ""},
    {"id": 24, "name": "Dr. Gyanendra Singh", "location": "Meerut", "hospital": "Metro Hospital and Heart Institute", "experience_years": 22, "specialty": "Cardiology", "estimated_reviews": 80, "estimated_rating": 4.5, "strengths": ["Metro Hospital brand"], "website": ""},
    {"id": 25, "name": "Dr. Vijay Narain Tyagi", "location": "Meerut", "hospital": "Metro Hospital and Heart Institute", "experience_years": 25, "specialty": "Cardiology", "estimated_reviews": 75, "estimated_rating": 4.4, "strengths": ["Metro Hospital brand", "Senior experience"], "website": ""},
    {"id": 26, "name": "Dr. Jitendra Sharma", "location": "Meerut", "hospital": "Metro Hospital and Heart Institute", "experience_years": 15, "specialty": "Cardiology", "estimated_reviews": 60, "estimated_rating": 4.3, "strengths": ["Metro Hospital brand"], "website": ""},
    {"id": 27, "name": "Dr. Harimohan Choudhary", "location": "Meerut", "hospital": "Lokpriya Hospital", "experience_years": 16, "specialty": "Cardiology", "estimated_reviews": 55, "estimated_rating": 4.3, "strengths": ["Lokpriya Hospital network"], "website": ""},
    {"id": 28, "name": "Dr. Oshin Bhardwaj", "location": "Meerut", "hospital": "Lokpriya Hospital", "experience_years": 10, "specialty": "Cardiology", "estimated_reviews": 40, "estimated_rating": 4.2, "strengths": ["Lokpriya Hospital"], "website": ""},
    {"id": 29, "name": "Dr. Jagadish J.", "location": "Meerut", "hospital": "Lokpriya Hospital", "experience_years": 12, "specialty": "Cardiology", "estimated_reviews": 45, "estimated_rating": 4.2, "strengths": ["Lokpriya Hospital"], "website": ""},
    {"id": 30, "name": "Dr. Rajendra Kumar Agarwal", "location": "Delhi NCR", "hospital": "Max Network / Regional Consultation", "experience_years": 30, "specialty": "Interventional Cardiology", "estimated_reviews": 200, "estimated_rating": 4.6, "strengths": ["Max brand authority", "Pan-NCR network"], "website": ""},
    {"id": 31, "name": "Dr. Amit Goel", "location": "Delhi NCR", "hospital": "Max Network / Regional Consultation", "experience_years": 22, "specialty": "Cardiology", "estimated_reviews": 180, "estimated_rating": 4.6, "strengths": ["Max brand", "Regional reach"], "website": ""},
    {"id": 32, "name": "Dr. C. P. Vashisht", "location": "Delhi NCR", "hospital": "Max Network / Regional Consultation", "experience_years": 25, "specialty": "Cardiology", "estimated_reviews": 160, "estimated_rating": 4.5, "strengths": ["Max brand"], "website": ""},
    {"id": 33, "name": "Dr. Rajiv Agarwal", "location": "Delhi NCR", "hospital": "Associated Heart Care Centers", "experience_years": 28, "specialty": "Cardiology", "estimated_reviews": 150, "estimated_rating": 4.5, "strengths": ["Multi-center network"], "website": ""},
    {"id": 34, "name": "Dr. Ripen Gupta", "location": "Delhi NCR", "hospital": "Associated Heart Care Centers", "experience_years": 20, "specialty": "Cardiology", "estimated_reviews": 140, "estimated_rating": 4.5, "strengths": ["Established practice"], "website": ""},
    {"id": 35, "name": "Dr. Rajeev Rathi", "location": "Delhi NCR", "hospital": "Associated Heart Care Centers", "experience_years": 18, "specialty": "Cardiology", "estimated_reviews": 120, "estimated_rating": 4.4, "strengths": ["Multi-center network"], "website": ""},
    {"id": 36, "name": "Dr. Sunil Kumar Agarwal", "location": "Delhi NCR", "hospital": "Associated Heart Care Centers", "experience_years": 22, "specialty": "Cardiology", "estimated_reviews": 110, "estimated_rating": 4.4, "strengths": ["Established network"], "website": ""},
    {"id": 37, "name": "Dr. Vijay Kumar Chopra", "location": "Delhi NCR", "hospital": "Associated Heart Care Centers", "experience_years": 25, "specialty": "Cardiology", "estimated_reviews": 100, "estimated_rating": 4.3, "strengths": ["Experience"], "website": ""},
    {"id": 38, "name": "Dr. Anupam Goel", "location": "Delhi NCR", "hospital": "Associated Heart Care Centers", "experience_years": 15, "specialty": "Cardiology", "estimated_reviews": 90, "estimated_rating": 4.3, "strengths": ["Network reach"], "website": ""},
    {"id": 39, "name": "Dr. Sumeet Sethi", "location": "Delhi NCR", "hospital": "Associated Heart Care Centers", "experience_years": 12, "specialty": "Cardiology", "estimated_reviews": 80, "estimated_rating": 4.2, "strengths": ["Growing practice"], "website": ""},
    {"id": 40, "name": "Dr. Arif Mustaqueem", "location": "Delhi NCR", "hospital": "Associated Heart Care Centers", "experience_years": 10, "specialty": "Cardiology", "estimated_reviews": 70, "estimated_rating": 4.2, "strengths": ["Multi-center reach"], "website": ""},
    {"id": 41, "name": "Dr. Alok Kumar", "location": "Meerut", "hospital": "Meerut Clinical Cardiac Services", "experience_years": 12, "specialty": "Cardiology", "estimated_reviews": 50, "estimated_rating": 4.1, "strengths": ["Independent practice"], "website": ""},
    {"id": 42, "name": "Dr. Manish Singhal", "location": "Meerut", "hospital": "Shanti Gopal Heart Centre", "experience_years": 15, "specialty": "Cardiology", "estimated_reviews": 55, "estimated_rating": 4.2, "strengths": ["Heart centre association"], "website": ""},
    {"id": 43, "name": "Dr. Pankaj Jain", "location": "Meerut", "hospital": "Jain Heart & General Clinic", "experience_years": 18, "specialty": "Cardiology", "estimated_reviews": 60, "estimated_rating": 4.3, "strengths": ["Own clinic", "Independent practice"], "website": ""},
    {"id": 44, "name": "Dr. Vineet Sharma", "location": "Meerut", "hospital": "Subharti Medical College Cardiology", "experience_years": 12, "specialty": "Cardiology", "estimated_reviews": 45, "estimated_rating": 4.1, "strengths": ["Medical college faculty"], "website": ""},
    {"id": 45, "name": "Dr. Anurag Mittal", "location": "Meerut", "hospital": "Mittal Heart Care Clinic", "experience_years": 10, "specialty": "Cardiology", "estimated_reviews": 40, "estimated_rating": 4.0, "strengths": ["Independent clinic"], "website": ""},
    {"id": 46, "name": "Dr. Ashish Kumar Gupta", "location": "Meerut", "hospital": "Garh Road Cardiac Practice", "experience_years": 15, "specialty": "Cardiology", "estimated_reviews": 50, "estimated_rating": 4.2, "strengths": ["Local practice"], "website": ""},
    {"id": 47, "name": "Dr. R. K. Sharma", "location": "Meerut", "hospital": "Meerut City Heart Bureau", "experience_years": 20, "specialty": "Cardiology", "estimated_reviews": 55, "estimated_rating": 4.2, "strengths": ["City center location"], "website": ""},
    {"id": 48, "name": "Dr. Neeraj Rastogi", "location": "Meerut", "hospital": "Rastogi Nursing Home & Heart Clinic", "experience_years": 12, "specialty": "Cardiology", "estimated_reviews": 45, "estimated_rating": 4.1, "strengths": ["Own nursing home"], "website": ""},
    {"id": 49, "name": "Dr. Manoj Kumar", "location": "Meerut", "hospital": "Delhi Road Cardiac Unit", "experience_years": 10, "specialty": "Cardiology", "estimated_reviews": 35, "estimated_rating": 4.0, "strengths": ["Delhi Road location"], "website": ""},
    {"id": 50, "name": "Dr. Sandeep Singhal", "location": "Meerut", "hospital": "Singhal Hospital & Heart Care", "experience_years": 20, "specialty": "Cardiology", "estimated_reviews": 65, "estimated_rating": 4.3, "strengths": ["Own hospital", "Established practice"], "website": ""},
    # ═══ MODINAGAR COMPETITORS ═══
    {"id": 51, "name": "Dr. Deepak (Modinagar)", "location": "Modinagar", "hospital": "GT Road, Raj Chopra ke paas, Modinagar", "experience_years": 15, "specialty": "Cardiology", "estimated_reviews": 45, "estimated_rating": 4.2, "strengths": ["Local Modinagar practice", "GT Road prime location"], "website": ""},
    {"id": 52, "name": "Dr. Shanky Jain", "location": "Modinagar", "hospital": "Bank Colony, Modinagar", "experience_years": 10, "specialty": "General Medicine & Cardiac", "estimated_reviews": 30, "estimated_rating": 4.0, "strengths": ["Local accessible clinic"], "website": ""},
    {"id": 53, "name": "Dr. Lokesh Kumar", "location": "Modinagar", "hospital": "Raj Chaupala ke paas, Modinagar", "experience_years": 8, "specialty": "General Consultation", "estimated_reviews": 25, "estimated_rating": 3.9, "strengths": ["Local Modinagar presence"], "website": ""},
    {"id": 54, "name": "Dr. Mahesh Mittal", "location": "Modinagar", "hospital": "KN Modi Complex, PNB ke paas, Modinagar", "experience_years": 12, "specialty": "General Medicine", "estimated_reviews": 30, "estimated_rating": 4.0, "strengths": ["Regular OPD timings"], "website": ""},
    {"id": 55, "name": "Aarogyam Heart & General Hospital", "location": "Modinagar", "hospital": "Bisokhar, Modinagar", "experience_years": 10, "specialty": "Heart & General Medicine", "estimated_reviews": 40, "estimated_rating": 4.1, "strengths": ["Hospital setup", "Emergency services"], "website": ""},
    # ═══ GHAZIABAD COMPETITORS ═══
    {"id": 56, "name": "Dr. Praveen Kumar Agrawal", "location": "Ghaziabad", "hospital": "Sarvodaya Hospital, Kavi Nagar Industrial Area, Ghaziabad", "experience_years": 20, "specialty": "Cardiology", "estimated_reviews": 120, "estimated_rating": 4.5, "strengths": ["Sarvodaya Hospital brand", "Advanced cardiac care"], "website": ""},
    {"id": 57, "name": "Dr. Ankul Gupta", "location": "Ghaziabad", "hospital": "Shastri Nagar, Ghaziabad", "experience_years": 12, "specialty": "Cardiology Consultation", "estimated_reviews": 70, "estimated_rating": 4.3, "strengths": ["Shastri Nagar location"], "website": ""},
    {"id": 58, "name": "Dr. Asit Khanna", "location": "Ghaziabad", "hospital": "Shastri Nagar, Ghaziabad", "experience_years": 15, "specialty": "Cardiology", "estimated_reviews": 65, "estimated_rating": 4.2, "strengths": ["Specialized cardiac consultation"], "website": ""},
    # ═══ HAPUR COMPETITORS ═══
    {"id": 59, "name": "Dr. Hariom Singh", "location": "Hapur", "hospital": "Patna Mor, Hapur", "experience_years": 10, "specialty": "General Medicine", "estimated_reviews": 30, "estimated_rating": 4.0, "strengths": ["24/7 availability", "Local support"], "website": ""},
    {"id": 60, "name": "Dr. Anuj Mudgal", "location": "Hapur", "hospital": "Avas Vikas Railway Station Road, Sanjay Vihar, Hapur", "experience_years": 8, "specialty": "General Medicine", "estimated_reviews": 35, "estimated_rating": 4.1, "strengths": ["High patient satisfaction"], "website": ""},
    {"id": 61, "name": "DEV NANDINI HOSPITAL", "location": "Hapur", "hospital": "Morepura, Navjyoti Colony, Hapur", "experience_years": 15, "specialty": "Multi-Speciality", "estimated_reviews": 80, "estimated_rating": 4.2, "strengths": ["Hospital setup", "Emergency services", "Multi-facility"], "website": ""},
    {"id": 62, "name": "Atmos Hospital", "location": "Hapur", "hospital": "Meerut Road, near JD School, Sanjay Colony, Hapur", "experience_years": 12, "specialty": "Multi-Speciality Emergency", "estimated_reviews": 70, "estimated_rating": 4.2, "strengths": ["Emergency hub", "Multi-speciality", "Critical care"], "website": ""},
]

TARGET_LOCATIONS = ["Meerut", "Delhi NCR", "Modinagar", "Hapur", "Ghaziabad", "Mohiuddinpur", "Partapur", "Shastri Nagar"]

SHARED_KEYWORDS = [
    # ── Meerut High-Volume Keywords ──
    "Cardiologist Meerut", "Heart Doctor Meerut", "Cardiac Physician Meerut",
    "Best Heart Doctor Meerut", "Top Cardiologist Meerut", "Heart Specialist Meerut",
    "BP Specialist Meerut", "Chest Pain Doctor Meerut", "Heart Clinic Meerut",
    "Heart Checkup Meerut", "Cardiology Doctor Meerut",
    "Heart Doctor Near Me Meerut", "Affordable Cardiologist Meerut",
    # ── Modinagar Keywords ──
    "Heart Doctor Modinagar", "Cardiologist Modinagar", "Cardiac Physician Modinagar",
    "Chest Pain Doctor Modinagar", "Heart Clinic Near Modinagar",
    # ── Ghaziabad Keywords ──
    "Cardiologist Ghaziabad", "Heart Doctor Ghaziabad", "Cardiac Physician Ghaziabad",
    "Affordable Heart Doctor Ghaziabad", "Heart Clinic Near Ghaziabad",
    # ── Hapur Keywords ──
    "Heart Doctor Hapur", "Cardiologist Hapur", "Cardiac Physician Hapur",
    "Heart Clinic Near Hapur", "Chest Pain Doctor Hapur",
    # ── Local Area Keywords ──
    "Heart Clinic Mohiuddinpur", "Cardiac Physician Partapur",
    "Heart Doctor Meerut South", "Heart Doctor Shastri Nagar Meerut",
    "Heart Specialist Delhi NCR", "Affordable Cardiologist Delhi NCR",
    # ── Procedure/Test Keywords ──
    "ECG Test Meerut", "2D Echo Test Meerut", "TMT Test Meerut",
    "Heart Checkup Meerut", "Cardiac Care Meerut",
    # ── Condition Keywords ──
    "Heart Attack Treatment", "Heart Failure Specialist",
    "Cholesterol Doctor", "Diabetes Heart Specialist",
    "High BP Treatment Meerut", "Chest Pain Evaluation Meerut",
    # ── Generic Medicine Keywords ──
    "PM Jan Aushadhi Heart Doctor", "Generic Medicine Heart Doctor Meerut",
    "Affordable Heart Treatment Meerut", "Low Cost Cardiologist Meerut",
]

COMPETITOR_ANALYSIS_PROMPT = """You are a Local SEO Competitor Analyst.
Your job:
1. Analyze local competitor data
2. Do keyword gap analysis — keywords competitors rank for that you don't
3. Give actionable recommendations to improve rankings
4. Give suggestions in Indian healthcare market context
5. Practical, implementable advice — no theory

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
    response = call_llm(messages, provider="groq", model="llama-3.1-8b-instant")
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
