#!/usr/bin/env python3
"""
setup.py — install Python deps and pull required Ollama models.
Run once before first use: python scripts/setup.py
"""
import subprocess
import sys
import os


OLLAMA_MODELS = [
    "gemma4:e2b",       # creative copywriter
    "mistral:7b",       # structured JSON tasks
    "nomic-embed-text", # RAG embeddings
]


def run(cmd, desc):
    print(f"\n[setup] {desc}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"  FAILED (exit {result.returncode})")
        return False
    print("  OK")
    return True


def main():
    print("=" * 55)
    print("Marketing Agent — Setup")
    print("=" * 55)

    # 1. Python deps
    requirements = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
    if os.path.exists(requirements):
        run(f"{sys.executable} -m pip install -r {requirements}", "Installing Python dependencies")
    else:
        print("[setup] requirements.txt not found — skipping pip install")

    # 2. Config check
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.py")
    if not os.path.exists(config_path):
        example = config_path.replace("config.py", "config.example.py")
        if os.path.exists(example):
            import shutil
            shutil.copy(example, config_path)
            print("\n[setup] Copied config.example.py → config.py")
            print("        Edit config.py and set your OPENROUTER_API_KEY before running the server.")
        else:
            print("\n[setup] WARNING: config.py not found. Create it from config.example.py.")
    else:
        print("\n[setup] config.py already exists — skipping copy")

    # 3. Ollama model pull
    print("\n[setup] Pulling Ollama models (this may take a few minutes on first run)...")
    for model in OLLAMA_MODELS:
        run(f"ollama pull {model}", f"Pulling {model}")

    print("\n" + "=" * 55)
    print("Setup complete. Start the server with:")
    print("  python app.py")
    print("  or: flask run")
    print("=" * 55)


if __name__ == "__main__":
    main()
