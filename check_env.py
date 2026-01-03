# D:\demo_project\FITMITRA\backend\check_env.py
import os
from pathlib import Path

print("🔍 Checking .env Configuration...")
print("="*50)

# Check current directory
current_dir = Path.cwd()
print(f"Current Directory: {current_dir}")

# Look for .env file
env_path = current_dir / '.env'
if env_path.exists():
    print(f"✅ Found .env file at: {env_path}")
    
    # Read and display (safely)
    with open(env_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'GOOGLE_API_KEY' in line:
                parts = line.split('=')
                if len(parts) >= 2:
                    key = parts[1].strip()
                    if key and key != 'AIzaSyB815iCM7vmXeBnbFLGToWS7h7YRf3gHGE':
                        print(f"✅ Valid API Key found: {key[:15]}...")
                    elif key == 'AIzaSyB815iCM7vmXeBnbFLGToWS7h7YRf3gHGE':
                        print("❌ OLD BLOCKED KEY - Need new one!")
                        print("Visit: https://aistudio.google.com/apikey")
                    else:
                        print("❌ No API key set in .env")
else:
    print("❌ .env file not found in current directory")
    
    # Check common locations
    locations = [
        current_dir / '.env',
        current_dir.parent / '.env',
        current_dir / 'backend' / '.env'
    ]
    
    for loc in locations:
        if loc.exists():
            print(f"Found at: {loc}")
            break

print("\n💡 If API key is blocked, get new one from:")
print("https://aistudio.google.com/apikey")
print("Then update .env file and restart server")