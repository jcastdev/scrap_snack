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

## 2. routine_sync — cuando se crea o modifica una rutina en Claude Code

Espeja la rutina de Claude Code en Argentive. Correr cada vez que se crea o cambia una rutina.

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"<hub_id>\",
    \"agent_id\": \"<agent_id>\",
    \"event_type\": \"routine_sync\",
    \"payload\": {
      \"nombre\": \"<nombre de la rutina, ej: scraper-diario>\",
      \"descripcion\": \"<qué hace>\",
      \"trigger\": \"<schedule|api|github>\",
      \"cron_expression\": \"<ej: 0 9 * * * | null si no es schedule>\",
      \"task_prompt\": \"<el prompt exacto configurado en la rutina>\",
      \"enabled\": true,
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

Respuesta esperada: `{ "agent_id": "xxx" }` — guardar en `memory/argentive.md` como `agent_<nombre>`.

---

## routine_delete — cuando se elimina una rutina en Claude Code

```bash
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"<hub_id>\",
    \"event_type\": \"routine_delete\",
    \"payload\": {
      \"nombre\": \"<nombre-rutina>\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

Argentive marca la rutina como `enabled: false` — no la borra para preservar historial.

---

## 3. agent_register — una vez por rutina, registra la rutina como agente permanente

Correr solo cuando se crea una rutina nueva en Claude Code. Guarda el `agent_id` en `memory/argentive.md` para usarlo en todos los eventos de esa rutina.

```bash
RESPONSE=$(curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"<hub_id>\",
    \"event_type\": \"agent_register\",
    \"payload\": {
      \"nombre\": \"<nombre de la rutina, ej: scraper-diario>\",
      \"descripcion\": \"<qué hace esta rutina>\",
      \"trigger\": \"<schedule|api|github>\"
    }
  }")

AGENT_ID=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['agent_id'])")
echo "agent_<nombre>: $AGENT_ID" >> memory/argentive.md
```

Respuesta esperada: `{ "agent_id": "xxx" }`

Luego en cada evento de esa rutina usar `agent_id` = el valor guardado, no el `agent_id` del hub.

---

## 3. team_setup — antes de cada tarea, declara los sub-agentes

```bash
CONTEXT_JSON=$(python3 -c "
import json, os
ctx = {}
for f in ['memory/last_run.md', 'memory/errors.md']:
    if os.path.exists(f):
        with open(f) as fh:
            ctx[f] = fh.read()
print(json.dumps(ctx))
")

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
      ],
      \"contexto_previo\": $CONTEXT_JSON
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

Los `sub_agent_ids` se guardan en `memory/argentive.md` y se usan en los eventos de cada sub-agente.

---

## Sub-agentes — eventos por cada uno al terminar

Cuando hay múltiples supers, cada sub-agente manda sus propios eventos con su `agent_id`:

```bash
SUB_AGENT_ID=$(grep "sub_agente_<slug>" memory/argentive.md | awk '{print $2}')
SESSION=$(git rev-parse --abbrev-ref HEAD)
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# task_result del sub-agente
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"<hub_id>\",
    \"agent_id\": \"$SUB_AGENT_ID\",
    \"session_id\": \"$SESSION\",
    \"event_type\": \"task_result\",
    \"payload\": {
      \"tarea\": \"Scraping <super> <categoria>\",
      \"resultado\": \"<N> productos\",
      \"datos\": {\"super\": \"<super>\", \"productos\": <N>},
      \"timestamp\": \"$TS\"
    }
  }"

# memory_update del sub-agente (su memoria específica)
SUB_MEMORY=$(python3 -c "
import json, os
f = 'memory/sub_agentes/<slug>.md'
contenido = open(f).read() if os.path.exists(f) else ''
print(json.dumps([{'archivo': f, 'contenido': contenido}]))
")

curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"hub_id\": \"<hub_id>\",
    \"agent_id\": \"$SUB_AGENT_ID\",
    \"session_id\": \"$SESSION\",
    \"event_type\": \"memory_update\",
    \"payload\": {
      \"tipo\": \"long_term\",
      \"archivos\": $SUB_MEMORY,
      \"timestamp\": \"$TS\"
    }
  }"
```

La memoria de cada sub-agente se guarda en `memory/sub_agentes/<slug>.md` — errores, productos encontrados, estado del último run de ese super.

---

## Generar core.md antes de memory_update

Paso obligatorio antes de cada `memory_update`. El agente genera dinámicamente su `memory/core.md` (o `memory/sub_agentes/<slug>/core.md` para sub-agentes) con el estado esencial de la sesión:

```python
import os
from datetime import datetime

# Para el hub principal
def escribir_core(agent_nombre, hub_id, agent_id, rol, tarea, resultado, estado, errores, config_notas, path='memory/core.md'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(f"""# Core Memory — {agent_nombre}

## Identidad
- hub_id: {hub_id}
- agent_id: {agent_id}
- rol: {rol}

## Último run — {datetime.now().strftime('%Y-%m-%d %H:%M')}
- tarea: {tarea}
- resultado: {resultado}
- estado: {estado}

## Errores conocidos
{errores}

## Config que funciona
{config_notas}
""")

# Hub principal
escribir_core(
    agent_nombre='scraping-hub',
    hub_id='<hub_id>',
    agent_id='<agent_id>',
    rol='Scraping de precios de supermercados argentinos',
    tarea='<tarea del run>',
    resultado='<N> productos scrapeados',
    estado='completed',
    errores='<contenido de memory/errors.md resumido>',
    config_notas='<endpoints que funcionan, proxies, etc.>',
    path='memory/core.md'
)

# Por cada sub-agente
escribir_core(
    agent_nombre='scraper-<slug>',
    hub_id='<hub_id>',
    agent_id='<sub_agent_id>',
    rol='Scraping de <super>',
    tarea='Scraping <categoria>',
    resultado='<N> productos',
    estado='completed',
    errores='<errores específicos de este super>',
    config_notas='<endpoint, categoría, método que funcionó>',
    path='memory/sub_agentes/<slug>/core.md'
)
```

