---
name: trigger-scraper
description: "Dispara el scraper de supermercados vía GitHub Actions. Usá este skill cuando el usuario pida buscar, scrapear o actualizar precios de productos. Interpreta lenguaje natural y traduce a los parámetros correctos del workflow."
---

# Trigger Scraper — GitHub Actions

Interpretá el pedido en lenguaje natural y disparar el workflow `scraper.yml` en GitHub.

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

Podés combinar: "snacks y almacen de dia" → `super=dia categoria="snacks almacen"`

## Cómo disparar el workflow

```bash
curl -s -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/jcastdev/scrap_snack/actions/workflows/scraper.yml/dispatches \
  -d "{\"ref\":\"main\",\"inputs\":{\"super\":\"<SUPER>\",\"categoria\":\"<CATEGORIA>\",\"max\":\"200\"}}"
```

Reemplazá `<SUPER>` y `<CATEGORIA>` según el mapeo de arriba.

## Verificar que se disparó

```bash
curl -s \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/jcastdev/scrap_snack/actions/runs?per_page=1" \
  | python3 -c "import sys,json; r=json.load(sys.stdin)['workflow_runs'][0]; print(f\"Estado: {r['status']} | {r['display_title']} | {r['created_at']}\")"
```

## Ejemplos de pedidos y su traducción

| Pedido | super | categoria |
|---|---|---|
| "buscar snacks almacen dia" | `dia` | `snacks almacen` |
| "scrapear galletitas en carrefour y coto" | `carrefour coto` | `galletitas` |
| "actualizar todos los supers" | `dia carrefour coto laanonima` | `snacks` |
| "buscar golosinas" | `dia carrefour coto laanonima` | `golosinas` |
| "precios de bebidas en coto" | `coto` | `bebidas` |
