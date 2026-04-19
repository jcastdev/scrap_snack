# Log de errores

<!-- Formato para agregar entradas:

## YYYYMMDD HH:MM — <Supermercado>

- **Código/Tipo**: HTTP 403 / Timeout / Mantenimiento / etc.
- **URL**: https://...
- **Detalle**: descripción breve del error
- **Acción tomada**: salteado / reintentado / etc.

-->

## 20260419 17:50 — Coto

- **Código/Tipo**: HTTP 403
- **URL**: https://www.cotodigital.com.ar/ (y todos los endpoints de la API ATG)
- **Detalle**: "Host not in allowlist" en todas las requests, incluyendo homepage, endpoint `/sitios/cdigi/browse` y vía ScraperAPI (premium). El WAF de Coto bloquea IPs de datacenter sin excepción.
- **Acción tomada**: 0 productos obtenidos. Requiere proxy residencial o acceso desde IP argentina no-datacenter.
