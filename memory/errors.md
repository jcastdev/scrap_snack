# Log de errores

## 20260419 — Coto

- **Código/Tipo**: HTTP 403 — "Host not in allowlist"
- **URLs probadas**:
  - `https://www.cotodigital3.com.ar/sitios/cdigi/browse?Ntt=snacks&format=json`
  - `https://www.cotodigital3.com.ar/sitios/cdigi/browse?Ntt=almacen&format=json`
  - `https://www.cotodigital3.com.ar/` (homepage)
  - `https://www.coto.com.ar/` (dominio principal)
- **Detalle**: El servidor Oracle ATG devuelve "Host not in allowlist" para todas las URLs, tanto en acceso directo como vía ScraperAPI (proxy residencial AR). El WAF de Coto bloquea IPs de datacenter sin excepción.
- **Acción tomada**: 0 productos obtenidos. Requiere proxy residencial o acceso desde IP argentina no-datacenter.
- **Próximo paso**: Verificar manualmente desde un browser real antes de reintentar. Considerar usar Playwright con IP argentina real o revisar si hay un API público alternativo.

<!-- Formato para agregar entradas:

## YYYYMMDD HH:MM — <Supermercado>

- **Código/Tipo**: HTTP 403 / Timeout / Mantenimiento / etc.
- **URL**: https://...
- **Detalle**: descripción breve del error
- **Acción tomada**: salteado / reintentado / etc.

-->
