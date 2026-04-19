---
name: supermarket-scraper-ar
description: "Scrapea precios y nombres de productos de supermercados argentinos: DIA, Carrefour, La Anónima y Coto. Usá este skill siempre que el usuario pida precios de supermercados, comparar precios entre cadenas, obtener productos de DIA / Carrefour / Coto / La Anónima, buscar marcas específicas (Lays, Krachitos, Pehuamar, Quento, etc.), hacer seguimiento de precios, o ejecutar cualquier tarea de scraping de supermercados argentinos — incluso si no menciona explícitamente 'scraping'."
---

# Supermarket Scraper Argentina

Obtiene nombre y precio de productos de **DIA, Carrefour, Coto y La Anónima**.

**No requiere browser ni Playwright.** Funciona en cualquier entorno con Python.

## Arquitectura por supermercado

| Super | Plataforma | Método |
|---|---|---|
| DIA | VTEX | API REST — path de categoría o búsqueda `ft=` por marca |
| Carrefour | VTEX + Intelligent Search | API REST — IS para marcas, path para categorías |
| Coto | Oracle ATG | `/browse?Ntt=<term>&format=json` — JSON nativo, sin browser |
| La Anónima | HTML server-side | BeautifulSoup — productos en atributos `data-*` del HTML |

## Setup (primera vez)

```bash
pip install httpx beautifulsoup4
```

Sin Playwright. Sin crawl4ai. Eso es todo.

## Uso del script

```bash
# Todos los supermercados, todas las categorías
python scraper.py

# Supermercados específicos
python scraper.py --super dia carrefour

# Filtrar categorías
python scraper.py --categoria bebidas lacteos

# Buscar marcas específicas en todos los supers
python scraper.py --marcas lays krachitos pehuamar quento

# Combinar: marcas en supers específicos
python scraper.py --super coto laanonima --marcas lays krachitos

# Limitar cantidad y cambiar output
python scraper.py --max 100 --output precios.json
```

## Parámetros

| Parámetro | Descripción | Default |
|---|---|---|
| `--super` | dia, carrefour, coto, laanonima | todos |
| `--categoria` | Categorías a scrapear | `snacks` |
| `--marcas` | Marcas específicas a buscar | — |
| `--max` | Máximo de productos por super | 200 |
| `--output` | Archivo de salida JSON | `productos_supermercados.json` |

> **`--marcas` vs `--categoria`**: Son mutuamente excluyentes en la práctica. `--marcas` hace búsqueda por término (más preciso para marcas), `--categoria` navega por árbol de categorías (más amplio, sin filtro de marca).

## Categorías disponibles por supermercado

### DIA — paths verificados

Los cluster IDs numéricos (573, 574...) **ya no funcionan**. Usar solo paths:

| key | path |
|---|---|
| galletitas | `almacen/galletitas` |
| golosinas | `almacen/golosinas` |
| chocolates | `almacen/chocolates` |
| cereales | `almacen/cereales-y-barras` |
| aceites | `almacen/aceites-y-condimentos` |
| arroz | `almacen/arroz-y-legumbres` |
| fideos | `almacen/fideos` |
| aderezos | `almacen/aderezos` |
| azucar | `almacen/azucar` |
| legumbres | `almacen/legumbres` |
| caramelos | `almacen/caramelos` |
| agua | `bebidas/agua` |
| gaseosas | `bebidas/gaseosas` |
| jugos | `bebidas/jugos-y-aguas-saborizadas` |
| cerveza | `bebidas/cervezas` |
| vino | `bebidas/vinos` |
| leche | `lacteos-y-frescos/leche` |
| yogur | `lacteos-y-frescos/yogures` |
| quesos | `lacteos-y-frescos/quesos` |
| **almacen** | *(alias que combina 10 subcategorías automáticamente)* |
| **bebidas** | *(alias que combina 4 subcategorías automáticamente)* |
| **lacteos** | *(alias que combina 3 subcategorías automáticamente)* |

### Carrefour — paths

| key | path |
|---|---|
| snacks | `almacen/snacks` |
| galletitas | `almacen/galletitas` |
| almacen | `almacen` |
| bebidas | `bebidas` |
| lacteos | `lacteos-y-frescos` |
| carnes | `carnes-y-pescados` |
| frutas | `frutas-y-verduras` |
| limpieza | `limpieza-del-hogar` |
| perfumeria | `perfumeria-y-cuidado-personal` |

