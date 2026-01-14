from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any

@dataclass
class Item:
    cantidad: float
    descripcion: str
    valor_unitario: float
    codigo: str = ""  # OPCIONAL

    @property
    def total_linea(self) -> float:
        return self.cantidad * self.valor_unitario

@dataclass
class OrdenCompra:
    numero: str
    fecha: datetime

    proveedor: Dict[str, Any]
    empresa_emisora: Dict[str, Any]

    centro_costo: str
    solicitado_por: str
    autorizado_por: str

    con_iva: bool

    # Opcionales
    cotizacion_n: str = ""
    entrega: Dict[str, Any] = field(default_factory=dict)

    items: List[Item] = field(default_factory=list)
    subtotal: float = 0.0
    iva: float = 0.0
    total: float = 0.0
