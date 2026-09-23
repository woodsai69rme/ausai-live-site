import requests
import json

url = "https://openrouter.ai/api/v1/models"
response = requests.get(url)
data = response.json()

free_models = []
for model in data.get("data", []):
    pricing = model.get("pricing", {})
    prompt_price = float(pricing.get("prompt", 1))
    completion_price = float(pricing.get("completion", 1))
    model_id = model.get("id", "")
    
    if prompt_price == 0 and completion_price == 0 or model_id.endswith(":free"):
        free_models.append(model_id)

print(f"Found {len(free_models)} current free models on OpenRouter:")
for m in free_models:
    print(f"- {m}")
