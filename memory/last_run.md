# Último run

## 20260419 — Primera ejecución (Coto snacks de almacén)

| Supermercado | Estado | Productos | Archivo | Nota |
|---|---|---|---|---|
| Coto | error 403 | — | — | Oracle ATG Host not in allowlist |

**Categoría solicitada**: snacks de almacén (`--categoria almacen`)

**Diagnóstico**: Coto bloquea todas las IPs externas incluyendo proxies residenciales de ScraperAPI. No es un bloqueo temporal — aplica al homepage y a todos los endpoints, incluyendo `www.coto.com.ar`.
