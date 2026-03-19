import re

# Patterns that flag potentially misleading or non-compliant claims
FLAGGED_PATTERNS = [
    (r"\b(guaranteed?|guarantee)\b", "Guarantee claim — requires substantiation"),
    (r"\b(cure[sd]?|heals?|treats?)\b", "Health claim — may require regulatory approval"),
    (r"\b(#\d+|number one|best in (the )?world)\b", "Superlative claim — requires proof"),
    (r"\b(free\s+trial|no\s+risk)\b", "Free offer — ensure T&Cs are disclosed"),
    (r"\b(limited\s+time|act\s+now|last\s+chance)\b", "Urgency language — ensure accuracy"),
    (r"\b(scientifically\s+proven|clinically\s+tested)\b", "Scientific claim — requires citation"),
    (r"\b(lose\s+weight|weight\s+loss)\b", "Weight loss claim — FTC regulated"),
]


def check(copy: dict) -> dict:
    """
    Check ad copy variants for compliance flags.

    Args:
        copy: dict with variant_1 and variant_2 keys

    Returns:
        dict with clean_copy (same shape as input) and flags (list of dicts)
    """
    flags = []
    clean_copy = {}

    for key in ("variant_1", "variant_2"):
        text = copy.get(key, "")
        clean_copy[key] = text
        for pattern, reason in FLAGGED_PATTERNS:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            if matches:
                flags.append({
                    "variant": key,
                    "matched": matches[0] if isinstance(matches[0], str) else matches[0][0],
                    "reason": reason,
                })

    return {"clean_copy": clean_copy, "flags": flags}
