import base64
import requests
import json
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL


def analyze(image_path: str, description: str) -> dict:
    """Send image to OpenRouter vision model and return tags/attributes."""
    try:
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")

        ext = image_path.rsplit(".", 1)[-1].lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Analyze this product image for a TikTok ad. "
                                "Return a JSON object with these keys: "
                                "product_type (str), visual_attributes (list of str), "
                                "mood (str), suggested_hashtags (list of str). "
                                f"Product description: {description}"
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{image_b64}"},
                        },
                    ],
                }
            ],
        }

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

        # Strip markdown fences if present
        content = content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())

    except Exception as e:
        return {
            "product_type": "unknown",
            "visual_attributes": [],
            "mood": "neutral",
            "suggested_hashtags": [],
            "error": str(e),
        }
