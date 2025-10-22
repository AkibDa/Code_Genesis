import requests
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def check_api_connections():
  """
  Checks if Gemini, Groq, and Hugging Face APIs are working correctly.
  Requires:
    - GEMINI_API_KEY
    - GROQ_API_KEY
    - HUGGINGFACE_TOKEN
  """

  results = {}

  # 1️⃣ Check Gemini API
  try:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
      raise ValueError("GEMINI_API_KEY not found in .env")
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content("Say OK if you're working")
    results["Gemini"] = "✅ Working" if "OK" in response.text else "⚠️ Unexpected response"
  except Exception as e:
    results["Gemini"] = f"❌ Error: {str(e)}"

  # 2️⃣ Check Groq API
  try:
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
      raise ValueError("GROQ_API_KEY not found in .env")
    response = requests.post(
      "https://api.groq.com/openai/v1/chat/completions",
      headers={"Authorization": f"Bearer {groq_key}"},
      json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "ping"}]},
      timeout=10
    )
    results["Groq"] = "✅ Working" if response.status_code == 200 else f"❌ Failed ({response.status_code})"
  except Exception as e:
    results["Groq"] = f"❌ Error: {str(e)}"

  # 3️⃣ Check Hugging Face API
  try:
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
      raise ValueError("HUGGINGFACE_TOKEN not found in .env")
    response = requests.get(
      "https://huggingface.co/api/whoami-v2",
      headers={"Authorization": f"Bearer {hf_token}"},
      timeout=10
    )
    results["HuggingFace"] = "✅ Working" if response.status_code == 200 else f"❌ Failed ({response.status_code})"
  except Exception as e:
    results["HuggingFace"] = f"❌ Error: {str(e)}"

  # Print formatted results
  print("\n🔍 API Health Check Results:")
  for api, status in results.items():
    print(f" - {api}: {status}")

  return results


if __name__ == "__main__":
  check_api_connections()
