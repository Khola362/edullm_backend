import json
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

api_key = os.getenv("RENDER_API_KEY", "punjab123")
url = "https://punjabtextbook-production.up.railway.app/ask"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
txt_file = f"response_{timestamp}.txt"
json_file = f"response_{timestamp}.json"

print(f"Testing and saving to:\n- {txt_file}\n- {json_file}")

try:
    response = requests.post(
        url,
        json={"question": "What is kinetic Energy?", "k": 3},
        headers={"Content-Type": "application/json", "x-api-key": api_key},
        timeout=30
    )
    
    # Save raw response to text file
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"Status: {response.status_code}\n")
        f.write(f"URL: {url}\n")
        f.write(f"Time: {datetime.now()}\n\n")
        f.write("Full Response:\n")
        f.write(response.text)
    
    # Try to save as JSON if valid
    try:
        if response.text:
            data = response.json()
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ JSON saved to: {json_file}")
    except:
        print("⚠️ Response not valid JSON, only saved as text")
    
    print(f"✅ Text saved to: {txt_file}")
    print(f"📊 Status: {response.status_code}")
    
except Exception as e:
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"ERROR: {e}\n")
    print(f"❌ Error: {e}")