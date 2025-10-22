import requests, json, os
from dotenv import load_dotenv

load_dotenv()

class ModelRouter:
    def __init__(self):
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")

    def query_model(self, model_name, prompt):
        try:
            if model_name.startswith("Qwen") or model_name.startswith("deepseek") or model_name.startswith("codellama"):
                return self._query_huggingface(model_name, prompt)
            elif model_name.startswith("gemini"):
                return self._query_gemini(prompt)
            elif model_name.startswith("groq"):
                return self._query_groq(prompt)
            elif model_name.startswith("openai"):
                return self._query_huggingface(model_name, prompt)  # fallback style
            elif model_name.startswith("ollama"):
                return self._query_ollama(model_name, prompt)
            else:
                raise ValueError(f"Unknown model: {model_name}")
        except Exception as e:
            return f"❌ Model call failed: {str(e)}"

    def _query_huggingface(self, model_name, prompt):
        url = f"https://api-inference.huggingface.co/models/{model_name}"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        payload = {"inputs": prompt, "options": {"wait_for_model": True}}
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        return response.json()

    def _query_gemini(self, prompt):
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": self.gemini_key}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, headers=headers, params=params, json=data)
        return response.json()

    def _query_groq(self, prompt):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def _query_ollama(self, model_name, prompt):
        url = "http://localhost:11434/api/generate"
        data = {"model": model_name.split("/")[1], "prompt": prompt}
        response = requests.post(url, json=data)
        return response.json()
