# D:\demo_project\FITMITRA\backend\ai\services\gemini.py
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION ====================
# Default model for speed - Gemini-1.5-Flash is extremely fast
DEFAULT_MODEL = 'models/gemini-1.5-flash'

def get_available_model(api_key):
    """
    Directly return the fastest model to avoid network overhead of listing models.
    """
    return DEFAULT_MODEL

# ==================== QUERY CLASSIFICATION ====================
def classify_query_intent(user_message):
    """Advanced query intent detection"""
    message_lower = user_message.lower()
    
    # Language detection
    is_hindi = bool(re.search(r'[\u0900-\u097F]', user_message))
    
    # Intent patterns
    patterns = {
        'workout_plan': [
            r'gym.*plan', r'workout.*plan', r'exercise.*plan', r'रूटीन',
            r'दिन.*क्या.*करूं', r'monday.*saturday', r'weekly.*schedule',
            r'सप्ताह.*योजना', r'किस.*दिन.*क्या', r'plan.*batao'
        ],
        'exercise_technique': [
            r'how.*to', r'कैसे.*करें', r'tips', r'technique', r'form',
            r'सही.*तरीका', r'proper.*way', r'correct.*form'
        ],
        'nutrition_plan': [
            r'diet', r'खाना', r'आहार', r'nutrition', r'meal',
            r'क्या.*खाएं', r'what.*to.*eat', r'डाइट', r'breakfast',
            r'सुबह.*क्या.*खाएं'
        ],
        'specific_exercise': [
            r'pushup', r'pullup', r'squat', r'chest', r'back',
            r'पुशअप', r'पुलअप', r'स्क्वाट', r'छाती', r'पीठ'
        ],
        'home_workout': [
            r'home.*workout', r'without.*equipment', r'घर.*पर',
            r'बिना.*उपकरण', r'bodyweight'
        ]
    }
    
    # Check patterns
    for intent, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return {
                    'intent': intent,
                    'language': 'hindi' if is_hindi else 'english'
                }
    
    return {'intent': 'general', 'language': 'hindi' if is_hindi else 'english'}

