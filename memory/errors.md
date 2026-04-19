# Log de errores

## 20260419 — Coto

- **Código/Tipo**: HTTP 403 — Host not in allowlist
- **URLs probadas**:
  - `https://www.cotodigital3.com.ar/sitios/cdigi/browse?Ntt=snacks&format=json`
  - `https://www.cotodigital3.com.ar/sitios/cdigi/browse?Ntt=almacen&format=json`
  - `https://www.cotodigital3.com.ar/` (homepage)
  - `https://www.coto.com.ar/` (dominio principal)
- **Detalle**: El servidor Oracle ATG devuelve "Host not in allowlist" para todas las URLs, tanto en acceso directo como vía ScraperAPI (proxy residencial AR). El error indica que la aplicación ATG tiene configurada una IP/host allowlist restrictiva — solo acepta tráfico desde su CDN o red interna.
- **Acción tomada**: Salteado. No se obtuvieron productos.
- **Próximo paso**: Verificar manualmente desde un browser real antes de reintentar. Considerar usar Playwright con IP argentina real o revisar si hay un API público alternativo.
