import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"Loaded key starts with: {api_key[:5] if api_key else None}")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-3.6-flash")

try:
    response = model.generate_content("hello")
    print("Success! AI responded:", response.text)
except Exception as e:
    print("Error during API call:", type(e).__name__, str(e))