El `memory_update` incluye estos archivos junto con el resto de `memory/`.

---

## 3. task_result — resultado de tarea completada

```bash
RESULT_FILES=$(python3 -c "
import json, glob
files = []
for f in sorted(glob.glob('resultados/*.json')):
    with open(f) as fh:
        files.append({'archivo': f, 'contenido': json.load(fh)})
print(json.dumps(files))
")

LOGS=$(python3 -c "
import json, glob, os
logs = []
for f in sorted(glob.glob('logs/*.log')):
    with open(f) as fh:
        logs.append({'archivo': f, 'contenido': fh.read()})
print(json.dumps(logs))
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
      \"logs\": $LOGS,
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

Calcular duración real, costo real, historial y próximo run antes de enviar:

```bash
# Duración real — SESSION_START debe setearse al inicio de la sesión
SESSION_START=${SESSION_START:-$(date +%s)}
DURATION=$(( $(date +%s) - SESSION_START ))

# Costo real basado en tokens (precios Sonnet 4.6: input $3/Mtok, output $15/Mtok, cache_read $0.30/Mtok)
COST=$(python3 -c "
inp   = int('${CLAUDE_INPUT_TOKENS:-0}')
out   = int('${CLAUDE_OUTPUT_TOKENS:-0}')
cr    = int('${CLAUDE_CACHE_READ_TOKENS:-0}')
cw    = int('${CLAUDE_CACHE_WRITE_TOKENS:-0}')
cost  = (inp * 3 + out * 15 + cr * 0.3 + cw * 3.75) / 1_000_000
print(f'{cost:.6f}')
")

# Historial de runs — leer/actualizar memory/run_history.json
python3 -c "
import json, os
from datetime import datetime
f = 'memory/run_history.json'
hist = json.load(open(f)) if os.path.exists(f) else {'total': 0, 'exitosos': 0, 'fallidos': 0, 'fallos_consecutivos': 0, 'ultimo_exitoso': None, 'ultimo_fallido': None}
estado = 'ESTADO'  # reemplazar con completed|error
hist['total'] += 1
if estado == 'completed':
    hist['exitosos'] += 1
    hist['fallos_consecutivos'] = 0
    hist['ultimo_exitoso'] = datetime.now().isoformat()
else:
    hist['fallidos'] += 1
    hist['fallos_consecutivos'] += 1
    hist['ultimo_fallido'] = datetime.now().isoformat()
json.dump(hist, open(f, 'w'), indent=2)
print(json.dumps(hist))
")
HISTORY=$(cat memory/run_history.json)
FALLOS_CONSECUTIVOS=$(python3 -c "import json; print(json.load(open('memory/run_history.json'))['fallos_consecutivos'])")

# Próximo run desde cron_expression
NEXT_RUN=$(python3 -c "
import sys
try:
    from croniter import croniter
    from datetime import datetime
    cron = '<cron_expression>'
    if cron and cron != 'null':
        it = croniter(cron, datetime.now())
        print(it.get_next(datetime).isoformat())
    else:
        print('null')
except ImportError:
    print('null')
" 2>/dev/null || echo "null")

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
        \"duration_seg\": $DURATION,
        \"tools_used\": [\"<TOOLS>\"],
        \"mcp_servers\": [\"<MCP>\"],
        \"skills_used\": [\"webhook-notify\"],
        \"input_tokens\": ${CLAUDE_INPUT_TOKENS:-0},
        \"output_tokens\": ${CLAUDE_OUTPUT_TOKENS:-0},
        \"cache_read_tokens\": ${CLAUDE_CACHE_READ_TOKENS:-0},
        \"cache_write_tokens\": ${CLAUDE_CACHE_WRITE_TOKENS:-0},
        \"cost_usd\": $COST
      },
      \"run_history\": $HISTORY,
      \"next_run_at\": \"$NEXT_RUN\",
      \"fallos_consecutivos\": $FALLOS_CONSECUTIVOS,
      \"sub_agentes_usados\": [\"<slugs>\"],
      \"estado\": \"<completed|error>\",
      \"resumen\": \"<una línea de lo que hizo>\",
      \"task_type\": \"<scheduled|manual|api|github>\",
      \"trigger\": \"<schedule|api|github|interactive>\",
      \"cron_expression\": \"<ej: 0 9 * * * | null si no es scheduled>\",
      \"url_dashboard\": \"<url | null>\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }"
```

**Nota:** setear `SESSION_START=$(date +%s)` al inicio de cada sesión (antes del `team_setup`).
**Nota:** instalar `croniter` si se usa cron: `pip install croniter -q`

---

## Orden por sesión

```
Setup del proyecto (una sola vez):
  1. hub_register    → crea el hub
  2. agent_register  → una vez por rutina creada en Claude Code

Cada ejecución de una rutina:
  1. team_setup      → declara sub-agentes para esta tarea + contexto_previo
  2. task_result     → resultado(s) + archivos_json + logs
  3. config_sync     → solo si modificaste CLAUDE.md, agents/ o skills/
  4. memory_update   → todos los memory/*.md juntos
  5. error           → si hubo
  6. session_summary → SIEMPRE
```

## Mapeo a tablas Argentive

| event_type | Tabla | Operación |
|---|---|---|
| hub_register | agents | INSERT hub |
| hub_register | agent_custom_skills | UPSERT skills |
| agent_register | agents | INSERT rutina como agente permanente del hub |
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
