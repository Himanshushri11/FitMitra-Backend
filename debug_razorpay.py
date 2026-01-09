import os
from dotenv import load_dotenv
from pathlib import Path

def check_env(file_path):
    print(f"\n--- Checking {file_path} ---")
    if not Path(file_path).exists():
        print("File does not exist")
        return
    
    # Clear env
    for key in ['RAZORPAY_KEY_ID', 'RAZORPAY_KEY_SECRET']:
        if key in os.environ:
            del os.environ[key]
            
    load_dotenv(file_path)
    rid = os.getenv('RAZORPAY_KEY_ID')
    rsecret = os.getenv('RAZORPAY_KEY_SECRET')
    
    if rid:
        print(f"RAZORPAY_KEY_ID: {rid[:10]}... (Length: {len(rid)})")
    else:
        print("RAZORPAY_KEY_ID not found")
        
    if rsecret:
        print(f"RAZORPAY_KEY_SECRET: {rsecret[:3]}... (Length: {len(rsecret)})")
    else:
        print("RAZORPAY_KEY_SECRET not found")

check_env('d:/demo_project/FITMITRA/Backend/.env')
check_env('d:/demo_project/FITMITRA/Backend/.env.local')
check_env('d:/demo_project/FITMITRA/.env')
