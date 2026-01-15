# oc/models.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ItemOC:
    """
    Representa una línea / ítem dentro de la OC.
    """
    codigo: str = ""
    descripcion: str = ""
    cantidad: float = 0.0
    valor_unitario: float = 0.0  # clave para Excel (col E)


# ✅ Alias de compatibilidad por si tu código antiguo importaba otro nombre
Item = ItemOC


@dataclass
class OrdenCompra:
    """
    Modelo principal de Orden de Compra.
    Los nombres están pensados para que excel.py pueda mapearlos fácil.
    """

    # Empresa emisora (D3:D7)
    empresa_nombre: str = ""
    empresa_rut: str = ""
    empresa_giro: str = ""
    empresa_direccion: str = ""
    empresa_otro: str = ""  # D7 (si aplica)

    # Proveedor (dict desde CSV)
    proveedor: Dict[str, str] = field(default_factory=dict)

    # Condición de pago (C17)
    condicion_pago: str = ""

    # Información de entrega (C20:C23)
    entrega_direccion: str = ""
    entrega_contacto: str = ""
    entrega_telefono: str = ""
    entrega_correo: str = ""

    # Interno (B52/B54/B56)
    centro_costo: str = ""
    nombre_solicitante: str = ""
    autoriza: str = ""

    # Ítems
    items: List[ItemOC] = field(default_factory=list)
