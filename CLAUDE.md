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

## Flujo de ejecución

1. **Leer memoria** — revisá `memory/last_run.md` y `memory/errors.md` para entender el estado anterior
2. **Scrapear** — ejecutá `scraper.py` con los parámetros pedidos (tiene acceso directo a internet)
3. **Guardar resultados** — los JSONs van a `resultados/` y también como `productos_{super}.json` en raíz
4. **Actualizar memoria** — escribí en `memory/last_run.md` la fecha, qué supermercados corrieron y cuántos productos; agregá errores nuevos a `memory/errors.md`
5. **Pushear a main** — solo resultados y memoria:
   ```bash
   git add resultados/ memory/ productos_*.json
   git commit -m "results: FECHA — N productos"
   git fetch origin main && git rebase origin/main
   git push origin HEAD:main
   ```
6. **Responder con la URL** — siempre terminá con este mensaje:

> ✅ Scraping completado — {supermercados} / {categorías} — {N} productos
> Ver resultados: https://jcastdev.github.io/scrap_snack

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
| `memory/last_run.md` | Fecha y resumen del último run exitoso por supermercado |
| `memory/errors.md` | Log de errores persistentes o sitios caídos |

Siempre leé la memoria antes de ejecutar. Si un supermercado tuvo HTTP 403 en el run anterior, verificá manualmente antes de reintentar.

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
