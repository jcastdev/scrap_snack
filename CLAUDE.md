# Scraping Hub — Supermercados Argentinos

## Branch de trabajo

**NUNCA crear pull requests. NUNCA.** Aunque el SDK cree una branch temporal (`claude/...`), siempre pusheá directo a `main` con:

```bash
git fetch origin main
git checkout main
git pull origin main
git checkout -          # volvé a tu branch temporal
git rebase origin/main  # incorporá los últimos cambios de main
git push origin HEAD:main
```

Si hay conflictos en el rebase, resolvelos y continuá (`git rebase --continue`). Nunca abrir un PR.

## Rol del hub

Este repo orquesta el scraping de precios de snacks en supermercados argentinos. El objetivo es correr cada specialist, consolidar los resultados en `resultados/`, y mantener un registro de ejecuciones en `memory/`.

## Flujo de ejecución

1. **Leer memoria** — revisá `memory/last_run.md` y `memory/errors.md` para entender el estado anterior
2. **Correr specialists** — ejecutá cada agente en `agents/` en el orden: DIA → Carrefour → Coto → La Anónima
3. **Guardar resultados** — cada specialist escribe su JSON en `resultados/`
4. **Actualizar memoria** — escribí en `memory/last_run.md` la fecha, qué supermercados corrieron y cuántos productos se obtuvieron; agregá errores nuevos a `memory/errors.md`
5. **Commitear a main** — Commiteá en tu branch y pusheá directo a `main` sin PR:
   ```bash
   git add resultados/ memory/
   git commit -m "results: FECHA"
   git fetch origin main && git rebase origin/main
   git push origin HEAD:main
   ```
6. **Responder con la URL** — siempre terminá con este mensaje:

> ✅ Scraping completado — {supermercados} / {categorías} — {N} productos
> Ver resultados: https://jcastdev.github.io/scrap_snack

## Specialists disponibles (`agents/`)

| Archivo | Supermercado | Plataforma | Browser |
|---|---|---||---|
| `agents/dia.md` | DIA | VTEX (API REST) | No |
| `agents/carrefour.md` | Carrefour | VTEX (API REST) | No |
| `agents/coto.md` | Coto | Oracle ATG + React | Sí |
| `agents/laanonima.md` | La Anónima | Custom / infinite scroll | Sí |

## Skills disponibles (`skills/`)

Las skills son utilidades reutilizables entre specialists. El directorio `skills/` se completa por separado — consultá los archivos disponibles antes de correr un specialist para ver si hay helpers aprovechables (ej: normalización de precios, deduplicación, retry HTTP).

## Memoria (`memory/`)

| Archivo | Contenido |
|---|---|
| `memory/last_run.md` | Fecha y resumen del último run exitoso por supermercado |
| `memory/errors.md` | Log de errores persistentes o sitios caídos |

Siempre leé la memoria antes de ejecutar. Si un supermercado tuvo HTTP 403 en el run anterior, verificá manualmente antes de reintentar.

## Estructura de directorios

```
scrap_snack/
├── CLAUDE.md              # este archivo
├── setup.sh               # setup del environment
├── agents/
│   ├── dia.md
│   ├── carrefour.md
│   ├── coto.md
│   └── laanonima.md
├── memory/
│   ├── last_run.md
│   └── errors.md
├── skills/                # utilidades (se agregan por separado)
├── resultados/            # JSONs de output por ejecución
└── logs/                  # logs de ejecución
```
