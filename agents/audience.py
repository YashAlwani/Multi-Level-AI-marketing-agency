import requests
import json
from config import OLLAMA_URL, OLLAMA_MODEL


def segment(description: str, vision_tags: dict) -> dict:
    """Derive a target audience persona from product description and vision tags."""
    try:
        tags_summary = ", ".join(vision_tags.get("visual_attributes", []))
        mood = vision_tags.get("mood", "")
        product_type = vision_tags.get("product_type", "")

        system_prompt = (
            "You are a marketing audience analyst. "
            "Given a product description and visual tags, derive a target audience persona. "
            "Respond with ONLY a valid JSON object — no markdown, no explanation. "
            "Required keys: age_range (str), interests (list of 3-5 str), "
            "platform_behavior (str), persona_label (str, max 40 chars)."
        )

        user_prompt = (
            f"Product type: {product_type}\n"
            f"Visual attributes: {tags_summary}\n"
            f"Mood: {mood}\n"
            f"Description: {description}"
        )

        payload = {
            "model": OLLAMA_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        resp = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json()["message"]["content"].strip()

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())

    except Exception as e:
        return {
            "age_range": "18–35",
            "interests": ["lifestyle", "shopping", "social media"],
            "platform_behavior": "Scrolls TikTok daily, engages with trending content",
            "persona_label": "General audience",
            "error": str(e),
        }