# ==================== STRUCTURED RESPONSES ====================
def get_workout_plan_response(user_message, user_goal, language):
    """Professional gym plan response"""
    goal_display = user_goal.replace('_', ' ').title()
    
    if language == 'hindi':
        return f"""🏋️‍♂️ **व्यायाम योजना - {goal_display} के लिए**

आपकी क्वेरी: "{user_message}"

✅ **सोमवार से शनिवार पेशेवर जिम प्रोग्राम:**

**सोमवार: छाती + ट्राइसेप्स**
• बेंच प्रेस: 4 सेट (8-12 रेप्स)
• इंक्लाइन डंबल प्रेस: 3 सेट (10-15 रेप्स)
• केबल फ्लाई: 3 सेट (12-15 रेप्स)
• ट्राइसेप्स पुशडाउन: 4 सेट (10-15 रेप्स)
• ओवरहेड ट्राइसेप्स: 3 सेट (12-15 रेप्स)
⏰ समय: 60 मिनट

**मंगलवार: पीठ + बाइसेप्स**
• डेडलिफ्ट: 4 सेट (6-8 रेप्स)
• लैट पुलडाउन: 3 सेट (10-12 रेप्स)
• बेंट ओवर रो: 3 सेट (8-12 रेप्स)
• बारबेल कर्ल: 4 सेट (8-12 रेप्स)
• हैमर कर्ल: 3 सेट (10-15 रेप्स)
⏰ समय: 60 मिनट

**बुधवार: पैर + कंधे**
• स्क्वाट: 4 सेट (8-10 रेप्स)
• लेग प्रेस: 3 सेट (12-15 रेप्स)
• लेग एक्सटेंशन: 3 सेट (15-20 रेप्स)
• ओवरहेड प्रेस: 4 सेट (8-12 रेप्स)
• लेटरल रेज: 3 सेट (12-15 रेप्स)
⏰ समय: 60 मिनट

**गुरुवार: कार्डियो + कोर**
• ट्रेडमिल: 30 मिनट
• साइकिल: 20 मिनट
• प्लैंक: 3 सेट (60 सेकंड)
• रशियन ट्विस्ट: 3 सेट (15-20 रेप्स)
• लेग रेज: 3 सेट (15-20 रेप्स)
⏰ समय: 60 मिनट

**शुक्रवार: ऊपरी शरीर**
• पुश-अप: 4 सेट (अधिकतम)
• पुल-अप: 4 सेट (अधिकतम)
• डिप्स: 3 सेट (अधिकतम)
• प्लैंक: 3 सेट (60 सेकंड)
• साइड प्लैंक: 3 सेट (30 सेकंड प्रति तरफ)
⏰ समय: 45 मिनट

**शनिवार: एक्टिव रिकवरी**
• हल्की स्ट्रेचिंग: 20 मिनट
• योग: 30 मिनट
• वॉक: 30 मिनट
• फोम रोलिंग: 10 मिनट
⏰ समय: 90 मिनट

**रविवार: पूर्ण आराम**

📊 **{goal_display} के लिए विशेष सुझाव:**
1. वर्कआउट के बाद 20 मिनट कार्डियो
2. प्रोटीन: प्रति दिन 2g/kg शरीर के वजन
3. पानी: 3-4 लीटर प्रति दिन
4. नींद: 7-8 घंटे प्रति रात

💡 **प्रगति ट्रैकिंग:**
• साप्ताहिक वजन माप
• मासिक फोटो तुलना
• ताकत में वृद्धि रिकॉर्ड
• ऊर्जा स्तर नोट करें

किस विशेष व्यायाम के बारे में और जानना चाहते हैं?"""
    else:
        return f"""🏋️‍♂️ **YOUR PERSONALIZED WORKOUT PLAN**

Great! I've created a customized weekly plan for your goal: **{goal_display}**

Your Query: "{user_message}"

---

**📅 WEEKLY TRAINING SCHEDULE:**

**Day 1: CHEST & TRICEPS**
Workout:
- Bench Press – 4x8-12 (Rest: 90s)
- Incline Dumbbell Press – 3x10-15 (Rest: 60s)
- Cable Fly – 3x12-15 (Rest: 60s)
- Triceps Pushdown – 4x10-15 (Rest: 45s)
- Overhead Triceps Extension – 3x12-15 (Rest: 45s)

**Tips:** Control the negative (lowering) phase. Focus on chest contraction. Keep core engaged.
⏰ Duration: 60 minutes

---

**Day 2: BACK & BICEPS**
Workout:
- Deadlift – 4x6-8 (Rest: 2-3 min)
- Lat Pulldown – 3x10-12 (Rest: 60s)
- Bent Over Row – 3x8-12 (Rest: 90s)
- Barbell Curl – 4x8-12 (Rest: 60s)
- Hammer Curl – 3x10-15 (Rest: 45s)

**Tips:** Keep spine neutral in deadlifts. Squeeze shoulder blades together. No swinging on curls.
⏰ Duration: 60 minutes

---

**Day 3: LEGS & SHOULDERS**
Workout:
- Squat – 4x8-10 (Rest: 2-3 min)
- Leg Press – 3x12-15 (Rest: 90s)
- Leg Extension – 3x15-20 (Rest: 60s)
- Overhead Press – 4x8-12 (Rest: 90s)
- Lateral Raise – 3x12-15 (Rest: 45s)

**Tips:** Squat depth matters! Full range of motion. Keep knees aligned with toes.
⏰ Duration: 60 minutes

---

**Day 4: CARDIO & CORE**
Workout:
- Treadmill Run – 30 min (Moderate pace)
- Stationary Bike – 20 min (HIIT intervals)
- Plank – 3x60s (Rest: 30s)
- Russian Twist – 3x15-20 each side (Rest: 30s)
- Leg Raises – 3x15-20 (Rest: 30s)

**Tips:** Stay hydrated! Core stability is key to all exercises. Breathe properly.
⏰ Duration: 60 minutes

---

**Day 5: UPPER BODY BURN**
Workout:
- Push-ups – 4 sets x max reps (Rest: 60s)
- Pull-ups – 4 sets x max reps (Rest: 90s)
- Dips – 3 sets x max reps (Rest: 60s)
- Plank – 3x60s (Rest: 30s)
- Side Plank – 3x30s each side (Rest: 30s)

**Tips:** Quality over quantity. Perfect form beats high reps. Progressive overload weekly.
⏰ Duration: 45 minutes

---

**Day 6: ACTIVE RECOVERY**
Workout:
- Light Stretching – 20 min
- Yoga Flow – 30 min
- Light Walk – 30 min
- Foam Rolling – 10 min

**Tips:** Recovery is when muscles grow. Listen to your body. Stay mobile and flexible.
⏰ Duration: 90 minutes

---

**Day 7: COMPLETE REST**
Your body needs this! Sleep well, eat clean, hydrate.

---

🎯 **SPECIAL TIPS FOR {goal_display.upper()}:**
1. **Post-Workout Cardio:** Add 20 min after strength training
2. **Protein Intake:** 2g/kg body weight daily
3. **Hydration:** 3-4 liters of water per day
4. **Sleep:** 7-8 hours every night for recovery

💡 **PROGRESS TRACKING:**
• Weekly weigh-in (same time, same day)
• Monthly progress photos
• Track strength increases (weight/reps)
• Monitor energy levels and recovery

⚠️ **IMPORTANT REMINDERS:**
- Always warm up for 5-10 minutes before training
- Cool down and stretch after every session
- If any exercise causes pain (not muscle burn), stop and modify
- Progressive overload: Increase weight/reps gradually

💪 **MOTIVATION:** Consistency beats perfection! Track your workouts, celebrate small wins, and remember: Every rep brings you closer to your goal.

Want details on proper form for any specific exercise? Just ask! 🔥"""

