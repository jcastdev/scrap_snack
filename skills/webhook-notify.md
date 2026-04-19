---
name: webhook-notify
description: "Envía eventos a Argentive. Usá este skill para registrar el hub, armar el equipo, notificar resultados y cerrar sesión."
---

# Webhook Notify — Argentive

Endpoint: `https://argentive.ai/api/webhook/claude`
Auth: `Authorization: Bearer $ARGENTIVE_TOKEN`

Variables de entorno:
| Variable | Descripción |
|---|---|
| `ARGENTIVE_TOKEN` | Bearer token del usuario — nunca hardcodear |

IDs dinámicos (se leen de `memory/argentive.md` después del primer `hub_register`):
- `hub_id`
- `agent_id`
- `sub_agentes.<slug>`

---

## 1. hub_register — primera sesión, crea el hub y el agente principal

```bash
RESPONSE=$(curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"event_type\": \"hub_register\",
    \"payload\": {
      \"nombre\": \"<NOMBRE_HUB>\",
      \"descripcion\": \"<DESCRIPCION>\",
      \"claude_md\": $(cat CLAUDE.md | python3 -c \"import sys,json; print(json.dumps(sys.stdin.read()))\"),
      \"skills\": [
        { \"nombre\": \"webhook-notify\",
          \"contenido\": $(cat skills/webhook-notify.md | python3 -c \"import sys,json; print(json.dumps(sys.stdin.read()))\") }
      ]
    }
  }")

# Guardá hub_id y agent_id en memoria
echo "hub_id: $(echo $RESPONSE | python3 -c \"import sys,json; print(json.load(sys.stdin)['hub_id'])\")" > memory/argentive.md
echo "agent_id: $(echo $RESPONSE | python3 -c \"import sys,json; print(json.load(sys.stdin)['agent_id'])\")" >> memory/argentive.md
```

Respuesta esperada de Argentive:
```json
{ "hub_id": "xxx", "agent_id": "yyy" }
```

---

## 2. team_setup — antes de cada tarea, declara los sub-agentes

```bash
RESPONSE=$(curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"<hub_id>\",
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"team_setup\",
    \"payload\": {
      \"tarea\": \"<descripcion del pedido>\",
      \"sub_agentes\": [
        { \"slug\": \"<slug>\", \"descripcion\": \"<qué hace>\" }
      ]
    }
  }")

# Guardá los agent_id de los sub-agentes
echo $RESPONSE | python3 -c "
import sys, json
data = json.load(sys.stdin)
for slug, aid in data.get('sub_agent_ids', {}).items():
    print(f'sub_agente_{slug}: {aid}')
" >> memory/argentive.md
```

Respuesta esperada:
```json
{ "sub_agent_ids": { "scraper-dia": "aaa", "scraper-carrefour": "bbb" } }
```

Si no hay sub-agentes, mandar `"sub_agentes": []`.

---

## 3. task_result — resultado de tarea completada

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"<hub_id>\",
    \"agent_id\": \"<agent_id del sub-agente que ejecutó, o hub agent_id si fue directo>\",
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"task_result\",
    \"payload\": {
      \"tarea\": \"<descripcion>\",
      \"resultado\": \"<resumen libre>\",
      \"datos\": <JSONB libre con lo que produjo la tarea>,
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

## 4. config_sync — cuando cambia CLAUDE.md, skills/ o agents/

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"<hub_id>\",
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"config_sync\",
    \"payload\": {
      \"claude_md\": $(cat CLAUDE.md | python3 -c \"import sys,json; print(json.dumps(sys.stdin.read()))\"),
      \"skills\": [
        { \"nombre\": \"<nombre>\", \"contenido\": \"<contenido>\" }
      ],
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

## 5. memory_update — cuando escribís memoria

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"<hub_id>\",
    \"agent_id\": \"<agent_id>\",
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"memory_update\",
    \"payload\": {
      \"tipo\": \"long_term\",
      \"archivo\": \"<memory/archivo.md>\",
      \"contenido\": \"<contenido>\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

## 6. error — cuando algo falla

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"<hub_id>\",
    \"agent_id\": \"<agent_id>\",
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"error\",
    \"payload\": {
      \"mensaje\": \"<mensaje>\",
      \"contexto\": \"<donde ocurrió>\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

## 7. session_summary — SIEMPRE al final

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"<hub_id>\",
    \"agent_id\": \"<agent_id>\",
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"session_summary\",
    \"payload\": {
      \"task_log\": {
        \"provider\": \"anthropic\",
        \"model\": \"claude-sonnet-4-6\",
        \"duration_seg\": <SEG>,
        \"tools_used\": [\"<TOOLS>\"],
        \"mcp_servers\": [\"<MCP>\"],
        \"skills_used\": [\"webhook-notify\"],
        \"cost_usd\": <ESTIMADO>
      },
      \"sub_agentes_usados\": [\"<slugs>\"],
      \"estado\": \"completed\",
      \"resumen\": \"<una línea de lo que hizo>\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

## Orden por sesión

```
Primera sesión:
  1. hub_register  → crea hub + agent_id en Argentive
  2. team_setup    → declara sub-agentes para esta tarea
  3. task_result   → resultado(s) de la tarea
  4. memory_update → memoria actualizada
  5. error         → si hubo errores
  6. session_summary → SIEMPRE al final

Sesiones siguientes:
  1. team_setup    → (lee hub_id/agent_id de memory/argentive.md)
  2. task_result
  3. memory_update
  4. error
  5. session_summary
```

## Mapeo a tablas Argentive

| event_type | Tabla | Operación |
|---|---|---|
| hub_register | agents | INSERT hub |
| hub_register | agent_team_roles | INSERT specialist principal |
| hub_register | agent_custom_skills | UPSERT skills |
| team_setup | agent_team_roles | INSERT sub-agentes dinámicos |
| task_result | agent_chat_messages | INSERT role=assistant |
| config_sync | agents + agent_custom_skills | UPSERT |
| memory_update | agent_memory | UPSERT long_term |
| error | agent_chat_messages | INSERT role=error |
| session_summary | agent_task_logs | INSERT |

## Reglas

- `session_summary` es **obligatorio** — siempre, incluso si hubo errores
- Si curl falla (non-200), reintentá 3 veces con 2s entre intentos
- Nunca hardcodear tokens ni IDs — siempre desde env vars o `memory/argentive.md`
- `hub_register` solo si `memory/argentive.md` no existe
