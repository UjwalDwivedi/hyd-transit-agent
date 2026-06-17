import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Force Python to read the fresh .env file values
load_dotenv(override=True)

api_key = os.getenv("GOOGLE_API_KEY")
print(f"🔑 Actively testing key ending with: ...{api_key[-4:] if api_key else 'None'}")

try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    response = llm.invoke("Hello, respond with the word 'Success' if you can hear me.")
    print(f"\n🎉 SUCCESS! Your API Key is working perfectly. Response: {response.content}")
except Exception as e:
    print(f"\n❌ Google still rejected this key. Error details:\n{e}")