def get_technique_response(user_message, language):
    """Exercise technique response"""
    if language == 'hindi':
        return f"""💪 **व्यायाम तकनीक मार्गदर्शन**

आपकी क्वेरी: "{user_message}"

✅ **सही तकनीक के 5 सुनहरे नियम:**

1. **फॉर्म पर ध्यान दें**
   • धीमी और नियंत्रित गति
   • पूरी रेंज ऑफ मोशन
   • मांसपेशी-मन कनेक्शन

2. **सांस लेने का सही तरीका**
   • वजन उठाते समय सांस छोड़ें
   • वजन नीचे करते समय सांस लें
   • सांस रोककर न रखें

3. **वार्म-अप अनिवार्य**
   • 5-10 मिनट हल्का कार्डियो
   • डायनामिक स्ट्रेचिंग
   • 1-2 लाइट सेट

4. **कोर एक्टिवेट रखें**
   • पेट की मांसपेशियां टाइट
   • रीढ़ की हड्डी न्यूट्रल
   • श्रोणि सही स्थिति में

5. **प्रगतिशील ओवरलोड**
   • धीरे-धीरे वजन बढ़ाएं
   • रेप्स या सेट्स बढ़ाएं
   • आराम का समय कम करें

⚠️ **सामान्य गलतियां:**
• बहुत भारी वजन उठाना
• आधी रेंज में व्यायाम करना
• झटके से वजन उठाना
• पर्याप्त आराम न लेना

🎯 **विशिष्ट व्यायाम के लिए पूछें:**
"स्क्वाट की सही तकनीक"
"बेंच प्रेस में कंधे की सुरक्षा"
"डेडलिफ्ट में पीठ सीधी कैसे रखें"

मैं आपको वीडियो लिंक और विस्तृत मार्गदर्शन दूंगा! 📹"""
    else:
        return f"""💪 **EXERCISE TECHNIQUE GUIDE**

Your Query: "{user_message}"

✅ **5 GOLDEN RULES OF PROPER TECHNIQUE:**

1. **FOCUS ON FORM**
   • Slow and controlled movements
   • Full range of motion
   • Mind-muscle connection

2. **PROPER BREATHING**
   • Exhale during exertion (lifting)
   • Inhale during relaxation (lowering)
   • Never hold your breath

3. **WARM-UP IS MANDATORY**
   • 5-10 minutes light cardio
   • Dynamic stretching
   • 1-2 light sets

4. **KEEP CORE ENGAGED**
   • Abdominal muscles tight
   • Neutral spine position
   • Proper pelvic alignment

5. **PROGRESSIVE OVERLOAD**
   • Gradually increase weight
   • Increase reps or sets
   • Decrease rest time

⚠️ **COMMON MISTAKES:**
• Lifting too heavy
• Half-range movements
• Using momentum
• Insufficient rest

🎯 **ASK FOR SPECIFIC EXERCISES:**
"Proper squat technique"
"Shoulder safety in bench press"
"How to keep back straight in deadlift"

I'll provide video links and detailed guidance! 📹"""

