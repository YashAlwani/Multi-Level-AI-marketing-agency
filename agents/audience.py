import requests
import json
from config import OLLAMA_URL, OLLAMA_FAST_MODEL as OLLAMA_MODEL


def segment(description: str, vision_tags: dict, doc_context: list = None) -> dict:
    """Derive a target audience persona from product description and vision tags."""
    try:
        product_type = vision_tags.get("product_type", "")
        product_tags = ", ".join(vision_tags.get("product_tags", []))
        target_signals = ", ".join(vision_tags.get("target_signals", []))
        mood = vision_tags.get("mood", "")

        system_prompt = (
            "You are a marketing audience analyst. "
            "Given product tags and buyer signals extracted from a product image, "
            "derive a precise target audience persona for a TikTok ad campaign. "
            "Respond with ONLY a valid JSON object — no markdown, no explanation. "
            "Required keys: age_range (str), interests (list of 3-5 str), "
            "platform_behavior (str), persona_label (str, max 40 chars)."
        )

        user_prompt = (
            f"Product type: {product_type}\n"
            f"Product tags: {product_tags}\n"
            f"Buyer signals: {target_signals}\n"
            f"Mood: {mood}\n"
            f"Description: {description}"
        )

        if doc_context:
            context_block = "\n\n---\nRelevant brand/product knowledge:\n"
            context_block += "\n\n".join(f"[{i+1}] {chunk}" for i, chunk in enumerate(doc_context))
            user_prompt += context_block

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
            timeout=120,
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
