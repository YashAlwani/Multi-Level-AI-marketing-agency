import requests
import json
from config import OLLAMA_URL, OLLAMA_MODEL


def generate(description: str, vision_data: dict, color_data: dict,
             tone: str, audience_data: dict, doc_context: list = None) -> dict:
    """Generate two TikTok ad copy variants using Ollama."""
    try:
        persona_label = audience_data.get("persona_label", "General audience")
        age_range = audience_data.get("age_range", "18–35")
        interests = ", ".join(audience_data.get("interests", []))

        system_prompt = (
            "You are a TikTok ad copywriter. "
            f"Target audience: {persona_label} (age {age_range}), interested in {interests}. "
            "Create two distinct ad copy variants for TikTok. "
            "Each variant must be under 150 characters and include a clear CTA. "
            "Respond with ONLY a valid JSON object — no markdown, no explanation. "
            "Required keys: variant_1 (str), variant_2 (str)."
        )

        attrs = ", ".join(vision_data.get("product_tags", []))
        hashtags = " ".join(vision_data.get("suggested_hashtags", []))
        user_prompt = (
            f"Product description: {description}\n"
            f"Visual attributes: {attrs}\n"
            f"Dominant color: {color_data.get('dominant', '')}\n"
            f"Mood: {vision_data.get('mood', '')}\n"
            f"Tone: {tone}\n"
            f"Suggested hashtags: {hashtags}"
        )

        if doc_context:
            context_block = "\n\nBrand/product reference material (use as creative context):\n"
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
            "variant_1": "Check out this amazing product! Shop now. #trending",
            "variant_2": "You need this in your life. Get yours today! #viral",
            "error": str(e),
        }
