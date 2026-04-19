# Specialist — La Anónima

## Plataforma

Custom — infinite scroll. Requiere browser (Playwright + Chromium). No hay API paginada; el contenido se carga al hacer scroll.

## Pre-verificación

Antes de correr el scraper, verificá que el sitio esté up:

```bash
curl -s -o /dev/null -w "%{http_code}" https://www.laanonima.com.ar
```

Si el código de respuesta no es `200`, loguear en `memory/errors.md` y saltá este supermercado. **No es un error crítico** — el sitio entra frecuentemente en mantenimiento programado.

## Comando

```bash
python scraper.py --super laanonima --categoria snacks --max 200 --output resultados/laanonima_FECHA.json
```

Reemplazá `FECHA` con la fecha de hoy en formato `YYYYMMDD`.

## Manejo de errores

| Situación | Acción |
|---|---|
| Sitio en mantenimiento (curl != 200) | Loguear en `memory/errors.md` y saltá. No es error crítico. |
| Timeout / scroll infinito sin nuevos productos | Loguear y terminá con los productos ya recolectados. |
| Crash del browser | Loguear y continuá con el siguiente supermercado. |

## Notas

- El infinite scroll puede requerir múltiples eventos de scroll; implementá un límite de intentos para no quedar en loop.
- El sitio tiene ventanas de mantenimiento frecuentes, especialmente de madrugada. Si falló el run anterior, revisá `memory/errors.md` antes de intentar.