def get_nutrition_response(user_goal, language):
    """Nutrition plan response"""
    goal_display = user_goal.replace('_', ' ').title()
    
    if language == 'hindi':
        return f"""🥗 **पोषण योजना - {goal_display} के लिए**

🎯 **लक्ष्य: {goal_display}**

✅ **दैनिक पोषण दिशानिर्देश:**

**प्रोटीन:**
• मात्रा: 1.6-2.2g प्रति kg शरीर के वजन
• स्रोत: चिकन, मछली, अंडे, दाल, पनीर
• समय: हर 3-4 घंटे में

**कार्बोहाइड्रेट:**
• मात्रा: 3-5g प्रति kg (गतिविधि के अनुसार)
• स्रोत: ब्राउन राइस, ओट्स, शकरकंद, फल
• समय: वर्कआउट से पहले और बाद में

**वसा:**
• मात्रा: कुल कैलोरी का 20-30%
• स्रोत: एवोकाडो, नट्स, ऑलिव ऑयल, घी
• समय: भोजन के साथ

**आदर्श दैनिक सारणी:**

🌅 **सुबह (सुबह 7-8 बजे):**
• 1 गिलास गुनगुना पानी + नींबू
• 1 कप ग्रीन टी
• मुट्ठी भर भीगे बादाम

🍳 **नाश्ता (सुबह 8-9 बजे):**
• 2 अंडे (उबले या ऑमलेट)
• 2 ब्राउन ब्रेड स्लाइस
• 1 कप दही या छाछ

🥪 **दोपहर का भोजन (दोपहर 1-2 बजे):**
• 1 कप ब्राउन राइस या 2 रोटी
• 1 कप दाल या राजमा
• 1 कप सब्जियां (हरी पत्तेदार)
• 1 कप सलाद

☕ **शाम का नाश्ता (शाम 4-5 बजे):**
• 1 कप ग्रीन टी
• 1 मुट्ठी मुरमुरे या भुना चना
• 1 फल (सेब, केला, संतरा)

🍲 **रात का भोजन (रात 8-9 बजे):**
• 1 कप सब्जियों का सूप
• 100-150g ग्रिल्ड चिकन या पनीर
• 1 कप सलाद

💧 **पानी:**
• कुल: 3-4 लीटर प्रतिदिन
• सुबह: 1 लीटर (धीरे-धीरे)
• वर्कआउट के दौरान: 500ml प्रति घंटा
• रात: सोने से 1 घंटे पहले 1 गिलास

🚫 **परहेज:**
• प्रोसेस्ड फूड
• शक्कर युक्त पेय
• अत्यधिक तला हुआ भोजन
• शराब और धूम्रपान

📊 **{goal_display} के लिए विशेष:**
• कैलोरी घाटा: 300-500 कैलोरी प्रतिदिन
• प्रोटीन प्राथमिकता: हर भोजन में
• कार्ब समय: वर्कआउट के आसपास
• फाइबर: 30-40g प्रतिदिन

विशिष्ट भोजन योजना या व्यंजनों के लिए पूछें! 🍽️"""
    else:
        return f"""🥗 **NUTRITION PLAN - FOR {goal_display.upper()}**

🎯 **GOAL: {goal_display}**

✅ **DAILY NUTRITION GUIDELINES:**

**PROTEIN:**
• Amount: 1.6-2.2g per kg body weight
• Sources: Chicken, fish, eggs, lentils, paneer
• Timing: Every 3-4 hours

**CARBOHYDRATES:**
• Amount: 3-5g per kg (based on activity)
• Sources: Brown rice, oats, sweet potato, fruits
• Timing: Around workouts

**FATS:**
• Amount: 20-30% of total calories
• Sources: Avocado, nuts, olive oil, ghee
• Timing: With meals

**IDEAL DAILY SCHEDULE:**

🌅 **MORNING (7-8 AM):**
• 1 glass warm water + lemon
• 1 cup green tea
• Handful of soaked almonds

🍳 **BREAKFAST (8-9 AM):**
• 2 eggs (boiled or omelette)
• 2 brown bread slices
• 1 cup yogurt or buttermilk

🥪 **LUNCH (1-2 PM):**
• 1 cup brown rice or 2 rotis
• 1 cup dal or kidney beans
• 1 cup vegetables (leafy greens)
• 1 cup salad

☕ **EVENING SNACK (4-5 PM):**
• 1 cup green tea
• Handful of puffed rice or roasted chickpeas
• 1 fruit (apple, banana, orange)

🍲 **DINNER (8-9 PM):**
• 1 cup vegetable soup
• 100-150g grilled chicken or paneer
• 1 cup salad

💧 **WATER:**
• Total: 3-4 liters daily
• Morning: 1 liter (gradually)
• During workout: 500ml per hour
• Night: 1 glass 1 hour before sleep

🚫 **AVOID:**
• Processed foods
• Sugary drinks
• Excessive fried food
• Alcohol and smoking

📊 **SPECIAL FOR {goal_display.upper()}:**
• Calorie deficit: 300-500 calories daily
• Protein priority: In every meal
• Carb timing: Around workouts
• Fiber: 30-40g daily

Ask for specific meal plans or recipes! 🍽️"""

