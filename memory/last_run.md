# Último run

## 20260419 19:30

| Supermercado | Estado | Productos | Archivo |
|---|---|---|---|
| La Anónima | ok | 153 | resultados/laanonima_20260419.json |

**Categoría**: snacks (`snacks/n2_522`)
**Nota**: curl directo devuelve 403 (CloudFront/datacenter) — scraper vía ScraperAPI funciona correctamente.

---

## 20260419 19:00

| Supermercado | Estado | Productos | Archivo |
|---|---|---|---|
| DIA | ok | 80 | resultados/dia_20260419.json |

**Categoría**: snacks (`almacen/picadas/snacks`)
**Fix**: API VTEX devuelve HTTP 206 (no 200) — scraper.py actualizado para aceptar ambos.

---

## 20260419 18:23

| Supermercado | Productos |
|---|---|
| Supermercados DIA | 62 |

**Total: 62 productos** -- `resultados/todos_20260419.json`

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
