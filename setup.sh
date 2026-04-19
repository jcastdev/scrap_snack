#!/bin/bash
set -e

echo "==> Instalando dependencias Python..."
pip install httpx beautifulsoup4 --break-system-packages -q

echo "==> Setup completo."
