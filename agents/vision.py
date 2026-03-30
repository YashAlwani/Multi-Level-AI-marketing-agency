import base64
import requests
import json
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_FALLBACK_MODEL

VISION_MODELS = [OPENROUTER_MODEL, OPENROUTER_FALLBACK_MODEL]


def _build_payload(model: str, image_b64: str, mime: str, description: str) -> dict:
    return {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a product analyst specializing in consumer goods and TikTok marketing. "
                    "Analyze the product in the image and extract structured tags that will be used "
                    "to derive a target audience persona. "
                    "Respond with ONLY a valid JSON object — no markdown, no explanation. "
                    "Required keys: "
                    "product_type (str), "
                    "product_tags (list of str — specific attributes like materials, use-case, lifestyle fit), "
                    "mood (str — e.g. energetic, calm, luxurious, playful), "
                    "target_signals (list of str — cues about who buys this, e.g. 'fitness enthusiast', 'eco-conscious', 'budget shopper'), "
                    "suggested_hashtags (list of str)."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Product description: {description}\n\nAnalyze the product image and return the JSON.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{image_b64}"},
                    },
                ],
            },
        ],
    }


def _parse_content(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content.strip())


def analyze(image_path: str, description: str) -> dict:
    """Try each vision model in order, return first successful product analysis."""
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    ext = image_path.rsplit(".", 1)[-1].lower()
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

    last_error = None
    for model in VISION_MODELS:
        try:
            payload = _build_payload(model, image_b64, mime, description)
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            result = _parse_content(content)
            result["model_used"] = model
            return result
        except Exception as e:
            last_error = f"{model}: {e}"
            continue

    return {
        "product_type": "unknown",
        "product_tags": [],
        "mood": "neutral",
        "target_signals": [],
        "suggested_hashtags": [],
        "model_used": None,
        "error": last_error,
    }
