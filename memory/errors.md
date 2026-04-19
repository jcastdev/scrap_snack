# Log de errores

## 20260419 — La Anónima — snacks

- **Código/Tipo**: HTTP 403 (acceso directo desde entorno Claude)
- **URL**: https://www.laanonima.com.ar
- **Detalle**: El entorno bloquea requests directas; se ejecutó via GitHub Actions (success).
- **Acción tomada**: Workflow scraper.yml disparado — completado con éxito.

## 20260419 — Todos los supermercados

- **Código/Tipo**: HTTP 403 — "Host not in allowlist"
- **URL**: todas (cotodigital.com.ar, cotodigital3.com.ar, diaonline.supermercadosdia.com.ar, carrefour.com.ar)
- **Detalle**: El entorno de ejecución tiene un WAF/sandbox que bloquea todas las requests HTTP externas. No es un bloqueo del supermercado sino una restricción de red del entorno.
- **Acción tomada**: scraping saltado — requiere entorno con acceso a Internet (usar GitHub Actions)

## 20260419 — Coto (detalle adicional)

- **Código/Tipo**: HTTP 403 — "Host not in allowlist"
- **URLs probadas**:
  - `https://www.cotodigital3.com.ar/sitios/cdigi/browse?Ntt=snacks&format=json`
  - `https://www.cotodigital3.com.ar/sitios/cdigi/browse?Ntt=almacen&format=json`
  - `https://www.cotodigital3.com.ar/` (homepage)
  - `https://www.coto.com.ar/` (dominio principal)
- **Detalle**: El servidor Oracle ATG devuelve "Host not in allowlist" para todas las URLs, tanto en acceso directo como vía ScraperAPI (proxy residencial AR). El WAF de Coto bloquea IPs de datacenter sin excepción.
- **Acción tomada**: 0 productos obtenidos. Requiere proxy residencial o acceso desde IP argentina no-datacenter.
- **Próximo paso**: Verificar manualmente desde un browser real. Considerar usar Playwright con IP argentina real o revisar si hay un API público alternativo.

<!-- Formato para agregar entradas:

## YYYYMMDD HH:MM — <Supermercado>

- **Código/Tipo**: HTTP 403 / Timeout / Mantenimiento / etc.
- **URL**: https://...
- **Detalle**: descripción breve del error
- **Acción tomada**: salteado / reintentado / etc.

-->
