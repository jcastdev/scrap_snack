# Specialist — Coto

## Plataforma

Oracle ATG + React. Requiere browser (Playwright + Chromium). El sitio renderiza el catálogo client-side.

## Categoría snacks

Path en el catálogo: `catalogo-almacén-snacks/catv00003541`

## Comando

```bash
python scraper.py --super coto --categoria snacks --max 200 --output resultados/coto_FECHA.json
```

Reemplazá `FECHA` con la fecha de hoy en formato `YYYYMMDD`.

## Manejo de errores

| Situación | Acción |
|---|---|
| Timeout de página | Loguear con URL y timestamp, y continuá con el siguiente supermercado. |
| Error de navegación / crash del browser | Loguear y continuá. |
| 0 productos scraped | Loguear como fallo silencioso. |

## Notas

- El renderizado puede tardar 5-10 segundos por página; usá `waitUntil: networkidle` o equivalente.
- No hay rate limiting explícito, pero respetá pausas de 2-3 segundos entre páginas.
- Requiere que `playwright install chromium` esté ejecutado (ver `setup.sh`).
