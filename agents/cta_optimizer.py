import requests
import json
import re
from config import OLLAMA_URL, OLLAMA_MODEL


def _extract_cta(text: str) -> str:
    """Heuristically pull the last sentence or imperative phrase as the CTA."""
    sentences = re.split(r"[.!?]", text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences[-1] if sentences else text.strip()


def optimize(copy: dict, tone: str, audience_data: dict) -> dict:
    """Score each variant's CTA and suggest a stronger alternative."""
    try:
        persona_label = audience_data.get("persona_label", "General audience")
        age_range = audience_data.get("age_range", "18–35")

        system_prompt = (
            "You are a conversion rate optimization expert for TikTok ads. "
            f"Target audience: {persona_label} (age {age_range}), tone: {tone}. "
            "For each ad variant, score the CTA from 1–10 and suggest a stronger one. "
            "Respond with ONLY a valid JSON object — no markdown, no explanation. "
            "Required structure: "
            '{"variant_1": {"original_cta": str, "score": int, "suggestion": str, "reasoning": str}, '
            '"variant_2": {"original_cta": str, "score": int, "suggestion": str, "reasoning": str}}'
        )

        user_prompt = (
            f"Variant 1: {copy.get('variant_1', '')}\n"
            f"Variant 2: {copy.get('variant_2', '')}"
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
            "variant_1": {
                "original_cta": _extract_cta(copy.get("variant_1", "")),
                "score": 0,
                "suggestion": copy.get("variant_1", ""),
                "reasoning": f"CTA optimizer unavailable: {e}",
            },
            "variant_2": {
                "original_cta": _extract_cta(copy.get("variant_2", "")),
                "score": 0,
                "suggestion": copy.get("variant_2", ""),
                "reasoning": f"CTA optimizer unavailable: {e}",
            },
        }
