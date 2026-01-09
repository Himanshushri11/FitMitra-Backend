
import razorpay
import warnings
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

warnings.filterwarnings("ignore")

KEY_ID = "rzp_test_S1nU86EANud9hg"
KEY_SECRET = "H0RdRIDLQmpHu85RfDo0nwhzX"

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
    print("SUCCESS! Auth is valid.")
    print(f"Order ID: {order['id']}")
    
except Exception as e:
    print(f"FAILED! Error: {e}")
    if "Authentication failed" in str(e):
        print(">>> The keys provided are definitely INVALID/INACTIVE or MISMATCHED.")
