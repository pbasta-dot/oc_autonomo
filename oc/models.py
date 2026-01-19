# oc/models.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ItemOC:
    """
    Item compatible con oc/menu.py:
    - menu usa: descripcion, cantidad, precio_unitario, subtotal
    """
    codigo: str = ""
    descripcion: str = ""
    cantidad: float = 0.0
    precio_unitario: float = 0.0

    @property
    def subtotal(self) -> float:
        try:
            return float(self.cantidad) * float(self.precio_unitario)
        except Exception:
            return 0.0


@dataclass
class OrdenCompra:
    """
    Orden compatible con oc/menu.py:
    - menu usa: oc.empresa (dict), oc.proveedor (dict), oc.items, oc.neto, oc.iva, oc.total
    Además incluye campos para Excel: centro_costo, solicitante, autoriza, entrega, condición de pago
    """
    # Dicts para menú
    empresa: Dict[str, str] = field(default_factory=dict)
    proveedor: Dict[str, str] = field(default_factory=dict)

    # Datos adicionales
    condicion_pago: str = ""
    entrega: Dict[str, str] = field(default_factory=dict)

    centro_costo: str = ""
    solicitante: str = ""   # (texto “NOMBRE SOLICITANTE”)
    autoriza: str = ""      # (texto “AUTORIZA”)

    items: List[ItemOC] = field(default_factory=list)

    # Totales (pueden ser calculados al final del flow)
    neto: float = 0.0
    iva: float = 0.0
    total: float = 0.0
