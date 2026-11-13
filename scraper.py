import json
import sys
from pathlib import Path
from supermercapy import search_all

# ============================================================
# CONFIGURACIÓN
# ============================================================
# Lista ampliada de productos para capturar más variedad
PRODUCTOS = [
    # Lácteos y huevos
    "leche entera", "leche semidesnatada", "leche desnatada", "yogur natural", "queso curado", "huevos frescos",
    # Despensa
    "arroz redondo", "arroz largo", "pasta espaguetis", "pasta macarrones", "aceite de oliva virgen extra", "aceite de girasol",
    "tomate frito", "atún en aceite", "atún al natural", "legumbres cocidas", "harina de trigo", "azúcar blanco", "sal fina",
    # Carnicería y pescadería
    "pechuga de pollo", "muslos de pollo", "carne picada", "lomo de cerdo", "salmón fresco", "merluza",
    # Frutería y verdulería
    "manzanas", "plátanos", "naranjas", "peras", "tomates", "cebollas", "patatas", "zanahorias", "lechuga",
    # Panadería y bollería
    "pan de molde", "pan de barra", "croissants", "magdalenas",
    # Bebidas
    "agua mineral", "zumo de naranja", "refresco de cola", "cerveza", "vino tinto",
    # Limpieza e higiene
    "detergente ropa", "lavavajillas líquido", "limpiacristales", "papel higiénico", "gel de ducha", "pasta de dientes",
]

# Código postal para localizar precios de tu zona
POSTAL_CODE = "28001"
# Máximo de resultados por producto y supermercado
PAGE_SIZE = 3


def main():
    resultados = []
    errores_totales = []

    for termino in PRODUCTOS:
        print(f"Buscando: {termino}...", file=sys.stderr)

        try:
            result = search_all(termino, postal_code=POSTAL_CODE, page_size=PAGE_SIZE)
        except Exception as e:
            error_msg = f"Error crítico en search_all para '{termino}': {type(e).__name__}: {e}"
            print(f"❌ {error_msg}", file=sys.stderr)
            errores_totales.append(error_msg)
            continue

        # Procesar productos encontrados
        for store, product in result.products:
            if not hasattr(product, "price") or not hasattr(product.price, "amount"):
                continue
            precio = product.price.amount
            if precio is None:
                continue
            try:
                precio_float = float(precio)
            except (TypeError, ValueError):
                continue
            if precio_float <= 0:
                continue

            resultados.append({
                "store": store.capitalize(),
                "product": product.name,
                "price": precio_float,
                "unit": getattr(product, "unit", "") or "",
                "search_term": termino,
            })

        # Reportar qué supermercados fallaron para este término (ej. Carrefour)
        for entry in result.failed:
            error_detallado = f"{entry.store} falló para '{termino}': {entry.error_type} - {entry.reason}"
            print(f"⚠️  {error_detallado}", file=sys.stderr)
            errores_totales.append(error_detallado)

    # Deduplicar y ordenar
    vistos = set()
    unicos = []
    for item in resultados:
        key = (item["store"], item["product"])
        if key not in vistos:
            vistos.add(key)
            unicos.append(item)

    unicos.sort(key=lambda x: (x["search_term"], x["price"]))

    # Guardar JSON
    output_path = Path("precios.json")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(unicos, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Generados {len(unicos)} registros en {output_path}", file=sys.stderr)
    
    if errores_totales:
        print(f"\n⚠️  Se produjeron {len(errores_totales)} errores/fallos parciales durante el scraping. Revisa el log para más detalles.", file=sys.stderr)


if __name__ == "__main__":
    main()
