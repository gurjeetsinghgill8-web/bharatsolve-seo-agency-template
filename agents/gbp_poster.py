"""
BHARATSOLVE SEO AGENCY — GBP Weekly Heart Health Tips Auto-Poster
Auto-posts cardiology tips to Google Business Profile every week.
Helps beat competitors who post 3x more on GBP.
"""
import random
import time
from datetime import datetime
from typing import Dict, List, Optional

from utils.llm_client import call_llm
from db.operations import log_agent_action

# ═══════════════════════════════════════════════════════════════════════
# READY-MADE HEART HEALTH TIPS (40+ tips — works without AI)
# ═══════════════════════════════════════════════════════════════════════

HEART_TIPS_HINDI = [
    "❤️ दिल को स्वस्थ रखने के लिए रोज़ 30 मिनट वॉक करें। brisk walking आपके heart muscles को strong बनाती है। #HeartHealth #GillHeartClinic",
    "🧂 नमक कम करें! High BP patients को रोज़ 5gm से कम नमक लेना चाहिए। packaged food में hidden salt होता है — label ज़रूर पढ़ें। #BPControl #Meerut",
    "🩺 साल में एक बार heart checkup ज़रूर कराएं — ECG, BP, Sugar, Cholesterol. Prevention is better than cure! Book appointment: 9639011155",
    "🥗 दिल के मरीज़ों के लिए best diet: हरी सब्ज़ियाँ, fruits, whole grains, nuts. तली-भुनी चीज़ें avoid करें। आपका दिल आपको thank you बोलेगा!",
    "😰 Stress आपके दिल का दुश्मन है! daily 10 min meditation या deep breathing करें। BP control में रहेगा और heart attack का risk कम होगा।",
    "🚭 सिगरेट और तंबाकू छोड़ें! smoking से heart attack का risk 2-4 गुना बढ़ जाता है। quitting के 1 साल बाद ही risk आधा हो जाता है।",
    "💊 BP की दवा time पर लें — doctor ने जैसा बताया है। खुद से दवा बंद न करें। irregular medicine stroke का कारण बन सकती है।",
    "🍎 एक apple रोज़ खाएं — fiber, antioxidants, और pectin से cholesterol कम होता है। सस्ता और असरदार heart care!",
    "⚖️ मोटापा दिल का दुश्मन #1 है। BMI 25 से नीचे रखें। हर 1 kg weight loss से BP 1 point कम होता है।",
    "🧘‍♂️ Yoga आपके दिल के लिए वरदान है! Anulom Vilom, Bhramari, और Shavasana — रोज़ 15 मिनट करें। BP control और stress relief दोनों।",
    "🌙 7-8 घंटे की नींद ज़रूर लें। sleep deprivation से BP बढ़ता है और heart attack का risk 48% तक बढ़ जाता है।",
    "🥤 Cold drinks और packaged juices छोड़ें — इनमें hidden sugar होता है जो diabetes और heart disease का कारण बनता है।",
    "🏥 सीने में दर्द हो तो ignore न करें! तुरंत cardiologist से consult करें। हर मिनट कीमती है। आपातकाल में कॉल करें: 9639011155",
    "🐟 हफ्ते में 2 बार fish खाएं — omega-3 fatty acids आपके दिल की arteries को clean रखते हैं। vegetarian हैं तो flaxseeds और walnuts खाएं।",
    "💧 रोज़ 8-10 glass पानी पिएं। dehydration से blood thick होता है जिससे heart पर extra pressure पड़ता है।",
    "🍌 Potassium-rich foods खाएं — केला, पालक, शकरकंद, नारियल पानी। potassium BP control करने में मदद करता है।",
    "❌ Trans fats से दूर रहें — बेकरी items, margarine, fried fast food. ये LDL (bad cholesterol) बढ़ाते हैं और HDL (good cholesterol) घटाते हैं।",
    "📱 अपने phone में BP reading, sugar level, और weight का record रखें। doctor को दिखाने में आसानी होगी।",
    "🌿 लहसुन रोज़ खाएं — 1-2 raw garlic cloves या garlic supplement. natural blood thinner और BP reducer है।",
    "🏃‍♂️ High intensity exercise से पहले warm-up और बाद में cool-down ज़रूर करें। अचानक exercise बंद करने से heart rhythm disturb हो सकता है।",
    "🫒 Cooking oil smartly choose करें — mustard oil, olive oil, rice bran oil. एक ही oil बार-बार गरम न करें।",
    "🍵 Green tea पिएं — day में 2-3 cup। antioxidants से arteries healthy रहती हैं और BP control में मदद मिलती है।",
    "🧬 Family history है heart disease की? तो 30 की उम्र से ही regular checkup शुरू कर दें। prevention आपका सबसे बड़ा हथियार है।",
    "🥜 रोज़ मुट्ठी भर nuts खाएं — almonds, walnuts, pistachios। healthy fats, protein, और fiber — तीनों का perfect combo!",
    "📉 LDL cholesterol 100 से नीचे रखें, HDL 40 (men) / 50 (women) से ऊपर। diet + exercise + medicine — तीनों ज़रूरी हैं।",
    "❤️‍🩹 Heart attack के warning signs: सीने में दबाव, बाएं हाथ/जबड़े में दर्द, सांस फूलना, पसीना आना, उल्टी जैसा लगना। तुरंत hospital जाएं!",
    "🚶‍♀️ Lift की जगह सीढ़ियाँ use करें। day में बस 10 मिनट stair climbing आपके heart health को 20% improve कर सकती है।",
    "🧑‍⚕️ डॉक्टर से खुलकर बात करें — अपनी सारी symptoms, diet, lifestyle habits share करें। सही जानकारी से ही सही इलाज होगा।",
    "☀️ Vitamin D की कमी heart disease से जुड़ी है। रोज़ 15-20 मिनट धूप में बैठें (सुबह 8-10 बजे)। supplement भी ले सकते हैं।",
    "📅 अपना BP check-up schedule fix करें — week में एक बार same time पर। morning BP सबसे accurate होता है।",
]

