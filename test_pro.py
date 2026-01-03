# D:\demo_project\FITMITRA\backend\test_pro.py
import sys
import os

# Add to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.services.gemini import get_gemini_response

print("🧪 Testing Professional Fitty AI...")
print("="*80)

test_queries = [
    {
        "query": "meko monday to saturday ka gym plan batao kon kon sa workout kis din lu",
        "goal": "weight_loss",
        "description": "Hindi gym plan request"
    },
    {
        "query": "how to build chest muscles at home without equipment?",
        "goal": "muscle_gain", 
        "description": "English home workout request"
    },
    {
        "query": "वजन घटाने के लिए सुबह क्या खाएं और क्या नहीं?",
        "goal": "weight_loss",
        "description": "Hindi nutrition query"
    }
]

for test in test_queries:
    print(f"\n📝 Test: {test['description']}")
    print(f"Query: {test['query']}")
    print(f"Goal: {test['goal']}")
    print("-"*80)
    
    try:
        response = get_gemini_response(test['query'], test['goal'])
        print(f"Response Preview:\n{response[:500]}...\n")
        print(f"Response Length: {len(response)} characters")
    except Exception as e:
        print(f"Error: {e}")
    
    print("="*80)

print("\n✅ Test completed!")