def get_home_workout_response(user_message, language):
    """Home workout without equipment"""
    if language == 'hindi':
        return f"""🏠 **बिना उपकरण घर पर वर्कआउट**

आपकी क्वेरी: "{user_message}"

✅ **पूर्ण शरीर घर वर्कआउट:**

**वार्म-अप (10 मिनट):**
• जगह पर दौड़ना: 3 मिनट
• जंपिंग जैक: 1 मिनट
• हाई नी: 1 मिनट
• डायनामिक स्ट्रेच: 5 मिनट

**मुख्य वर्कआउट (सर्किट शैली):**

🔁 **सर्किट 1: छाती और ट्राइसेप्स**
1. पुश-अप: 3 सेट (अधिकतम रेप्स)
2. डायमंड पुश-अप: 3 सेट (10-15 रेप्स)
3. ट्राइसेप्स डिप्स (कुर्सी पर): 3 सेट (10-15 रेप्स)
4. प्लैंक टैप: 3 सेट (10 प्रति तरफ)

⏱️ आराम: सेट के बीच 30 सेकंड, सर्किट के बीच 60 सेकंड

🔁 **सर्किट 2: पीठ और बाइसेप्स**
1. पुल-अप (अगर बार उपलब्ध हो): 3 सेट (अधिकतम)
2. सुपरमैन: 3 सेट (15-20 रेप्स)
3. इनवर्टेड रो (टेबल के नीचे): 3 सेट (10-12 रेप्स)
4. बाइसेप्स कर्ल (बैग या बोतल से): 3 सेट (15-20 रेप्स)

⏱️ आराम: सेट के बीच 30 सेकंड

🔁 **सर्किट 3: पैर और कंधे**
1. स्क्वाट: 4 सेट (15-20 रेप्स)
2. लंग्स: 3 सेट (10 प्रति पैर)
3. कैल्फ रेज: 3 सेट (20-25 रेप्स)
4. पाइक पुश-अप: 3 सेट (10-12 रेप्स)
5. साइड प्लैंक: 3 सेट (30 सेकंड प्रति तरफ)

⏱️ आराम: सेट के बीच 45 सेकंड

🔁 **सर्किट 4: कोर**
1. प्लैंक: 3 सेट (60-90 सेकंड)
2. रशियन ट्विस्ट: 3 सेट (20 प्रति तरफ)
3. लेग रेज: 3 सेट (15-20 रेप्स)
4. माउंटेन क्लाइम्बर: 3 सेट (30 सेकंड)
5. बाइसाइकिल क्रंच: 3 सेट (20 प्रति तरफ)

⏰ **कुल समय:** 45-60 मिनट

**कूल-डाउन (10 मिनट):**
• हल्की स्ट्रेचिंग
• डीप ब्रीदिंग
• फोम रोलिंग (यदि उपलब्ध हो)

📅 **साप्ताहिक अनुसूची:**
• सोमवार: पूर्ण शरीर (ऊपर दिया गया)
• मंगलवार: कार्डियो + कोर
• बुधवार: ऊपरी शरीर फोकस
• गुरुवार: सक्रिय आराम
• शुक्रवार: निचला शरीर फोकस
• शनिवार: HIIT कार्डियो
• रविवार: पूर्ण आराम

💡 **युक्तियाँ:**
• प्रगतिशील ओवरलोड: रेप्स या समय बढ़ाएं
• फॉर्म पर ध्यान दें: वीडियो रिकॉर्ड करें
• हाइड्रेटेड रहें: पानी पीते रहें
• संगत रहें: हर दिन नहीं, लेकिन नियमित

विशिष्ट व्यायाम के लिए डेमो चाहिए? 📹"""
    else:
        return f"""🏠 **HOME WORKOUT WITHOUT EQUIPMENT**

Your Query: "{user_message}"

✅ **FULL BODY HOME WORKOUT:**

**WARM-UP (10 MINUTES):**
• Jog in place: 3 minutes
• Jumping Jacks: 1 minute
• High Knees: 1 minute
• Dynamic Stretch: 5 minutes

**MAIN WORKOUT (CIRCUIT STYLE):**

🔁 **CIRCUIT 1: CHEST & TRICEPS**
1. Push-ups: 3 sets (max reps)
2. Diamond Push-ups: 3 sets (10-15 reps)
3. Tricep Dips (using chair): 3 sets (10-15 reps)
4. Plank Tap: 3 sets (10 each side)

⏱️ Rest: 30 seconds between sets, 60 seconds between circuits

🔁 **CIRCUIT 2: BACK & BICEPS**
1. Pull-ups (if bar available): 3 sets (max)
2. Superman: 3 sets (15-20 reps)
3. Inverted Row (under table): 3 sets (10-12 reps)
4. Bicep Curls (using bag/bottle): 3 sets (15-20 reps)

⏱️ Rest: 30 seconds between sets

🔁 **CIRCUIT 3: LEGS & SHOULDERS**
1. Squats: 4 sets (15-20 reps)
2. Lunges: 3 sets (10 each leg)
3. Calf Raises: 3 sets (20-25 reps)
4. Pike Push-ups: 3 sets (10-12 reps)
5. Side Plank: 3 sets (30 seconds each side)

⏱️ Rest: 45 seconds between sets

🔁 **CIRCUIT 4: CORE**
1. Plank: 3 sets (60-90 seconds)
2. Russian Twist: 3 sets (20 each side)
3. Leg Raises: 3 sets (15-20 reps)
4. Mountain Climbers: 3 sets (30 seconds)
5. Bicycle Crunch: 3 sets (20 each side)

⏰ **TOTAL TIME:** 45-60 minutes

**COOL-DOWN (10 MINUTES):**
• Light stretching
• Deep breathing
• Foam rolling (if available)

📅 **WEEKLY SCHEDULE:**
• Monday: Full Body (as above)
• Tuesday: Cardio + Core
• Wednesday: Upper Body Focus
• Thursday: Active Recovery
• Friday: Lower Body Focus
• Saturday: HIIT Cardio
• Sunday: Complete Rest

💡 **TIPS:**
• Progressive Overload: Increase reps or time
• Focus on Form: Record yourself
• Stay Hydrated: Keep drinking water
• Be Consistent: Not daily, but regular

Need demo for specific exercises? 📹"""

