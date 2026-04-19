---
name: webhook-notify
description: "Envía eventos a Argentive al terminar cada tarea. Usá este skill al final de cualquier rutina para notificar resultados, config, memoria y resumen de sesión."
---

# Webhook Notify — Argentive

Endpoint: `https://argentive.ai/api/webhook/claude`
Auth: `Authorization: Bearer $ARGENTIVE_TOKEN`

Variables de entorno requeridas:
| Variable | Descripción |
|---|---|
| `ARGENTIVE_TOKEN` | Bearer token del usuario |
| `ARGENTIVE_HUB_ID` | ID del hub en Argentive |
| `ARGENTIVE_AGENT_ID` | ID del agente/specialist en Argentive |

---

## Eventos disponibles

### 1. config_sync — cuando cambia CLAUDE.md, agents/, skills/ o memory/

Enviá este evento cada vez que modifiques archivos de configuración del repo.
Argentive usa esto para mantener un espejo de la config de Claude Code.

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"$ARGENTIVE_HUB_ID\",
    \"agent_id\": \"$ARGENTIVE_AGENT_ID\",
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"config_sync\",
    \"payload\": {
      \"claude_md\": \"<CONTENIDO_CLAUDE_MD>\",
      \"specialists\": [
        { \"slug\": \"<SLUG>\", \"prompt\": \"<CONTENIDO_AGENT_MD>\" }
      ],
      \"skills\": [
        { \"nombre\": \"<NOMBRE>\", \"contenido\": \"<CONTENIDO_SKILL_MD>\" }
      ],
      \"memoria\": {
        \"last_run\": \"<CONTENIDO_LAST_RUN>\",
        \"errors\": \"<CONTENIDO_ERRORS>\"
      },
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

### 2. task_result — resultado de cualquier tarea ejecutada

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"$ARGENTIVE_HUB_ID\",
    \"agent_id\": \"$ARGENTIVE_AGENT_ID\",
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"task_result\",
    \"payload\": {
      \"tarea\": \"<DESCRIPCION_TAREA>\",
      \"resultado\": \"<RESULTADO_LIBRE>\",
      \"datos\": { },
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

### 3. memory_update — cuando se escribe memoria

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"$ARGENTIVE_HUB_ID\",
    \"agent_id\": \"$ARGENTIVE_AGENT_ID\",
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"memory_update\",
    \"payload\": {
      \"tipo\": \"long_term\",
      \"archivo\": \"<ARCHIVO>\",
      \"contenido\": \"<CONTENIDO>\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

### 4. error — cuando algo falla

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"$ARGENTIVE_HUB_ID\",
    \"agent_id\": \"$ARGENTIVE_AGENT_ID\",
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"error\",
    \"payload\": {
      \"mensaje\": \"<MENSAJE>\",
      \"contexto\": \"<DONDE_OCURRIO>\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

### 5. session_summary — SIEMPRE al final de cada sesión

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"$ARGENTIVE_HUB_ID\",
    \"agent_id\": \"$ARGENTIVE_AGENT_ID\",
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"session_summary\",
    \"payload\": {
      \"task_log\": {
        \"provider\": \"anthropic\",
        \"model\": \"claude-sonnet-4-6\",
        \"duration_seg\": <SEG>,
        \"tools_used\": [\"<TOOLS>\"],
        \"mcp_servers\": [\"<MCP>\"],
        \"skills_used\": [\"<SKILLS>\"],
        \"cost_usd\": <COSTO_ESTIMADO>
      },
      \"estado\": \"completed\",
      \"resumen\": \"<UNA_LINEA_DE_LO_QUE_HIZO>\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

## Orden de envío por sesión

```
1. config_sync     → si modificaste CLAUDE.md, agents/, skills/ o memory/
2. task_result     → por cada tarea completada
3. memory_update   → si escribiste memoria
4. error           → si hubo errores
5. session_summary → SIEMPRE al final (obligatorio)
```

## Mapeo a tablas Argentive

| event_type | Tabla destino | Operación |
|---|---|---|
| config_sync → claude_md | agents | UPSERT prompt |
| config_sync → specialists | agent_team_roles | UPSERT por slug |
| config_sync → skills | agent_custom_skills | UPSERT por nombre |
| config_sync → memoria | agent_memory | UPSERT long_term |
| task_result | agent_chat_messages | INSERT |
| memory_update | agent_memory | UPSERT long_term |
| error | agent_chat_messages | INSERT role=error |
| session_summary | agent_task_logs | INSERT |

## Reglas

- `session_summary` es **obligatorio** — enviarlo siempre, incluso si hubo errores
- Si el curl falla (non-200), reintentá 3 veces con 2s entre intentos
- Nunca hardcodees tokens — siempre usar variables de entorno
- `config_sync` solo cuando realmente cambiaron archivos de config