> Si el VTEX path devuelve HTTP 206 (sin resultados), el scraper hace fallback automático al endpoint de Intelligent Search.

### Coto — términos de búsqueda

El endpoint `/sitios/cdigi/browse?Ntt=<term>&format=json` acepta tanto nombres de categoría como nombres de marca:

| key | término |
|---|---|
| snacks | `snacks` |
| almacen | `almacen` |
| galletitas | `galletitas` |
| golosinas | `golosinas` |
| bebidas | `bebidas` |
| lacteos | `lacteos` |
| limpieza | `limpieza` |
| perfumeria | `perfumeria` |

### La Anónima — paths de categoría

URL pattern: `laanonima.com.ar/<slug>/nNivel_ID/`

| key | path |
|---|---|
| snacks | `snacks/n2_522` |
| galletitas_dulces | `galletitas-dulces/n3_598` |
| galletitas_saladas | `galletitas-saladas-y-tostadas/n3_599` |
| golosinas | `golosinas/n3_845` |
| chocolates | `chocolates/n3_844` |
| cereales | `cereales/n3_842` |
| conservas | `conservas-y-encurtidos/n2_527` |
| pastas | `arroz-pastas-y-legumbres/n2_526` |
| almacen | `almacen/n1_512` |
| gaseosas | `gaseosas/n2_541` |
| cervezas | `cervezas/n2_540` |
| bebidas | `bebidas/n1_513` |
| lacteos | `lacteos-y-frescos/n1_516` |
| limpieza | `limpieza/n1_514` |
| perfumeria | `perfumeria/n1_820` |

### Agregar una categoría nueva desde URL

| Super | Ejemplo URL | Qué extraer |
|---|---|---|
| DIA | `.../almacen/galletitas/...` | path: `almacen/galletitas` |
| Carrefour | `.../almacen/snacks/...` | path: `almacen/snacks` |
| Coto | `...?Ntt=golosinas...` | término: `golosinas` |
| La Anónima | `.../snacks/n2_522/` | path: `snacks/n2_522` |

## Formato de salida JSON

```json
[
  {
    "supermercado": "Supermercados DIA",
    "categoria": "golosinas",
    "nombre": "Alfajor Triple Chocolate Milka 55 g.",
    "marca": "Milka",
    "precio": 1850.0,
    "precio_lista": 2200.0,
    "url": "https://diaonline.supermercadosdia.com.ar/...",
    "timestamp": "2026-04-16T18:30:00"
  }
]
```

> `precio_lista` en La Anónima corresponde al precio anterior (tachado) cuando hay oferta activa.

## Archivos generados

- `productos_dia.json` — parcial DIA
- `productos_carrefour.json` — parcial Carrefour
- `productos_coto.json` — parcial Coto
- `productos_laanonima.json` — parcial La Anónima
- `productos_supermercados.json` — **todos unificados** (default)

## Workflow para el agente

1. Verificar que `scraper.py` esté presente. Si no, copiarlo desde `scripts/scraper.py`
2. Verificar dependencias: `pip show httpx beautifulsoup4`
3. Si falta alguna: `pip install httpx beautifulsoup4`
4. Ejecutar con los parámetros que pidió el usuario
5. Reportar: total de productos obtenidos, desglose por supermercado, path del archivo

## Errores comunes

- **HTTP 429** → rate limiting. Esperar 30s y reintentar.
- **HTTP 206 en DIA** → el path de categoría no existe o el cluster ID está deprecado. Usar path verificado de la tabla de arriba.
- **HTTP 206 en Carrefour** → el VTEX path no funciona; el scraper hace fallback automático a Intelligent Search.
- **0 productos en Coto** → el término de búsqueda no matchea. Probar directamente con el nombre de marca (ej: `krachitos` en lugar de `snacks`).
- **0 productos en La Anónima** → el sitio puede estar en mantenimiento. Reintentar en unos minutos.
- **ImportError: No module named 'bs4'** → `pip install beautifulsoup4 --break-system-packages`
