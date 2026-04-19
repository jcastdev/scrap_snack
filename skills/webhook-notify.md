---
name: webhook-notify
description: "Envía eventos a Argentive al terminar cada tarea. Usá este skill al final de cualquier rutina para notificar resultados, errores, memoria y resumen de sesión."
---

# Webhook Notify — Argentive

Endpoint: `https://argentive.ai/api/webhook/claude`
Auth: `Authorization: Bearer $ARGENTIVE_TOKEN`

Enviá **siempre** estos eventos en orden al terminar una rutina:

---

## 1. Evento: scraping (si corriste el scraper)

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"scraping\",
    \"payload\": {
      \"supermercados\": [\"<SUPERS>\"],
      \"categorias\": [\"<CATS>\"],
      \"total\": <N>,
      \"duracion_seg\": <SEG>,
      \"productos\": <PRODUCTOS_JSON>,
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

## 2. Evento: memory_update (si escribiste memoria)

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"memory_update\",
    \"payload\": {
      \"archivo\": \"<ARCHIVO>\",
      \"accion\": \"write\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

## 3. Evento: error (si hubo errores)

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"error\",
    \"payload\": {
      \"supermercado\": \"<SUPER>\",
      \"http_status\": <STATUS>,
      \"mensaje\": \"<MENSAJE>\",
      \"url\": \"<URL>\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

## 4. Evento: session_summary (SIEMPRE al final)

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"session_summary\",
    \"payload\": {
      \"agentes\": [\"<AGENTES_USADOS>\"],
      \"sub_agentes\": [],
      \"tools\": [\"<TOOLS_USADOS>\"],
      \"mcp\": [\"<MCP_USADOS>\"],
      \"memoria\": {
        \"leidas\": [\"<ARCHIVOS_LEIDOS>\"],
        \"escritas\": [\"<ARCHIVOS_ESCRITOS>\"]
      },
      \"bash_commands\": [\"<COMANDOS_EJECUTADOS>\"],
      \"duracion_seg\": <SEG>,
      \"estado\": \"completed\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

## Reglas

- Enviá los eventos **en orden**: scraping → memory_update → error → session_summary
- El evento `session_summary` es **obligatorio** — siempre al final, incluso si hubo errores
- Si el curl falla (non-200), reintentá hasta 3 veces con 2s de espera entre intentos
- `$ARGENTIVE_TOKEN` viene de las variables de entorno de la rutina — nunca lo hardcodees
- En `session_summary` listá todos los tools y MCP que realmente usaste en la sesión

## Variables de entorno requeridas

| Variable | Descripción |
|---|---|
| `ARGENTIVE_TOKEN` | Bearer token del usuario para autenticar en Argentive |
