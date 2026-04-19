"""
Scraper de Supermercados Argentina — v2 (sin browser)
Soporta: DIA, Carrefour, Coto y La Anónima
Salida: JSON unificado con nombre y precio

Sin dependencias de Playwright/Crawl4AI. Solo httpx + beautifulsoup4.

Uso:
    python scraper.py                              # Scrapea todos, todas las categorías
    python scraper.py --super dia coto             # Supermercados específicos
    python scraper.py --categoria bebidas lacteos  # Filtrar por categoría
    python scraper.py --marcas lays krachitos      # Buscar marcas específicas (todos los supers)
    python scraper.py --max 200 --output out.json  # Límite y archivo de salida
    python scraper.py --super carrefour --marcas pehuamar quento --max 100
"""

import asyncio
import json
import argparse
import os
import time
from datetime import datetime
from collections import Counter

import httpx
from bs4 import BeautifulSoup
# ScraperAPI key para La Anónima (CloudFront WAF bloquea IPs de datacenter)
SCRAPERAPI_KEY = "41bdfa3935e60c7402a063aaf31a1c11"

def _scraperapi_url(target_url: str) -> str:
    from urllib.parse import quote
    return f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={quote(target_url, safe='')}&country_code=ar&premium=true"


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE SUPERMERCADOS
# ─────────────────────────────────────────────────────────────────────────────

