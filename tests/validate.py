#!/usr/bin/env python3
"""
validate.py — pipeline acceptance tests against Requirements3.pdf criteria.

Tests structural correctness of agent outputs without running the full
web server. Uses the agents directly.

Run: python tests/validate.py
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents import audience, copywriter, guardrails, cta_optimizer, color

SAMPLE_DESC = (
    "Sustainable insulated water bottle. Keeps drinks cold 24h, hot 12h. "
    "BPA-free bamboo lid. For eco-conscious athletes and daily commuters."
)

SAMPLE_VISION = {
    "product_type": "water bottle",
    "product_tags": ["insulated", "eco-friendly", "BPA-free", "bamboo"],
    "mood": "energetic",
    "target_signals": ["eco-conscious", "fitness enthusiast", "sustainability-minded"],
    "suggested_hashtags": ["#EcoHydration", "#StayGreen", "#GoGreen"],
    "model_used": "test-stub",
}

SAMPLE_COLOR = {
    "dominant": "#4caf50",
    "palette": ["#4caf50", "#2e7d32", "#81c784"],
}

RESULTS = []


def check(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    RESULTS.append((name, passed, detail))
    icon = "✅" if passed else "❌"
    print(f"  {icon}  {name}")
    if detail and not passed:
        print(f"       {detail}")


def section(title):
    print(f"\n{'─' * 55}")
    print(f"  {title}")
    print(f"{'─' * 55}")


def test_guardrails():
    section("FR7 — Guardrails (compliance detection)")

    clean_copy = guardrails.check(
        {"variant_1": "Results guaranteed! Shop now.", "variant_2": "Regular copy here."}
    )
    check("Detects 'guaranteed'", any(f["matched"] in ("guaranteed", "guarantee") for f in clean_copy["flags"]))
    check("Output has clean_copy key", "clean_copy" in clean_copy)
    check("Output has flags key", "flags" in clean_copy)
    check("Flags is a list", isinstance(clean_copy["flags"], list))

    clean_copy2 = guardrails.check(
        {"variant_1": "Clinically tested formula.", "variant_2": "Also clinically proven."}
    )
    check("Detects health/scientific claims", len(clean_copy2["flags"]) >= 1)

    clean_pass = guardrails.check(
        {"variant_1": "Stay hydrated, stay green.", "variant_2": "Your gym companion."}
    )
    check("Clean copy returns empty flags", len(clean_pass["flags"]) == 0)


def test_audience():
    section("FR5 — Audience segmentation")

    t_start = time.time()
    aud = audience.segment(SAMPLE_DESC, SAMPLE_VISION)
    elapsed = time.time() - t_start

    check("Returns persona_label", bool(aud.get("persona_label")))
    check("persona_label is not generic", aud.get("persona_label", "").lower() not in ("general audience", "everyone", "all"))
    check("Returns age_range", bool(aud.get("age_range")))
    check("Returns interests list", isinstance(aud.get("interests"), list) and len(aud.get("interests", [])) > 0)
    check("Returns platform_behavior", bool(aud.get("platform_behavior")))
    check(f"Audience agent responds in <60s ({elapsed:.1f}s)", elapsed < 60)


def test_copywriter(audience_data):
    section("FR4 — Copy generation (2 variants, ≤150 chars)")

    t_start = time.time()
    copy = copywriter.generate(SAMPLE_DESC, SAMPLE_VISION, SAMPLE_COLOR, "energetic", audience_data)
    elapsed = time.time() - t_start

    check("Returns variant_1", bool(copy.get("variant_1")))
    check("Returns variant_2", bool(copy.get("variant_2")))
    v1_len = len(copy.get("variant_1", ""))
    v2_len = len(copy.get("variant_2", ""))
    check(f"variant_1 ≤150 chars ({v1_len})", v1_len <= 150)
    check(f"variant_2 ≤150 chars ({v2_len})", v2_len <= 150)
    check("Variants are distinct", copy.get("variant_1") != copy.get("variant_2"))

    # Levenshtein-ish check: variants should differ by more than minor word swaps
    v1, v2 = copy.get("variant_1", ""), copy.get("variant_2", "")
    word_overlap = len(set(v1.lower().split()) & set(v2.lower().split()))
    total_words  = len(set(v1.lower().split()) | set(v2.lower().split()))
    similarity   = word_overlap / max(total_words, 1)
    check(f"Variants meaningfully differ (word overlap {similarity:.0%})", similarity < 0.75)

    check(f"Copywriter responds in <120s ({elapsed:.1f}s)", elapsed < 120)
    return copy


def test_cta(copy, audience_data):
    section("FR8 — CTA analysis (score per variant)")

    result = guardrails.check(copy)
    cta = cta_optimizer.optimize(result["clean_copy"], "energetic", audience_data)

    check("Returns variant_1 CTA", "variant_1" in cta)
    check("Returns variant_2 CTA", "variant_2" in cta)

    for key in ("variant_1", "variant_2"):
        v = cta.get(key, {})
        score = v.get("score")
        check(f"{key} has numeric score", isinstance(score, (int, float)))
        check(f"{key} score 1–10 ({score})", score is not None and 1 <= score <= 10)
        check(f"{key} has suggestion", bool(v.get("suggestion")))
        check(f"{key} has reasoning", bool(v.get("reasoning")))


def test_pipeline_timing():
    section("Assignment criterion — pipeline completes in <120s")

    t_start = time.time()
    aud = audience.segment(SAMPLE_DESC, SAMPLE_VISION)
    copy = copywriter.generate(SAMPLE_DESC, SAMPLE_VISION, SAMPLE_COLOR, "energetic", aud)
    result = guardrails.check(copy)
    cta_optimizer.optimize(result["clean_copy"], "energetic", aud)
    elapsed = time.time() - t_start

    check(f"Full text pipeline in <120s ({elapsed:.1f}s)", elapsed < 120)


def main():
    print("=" * 55)
    print("Marketing Agent — Acceptance Tests")
    print("=" * 55)

    test_guardrails()
    aud = audience.segment(SAMPLE_DESC, SAMPLE_VISION)
    test_audience()
    copy = test_copywriter(aud)
    test_cta(copy, aud)
    test_pipeline_timing()

    print(f"\n{'═' * 55}")
    passed = sum(1 for _, p, _ in RESULTS if p)
    total  = len(RESULTS)
    print(f"  Results: {passed}/{total} passed")
    if passed == total:
        print("  All checks passed.")
    else:
        failed = [(n, d) for n, p, d in RESULTS if not p]
        print(f"  {len(failed)} failed:")
        for name, detail in failed:
            print(f"    ✗ {name}" + (f" — {detail}" if detail else ""))
    print("═" * 55)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
