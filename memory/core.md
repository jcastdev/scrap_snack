# Core Memory — scraping-hub

## Identidad
- hub_id: 9dd81776-62d8-4641-b065-b98936071bdf
- agent_id: 9dd81776-62d8-4641-b065-b98936071bdf
- rol: Scraping de precios de supermercados argentinos

## Último run — 2026-04-20 21:58
- tarea: Scraping snacks La Anónima
- resultado: 150 productos (caché — ScraperAPI bloqueado)
- estado: partial

## Errores conocidos
- ScraperAPI bloqueado (Host not in allowlist) en entorno Claude Code web
- La Anónima requiere proxy residencial AR o acceso desde IP no-datacenter

## Config que funciona
- DIA: VTEX API directa, sin proxy
- Carrefour: VTEX + Intelligent Search, sin proxy
- Coto: Oracle ATG via ScraperAPI (bloqueado en este entorno)
- La Anónima: HTML data-attrs via ScraperAPI (bloqueado en este entorno)
