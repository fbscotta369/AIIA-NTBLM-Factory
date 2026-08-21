#!/usr/bin/env python3
"""
AIIA-NTBLM-Factory — Setup script
Installs all dependencies for the NotebookLM-driven digital product factory.

Usage:
  python3 setup.py
"""
import subprocess, sys, os

def run(cmd, check=True):
    """Run a command and return its result."""
    print(f"  → {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print(f"    {result.stdout.strip()[:200]}")
    if result.returncode != 0 and check:
        print(f"    ERROR: {result.stderr.strip()[:200]}")
        return False
    return result.returncode == 0

def main():
    print("=" * 60)
    print("AIIA-NTBLM-Factory — Setup")
    print("=" * 60)

    # 1. Python dependencies
    print("\n[1/4] Installing Python dependencies...")
    ok = run(f"{sys.executable} -m pip install -r requirements.txt")
    if not ok:
        print("  ⚠️  Some Python packages may have failed. Check above.")

    # 2. Playwright browsers
    print("\n[2/4] Installing Playwright browsers (Chromium)...")
    ok = run(f"{sys.executable} -m playwright install chromium", check=False)
    if not ok:
        print("  ⚠️  Playwright browser install may have failed.")

    # 3. System dependencies
    print("\n[3/4] Checking system dependencies...")
    system_deps = {
        "texlive (LaTeX)": "pdflatex --version",
        "pandoc": "pandoc --version",
        "ffmpeg": "ffmpeg -version",
    }
    for name, cmd in system_deps.items():
        result = subprocess.run(f"which {cmd.split()[0]} 2>/dev/null", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ {name} encontrado")
        else:
            print(f"  ❌ {name} NO encontrado")
            if name.startswith("texlive"):
                print(f"     Instalar con: sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-latex-extra")
            elif name == "pandoc":
                print(f"     Instalar con: sudo apt-get install pandoc")
            elif name == "ffmpeg":
                print(f"     Instalar con: sudo apt-get install ffmpeg")

    # 4. Environment file
    print("\n[4/4] Checking environment configuration...")
    if os.path.exists(".env"):
        print("  ✅ .env existe")
    else:
        if os.path.exists(".env.example"):
            print("  ⚠️  .env no existe. Copia .env.example → .env y completa tus credenciales:")
            print("     cp .env.example .env")
        else:
            print("  ❌ Ni .env ni .env.example existen")

    # Summary
    print("\n" + "=" * 60)
    print("Setup completado.")
    print("\nPróximos pasos:")
    print("  1. Copia .env.example → .env y completa credenciales")
    print("  2. Ejecuta: python3 orchestrator.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
