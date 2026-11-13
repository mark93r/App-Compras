import json
import sys
from pathlib import Path
from supermercapy import search_all

# ============================================================
# CONFIGURACIÓN
# ============================================================
# Lista de productos que quieres comparar.
# Puedes añadir, quitar o modificar los términos libremente.
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

# Código postal para localizar precios de tu zona
POSTAL_CODE = "28001"

# Máximo de resultados por producto y supermercado
PAGE_SIZE = 5


# ============================================================
# LÓGICA PRINCIPAL
# ============================================================
def main():
    resultados = []

    for termino in PRODUCTOS:
        print(f"Buscando: {termino}...", file=sys.stderr)

        try:
            result = search_all(termino, postal_code=POSTAL_CODE, page_size=PAGE_SIZE)
        except Exception as e:
            print(f"❌ Error crítico buscando '{termino}': {type(e).__name__}: {e}", file=sys.stderr)
            continue

        for store, product in result.products:
            # Comprobar que el producto tiene estructura de precio válida
            if not hasattr(product, "price") or not hasattr(product.price, "amount"):
                continue

            precio = product.price.amount

            # Saltar productos sin precio (amount == None)
            if precio is None:
                print(f"⚠️  Omitido '{product.name}' ({store}): precio no disponible", file=sys.stderr)
                continue

            # Convertir a float con protección
            try:
                precio_float = float(precio)
            except (TypeError, ValueError):
                print(f"⚠️  Omitido '{product.name}' ({store}): precio inválido ({precio})", file=sys.stderr)
                continue

            # Saltar precios no positivos por seguridad
            if precio_float <= 0:
                continue

            resultados.append({
                "store": store.capitalize(),
                "product": product.name,
                "price": precio_float,
                "unit": getattr(product, "unit", "") or "",
                "search_term": termino,
            })

        # Reportar supermercados que fallaron en esta búsqueda (sin detener el script)
        for entry in result.failed:
            print(
                f"⚠️  Falló {entry.store} para '{termino}': {entry.error_type} - {entry.reason}",
                file=sys.stderr,
            )

    # ========================================================
    # DEDUPLICACIÓN Y ORDENACIÓN
    # ========================================================
    vistos = set()
    unicos = []
    for item in resultados:
        key = (item["store"], item["product"])
        if key not in vistos:
            vistos.add(key)
            unicos.append(item)

    unicos.sort(key=lambda x: (x["search_term"], x["price"]))

    # ========================================================
    # GUARDAR JSON
    # ========================================================
    output_path = Path("precios.json")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(unicos, f, ensure_ascii=False, indent=2)

    print(f"✅ Generados {len(unicos)} registros en {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
