"""
BHARATSOLVE SEO AGENCY — Local Search Intent Auto-Engine
Auto-detects what Meerut/Delhi NCR people search for and creates targeted content.
50+ high-intent local search queries → auto-blogs → auto-rank → patient conversion.

"Jab log Meerut mein heart doctor search karein, 
hamari website automatically unke saamne aaye"
"""
import json
import random
from datetime import datetime
from typing import List, Dict


# ═══════════════════════════════════════════════════════════════════════
# 50+ HIGH-INTENT LOCAL SEARCH QUERIES
# What people in Meerut/Delhi NCR ACTUALLY search for
# ═══════════════════════════════════════════════════════════════════════

LOCAL_SEARCH_QUERIES = {
    # ── Direct Doctor Searches (Highest Intent → Book Appointment) ──
    "direct_doctor": [
        {"query": "heart doctor near me", "intent": "book_appointment", "volume": "high", "conversion": "very_high"},
        {"query": "Cardiac Physician in Meerut", "intent": "book_appointment", "volume": "high", "conversion": "very_high"},
        {"query": "experienced heart doctor Meerut", "intent": "book_appointment", "volume": "high", "conversion": "very_high"},
        {"query": "heart specialist near Mohiuddinpur", "intent": "book_appointment", "volume": "medium", "conversion": "high"},
        {"query": "heart doctor near me open now", "intent": "emergency", "volume": "medium", "conversion": "very_high"},
        {"query": "Dr. Gurjeet Singh Gill Cardiac Physician", "intent": "brand_search", "volume": "medium", "conversion": "very_high"},
        {"query": "Gill Heart Clinic Meerut appointment", "intent": "book_appointment", "volume": "low", "conversion": "very_high"},
        {"query": "heart doctor Meerut", "intent": "book_appointment", "volume": "medium", "conversion": "high"},
        {"query": "child heart doctor Meerut", "intent": "book_appointment", "volume": "medium", "conversion": "high"},
        {"query": "heart doctor Delhi NCR", "intent": "book_appointment", "volume": "high", "conversion": "high"},
    ],
    
    # ── Symptom Searches (Mid Intent → Need Diagnosis) ──
    "symptoms": [
        {"query": "chest pain causes in Hindi", "intent": "information", "volume": "very_high", "conversion": "high"},
        {"query": "सीने में दर्द का कारण और इलाज", "intent": "information", "volume": "very_high", "conversion": "high"},
        {"query": "left side chest pain reason", "intent": "information", "volume": "high", "conversion": "high"},
        {"query": "heart attack ke lakshan", "intent": "information", "volume": "very_high", "conversion": "high"},
        {"query": "heart attack symptoms in women over 50", "intent": "information", "volume": "high", "conversion": "medium"},
        {"query": "सांस फूलने का कारण heart", "intent": "information", "volume": "high", "conversion": "high"},
        {"query": "palpitations after eating", "intent": "information", "volume": "medium", "conversion": "medium"},
        {"query": "sharp pain in chest while breathing", "intent": "information", "volume": "high", "conversion": "high"},
        {"query": "chest pain vs gas pain difference", "intent": "information", "volume": "high", "conversion": "medium"},
        {"query": "anxiety or heart attack how to tell", "intent": "information", "volume": "high", "conversion": "medium"},
    ],
    
    # ── Test/Procedure Searches (Mid Intent → Need Tests) ──
    "tests_procedures": [
        {"query": "ECG test near me Meerut", "intent": "book_test", "volume": "high", "conversion": "high"},
        {"query": "2D Echo test price Meerut", "intent": "price_check", "volume": "high", "conversion": "high"},
        {"query": "TMT test cost in Meerut", "intent": "price_check", "volume": "medium", "conversion": "high"},
        {"query": "angiography cost in Meerut", "intent": "price_check", "volume": "medium", "conversion": "medium"},
        {"query": "ECG report normal reading", "intent": "information", "volume": "high", "conversion": "low"},
        {"query": "2D echo vs ECG difference", "intent": "information", "volume": "medium", "conversion": "medium"},
        {"query": "heart checkup package Meerut", "intent": "price_check", "volume": "medium", "conversion": "high"},
        {"query": "full body checkup with heart test Meerut", "intent": "price_check", "volume": "medium", "conversion": "medium"},
        {"query": "lipid profile test near me", "intent": "book_test", "volume": "medium", "conversion": "low"},
        {"query": "blood test for heart blockage", "intent": "information", "volume": "medium", "conversion": "medium"},
    ],
    
    # ── Condition/Disease Searches (Education → Book Later) ──
    "conditions": [
        {"query": "high BP treatment in Hindi", "intent": "information", "volume": "very_high", "conversion": "medium"},
        {"query": "बीपी कंट्रोल कैसे करें", "intent": "information", "volume": "very_high", "conversion": "medium"},
        {"query": "cholesterol kam karne ke upay", "intent": "information", "volume": "high", "conversion": "medium"},
        {"query": "diabetes and heart disease connection", "intent": "information", "volume": "high", "conversion": "medium"},
        {"query": "heart failure life expectancy in Hindi", "intent": "information", "volume": "medium", "conversion": "medium"},
        {"query": "heart blockage treatment without surgery", "intent": "information", "volume": "high", "conversion": "high"},
        {"query": "angioplasty vs bypass which is better", "intent": "information", "volume": "high", "conversion": "medium"},
        {"query": "stent daalne ke baad kya karein", "intent": "information", "volume": "medium", "conversion": "medium"},
        {"query": "pacemaker life in Hindi", "intent": "information", "volume": "low", "conversion": "low"},
        {"query": "hole in heart treatment for adults", "intent": "information", "volume": "medium", "conversion": "medium"},
    ],
    
    # ── Lifestyle/Diet Searches (Education → Long-term Patient) ──
    "lifestyle": [
        {"query": "heart healthy diet plan Indian", "intent": "information", "volume": "very_high", "conversion": "low"},
        {"query": "दिल के मरीज का खाना", "intent": "information", "volume": "high", "conversion": "medium"},
        {"query": "best exercise for heart patients", "intent": "information", "volume": "high", "conversion": "low"},
        {"query": "yoga for heart health in Hindi", "intent": "information", "volume": "high", "conversion": "low"},
        {"query": "walking benefits for heart patients", "intent": "information", "volume": "medium", "conversion": "low"},
        {"query": "foods to avoid in high BP", "intent": "information", "volume": "high", "conversion": "medium"},
        {"query": "heart patient diet chart Indian veg", "intent": "information", "volume": "high", "conversion": "medium"},
        {"query": "can heart patient drink tea coffee", "intent": "information", "volume": "medium", "conversion": "low"},
        {"query": "heart patient fruits list", "intent": "information", "volume": "medium", "conversion": "low"},
        {"query": "ज्यादा पानी पीने से heart पर असर", "intent": "information", "volume": "medium", "conversion": "low"},
    ],
    
    # ── Emergency/Local Searches (HIGHEST Intent → IMMEDIATE) ──
    "emergency_local": [
        {"query": "heart doctor emergency Meerut", "intent": "emergency", "volume": "medium", "conversion": "very_high"},
        {"query": "cardiologist open on Sunday Meerut", "intent": "emergency", "volume": "low", "conversion": "very_high"},
        {"query": "heart clinic near me open now", "intent": "emergency", "volume": "medium", "conversion": "very_high"},
        {"query": "chest pain doctor near me 24 hours", "intent": "emergency", "volume": "medium", "conversion": "very_high"},
        {"query": "heart attack emergency number Meerut", "intent": "emergency", "volume": "low", "conversion": "very_high"},
        {"query": "ECG at home Meerut", "intent": "book_service", "volume": "medium", "conversion": "high"},
        {"query": "cardiologist home visit Meerut", "intent": "book_service", "volume": "low", "conversion": "very_high"},
        {"query": "heart checkup at home near me", "intent": "book_service", "volume": "medium", "conversion": "high"},
        {"query": "BP check near me free", "intent": "walk_in", "volume": "medium", "conversion": "high"},
        {"query": "heart camp in Meerut today", "intent": "event", "volume": "low", "conversion": "high"},
    ],
}


