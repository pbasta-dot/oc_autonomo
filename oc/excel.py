import os
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell

from config import PLANTILLA_OC_XLSX, CONDICION_PAGO_DEFAULT

# =========================
# Celdas (según tu plantilla)
# =========================

# Empresa emisora
CELL_EMISORA_NOMBRE = "D3"
CELL_EMISORA_RUT = "D4"
CELL_EMISORA_GIRO = "D5"
CELL_EMISORA_DIRECCION = "D6"
CELL_EMISORA_CORREO_FACTURAS = "D7"
CORREO_FACTURAS = "PROVEEDORES@REST911.CL (envío de factura para pago)."

# Encabezado OC
CELL_COTIZACION = "E8"     # Cotización N° (opcional)
CELL_FECHA = "F2"          # Fecha de emisión
CELL_COND_PAGO = "C17"     # Condición de pago
CELL_CENTRO_COSTO = "B52"  # "Centro de Costo: XXXX"

# Firmas (solo string)
CELL_SOLICITADO_POR = "B54"
CELL_AUTORIZADO_POR = "B56"

# Proveedor (INFORMACION DEL PROVEEDOR)
CELL_RAZON = "D9"
CELL_RUT = "D10"
CELL_GIRO = "D11"
CELL_DIRECCION = "D12"
CELL_COMUNA = "D13"
CELL_CIUDAD = "D14"
CELL_TELEFONO = "D15"
CELL_CONTACTO = "D16"

# Entrega (INFORMACION DE ENTREGA)
CELL_ENTREGA_NOMBRE = "D21"
CELL_ENTREGA_TELEFONO = "D22"
CELL_ENTREGA_CORREO = "D23"

# Tabla de ítems
START_ROW_ITEMS = 25
COL_CODIGO = "B"   # Código producto (opcional)
COL_CANT = "C"
COL_DESC = "D"
COL_UNIT = "E"
COL_TOTAL = "F"

# Totales
CELL_NETO = "F52"
CELL_DESC = "F53"
CELL_SUBTOTAL = "F54"
CELL_IVA = "F55"
CELL_DESPACHO = "F56"
CELL_TOTAL_PAGAR = "F57"


def _safe_str(x):
    return "" if x is None else str(x).strip()

def _set_value(ws, addr: str, value) -> bool:
    """
    Escribe valor solo si la celda NO es MergedCell (read-only).
    Si es merged, no escribe (mantiene formato) y retorna False.
    """
    cell = ws[addr]
    if isinstance(cell, MergedCell):
        return False
    cell.value = value
    return True

def _is_writable(ws, addr: str) -> bool:
    return not isinstance(ws[addr], MergedCell)

