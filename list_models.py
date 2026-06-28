import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY = "YOUR_GEMINI_API_KEY_HERE"

from google import genai
client = genai.Client(api_key=API_KEY)
models = list(client.models.list())
for m in models:
    print(m.name)
