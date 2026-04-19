#!/bin/bash
set -e

echo "==> Instalando dependencias Python..."
pip install crawl4ai httpx --break-system-packages -q

echo "==> Instalando Chromium para Playwright..."
python -m playwright install chromium --with-deps

echo "==> Setup completo."
