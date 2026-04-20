---
name: trigger-scraper
description: "Scrapea supermercados y notifica resultados a Argentive. Usá este skill cuando el usuario pida buscar, scrapear o actualizar precios de productos. Interpreta lenguaje natural y ejecuta el flujo completo."
---

# Trigger Scraper

Interpretá el pedido en lenguaje natural, ejecutá el scraping directamente y notificá a Argentive.

## Mapeo de lenguaje natural

### Supermercados
| Si menciona... | Parámetro `super` |
|---|---|
| dia, DIA | `dia` |
| carrefour | `carrefour` |
| coto | `coto` |
| anonima, la anonima, anónima | `laanonima` |
| todos, all, (nada específico) | `dia carrefour coto laanonima` |

### Categorías
| Si menciona... | Parámetro `categoria` |
|---|---|
| snacks | `snacks` |
| almacen, almacén | `almacen` |
| galletitas | `galletitas` |
| golosinas | `golosinas` |
| bebidas | `bebidas` |
| lacteos, lácteos | `lacteos` |
| todo, all, (nada específico) | `snacks` |

## Flujo completo

### 1. team_setup (leer hub_id de memory/argentive.md)

```bash
HUB_ID=$(grep hub_id memory/argentive.md | awk '{print $2}')
AGENT_ID=$(grep agent_id memory/argentive.md | awk '{print $2}')
SESSION=$(git rev-parse --abbrev-ref HEAD)

CONTEXT=$(python3 -c "
import json, os
ctx = {}
for f in ['memory/last_run.md', 'memory/errors.md']:
    if os.path.exists(f): ctx[f] = open(f).read()
print(json.dumps(ctx))
")

curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"hub_id\":\"$HUB_ID\",\"session_id\":\"$SESSION\",\"event_type\":\"team_setup\",\"payload\":{\"tarea\":\"Scraping <SUPER> <CATEGORIA>\",\"sub_agentes\":[],\"contexto_previo\":$CONTEXT}}"
```

### 2. Ejecutar scraper

```bash
python3 scraper.py --super <SUPER> --categoria <CATEGORIA> --max 200
```

### 3. Normalizar y sobreescribir todos_FECHA.json

```python
import json, glob
from datetime import date

hoy = date.today().strftime('%Y%m%d')
productos = []
for f in glob.glob('resultados/<SUPER>_*.json'):
    productos += json.load(open(f))

out = [{'nombre': p.get('nombre',''), 'marca': p.get('marca',''),
        'precio': p.get('precio'), 'precio_lista': p.get('precio_lista'),
        'supermercado': p.get('super', p.get('supermercado','')),
        'categoria': p.get('categoria',''), 'url': p.get('url','')}
       for p in productos]

with open(f'resultados/todos_{hoy}.json', 'w') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
```

### 4. Notificar task_result a Argentive

```bash
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
HOY=$(date +%Y%m%d)
URL_DASHBOARD="https://jcastdev.github.io/scrap_snack"

RESULT_FILES=$(python3 -c "
import json, glob
files = [{'archivo': f, 'contenido': json.load(open(f))} for f in sorted(glob.glob('resultados/todos_*.json'))]
print(json.dumps(files[-1:]))
")

LOGS=$(python3 -c "
import json, os
entries = [json.loads(l) for l in open('logs/session.jsonl')] if os.path.exists('logs/session.jsonl') else []
print(json.dumps(entries))
")

curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"hub_id\":\"$HUB_ID\",\"agent_id\":\"$AGENT_ID\",\"session_id\":\"$SESSION\",\"event_type\":\"task_result\",\"payload\":{\"tarea\":\"Scraping <SUPER> <CATEGORIA>\",\"resultado\":\"<N> productos scrapeados\",\"datos\":{\"super\":\"<SUPER>\",\"categoria\":\"<CATEGORIA>\",\"productos\":<N>},\"url_dashboard\":\"$URL_DASHBOARD\",\"archivos_json\":$RESULT_FILES,\"logs\":$LOGS,\"timestamp\":\"$TS\"}}"
```

### 5. memory_update + session_summary

```bash
# memory_update
MEMORY=$(python3 -c "import json,glob; print(json.dumps([{'archivo':f,'contenido':open(f).read()} for f in sorted(glob.glob('memory/*.md'))]))")
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"hub_id\":\"$HUB_ID\",\"agent_id\":\"$AGENT_ID\",\"session_id\":\"$SESSION\",\"event_type\":\"memory_update\",\"payload\":{\"tipo\":\"long_term\",\"archivos\":$MEMORY,\"timestamp\":\"$TS\"}}"

# session_summary
curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"hub_id\":\"$HUB_ID\",\"agent_id\":\"$AGENT_ID\",\"session_id\":\"$SESSION\",\"event_type\":\"session_summary\",\"payload\":{\"task_log\":{\"provider\":\"anthropic\",\"model\":\"claude-sonnet-4-6\",\"duration_seg\":<SEG>,\"tools_used\":[\"Bash\"],\"skills_used\":[\"trigger-scraper\",\"webhook-notify\"],\"input_tokens\":${CLAUDE_INPUT_TOKENS:-0},\"output_tokens\":${CLAUDE_OUTPUT_TOKENS:-0},\"cache_read_tokens\":${CLAUDE_CACHE_READ_TOKENS:-0},\"cache_write_tokens\":${CLAUDE_CACHE_WRITE_TOKENS:-0},\"cost_usd\":0.03},\"sub_agentes_usados\":[],\"estado\":\"completed\",\"resumen\":\"Scraping <SUPER> <CATEGORIA> — <N> productos\",\"task_type\":\"manual\",\"trigger\":\"interactive\",\"cron_expression\":null,\"url_dashboard\":\"$URL_DASHBOARD\",\"timestamp\":\"$TS\"}}"
```

### 6. Push a main

```bash
git add resultados/ memory/ productos_*.json
git commit -m "results: $(date +%Y%m%d) — <N> productos <SUPER>"
git fetch origin main && git rebase origin/main && git push origin HEAD:main
```

### 7. Respuesta al usuario

```
✅ Scraping completado — <SUPER> / <CATEGORIA> — <N> productos
Ver resultados: https://jcastdev.github.io/scrap_snack
```

## Ejemplos

| Pedido | super | categoria |
|---|---|---|
| "buscar snacks de dia" | `dia` | `snacks` |
| "scrapear galletitas en carrefour y coto" | `carrefour coto` | `galletitas` |
| "actualizar todos los supers" | `dia carrefour coto laanonima` | `snacks` |
| "precios de bebidas en coto" | `coto` | `bebidas` |
