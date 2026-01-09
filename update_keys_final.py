
import os

env_file = '.env'
new_id = "rzp_test_S1nr3QbOsO5BDg"
new_secret = "vO77kQmnfV09VvkS1gnHoNCO"

with open(env_file, 'r') as f:
    lines = f.readlines()

new_lines = []
id_found = False
secret_found = False

for line in lines:
    stripped = line.strip()
    if stripped.startswith('RAZORPAY_KEY_ID='):
        new_lines.append(f"RAZORPAY_KEY_ID={new_id}\n")
        id_found = True
    elif stripped.startswith('RAZORPAY_KEY_SECRET='):
        new_lines.append(f"RAZORPAY_KEY_SECRET={new_secret}\n")
        secret_found = True
    else:
        new_lines.append(line)

if not id_found:
    new_lines.append(f"\nRAZORPAY_KEY_ID={new_id}\n")
if not secret_found:
    new_lines.append(f"RAZORPAY_KEY_SECRET={new_secret}\n")

with open(env_file, 'w') as f:
    f.writelines(new_lines)

print("✅ .env safely updated with new valid keys.")