# ═══════════════════════════════════════════════════════════════════════
# INTENT-TO-ACTION MAPPING
# What to create when someone searches each intent type
# ═══════════════════════════════════════════════════════════════════════

INTENT_ACTION_MAP = {
    "book_appointment": {
        "action": "Show 'Book Appointment' CTA prominently + phone number",
        "content_type": "service_page",
        "urgency": "high",
    },
    "emergency": {
        "action": "Show EMERGENCY banner + phone number BIG + 'Walk-in Welcome'",
        "content_type": "landing_page",
        "urgency": "critical",
    },
    "information": {
        "action": "Show informative blog with 'Consult Our Cardiologist' CTA at end",
        "content_type": "blog",
        "urgency": "medium",
    },
    "price_check": {
        "action": "Show test/procedure page with price range + 'Book Test' button",
        "content_type": "service_page",
        "urgency": "high",
    },
    "book_test": {
        "action": "Show test info + 'Book ECG/Echo/TMT Now' button",
        "content_type": "service_page",
        "urgency": "high",
    },
    "brand_search": {
        "action": "Show clinic homepage with doctor profile + reviews",
        "content_type": "homepage",
        "urgency": "low",
    },
    "walk_in": {
        "action": "Show clinic address, timing, map + 'Visit Us' CTA",
        "content_type": "location_page",
        "urgency": "medium",
    },
    "book_service": {
        "action": "Show service info + 'Request Home Visit' form",
        "content_type": "service_page",
        "urgency": "high",
    },
    "event": {
        "action": "Show event details + registration form",
        "content_type": "event_page",
        "urgency": "medium",
    },
}


