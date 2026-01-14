from datetime import datetime
from config import EMPRESAS, ENTREGA_PREDEFINIDA
from .models import Item, OrdenCompra
from .calc import calcular_totales
from .proveedores_ui import seleccionar_proveedor_antiguo, crear_proveedor_nuevo

FLOW_VERSION = "FLOW v4 - codigo item primero + solicitado/autorizado"

def pedir_opcion(msg: str, opciones_validas: set[str]) -> str:
    while True:
        val = input(msg).strip()
        if val in opciones_validas:
            return val
        print(f"Opción inválida. Opciones: {', '.join(sorted(opciones_validas))}")

def pedir_texto(msg: str, requerido=True) -> str:
    while True:
        val = input(msg).strip()
        if val or not requerido:
            return val
        print("Este campo es obligatorio.")

def pedir_float(msg: str) -> float:
    while True:
        raw = input(msg).strip().replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            print("Ingresa un número válido (ej: 2, 2.5, 10000).")

def pedir_empresa_emisora():
    print("\nEmpresa emisora:")
    for k, v in EMPRESAS.items():
        print(f"  {k}) {v['nombre']} ({v['rut']})")
    op = pedir_opcion("Selecciona 1 o 2: ", set(EMPRESAS.keys()))
    return EMPRESAS[op]

def pedir_cotizacion_opcional():
    print("\n¿Deseas ingresar COTIZACIÓN N°? (Opcional)")
    print("  1) Sí")
    print("  2) No")
    op = pedir_opcion("Selecciona 1 o 2: ", {"1", "2"})
    if op == "1":
        return pedir_texto("COTIZACIÓN N°: ", requerido=False).strip()
    return ""

def pedir_iva() -> bool:
    print("\n¿La OC va con IVA?")
    print("  1) Con IVA (19%)")
    print("  2) Sin IVA")
    op = pedir_opcion("Selecciona 1 o 2: ", {"1", "2"})
    return op == "1"

def elegir_proveedor():
    while True:
        print("\n=== Proveedor ===")
        print("1) Proveedor antiguo (buscar en proveedores.csv)")
        print("2) Proveedor nuevo (crear y guardar)")
        print("0) Volver")

        op = pedir_opcion("Selecciona una opción: ", {"0", "1", "2"})

        if op == "0":
            return None

        if op == "1":
            p = seleccionar_proveedor_antiguo()
            if p:
                return p

        if op == "2":
            p = crear_proveedor_nuevo()
            if p:
                return p

def pedir_items():
    print("\nIngreso de ítems (0 para terminar).")
    print("Orden de ingreso: Código (opcional) → Cantidad → Descripción → Valor unitario\n")

    items = []
    while True:
        # ✅ CODIGO PRIMERO
        codigo = pedir_texto("Código producto (opcional, enter para vacío / 0 para terminar): ", requerido=False)
        if codigo.strip() == "0":
            break

        cantidad = pedir_float("Cantidad: ")
        descripcion = pedir_texto("Descripción del ítem: ")
        valor = pedir_float("Valor unitario: ")

        items.append(Item(
            cantidad=cantidad,
            descripcion=descripcion,
            valor_unitario=valor,
            codigo=codigo
        ))
        print("Ítem agregado.\n")

    return items

def crear_oc():
    proveedor = elegir_proveedor()
    if not proveedor:
        return None

    empresa_emisora = pedir_empresa_emisora()

    centro_costo = pedir_texto("Centro de costo: ")

    solicitado_por = pedir_texto("Solicitado por: ")
    autorizado_por = pedir_texto("Autorizado por: ")

    cotizacion_n = pedir_cotizacion_opcional()
    con_iva = pedir_iva()
    items = pedir_items()

    numero = datetime.now().strftime("DRAFT-%Y%m%d-%H%M%S")

    oc = OrdenCompra(
        numero=numero,
        fecha=datetime.now(),
        proveedor=proveedor,
        empresa_emisora=empresa_emisora,
        centro_costo=centro_costo,
        solicitado_por=solicitado_por,
        autorizado_por=autorizado_por,
        con_iva=con_iva,
        cotizacion_n=cotizacion_n,
        entrega=ENTREGA_PREDEFINIDA,
        items=items,
    )

    return calcular_totales(oc)