SUPERS = {
    "dia": {
        "nombre": "Supermercados DIA",
        "plataforma": "vtex",
        "base_url": "https://diaonline.supermercadosdia.com.ar",
        # Categorías por path de URL. Los cluster IDs numéricos (573, 574...) ya no funcionan.
        # Paths verificados que retornan productos:
        "categorias": {
            "galletitas":  "almacen/galletitas",
            "golosinas":   "almacen/golosinas",
            "chocolates":  "almacen/chocolates",
            "cereales":    "almacen/cereales-y-barras",
            "aceites":     "almacen/aceites-y-condimentos",
            "cafe":        "almacen/cafe-te-e-infusiones",
            "desayuno":    "almacen/desayuno-y-merienda",
            "arroz":       "almacen/arroz-y-legumbres",
            "fideos":      "almacen/fideos",
            "azucar":      "almacen/azucar",
            "legumbres":   "almacen/legumbres",
            "aderezos":    "almacen/aderezos",
            "caramelos":   "almacen/caramelos",
            "agua":        "bebidas/agua",
            "gaseosas":    "bebidas/gaseosas",
            "jugos":       "bebidas/jugos-y-aguas-saborizadas",
            "cerveza":     "bebidas/cervezas",
            "vino":        "bebidas/vinos",
            "leche":       "lacteos-y-frescos/leche",
            "yogur":       "lacteos-y-frescos/yogures",
            "quesos":      "lacteos-y-frescos/quesos",
            "snacks":        "almacen/picadas/snacks",
            # Alias generales -> lista de paths a combinar
            "almacen": [
                "almacen/galletitas", "almacen/golosinas", "almacen/chocolates",
                "almacen/arroz-y-legumbres", "almacen/fideos", "almacen/aderezos",
                "almacen/azucar", "almacen/legumbres", "almacen/caramelos",
                "almacen/aceites-y-condimentos",
            ],
            "bebidas": [
                "bebidas/agua", "bebidas/gaseosas",
                "bebidas/jugos-y-aguas-saborizadas", "bebidas/cervezas",
            ],
            "lacteos": [
                "lacteos-y-frescos/leche", "lacteos-y-frescos/yogures",
                "lacteos-y-frescos/quesos",
            ],
        },
    },
    "carrefour": {
        "nombre": "Carrefour Argentina",
        "plataforma": "vtex_is",
        "base_url": "https://www.carrefour.com.ar",
        "categorias": {
            "snacks":     "almacen/snacks",
            "galletitas": "almacen/galletitas",
            "almacen":    "almacen",
            "bebidas":    "bebidas",
            "lacteos":    "lacteos-y-frescos",
            "carnes":     "carnes-y-pescados",
            "frutas":     "frutas-y-verduras",
            "limpieza":   "limpieza-del-hogar",
            "perfumeria": "perfumeria-y-cuidado-personal",
        },
    },
    "coto": {
        "nombre": "Coto Digital",
        "plataforma": "atg_browse",
        "base_url": "https://www.cotodigital.com.ar",
        "categorias": {
            "snacks":     "snacks",
            "almacen":    "almacen",
            "galletitas": "galletitas",
            "golosinas":  "golosinas",
            "bebidas":    "bebidas",
            "lacteos":    "lacteos",
            "limpieza":   "limpieza",
            "perfumeria": "perfumeria",
        },
    },
    "laanonima": {
        "nombre": "La Anónima",
        "plataforma": "html_attrs",
        "base_url": "https://www.laanonima.com.ar",
        "categorias": {
            "snacks":             "snacks/n2_522",
            "galletitas_dulces":  "galletitas-dulces/n3_598",
            "galletitas_saladas": "galletitas-saladas-y-tostadas/n3_599",
            "golosinas":          "golosinas/n3_845",
            "chocolates":         "chocolates/n3_844",
            "cereales":           "cereales/n3_842",
            "conservas":          "conservas-y-encurtidos/n2_527",
            "pastas":             "arroz-pastas-y-legumbres/n2_526",
            "aceites":            "aceite-aderezos-y-condimentos/n2_524",
            "almacen":            "almacen/n1_512",
            "gaseosas":           "gaseosas/n2_541",
            "cervezas":           "cervezas/n2_540",
            "aguas_jugos":        "aguas-y-jugos/n2_543",
            "vinos":              "vinos-y-espumantes/n2_542",
            "bebidas":            "bebidas/n1_513",
            "leche":              "leches/n3_722",
            "yogur":              "yogures/n3_724",
            "quesos":             "quesos/n3_731",
            "lacteos":            "lacteos-y-frescos/n1_516",
            "limpieza":           "limpieza/n1_514",
            "perfumeria":         "perfumeria/n1_820",
            "carniceria":         "carniceria/n1_518",
            "frutas_verduras":    "frutas-y-verduras/n1_517",
            "congelados":         "congelados/n1_766",
        },
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "es-AR,es;q=0.9",
}


# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────────────────────

def _parse_precio(raw) -> float | None:
    if raw is None:
        return None
    cleaned = str(raw).replace("$", "").replace(" ", "").replace(".", "").replace(",", ".").strip()
    try:
        v = float(cleaned)
        return v if v > 0 else None
    except ValueError:
        return None


def _make_producto(supermercado, categoria, nombre, marca, precio, precio_lista, url):
    return {
        "supermercado": supermercado,
        "categoria": categoria,
        "nombre": (nombre or "").strip(),
        "marca": (marca or "").strip() or None,
        "precio": precio,
        "precio_lista": precio_lista,
        "url": url,
        "timestamp": datetime.now().isoformat(),
    }


def _marca_match(nombre: str, marca: str, marcas: list[str]) -> bool:
    nombre_l = nombre.lower()
    marca_l = marca.lower()
    return any(m.lower() in nombre_l or m.lower() in marca_l for m in marcas)


def deduplicar(productos: list[dict]) -> list[dict]:
    seen = set()
    uniq = []
    for p in productos:
        key = (p["supermercado"], p["nombre"], p["precio"])
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    return uniq


# ─────────────────────────────────────────────────────────────────────────────
# SCRAPER DIA  (VTEX API -- path-based o busqueda por ft=)
# ─────────────────────────────────────────────────────────────────────────────

async def scrape_dia(categorias, marcas, max_productos):
    cfg = SUPERS["dia"]
    base = cfg["base_url"]
    todos = []

    async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
        if marcas:
            for marca in marcas:
                print(f"  [DIA] Buscando: {marca} ...")
                offset = 0
                while offset < max_productos:
                    url = (f"{base}/api/catalog_system/pub/products/search"
                           f"?ft={marca}&_from={offset}&_to={min(offset+49, max_productos-1)}")
                    try:
                        resp = await client.get(url)
                        if resp.status_code != 200:
                            break
                        products = resp.json()
                        if not products:
                            break
                        for p in products:
                            nombre = p.get("productName", "")
                            brand = p.get("brand", "")
                            if not _marca_match(nombre, brand, marcas):
                                continue
                            item = p.get("items", [{}])[0]
                            seller = item.get("sellers", [{}])[0].get("commertialOffer", {})
                            todos.append(_make_producto(
                                cfg["nombre"], "marcas", nombre, brand,
                                seller.get("Price"), seller.get("ListPrice"),
                                f"{base}{p.get('link', '')}",
                            ))
                        offset += 50
                        if len(products) < 50:
                            break
                        await asyncio.sleep(0.25)
                    except httpx.RequestError as e:
                        print(f"    Error: {e}")
                        break
        else:
            cats = cfg["categorias"]
            target = {k: v for k, v in cats.items()
                      if not categorias or k in categorias}
            for cat_nombre, cat_val in target.items():
                paths = cat_val if isinstance(cat_val, list) else [cat_val]
                for path in paths:
                    print(f"  [DIA] {cat_nombre} ({path}) ...")
                    offset = 0
                    while offset < max_productos:
                        url = (f"{base}/api/catalog_system/pub/products/search/{path}/"
                               f"?_from={offset}&_to={min(offset+49, max_productos-1)}")
                        try:
                            resp = await client.get(url)
                            if resp.status_code != 200:
                                break
                            products = resp.json()
                            if not products:
                                break
                            for p in products:
                                item = p.get("items", [{}])[0]
                                seller = item.get("sellers", [{}])[0].get("commertialOffer", {})
                                todos.append(_make_producto(
                                    cfg["nombre"], cat_nombre,
                                    p.get("productName", ""), p.get("brand", ""),
                                    seller.get("Price"), seller.get("ListPrice"),
                                    f"{base}{p.get('link', '')}",
                                ))
                            offset += 50
                            if len(products) < 50:
                                break
                            await asyncio.sleep(0.25)
                        except httpx.RequestError as e:
                            print(f"    Error: {e}")
                            break
    return todos


# ─────────────────────────────────────────────────────────────────────────────
# SCRAPER CARREFOUR  (Intelligent Search + VTEX path fallback)
# ─────────────────────────────────────────────────────────────────────────────

async def scrape_carrefour(categorias, marcas, max_productos):
    cfg = SUPERS["carrefour"]
    base = cfg["base_url"]
    todos = []

    async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
        if marcas:
            for marca in marcas:
                print(f"  [Carrefour] Buscando: {marca} ...")
                page = 1
                while True:
                    url = (f"{base}/api/io/_v/api/intelligent-search/product_search"
                           f"?query={marca}&count=50&page={page}")
                    try:
                        resp = await client.get(url)
                        if resp.status_code != 200:
                            break
                        items = resp.json().get("products", [])
                        if not items:
                            break
                        for p in items:
                            brand = p.get("brand", "")
                            nombre = p.get("productName", "")
                            if not _marca_match(nombre, brand, marcas):
                                continue
                            sku = p.get("items", [{}])[0]
                            seller = sku.get("sellers", [{}])[0].get("commertialOffer", {})
                            todos.append(_make_producto(
                                cfg["nombre"], "marcas", nombre, brand,
                                seller.get("Price"), seller.get("ListPrice"),
                                f"{base}/{p.get('linkText', '')}/p",
                            ))
                        if len(items) < 50 or len(todos) >= max_productos:
                            break
                        page += 1
                        await asyncio.sleep(0.25)
                    except httpx.RequestError as e:
                        print(f"    Error: {e}")
                        break
        else:
            cats = cfg["categorias"]
            target = {k: v for k, v in cats.items()
                      if not categorias or k in categorias}
            for cat_nombre, path in target.items():
                print(f"  [Carrefour] {cat_nombre} ...")
                offset = 0
                while offset < max_productos:
                    url = (f"{base}/api/catalog_system/pub/products/search/{path}/"
                           f"?_from={offset}&_to={min(offset+49, max_productos-1)}")
                    try:
                        resp = await client.get(url)
                        if resp.status_code not in (200, 206):
                            break
                        if resp.status_code == 206:
                            # Fallback: Intelligent Search por nombre de categoría
                            url2 = (f"{base}/api/io/_v/api/intelligent-search/product_search"
                                    f"?query={cat_nombre}&count=50&page=1")
                            resp2 = await client.get(url2)
                            if resp2.status_code == 200:
                                for p in resp2.json().get("products", []):
                                    sku = p.get("items", [{}])[0]
                                    seller = sku.get("sellers", [{}])[0].get("commertialOffer", {})
                                    todos.append(_make_producto(
                                        cfg["nombre"], cat_nombre,
                                        p.get("productName", ""), p.get("brand", ""),
                                        seller.get("Price"), seller.get("ListPrice"),
                                        f"{base}/{p.get('linkText', '')}/p",
                                    ))
                            break
                        products = resp.json()
                        if not products:
                            break
                        for p in products:
                            item = p.get("items", [{}])[0]
                            seller = item.get("sellers", [{}])[0].get("commertialOffer", {})
                            todos.append(_make_producto(
                                cfg["nombre"], cat_nombre,
                                p.get("productName", ""), p.get("brand", ""),
                                seller.get("Price"), seller.get("ListPrice"),
                                f"{base}{p.get('link', '')}",
                            ))
                        offset += 50
                        if len(products) < 50:
                            break
                        await asyncio.sleep(0.25)
                    except httpx.RequestError as e:
                        print(f"    Error: {e}")
                        break
    return todos


# ─────────────────────────────────────────────────────────────────────────────
# SCRAPER COTO  (Oracle ATG -- /browse?format=json, sin browser)
# ─────────────────────────────────────────────────────────────────────────────

def _coto_results_list(obj):
    if isinstance(obj, dict):
        if obj.get("@type") == "COTO_ResultsList":
            return obj
        for v in obj.values():
            res = _coto_results_list(v)
            if res:
                return res
    elif isinstance(obj, list):
        for item in obj:
            res = _coto_results_list(item)
            if res:
                return res
    return None


async def scrape_coto(categorias, marcas, max_productos):
    cfg = SUPERS["coto"]
    base = cfg["base_url"]
    cats = cfg["categorias"]
    todos = []

    terminos = (
        {m: m for m in marcas}
        if marcas
        else {k: v for k, v in cats.items() if not categorias or k in categorias}
    )

    async with httpx.AsyncClient(headers=HEADERS, timeout=60, follow_redirects=True) as client:
        for tag, term in terminos.items():
            print(f"  [Coto] Buscando: {tag} ...")
            offset = 0
            page_size = 48
            while offset < max_productos:
                target_url = (f"{base}/sitios/cdigi/browse"
                              f"?Ntt={term}&No={offset}&Nrpp={page_size}&format=json")
                url = _scraperapi_url(target_url)
                try:
                    resp = await client.get(url)
                    if resp.status_code != 200:
                        print(f"    HTTP {resp.status_code} — saltando.")
                        break
                    rl = _coto_results_list(resp.json())
                    if not rl or not rl.get("records"):
                        break
                    total = rl.get("totalNumRecs", 0)
                    for rec in rl["records"]:
                        nombre_top = (
                            rec.get("attributes", {}).get("product.displayName") or [""]
                        )[0]
                        for inner in rec.get("records", [rec]):
                            attrs = inner.get("attributes", {})
                            marca = (attrs.get("product.brand") or [""])[0].strip()
                            nombre = (
                                attrs.get("product.description")
                                or attrs.get("sku.displayName")
                                or [nombre_top]
                            )[0].strip()
                            if marcas and not _marca_match(nombre, marca, marcas):
                                continue
                            precio_raw = (attrs.get("sku.referencePrice") or [None])[0]
                            detail = inner.get("detailsAction", {}).get("recordState", "")
                            todos.append(_make_producto(
                                cfg["nombre"], tag, nombre, marca or None,
                                _parse_precio(precio_raw), None,
                                f"{base}/sitios/cdigi/producto/{detail}" if detail else "",
                            ))
                    if rl.get("lastRecNum", 0) >= total:
                        break
                    offset += page_size
                    await asyncio.sleep(0.3)
                except httpx.RequestError as e:
                    print(f"    Error: {e}")
                    break
    return todos


# ─────────────────────────────────────────────────────────────────────────────
# SCRAPER LA ANONIMA  (HTML server-side -- data-* attrs en cada producto)
# ─────────────────────────────────────────────────────────────────────────────

async def scrape_laanonima(categorias, marcas, max_productos):
    cfg = SUPERS["laanonima"]
    base = cfg["base_url"]
    cats = cfg["categorias"]
    todos = []

    # La Anónima usa CloudFront WAF que bloquea IPs de datacenter.
    # Todas las requests se rutean por ScraperAPI (proxy residencial).
    async with httpx.AsyncClient(headers=HEADERS, timeout=60, follow_redirects=True) as client:
        target = {k: v for k, v in cats.items()
                  if not categorias or k in categorias}
        for cat_nombre, cat_path in target.items():
            target_url = f"{base}/{cat_path}/"
            url = _scraperapi_url(target_url)
            print(f"  [La Anonima] {cat_nombre} ...")
            intentos = 0
            while intentos < 3:
                try:
                    resp = await client.get(url)
                    if resp.status_code == 403:
                        print(f"    HTTP 403 — reintentando en 5s ...")
                        await asyncio.sleep(5)
                        intentos += 1
                        continue
                    if resp.status_code != 200:
                        print(f"    HTTP {resp.status_code} — saltando.")
                        break
                    soup = BeautifulSoup(resp.text, "html.parser")
                    cards = soup.find_all("a", attrs={"data-nombre": True, "data-marca": True})
                    if not cards:
                        print(f"    Sin productos en HTML.")
                        break
                    count = 0
                    for card in cards[:max_productos]:
                        marca = card.get("data-marca", "").strip()
                        nombre = card.get("data-nombre", "").strip()
                        if marcas and not _marca_match(nombre, marca, marcas):
                            continue
                        precio = _parse_precio(
                            card.get("data-precio_oferta") or card.get("data-precio")
                        )
                        precio_anterior = _parse_precio(card.get("data-precio_anterior"))
                        href = card.get("href", "")
                        todos.append(_make_producto(
                            cfg["nombre"], cat_nombre, nombre, marca or None,
                            precio,
                            precio_anterior if precio_anterior != precio else None,
                            f"{base}{href}" if href.startswith("/") else href,
                        ))
                        count += 1
                    print(f"    {count} productos")
                    await asyncio.sleep(0.5)
                    break
                except httpx.RequestError as e:
                    print(f"    Error: {e}")
                    break
    return todos


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def guardar_json(datos, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"  Guardado: {path}  ({len(datos)} productos)")


async def main():
    parser = argparse.ArgumentParser(description="Scraper supermercados Argentina -- sin browser")
    parser.add_argument("--super", nargs="+",
                        choices=["dia", "carrefour", "laanonima", "coto"],
                        default=["dia", "carrefour", "laanonima", "coto"])
    parser.add_argument("--categoria", nargs="+", default=["snacks"])
    parser.add_argument("--marcas", nargs="+")
    parser.add_argument("--max", type=int, default=200)
    parser.add_argument("--output", type=str, default="productos_supermercados.json")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  SCRAPER SUPERMERCADOS ARGENTINA v2 (sin browser)")
    print(f"  Supermercados : {', '.join(args.super)}")
    if args.categoria:
        print(f"  Categorias    : {', '.join(args.categoria)}")
    if args.marcas:
        print(f"  Marcas        : {', '.join(args.marcas)}")
    print(f"  Max. por super: {args.max}")
    print(f"{'='*60}\n")

    scrapers = {
        "dia":       scrape_dia,
        "carrefour": scrape_carrefour,
        "coto":      scrape_coto,
        "laanonima": scrape_laanonima,
    }

    todos = []
    t0 = time.time()

    for super_key in args.super:
        cfg = SUPERS[super_key]
        print(f"\n {cfg['nombre']}")
        try:
            resultado = await scrapers[super_key](args.categoria, args.marcas, args.max)
            resultado = deduplicar(resultado)
            print(f"  {len(resultado)} productos")
            todos.extend(resultado)
            guardar_json(resultado, f"productos_{super_key}.json")
        except Exception as e:
            print(f"  Error en {cfg['nombre']}: {e}")

    todos = deduplicar(todos)

    # Combinar con resultados previos de otros supers (para runs parciales)
    fecha_hoy = datetime.now().strftime("%Y%m%d")
    todos_path = f"resultados/todos_{fecha_hoy}.json"
    if os.path.exists(todos_path):
        with open(todos_path, encoding="utf-8") as f:
            previos = json.load(f)
        supers_actuales = {p["supermercado"] for p in todos}
        previos_otros = [p for p in previos if p["supermercado"] not in supers_actuales]
        todos = deduplicar(previos_otros + todos)

    print(f"\n{'='*60}")
    print(f"  TOTAL: {len(todos)} productos | Tiempo: {time.time() - t0:.1f}s")
    os.makedirs("resultados", exist_ok=True)
    guardar_json(todos, todos_path)
    guardar_json(todos, args.output)
    counts = Counter(p["supermercado"] for p in todos)
    print("\n  Desglose:")
    for nombre, count in counts.items():
        print(f"    {nombre}: {count}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
