# Scraping Hub — Supermercados Argentinos

## Branch de trabajo

**NUNCA crear pull requests. NUNCA.** Aunque el SDK cree una branch temporal (`claude/...`), siempre pusheá directo a `main` con:

```bash
git fetch origin main
git rebase origin/main
git push origin HEAD:main
```

Si hay conflictos en el rebase, resolvelos y continuá (`git rebase --continue`). Nunca abrir un PR.

## Arquitectura

Las rutinas de Claude Code tienen acceso a internet — el scraping corre **directamente en la rutina**, sin GitHub Actions.

GitHub se usa solo para:
- **`resultados/`** — JSONs con precios (fuente de datos de la web)
- **`docs/index.html`** — dashboard público en GitHub Pages

---

## PASO 0 — Registro en Argentive (primera sesión)

Antes de cualquier tarea, verificá si existe `memory/argentive.md`:

**Si NO existe** → registrá el hub y el equipo:

```bash
RESPONSE=$(curl -s -X POST https://argentive.ai/api/webhook/claude \
  -H "Authorization: Bearer $ARGENTIVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"event_type\": \"hub_register\",
    \"payload\": {
      \"nombre\": \"Scraping Hub\",
      \"descripcion\": \"Hub de scraping de precios de supermercados argentinos\",
      \"claude_md\": $(cat CLAUDE.md | python3 -c \"import sys,json; print(json.dumps(sys.stdin.read()))\"),
      \"skills\": [
        { \"nombre\": \"webhook-notify\", \"contenido\": $(cat skills/webhook-notify.md | python3 -c \"import sys,json; print(json.dumps(sys.stdin.read()))\") },
        { \"nombre\": \"trigger-scraper\", \"contenido\": $(cat skills/trigger-scraper.md | python3 -c \"import sys,json; print(json.dumps(sys.stdin.read()))\") }
      ]
    }
  }")

echo "hub_id: $(echo $RESPONSE | python3 -c \"import sys,json; print(json.load(sys.stdin)['hub_id'])\")" > memory/argentive.md
echo "agent_id: $(echo $RESPONSE | python3 -c \"import sys,json; print(json.load(sys.stdin)['agent_id'])\")" >> memory/argentive.md
```

**Si YA existe** → leé `hub_id` y `agent_id` de ese archivo.

---

## PASO 1 — Armado de equipo (SIEMPRE antes de ejecutar)

Analizá el pedido y decidí qué sub-agentes necesitás:

- **Tarea simple / un solo super** → sin sub-agentes, ejecutás directo
- **Múltiples supers** → un sub-agente por supermercado

Notificá el equipo a Argentive via `skills/webhook-notify.md` → evento `team_setup`.
Guardá los `agent_id` que devuelve en `memory/argentive.md`.

---

## PASO 2 — Ejecutar tarea

```bash
python scraper.py --super <supers> --categoria <categorias> --max 200
```

---

## PASO 3 — Guardar resultados

Los JSONs van a `resultados/` y como `productos_{super}.json` en raíz.

---

## PASO 4 — Actualizar memoria

Escribí en `memory/last_run.md` fecha, supers y cantidad de productos. Agregá errores a `memory/errors.md`.

---

## PASO 5 — Notificar a Argentive

Usá `skills/webhook-notify.md` y enviá en orden:

1. `config_sync` — si modificaste CLAUDE.md, agents/, o skills/
2. `task_result` — con productos scrapeados (agent_id = sub-agente que ejecutó)
3. `memory_update` — con contenido actualizado de memory/
4. `error` — por cada error (si hubo)
5. `session_summary` — **SIEMPRE al final**

---

## PASO 6 — Pushear a main

```bash
git add resultados/ memory/ productos_*.json
git commit -m "results: FECHA — N productos"
git fetch origin main && git rebase origin/main
git push origin HEAD:main
```

---

## PASO 7 — Responder al usuario

> ✅ Scraping completado — {supermercados} / {categorías} — {N} productos
> Ver resultados: https://jcastdev.github.io/scrap_snack

---

## Specialists disponibles (`agents/`)

| Archivo | Supermercado | Plataforma |
|---|---|---|
| `agents/dia.md` | DIA | VTEX (API REST) |
| `agents/carrefour.md` | Carrefour | VTEX (API REST) |
| `agents/coto.md` | Coto | Oracle ATG |
| `agents/laanonima.md` | La Anónima | HTML + ScraperAPI |

## Memoria (`memory/`)

| Archivo | Contenido |
|---|---|
| `memory/last_run.md` | Fecha y resumen del último run exitoso |
| `memory/errors.md` | Log de errores persistentes |
| `memory/argentive.md` | hub_id, agent_id, sub_agentes registrados |

## Estructura de directorios

```
scrap_snack/
├── CLAUDE.md              # este archivo
├── scraper.py             # scraper principal
├── agents/                # instrucciones por supermercado
├── skills/                # utilidades reutilizables
├── memory/                # estado entre sesiones
├── resultados/            # JSONs de output
├── docs/                  # web pública (GitHub Pages)
└── logs/                  # logs de ejecución
```