def generar_excel_oc(oc, output_dir="outputs"):
    """
    Genera un Excel nuevo a partir de la plantilla PLANTILLA_OC_XLSX,
    rellenando los campos definidos y guardando el resultado en outputs/.
    """
    if not os.path.exists(PLANTILLA_OC_XLSX):
        raise FileNotFoundError(
            f"No se encontró la plantilla '{PLANTILLA_OC_XLSX}'. Revisa config.py (PLANTILLA_OC_XLSX)."
        )

    os.makedirs(output_dir, exist_ok=True)

    wb = load_workbook(PLANTILLA_OC_XLSX)
    ws = wb["ORDEN DE COMPRA"] if "ORDEN DE COMPRA" in wb.sheetnames else wb.active

    # =========================
    # 0) Empresa emisora (D3:D7)
    # =========================
    em = getattr(oc, "empresa_emisora", None) or {}
    _set_value(ws, CELL_EMISORA_NOMBRE, _safe_str(em.get("nombre")))
    _set_value(ws, CELL_EMISORA_RUT, _safe_str(em.get("rut")))
    _set_value(ws, CELL_EMISORA_GIRO, _safe_str(em.get("giro")))
    _set_value(ws, CELL_EMISORA_DIRECCION, _safe_str(em.get("direccion")))
    _set_value(ws, CELL_EMISORA_CORREO_FACTURAS, CORREO_FACTURAS)

    # =========================
    # 1) Encabezado (cotización opcional, fecha, condición pago)
    # F1 NO se toca (proveedores asigna OC final)
    # =========================
    cot = _safe_str(getattr(oc, "cotizacion_n", ""))
    if cot:
        _set_value(ws, CELL_COTIZACION, cot)

    _set_value(ws, CELL_FECHA, getattr(oc, "fecha"))
    _set_value(ws, CELL_COND_PAGO, CONDICION_PAGO_DEFAULT)

    # =========================
    # 2) Proveedor (D9:D16)
    # =========================
    p = getattr(oc, "proveedor", None) or {}
    _set_value(ws, CELL_RAZON, _safe_str(p.get("razon_social")))
    _set_value(ws, CELL_RUT, _safe_str(p.get("rut")))
    _set_value(ws, CELL_GIRO, _safe_str(p.get("giro")))
    _set_value(ws, CELL_DIRECCION, _safe_str(p.get("direccion")))
    _set_value(ws, CELL_COMUNA, _safe_str(p.get("comuna")))
    _set_value(ws, CELL_CIUDAD, _safe_str(p.get("ciudad")))
    _set_value(ws, CELL_TELEFONO, _safe_str(p.get("telefono")))
    _set_value(ws, CELL_CONTACTO, _safe_str(p.get("persona_contacto")))

    # =========================
    # 3) Entrega (D21:D23)
    # =========================
    e = getattr(oc, "entrega", None) or {}
    _set_value(ws, CELL_ENTREGA_NOMBRE, _safe_str(e.get("nombre")))
    _set_value(ws, CELL_ENTREGA_TELEFONO, _safe_str(e.get("telefono")))
    _set_value(ws, CELL_ENTREGA_CORREO, _safe_str(e.get("correo")))

    # =========================
    # 4) Centro de costo (B52)
    # =========================
    _set_value(ws, CELL_CENTRO_COSTO, f"Centro de Costo: {_safe_str(getattr(oc, 'centro_costo', ''))}")

    # =========================
    # 5) Ítems (desde fila 25, evitando merged cells)
    # Código en columna B (opcional)
    # =========================
    r = START_ROW_ITEMS
    items = getattr(oc, "items", []) or []

    for it in items:
        # Busca siguiente fila escribible en B..F
        while True:
            ok_b = _is_writable(ws, f"{COL_CODIGO}{r}")
            ok_c = _is_writable(ws, f"{COL_CANT}{r}")
            ok_d = _is_writable(ws, f"{COL_DESC}{r}")
            ok_e = _is_writable(ws, f"{COL_UNIT}{r}")
            ok_f = _is_writable(ws, f"{COL_TOTAL}{r}")
            if ok_b and ok_c and ok_d and ok_e and ok_f:
                break
            r += 1

        _set_value(ws, f"{COL_CODIGO}{r}", _safe_str(getattr(it, "codigo", "")))
        _set_value(ws, f"{COL_CANT}{r}", float(getattr(it, "cantidad", 0)))
        _set_value(ws, f"{COL_DESC}{r}", _safe_str(getattr(it, "descripcion", "")))
        _set_value(ws, f"{COL_UNIT}{r}", float(getattr(it, "valor_unitario", 0)))

        total_linea = float(getattr(it, "cantidad", 0)) * float(getattr(it, "valor_unitario", 0))
        _set_value(ws, f"{COL_TOTAL}{r}", total_linea)

        r += 1

    # =========================
    # 6) Totales (F52:F57)
    # =========================
    _set_value(ws, CELL_NETO, float(getattr(oc, "subtotal", 0.0)))
    _set_value(ws, CELL_DESC, 0.0)
    _set_value(ws, CELL_SUBTOTAL, float(getattr(oc, "subtotal", 0.0)))
    _set_value(ws, CELL_IVA, float(getattr(oc, "iva", 0.0)))
    _set_value(ws, CELL_DESPACHO, 0.0)
    _set_value(ws, CELL_TOTAL_PAGAR, float(getattr(oc, "total", 0.0)))

    # =========================
    # 7) Firmas (B54 y B56) - SOLO STRING, SIN PREFIJO
    # =========================
    solicitado = _safe_str(getattr(oc, "solicitado_por", ""))
    autorizado = _safe_str(getattr(oc, "autorizado_por", ""))

    _set_value(ws, CELL_SOLICITADO_POR, solicitado)
    _set_value(ws, CELL_AUTORIZADO_POR, autorizado)

    # =========================
    # 8) Guardar
    # =========================
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"{getattr(oc, 'numero', 'DRAFT')}_{stamp}.xlsx")
    wb.save(filename)
    return filename
