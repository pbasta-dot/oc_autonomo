# oc/flow.py
from __future__ import annotations

from config import EMPRESAS, CONDICION_PAGO_DEFAULT, ENTREGA_PREDEFINIDA, IVA_TASA
from oc.models import OrdenCompra, ItemOC
from oc.proveedores_ui import buscar_y_seleccionar_proveedor


def _input_no_vacio(msg: str) -> str:
    while True:
        v = input(msg).strip()
        if v:
            return v
        print("⚠️ Campo obligatorio.")


def _input_float(msg: str) -> float:
    while True:
        raw = input(msg).strip()
        try:
            # soporta 25.000 o 25,000 o 25000
            s = raw
            if "." in s and "," in s:
                s = s.replace(".", "").replace(",", ".")
            elif "," in s and "." not in s:
                s = s.replace(",", ".")
            return float(s)
        except Exception:
            print("⚠️ Ingresa un número válido (ej: 2 | 2,5 | 25000 | 25.000).")


def _input_nombre_archivo(oc: OrdenCompra, emp_key: str) -> str:
    """
    Nombre archivo:
      - Empresa 1 => RN
      - Empresa 2 => RT
    Formato: "RN - PROVEEDOR - CC"
    """
    pref = "RN" if emp_key == "1" else "RT"

    prov = getattr(oc, "proveedor", {}) or {}
    prov_nombre = (prov.get("razon_social") or prov.get("nombre") or "").strip()

    cc = (getattr(oc, "centro_costo", "") or "").strip()

    sugerido = f"{pref} - {prov_nombre} - {cc}".strip()
    nombre = input(f"\nNombre archivo (Enter = {sugerido}): ").strip()
    return nombre if nombre else sugerido


def crear_orden_compra(usuario=None) -> OrdenCompra:
    oc = OrdenCompra()

    # 1) Empresa emisora (dict para el menú)
    print("\n=== Empresa emisora ===")
    for k, e in EMPRESAS.items():
        print(f"{k}) {e.get('nombre', '')} ({e.get('rut', '')})")

    emp_key = _input_no_vacio("Selecciona empresa (ej: 1): ")
    if emp_key not in EMPRESAS:
        print("⚠️ Empresa no válida, se usará la 1.")
        emp_key = "1"

    oc.emp_key = emp_key  # ✅ guardar para usarlo al final / en el runner

    emp = EMPRESAS[emp_key]
    oc.empresa = {
        "nombre": emp.get("nombre", ""),
        "rut": emp.get("rut", ""),
        "giro": emp.get("giro", ""),
        "direccion": emp.get("direccion", ""),
        # D7 en Excel usa empresa["extra"], aquí lo mapeamos al correo
        "extra": emp.get("correo", ""),
    }

    # 2) Proveedor
    print("\n=== Proveedor ===")
    prov = buscar_y_seleccionar_proveedor()
    oc.proveedor = prov or {}

    # 3) Cotización
    print("\n=== Cotización ===")
    oc.cotizacion = input("N° Cotización (opcional): ").strip()

    # 4) Condición de pago
    print("\n=== Condición de pago ===")
    cp = input(f"Condición de pago (Enter = {CONDICION_PAGO_DEFAULT}): ").strip()
    oc.condicion_pago = cp if cp else CONDICION_PAGO_DEFAULT

    # 5) Información de entrega
    print("\n=== Información de entrega ===")
    oc.entrega = {
        "direccion": input("Dirección entrega (opcional): ").strip() or ENTREGA_PREDEFINIDA.get("direccion", ""),
        "contacto": input("Persona contacto (Enter = default): ").strip() or ENTREGA_PREDEFINIDA.get("contacto", ""),
        "telefono": input("Teléfono (Enter = default): ").strip() or ENTREGA_PREDEFINIDA.get("telefono", ""),
        "correo": input("Correo (Enter = default): ").strip() or ENTREGA_PREDEFINIDA.get("correo", ""),
    }

    # 6) Centro de costo / solicitante
    print("\n=== Interno ===")
    oc.centro_costo = _input_no_vacio("Centro de costo: ")
    oc.solicitante = _input_no_vacio("Nombre solicitante: ")

    # IVA: por defecto CON IVA (S)
    while True:
        r = input("¿OC con IVA? (S/N) [Enter = S]: ").strip().lower()
        if r == "":
            oc.con_iva = True
            break
        if r in ("s", "si", "sí"):
            oc.con_iva = True
            break
        if r in ("n", "no"):
            oc.con_iva = False
            break
        print("❌ Respuesta inválida. Usa S o N.")

    # 7) Ítems
    print("\n=== Ítems ===")
    while True:
        codigo = input("Código (Enter para terminar): ").strip()
        if not codigo:
            break
        desc = _input_no_vacio("Descripción: ")
        cantidad = _input_float("Cantidad: ")
        unit = _input_float("Valor unitario: ")

        oc.items.append(
            ItemOC(
                codigo=codigo,
                descripcion=desc,
                cantidad=cantidad,
                precio_unitario=unit,
            )
        )
        print("✅ Ítem agregado.\n")

    # 8) Totales para resumen del menú
    neto = sum(i.subtotal for i in oc.items)

    if getattr(oc, "con_iva", True):
        iva = round(neto * float(IVA_TASA), 2)
    else:
        iva = 0.0

    total = round(neto + iva, 2)

    oc.neto = round(neto, 2)
    oc.iva = iva
    oc.total = total

    # 9) Nombre de archivo (se usará al generar Excel)
    oc.nombre_archivo_base = _input_nombre_archivo(oc, oc.emp_key)

    return oc
