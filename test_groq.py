from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
print(f"API Key loaded: {api_key[:10]}...")

try:
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": "Test message"}
        ],
        model="llama-3.1-8b-instant",
        max_tokens=10
    )
    print("Success!", chat_completion.choices[0].message.content)
except Exception as e:
    print("Error:", e)
