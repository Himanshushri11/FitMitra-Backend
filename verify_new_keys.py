
import razorpay
import warnings
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings("ignore")

KEY_ID = "rzp_test_S1nr3QbOsO5BDg"
KEY_SECRET = "vO77kQmnfV09VvkS1gnHoNCO"

print(f"Testing Auth with: ID={KEY_ID}")

try:
    client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))
    
    order_data = {
        "amount": 100,  # 1 INR
        "currency": "INR",
        "payment_capture": 1
    }
    
    print("Attempting to create generic order...")
    order = client.order.create(data=order_data)
    print("SUCCESS! New keys are VALID.")
    print(f"Order ID: {order['id']}")
    
except Exception as e:
    print(f"FAILED! Error: {e}")
