import json
import sys
from pathlib import Path
from supermercapy import search_all

PRODUCTOS = [
    "leche entera",
    "arroz redondo",
    "aceite de oliva virgen extra",
    "huevos frescos",
    "pan de molde",
    "manzanas",
    "pechuga de pollo",
    "espaguetis",
    "tomate frito",
    "atún en aceite",
]

POSTAL_CODE = "28001"
PAGE_SIZE = 5

def main():
    resultados = []

    for termino in PRODUCTOS:
        print(f"Buscando: {termino}...", file=sys.stderr)
        try:
            result = search_all(termino, postal_code=POSTAL_CODE, page_size=PAGE_SIZE)
        except Exception as e:
            print(f"Error buscando '{termino}': {e}", file=sys.stderr)
            continue

        for store, product in result.products:
            if hasattr(product, "price") and hasattr(product.price, "amount"):
                precio = product.price.amount
            else:
                continue

            resultados.append({
                "store": store.capitalize(),
                "product": product.name,
                "price": float(precio),
                "unit": getattr(product, "unit", "") or "",
                "search_term": termino,
            })

    vistos = set()
    unicos = []
    for item in resultados:
        key = (item["store"], item["product"])
        if key not in vistos:
            vistos.add(key)
            unicos.append(item)

    unicos.sort(key=lambda x: (x["search_term"], x["price"]))

    output_path = Path("precios.json")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(unicos, f, ensure_ascii=False, indent=2)

    print(f"✅ Generados {len(unicos)} registros en {output_path}", file=sys.stderr)

if __name__ == "__main__":
    main()
