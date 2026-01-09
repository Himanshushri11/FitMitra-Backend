
import os
from pathlib import Path

def analyze_file(filename):
    file_path = Path(filename)
    print(f"\nANALYZING: {filename}")
    if not file_path.exists():
        print(f"File {filename} NOT FOUND!")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if '=' in line and 'RAZORPAY' in line:
                    key, val = line.split('=', 1)
                    val = val.strip()
                    val_len = len(val)
                    masked = f"{val[:5]}..." if val_len > 5 else val
                    print(f"FOUND {key}: Prefix={masked}, Length={val_len}")
    except Exception as e:
        print(f"Error reading: {e}")

analyze_file('.env')
analyze_file('.env.local')
