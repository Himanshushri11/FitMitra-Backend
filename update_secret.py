
import os

env_file = '.env'
new_secret = "H0RdRIDLQmpHu85RfDo0nwhzX"

with open(env_file, 'r') as f:
    lines = f.readlines()

new_lines = []
id_found = False
secret_found = False

for line in lines:
    if line.strip().startswith('RAZORPAY_KEY_SECRET='):
        new_lines.append(f"RAZORPAY_KEY_SECRET={new_secret}\n")
        secret_found = True
    elif line.strip().startswith('RAZORPAY_KEY_ID='):
        # Check ID length
        parts = line.split('=')
        if len(parts) > 1:
            curr_id = parts[1].strip()
            if len(curr_id) < 20:
                print(f"⚠️ WARNING: Current Key ID '{curr_id}' seems too short (Expected ~24 chars).")
        new_lines.append(line)
        id_found = True
    else:
        new_lines.append(line)

if not secret_found:
    new_lines.append(f"\nRAZORPAY_KEY_SECRET={new_secret}\n")

with open(env_file, 'w') as f:
    f.writelines(new_lines)

print("✅ .env updated with new RAZORPAY_KEY_SECRET")
