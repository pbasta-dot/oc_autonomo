from config import IVA_TASA
from .models import OrdenCompra

def calcular_totales(oc: OrdenCompra) -> OrdenCompra:
    oc.subtotal = sum(i.total_linea for i in oc.items)
    oc.iva = oc.subtotal * IVA_TASA if oc.con_iva else 0.0
    oc.total = oc.subtotal + oc.iva
    return oc