HEART_TIPS_ENGLISH = [
    "❤️ Walk 30 min daily — brisk walking strengthens your heart muscles. Your heart will thank you! #HeartHealth #GillHeartClinic",
    "🧂 Cut salt! High BP patients should limit salt to <5g/day. Hidden salt in packaged foods — always read labels! #BPControl",
    "🩺 Annual heart checkup is a MUST — ECG, BP, Sugar, Cholesterol. Prevention beats cure! Book: 9639011155",
    "🥗 Best diet for heart: green veggies, fruits, whole grains, nuts. Avoid fried foods. Your heart deserves the best!",
    "😰 Stress kills your heart! Just 10 min daily meditation or deep breathing keeps BP in check and reduces heart attack risk.",
    "🚭 Quit smoking today! Heart attack risk drops by 50% within 1 year of quitting. Your lungs AND heart will heal.",
    "💊 Never skip BP medicine! Take exactly as prescribed. Irregular medication is a leading cause of stroke.",
    "🍎 An apple a day really works! Fiber + antioxidants fight cholesterol. The cheapest heart medicine you'll ever find!",
    "⚖️ Obesity = Enemy #1 for your heart. Keep BMI under 25. Every 1 kg lost = 1 point BP reduction.",
    "🧘‍♂️ Yoga is magic for your heart — Anulom Vilom, Bhramari, Shavasana. 15 min daily for BP + stress control.",
    "🌙 Get 7-8 hours of sleep! Sleep deprivation raises BP and increases heart attack risk by 48%.",
    "🥤 Ditch cold drinks — hidden sugars lead to diabetes and heart disease. Choose water, coconut water, or buttermilk instead.",
    "🏥 Chest pain? DON'T IGNORE! Consult a cardiologist immediately. Every minute counts. Emergency: 9639011155",
    "🐟 Eat fish twice a week — omega-3 keeps arteries clean. Vegetarian? Try flaxseeds and walnuts!",
    "💧 Drink 8-10 glasses of water daily. Dehydration thickens blood = extra load on your heart.",
]


