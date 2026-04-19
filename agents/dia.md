# Specialist — DIA

## Plataforma

VTEX — API REST. No requiere browser. Todos los requests son HTTP directo con `httpx`.

## Categoría snacks

Path en la API VTEX: `almacen/picadas/snacks`

## Comando

```bash
python scraper.py --super dia --categoria snacks --max 200 --output resultados/dia_FECHA.json
```

Reemplazá `FECHA` con la fecha de hoy en formato `YYYYMMDD`.

## Manejo de errores

| Código HTTP | Acción |
|---|---|
| 429 Too Many Requests | Esperá 10 segundos y reintentá una sola vez. Si vuelve a fallar, loguear y saltá este supermercado. |
| 403 Forbidden | Loguear el error en `memory/errors.md` con fecha y URL, y saltá este supermercado. No reintentar. |
| Otros errores | Loguear y saltá. |

## Notas

- La API VTEX de DIA puede tener rate limiting agresivo en horarios pico (12-14 hs).
- Si el resultado tiene 0 productos, consideralo un fallo silencioso y loguealo.
