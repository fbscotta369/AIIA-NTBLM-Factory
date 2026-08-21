#!/usr/bin/env bash
#
# AIIA-NTBLM-Factory — Production run script
#
# Uso:
#   ./deploy.sh "Como auto educarse con IA. El metodo Dan Martell" all
#
# Requiere: .env con todas las credenciales (ver .env.example)
#
set -euo pipefail

TOPIC="${1:-Como auto educarse con IA. El metodo Dan Martell}"
LANG="${2:-all}"

cd "$(dirname "$0")"

echo "=================================================="
echo " AIIA-NTBLM-Factory — Production Run"
echo " Topic : $TOPIC"
echo " Lang  : $LANG"
echo "=================================================="

# 1. Verificar entorno
python3 -c "import sys; sys.version_info >= (3,11) or sys.exit('Python 3.11+ requerido')"
echo "✓ Python OK"

# 2. Verificar credenciales criticas
python3 - <<'PY'
import os
from dotenv import load_dotenv
load_dotenv()
req = ["GOOGLE_API_KEY","ELEVENLABS_API_KEY","OPENROUTER_API_KEY"]
missing = [k for k in req if not os.environ.get(k)]
if missing:
    raise SystemExit(f"Faltan credenciales en .env: {missing}")
print("✓ Credenciales criticas presentes")
PY

# 3. Instalar deps (idempotente)
pip install -q -r requirements.txt

# 4. Ejecutar pipeline con verificacion de calidad
python3 factory.py --topic "$TOPIC" --lang "$LANG" --verify

echo ""
echo "✅ Production run completado. Revisa output/ para los productos finales."