# ═══════════════════════════════════════════════════════════════════════
# GBP POSTING
# ═══════════════════════════════════════════════════════════════════════

def get_random_heart_tip(language: str = "hinglish") -> str:
    """Get a random pre-written heart health tip."""
    if language == "hindi":
        return random.choice(HEART_TIPS_HINDI)
    else:
        return random.choice(HEART_TIPS_ENGLISH + HEART_TIPS_HINDI)


def generate_ai_heart_tip() -> str:
    """Generate a fresh heart health tip using AI (Groq)."""
    try:
        prompt = """Generate ONE short, engaging heart health tip for Google Business Profile post.

Requirements:
- Must be in Hinglish (Hindi + English mix, natural Indian style)
- 2-4 sentences max
- Include 1 relevant emoji
- End with 2-3 relevant hashtags (e.g., #HeartHealth #Meerut)
- Must be patient-friendly and actionable
- Topic: Random heart health advice (diet, exercise, warning signs, checkup reminder, lifestyle, BP, cholesterol, diabetes, stress, etc.)

Reply with JUST the tip text, nothing else. No intro, no explanation."""

        messages = [
            {"role": "system", "content": "You are a cardiologist's social media assistant. Generate one short Hinglish heart health tip for Google Business Profile."},
            {"role": "user", "content": prompt}
        ]
        tip = call_llm(messages, provider="groq", model="llama-3.1-8b-instant", temperature=0.9)
        return tip.strip().strip('"')
    except:
        return get_random_heart_tip()


def post_to_gbp(content: str) -> Dict:
    """
    Post content to Google Business Profile.
    Returns success/error dict.
    """
    try:
        from utils.social_connectors import post_to_platform
        result = post_to_platform("google_business", content)
        if result.get("success"):
            log_agent_action("gbp_poster", f"GBP tip posted: {content[:60]}...")
            return {"success": True, "message": "Posted to GBP"}
        else:
            error = result.get("error", "Unknown GBP error")
            log_agent_action("gbp_poster", f"GBP post failed: {error}", 
                           status="error", error_message=error)
            return {"success": False, "error": error}
    except Exception as e:
        log_agent_action("gbp_poster", f"GBP post exception: {e}", 
                       status="error", error_message=str(e))
        return {"success": False, "error": str(e)}


def post_weekly_heart_tip(use_ai: bool = True) -> Dict:
    """
    Post a weekly heart health tip to Google Business Profile.
    Uses AI-generated tip if available, falls back to pre-written tips.
    """
    if use_ai:
        try:
            tip = generate_ai_heart_tip()
        except:
            tip = get_random_heart_tip()
    else:
        tip = get_random_heart_tip()
    
    # Ensure tip isn't too long (GBP has limits)
    if len(tip) > 1500:
        tip = tip[:1497] + "..."
    
    result = post_to_gbp(tip)
    result["tip"] = tip[:100]
    result["posted_at"] = datetime.now().isoformat()
    
    return result


def post_multiple_tips(count: int = 3) -> List[Dict]:
    """Post multiple heart tips (for initial setup or catching up)."""
    results = []
    used_tips = set()
    
    for i in range(count):
        tip = get_random_heart_tip()
        while tip in used_tips:  # Avoid duplicates
            tip = get_random_heart_tip()
        used_tips.add(tip)
        
        result = post_to_gbp(tip)
        result["tip"] = tip[:100]
        results.append(result)
        
        if i < count - 1:
            time.sleep(2)  # Rate limiting
    
    return results


# ═══════════════════════════════════════════════════════════════════════
# SCHEDULER TASK
# ═══════════════════════════════════════════════════════════════════════

def gbp_weekly_tip_task():
    """
    Scheduled task: Post a heart health tip to GBP every week.
    Called by the scheduler every 7 days.
    """
    print("📱 GBP Weekly Tip: Posting heart health tip...")
    result = post_weekly_heart_tip(use_ai=True)
    
    if result.get("success"):
        print(f"✅ GBP Tip posted: {result.get('tip', '')[:80]}")
    else:
        print(f"❌ GBP Tip failed: {result.get('error', '')}")
    
    return result