# ═══════════════════════════════════════════════════════════════════════
# AUTO-CONTENT PLAN GENERATOR
# ═══════════════════════════════════════════════════════════════════════

def generate_content_plan() -> Dict:
    """
    Generate a prioritized content plan based on local search queries.
    Returns prioritized list of what to create & publish.
    """
    plan = {
        "generated_at": datetime.now().isoformat(),
        "total_queries": 0,
        "priority_1_critical": [],   # Emergency + Book Appointment = IMMEDIATE
        "priority_2_high": [],        # Tests + Price + Symptoms = HIGH
        "priority_3_medium": [],      # Conditions + Diseases = MEDIUM
        "priority_4_nurture": [],     # Lifestyle + Diet = LONG-TERM
        "estimated_patients": 0,
    }
    
    for category, queries in LOCAL_SEARCH_QUERIES.items():
        for q in queries:
            plan["total_queries"] += 1
            entry = {
                "query": q["query"],
                "category": category,
                "intent": q["intent"],
                "volume": q["volume"],
                "conversion_potential": q["conversion"],
                "recommended_action": INTENT_ACTION_MAP.get(q["intent"], {}).get("action", "Create blog"),
                "content_type": INTENT_ACTION_MAP.get(q["intent"], {}).get("content_type", "blog"),
                "urgency": INTENT_ACTION_MAP.get(q["intent"], {}).get("urgency", "medium"),
            }
            
            if q["conversion"] == "very_high" or q["intent"] in ["emergency", "book_appointment"]:
                plan["priority_1_critical"].append(entry)
                plan["estimated_patients"] += 3  # High conversion queries
            elif q["conversion"] == "high":
                plan["priority_2_high"].append(entry)
                plan["estimated_patients"] += 1
            elif q["volume"] == "very_high":
                plan["priority_3_medium"].append(entry)
            else:
                plan["priority_4_nurture"].append(entry)
    
    return plan


def get_top_converting_queries(limit: int = 10) -> List[Dict]:
    """Get the highest-converting local search queries."""
    all_queries = []
    for category, queries in LOCAL_SEARCH_QUERIES.items():
        for q in queries:
            all_queries.append(q)
    
    # Sort by conversion potential (very_high > high > medium > low)
    conversion_order = {"very_high": 4, "high": 3, "medium": 2, "low": 1}
    all_queries.sort(key=lambda x: conversion_order.get(x["conversion"], 0), reverse=True)
    
    return all_queries[:limit]


def get_weekly_target_queries() -> List[Dict]:
    """Get 7 queries to target this week (1 per day)."""
    top = get_top_converting_queries(20)
    # Pick a diverse set: 3 emergency/book, 2 symptoms, 1 test, 1 condition
    selected = []
    categories_used = set()
    
    for q in top:
        cat = q.get("intent", "other")
        if cat not in categories_used or len(selected) < 7:
            selected.append(q)
            categories_used.add(cat)
        if len(selected) >= 7:
            break
    
    return selected
