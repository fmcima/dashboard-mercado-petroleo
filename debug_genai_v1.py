import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("List of available models (via google-genai SDK):")
# The new SDK might use a different way to list models. 
# Checking typical pattern: client.models.list()
try:
    for m in client.models.list():
        print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