def get_general_response(user_message, user_goal, language):
    """General professional response"""
    goal_display = user_goal.replace('_', ' ').title()
    
    if language == 'hindi':
        return f"""🤖 **फिट्टी पेशेवर ट्रेनर**

आपने पूछा: "{user_message}"

आपका लक्ष्य: **{goal_display}**

मैं एक उन्नत एआई फिटनेस ट्रेनर हूं। अधिक सटीक मार्गदर्शन के लिए कृपया विशिष्ट प्रश्न पूछें:

**उदाहरण:**
• "सोमवार से शनिवार जिम योजना बनाएं"
• "वजन घटाने के लिए 4-सप्ताह का डाइट चार्ट"
• "पुश-अप की सही तकनीक स्टेप बाय स्टेप बताएं"
• "घर पर बिना उपकरण पैरों की मांसपेशियां बनाएं"

**मैं प्रदान करता हूं:**
✅ वैज्ञानिक शोध-आधारित सलाह
✅ विस्तृत, चरणबद्ध योजनाएं
✅ व्यावहारिक क्रियान्वयन मार्गदर्शन
✅ प्रगति ट्रैकिंग सिस्टम
✅ सुरक्षा और चोट रोकथाम

कृपया अपना प्रश्न विस्तार से बताएं! 🔬💪"""
    else:
        return f"""🤖 **Fitty Professional Trainer**

You asked: "{user_message}"

Your Goal: **{goal_display}**

I'm an advanced AI fitness trainer. For precise guidance, please ask specific questions:

**Examples:**
• "Create Monday to Saturday gym plan"
• "4-week diet chart for weight loss"
• "Step-by-step proper push-up technique"
• "Build leg muscles at home without equipment"

**I Provide:**
✅ Scientific research-based advice
✅ Detailed, step-by-step plans
✅ Practical implementation guidance
✅ Progress tracking systems
✅ Safety and injury prevention

Please elaborate your query! 🔬💪"""

