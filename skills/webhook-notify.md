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

echo "hub_id: $(echo $RESPONSE | python3 -c \"import sys,json; print(json.load(sys.stdin)['hub_id'])\")" > memory/argentive.md
echo "agent_id: $(echo $RESPONSE | python3 -c \"import sys,json; print(json.load(sys.stdin)['agent_id'])\")" >> memory/argentive.md
```

Respuesta esperada: `{ "hub_id": "xxx", "agent_id": "yyy" }`

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

echo $RESPONSE | python3 -c "
import sys, json
data = json.load(sys.stdin)
for slug, aid in data.get('sub_agent_ids', {}).items():
    print(f'sub_agente_{slug}: {aid}')
" >> memory/argentive.md
```

Respuesta esperada: `{ "sub_agent_ids": { "scraper-dia": "aaa", "scraper-carrefour": "bbb" } }`

Si no hay sub-agentes: `"sub_agentes": []`

---

## 3. task_result — resultado de tarea completada

```bash
# Construir array de archivos JSON de resultados
RESULT_FILES=$(python3 -c "
import json, glob, os
files = []
for f in sorted(glob.glob('resultados/*.json')):
    with open(f) as fh:
        files.append({'archivo': f, 'contenido': json.load(fh)})
print(json.dumps(files))
")

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
      \"datos\": <JSONB libre>,
      \"archivos_json\": $RESULT_FILES,
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

## 4. config_sync — cuando cambia CLAUDE.md, skills/ o agents/

```bash
SKILLS_JSON=$(python3 -c "
import json, glob
skills = []
for f in sorted(glob.glob('skills/*.md')):
    with open(f) as fh:
        skills.append({'nombre': f, 'contenido': fh.read()})
print(json.dumps(skills))
")

AGENTS_JSON=$(python3 -c "
import json, glob
agents = []
for f in sorted(glob.glob('agents/*.md')):
    with open(f) as fh:
        agents.append({'nombre': f, 'contenido': fh.read()})
print(json.dumps(agents))
")

curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"<hub_id>\",
    \"session_id\": \"$(git rev-parse --abbrev-ref HEAD)\",
    \"event_type\": \"config_sync\",
    \"payload\": {
      \"claude_md\": $(cat CLAUDE.md | python3 -c \"import sys,json; print(json.dumps(sys.stdin.read()))\"),
      \"skills\": $SKILLS_JSON,
      \"agents\": $AGENTS_JSON,
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

---

## 5. memory_update — cuando escribís memoria

```bash
MEMORY_JSON=$(python3 -c "
import json, glob
files = []
for f in sorted(glob.glob('memory/*.md')):
    with open(f) as fh:
        files.append({'archivo': f, 'contenido': fh.read()})
print(json.dumps(files))
")

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
      \"archivos\": $MEMORY_JSON,
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
        \"input_tokens\": ${CLAUDE_INPUT_TOKENS:-0},
        \"output_tokens\": ${CLAUDE_OUTPUT_TOKENS:-0},
        \"cache_read_tokens\": ${CLAUDE_CACHE_READ_TOKENS:-0},
        \"cache_write_tokens\": ${CLAUDE_CACHE_WRITE_TOKENS:-0},
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
  1. hub_register    → crea hub + agent_id en Argentive
  2. team_setup      → declara sub-agentes para esta tarea
  3. task_result     → resultado(s) + archivos_json
  4. config_sync     → si modificaste CLAUDE.md, agents/ o skills/
  5. memory_update   → todos los memory/*.md juntos
  6. error           → si hubo
  7. session_summary → SIEMPRE

Sesiones siguientes:
  1. team_setup
  2. task_result
  3. config_sync     → solo si hubo cambios
  4. memory_update
  5. error
  6. session_summary
```

## Mapeo a tablas Argentive

| event_type | Tabla | Operación |
|---|---|---|
| hub_register | agents | INSERT hub |
| hub_register | agent_custom_skills | UPSERT skills |
| team_setup | agent_team_roles | INSERT sub-agentes dinámicos |
| task_result | agent_chat_messages | INSERT role=assistant |
| config_sync | agents + agent_custom_skills | UPSERT |
| memory_update | agent_memory | UPSERT long_term |
| error | agent_chat_messages | INSERT role=error |
| session_summary | agent_task_logs | INSERT |

Todos los eventos (excepto `hub_register`) también se insertan en `claude_code_events` para tener un timeline unificado por sesión:

```sql
SELECT * FROM claude_code_events WHERE session_id = '<branch>' ORDER BY created_at;
```

## Reglas

- `session_summary` es **obligatorio** — siempre, incluso si hubo errores
- Si curl falla (non-200), reintentá 3 veces con 2s entre intentos
- Nunca hardcodear tokens ni IDs — siempre desde env vars o `memory/argentive.md`
- `hub_register` solo si `memory/argentive.md` no existe
