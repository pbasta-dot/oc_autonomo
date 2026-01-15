# oc/flow.py
from __future__ import annotations

from config import EMPRESAS, CONDICION_PAGO_DEFAULT, ENTREGA_PREDEFINIDA
from oc.models import OrdenCompra, ItemOC

# Ajusta el import según tu proyecto
# Si tu función es "buscar_y_seleccionar_proveedor()", usa esa
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
            raw2 = raw.replace(".", "").replace(",", ".") if ("," in raw) else raw
            return float(raw2)
        except Exception:
            print("⚠️ Ingresa un número válido (ej: 2 o 2,5 o 25000).")


def crear_orden_compra() -> OrdenCompra:
    oc = OrdenCompra()

    # 1) Empresa emisora
    print("\n=== Empresa emisora ===")
    for k, e in EMPRESAS.items():
        print(f"{k}) {e['nombre']} ({e['rut']})")

    emp_key = _input_no_vacio("Selecciona empresa (1/2): ")
    if emp_key not in EMPRESAS:
        print("⚠️ Empresa no válida, se usará la 1.")
        emp_key = "1"

    emp = EMPRESAS[emp_key]
    oc.empresa_nombre = emp.get("nombre", "")
    oc.empresa_rut = emp.get("rut", "")
    oc.empresa_giro = emp.get("giro", "")
    oc.empresa_direccion = emp.get("direccion", "")
    oc.empresa_otro = emp.get("extra", "")

    # 2) Proveedor
    print("\n=== Proveedor ===")
    prov = buscar_y_seleccionar_proveedor()  # 👈 ajusta si tu función se llama distinto
    oc.proveedor = prov or {}

    # 3) Condición de pago
    print("\n=== Condición de pago ===")
    cp = input(f"Condición de pago (Enter = {CONDICION_PAGO_DEFAULT}): ").strip()
    oc.condicion_pago = cp if cp else CONDICION_PAGO_DEFAULT

    # 4) Información de entrega
    print("\n=== Información de entrega ===")
    oc.entrega_direccion = input("Dirección entrega (opcional): ").strip() or ENTREGA_PREDEFINIDA.get("direccion", "")
    oc.entrega_contacto = input("Persona contacto (Enter = default): ").strip() or ENTREGA_PREDEFINIDA.get("contacto", "")
    oc.entrega_telefono = input("Teléfono (Enter = default): ").strip() or ENTREGA_PREDEFINIDA.get("telefono", "")
    oc.entrega_correo = input("Correo (Enter = default): ").strip() or ENTREGA_PREDEFINIDA.get("correo", "")

    # 5) Centro de costo / solicitante / autoriza
    print("\n=== Interno ===")
    oc.centro_costo = _input_no_vacio("Centro de costo: ")
    oc.nombre_solicitante = _input_no_vacio("Nombre solicitante: ")
    oc.autoriza = _input_no_vacio("¿Quién autoriza?: ")

    # 6) Ítems
    print("\n=== Ítems ===")
    while True:
        codigo = input("Código (Enter para terminar): ").strip()
        if not codigo:
            break
        desc = _input_no_vacio("Descripción: ")
        cantidad = _input_float("Cantidad: ")
        unit = _input_float("Valor unitario: ")

        oc.items.append(ItemOC(
            codigo=codigo,
            descripcion=desc,
            cantidad=cantidad,
            valor_unitario=unit,
        ))
        print("✅ Ítem agregado.\n")

    if not oc.items:
        print("⚠️ No agregaste ítems. La OC saldrá sin detalle.")

    return oc
