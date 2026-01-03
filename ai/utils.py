# D:\demo_project\FITMITRA\backend\ai\utils.py
"""
Utility functions for AI module
"""

def detect_query_intent(query):
    """
    Detect what the user is asking about
    """
    query_lower = query.lower()
    
    intent_map = {
        'pushup': any(word in query_lower for word in ['pushup', 'push up', 'पुश']),
        'pullup': any(word in query_lower for word in ['pullup', 'pull up', 'चिनअप', 'पुल']),
        'squat': any(word in query_lower for word in ['squat', 'स्क्वाट', 'बैठक']),
        'diet': any(word in query_lower for word in ['diet', 'food', 'nutrition', 'खाना', 'आहार']),
        'weight_loss': any(word in query_lower for word in ['weight loss', 'fat loss', 'reduce', 'वजन', 'मोटापा']),
        'muscle_gain': any(word in query_lower for word in ['muscle', 'gain', 'build', 'size', 'मांसपेशी', 'बनाना']),
        'cardio': any(word in query_lower for word in ['cardio', 'running', 'cycling', 'हृदय']),
        'form': any(word in query_lower for word in ['form', 'technique', 'सही', 'तरीका']),
        'program': any(word in query_lower for word in ['program', 'plan', 'routine', 'योजना', 'कार्यक्रम'])
    }
    
    # Return first matching intent
    for intent, matches in intent_map.items():
        if matches:
            return intent
    
    return 'general'