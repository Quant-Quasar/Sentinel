import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("🔍 Listing available models for your API key...")
try:
    # List models that support 'generateContent'
    for model in client.models.list(config={"page_size": 100}):
        if "generateContent" in model.supported_generation_methods:
            print(f"   ✅ {model.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")