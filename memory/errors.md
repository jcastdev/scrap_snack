# Log de errores

## 20260419 — Todos los supermercados

- **Código/Tipo**: HTTP 403 — "Host not in allowlist"
- **URL**: todas (cotodigital.com.ar, cotodigital3.com.ar, diaonline.supermercadosdia.com.ar, carrefour.com.ar)
- **Detalle**: El entorno de ejecución tiene un WAF/sandbox que bloquea todas las requests HTTP externas. No es un bloqueo del supermercado sino una restricción de red del entorno.
- **Acción tomada**: scraping saltado — requiere entorno con acceso a Internet

<!-- Formato para agregar entradas:

## YYYYMMDD HH:MM — <Supermercado>

- **Código/Tipo**: HTTP 403 / Timeout / Mantenimiento / etc.
- **URL**: https://...
- **Detalle**: descripción breve del error
- **Acción tomada**: salteado / reintentado / etc.

-->
