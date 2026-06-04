#!/usr/bin/env python3
"""
health_check.py — verify Ollama and OpenRouter are reachable before a demo.
Run: python scripts/health_check.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests

try:
    import config
except ImportError:
    print("[FAIL] config.py not found — run: cp config.example.py config.py")
    sys.exit(1)


def check_ollama():
    try:
        resp = requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        tags = {m["name"] for m in resp.json().get("models", [])}
        needed = {config.OLLAMA_MODEL, config.OLLAMA_FAST_MODEL, config.EMBED_MODEL}
        missing = needed - tags
        if missing:
            print(f"  [WARN] Ollama reachable but models missing: {missing}")
            print(f"         Run: ollama pull <model>")
            return False
        print(f"  [OK]   Ollama reachable — models present: {', '.join(needed)}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"  [FAIL] Ollama not running at {config.OLLAMA_URL}")
        print("         Start with: ollama serve")
        return False
    except Exception as e:
        print(f"  [FAIL] Ollama check error: {e}")
        return False


def check_openrouter():
    if not config.OPENROUTER_API_KEY or config.OPENROUTER_API_KEY == "your-openrouter-api-key-here":
        print("  [FAIL] OPENROUTER_API_KEY not set in config.py")
        return False
    try:
        resp = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {config.OPENROUTER_API_KEY}"},
            timeout=8,
        )
        if resp.status_code == 401:
            print("  [FAIL] OpenRouter API key is invalid")
            return False
        resp.raise_for_status()
        print(f"  [OK]   OpenRouter reachable — vision model: {config.OPENROUTER_MODEL}")
        return True
    except requests.exceptions.ConnectionError:
        print("  [FAIL] Cannot reach openrouter.ai — check your internet connection")
        return False
    except Exception as e:
        print(f"  [FAIL] OpenRouter check error: {e}")
        return False


def check_chroma():
    try:
        import chromadb  # noqa
        print("  [OK]   chromadb installed")
        return True
    except ImportError:
        print("  [FAIL] chromadb not installed — run: pip install chromadb")
        return False


def main():
    print("=" * 55)
    print("Marketing Agent — Pre-flight Health Check")
    print("=" * 55)

    results = {
        "Ollama (local models)": check_ollama(),
        "OpenRouter (vision API)": check_openrouter(),
        "ChromaDB (RAG store)": check_chroma(),
    }

    print()
    all_ok = all(results.values())
    if all_ok:
        print("[READY] All systems operational. Run: python app.py")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"[NOT READY] Fix the above issues before running the server.")
        print(f"            Failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