# ==================== MAIN FUNCTION ====================
def get_gemini_response(user_message, user_goal="general fitness", history=None):
    """
    Advanced professional AI trainer response
    """
    print(f"\n🎯 Processing: {user_message[:50]}...")
    print(f"🏆 Goal: {user_goal}")
    
    # 1. Classify query
    intent_info = classify_query_intent(user_message)
    print(f"🧠 Intent: {intent_info['intent']}, Language: {intent_info['language']}")
    
    # 2. Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ No API key found")
        return get_structured_fallback(intent_info, user_message, user_goal)
    
    print(f"🔑 API Key: {api_key[:15]}...")
    
    # 3. Try Gemini API
    if api_key.startswith("AIzaSy") and "B815iCM7v" not in api_key:
        try:
            # Get available model
            model_name = get_available_model(api_key)
            if not hasattr(genai, 'is_configured'):
                genai.configure(api_key=api_key)
                genai.is_configured = True
            
            # Create professional elite trainer prompt
            language = intent_info['language']
            prompt = f"""You are Fitty, an elite AI fitness trainer, wellness coach, and planning assistant with 10+ years of professional experience, designed to work inside the "FitMitra" application.

You must behave at the same intelligence, clarity, and response quality level as ChatGPT, while maintaining the personality of a highly skilled, friendly, and motivating personal trainer.

USER CONTEXT:
- Fitness Goal: {user_goal}
- Current Query: "{user_message}"
- Language: {language}

CORE MISSION:
Provide fully personalized fitness guidance, workout plans, and nutrition advice. Your goal is to make the user feel like they are guided by a real expert who genuinely cares about their progress.

PERSONALITY & TONE:
- Professional, confident, and intelligent.
- Friendly, motivating, and supportive.
- Avoid robotic, generic, or overly short answers.
- Explain things simply but with deep expertise.
- Use emojis effectively (💪, 🔥, 🏋️, 🥗) to maintain engagement.

PLANNING RULES:
1. **Workout Plans:** Include specific exercises, sets, reps, rest intervals, and form tips. Always include warm-up and cool-down suggestions.
2. **Nutrition:** Provide realistic, Indian-friendly meal timing, protein focus, and hydration tips. Avoid medical prescriptions or extreme diets.
3. **Structure:** Use bold headings, bullet points, and tables where helpful. Maintain extreme readability.

DOWNLOADABLE CONTENT (CRITICAL):
If the user asks for a "PDF", "downloadable chart", "export", or "diet chart to download":
1. Prepare a very clean and summarized version of the plan.
2. Use the keyword "WORKOUT" or "GUIDE" or "DIET" clearly in the response.
3. Explicitly state: "This plan is READY FOR DOWNLOAD. You can export it using the button below."
4. Ensure the content is structured as a standalone resource.

SAFETY:
- Prioritize safety and correct form above all.
- Do not provide medical diagnosis.
- Warn against unsafe practices.

RESPONSE FORMAT:
Start with a motivating professional opening.
Provide the core information (Plans/Advice) in clear sections.
End with a supportive closing and a follow-up coaching question.

RESPOND IN {language.upper()} LANGUAGE.
"""

            # Check if model is available
            if not model_name:
                print("⚠️ No suitable model found, using structured response")
                return get_structured_fallback(intent_info, user_message, user_goal)
            
            try:
                model = genai.GenerativeModel(
                    model_name,
                    generation_config={
                        "temperature": 0.4,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 1024,
                    }
                )
                response = model.generate_content(prompt)
                return clean_response(response.text)
            except Exception as model_error:
                print(f"⚠️ Model error: {model_error}")
                # Use structured response instead of trying invalid model
                print("📝 Switching to structured response system")
                return get_structured_fallback(intent_info, user_message, user_goal)
                
        except Exception as e:
            print(f"❌ Gemini Error: {str(e)[:100]}")
            # Fallback to structured response
    
    # 4. Use structured response system
    print("📝 Using advanced structured response system")
    return get_structured_fallback(intent_info, user_message, user_goal)

