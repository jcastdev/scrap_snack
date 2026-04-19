# Último run

## 20260419 17:50

| Supermercado | Estado | Productos | Archivo | Nota |
|---|---|---|---|---|
| Coto | error HTTP 403 | — | — | Oracle ATG Host not in allowlist |

**Categoría solicitada**: snacks de almacén (`--categoria snacks almacen`)

**Diagnóstico**: Coto bloquea todas las IPs externas incluyendo proxies residenciales de ScraperAPI. No es un bloqueo temporal — aplica al homepage y a todos los endpoints, incluyendo `www.coto.com.ar`. Ver `memory/errors.md` para detalles.

---

<!-- Formato esperado después del primer run:

## YYYYMMDD HH:MM

| Supermercado | Estado | Productos | Archivo |
|---|---|---|---|
| DIA | ok | 142 | resultados/dia_20260419.json |
| Carrefour | ok | 187 | resultados/carrefour_20260419.json |
| Coto | ok | 95 | resultados/coto_20260419.json |
| La Anónima | mantenimiento | — | — |

-->