def get_structured_fallback(intent_info, user_message, user_goal):
    """Intelligent fallback responses"""
    intent = intent_info['intent']
    language = intent_info['language']
    
    if intent == 'workout_plan':
        return get_workout_plan_response(user_message, user_goal, language)
    elif intent == 'exercise_technique':
        return get_technique_response(user_message, language)
    elif intent == 'nutrition_plan':
        return get_nutrition_response(user_goal, language)
    elif intent == 'home_workout':
        return get_home_workout_response(user_message, language)
    elif intent == 'specific_exercise':
        # For specific exercises, use technique response
        return get_technique_response(user_message, language)
    else:
        return get_general_response(user_message, user_goal, language)

def clean_response(text):
    """Clean and format response"""
    # Remove excessive line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Ensure proper spacing
    text = re.sub(r'(\S)\n(\S)', r'\1 \n\2', text)
    return text.strip()

# ==================== TEST ====================
if __name__ == "__main__":
    tests = [
        ("meko monday to saturday ka gym plan batao kon kon sa workout kis din lu", "weight_loss"),
        ("how to build chest muscles at home without equipment?", "muscle_gain"),
        ("वजन घटाने के लिए सुबह क्या खाएं और क्या नहीं?", "weight_loss"),
        ("pushups ki technique batao", "general fitness")
    ]
    
    for query, goal in tests:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        response = get_gemini_response(query, goal)
        print(f"\nResponse Preview:\n{response[:300]}...")
        print(f"\nLength: {len(response)} chars")

def get_posture_feedback(workout, exercise, status, issue=None):
    """
    Generate professional AI trainer feedback for posture issues.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    
    prompt = f"""You are Fitty, a professional AI fitness trainer with 10+ years experience. 
    The user is performing '{exercise}' as part of a '{workout}' workout.
    Their current posture status is: {status.upper()}.
    Detected Issue: {issue if issue else "None - General improvement"}.

    Give a VERY SHORT, DIRECT, and MOTIVATIONAL coaching feedback (max 2 sentences).
    Sound like a real personal trainer standing next to them. 
    If Correct, say something encouraging. 
    If Unsafe or Needs Improvement, give specific advice.
    
    Output example: "Keep your chest up and engage your core! You've got this."
    """

    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Find a fast model for real-time feedback
            model_name = "models/gemini-1.5-flash"
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error in Gemini posture feedback: {e}")

    # Professional fallback responses
    if status.lower() == "correct":
        return "Perfect form! Keep maintaining that control."
    elif status.lower() == "unsafe":
        return f"Watch out! Your posture is unsafe: {issue}. Fix it now to avoid injury."
    else:
        return f"Focus on your form. {issue if issue else 'Keep your movements controlled'}."