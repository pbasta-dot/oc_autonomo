from __future__ import annotations

import csv
import os
from datetime import date
from typing import Any, Dict, List, Optional

from config import OCS_DETALLE_CSV  # ✅ toma ruta desde config.py

ARCHIVO = OCS_DETALLE_CSV

CAMPOS_OC = [
    "fecha",
    "oc",
    "centro_costo",
    "proveedor",
    "item",
    "cantidad",
    "valor_unitario",
    "total",
    "solicitado_por",
    "autorizado_por",
]


def asegurar_archivo() -> None:
    # ✅ asegura carpeta contenedora (ej: data/)
    folder = os.path.dirname(ARCHIVO)
    if folder:
        os.makedirs(folder, exist_ok=True)

    if not os.path.exists(ARCHIVO):
        with open(ARCHIVO, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS_OC)
            w.writeheader()


def _to_float(x: Any) -> float:
    """
    Acepta: 25000 | "25.000" | "25,000" | "25.000,50" | "10,5"
    """
    if x is None:
        return 0.0
    s = str(x).strip().replace(" ", "")
    if not s:
        return 0.0

    # "12.345,67" -> "12345.67"
    if "," in s and "." in s and s.rfind(",") > s.rfind("."):
        s = s.replace(".", "").replace(",", ".")
    # "12,345.67" -> "12345.67"
    elif "," in s and "." in s:
        s = s.replace(",", "")
    # "10,5" -> "10.5"
    elif "," in s and "." not in s and s.count(",") == 1:
        s = s.replace(",", ".")
    # "12.345" miles -> "12345"
    elif "." in s and s.count(".") == 1:
        left, right = s.split(".")
        if left.isdigit() and right.isdigit() and len(right) == 3:
            s = left + right

    return float(s)


def guardar_oc_items(
    *,
    oc_numero: str,
    centro_costo: str,
    proveedor: str,
    solicitado_por: str,
    autorizado_por: str,
    items: List[Dict[str, Any]],
    fecha_emision: Optional[str] = None,
) -> int:
    """
    items = [
        {"item": "Filtro aceite", "cantidad": 2, "valor_unitario": 4500},
        ...
    ]
    Retorna cantidad de filas escritas.
    """
    asegurar_archivo()

    if fecha_emision is None:
        fecha_emision = date.today().isoformat()

    filas: List[Dict[str, Any]] = []

    for it in items:
        cantidad = _to_float(it.get("cantidad"))
        valor_unitario = _to_float(it.get("valor_unitario"))
        total = round(cantidad * valor_unitario, 2)

        filas.append({
            "fecha": fecha_emision,
            "oc": str(oc_numero).strip(),
            "centro_costo": str(centro_costo).strip(),
            "proveedor": str(proveedor).strip(),
            "item": str(it.get("item", "")).strip(),
            "cantidad": cantidad,
            "valor_unitario": valor_unitario,
            "total": total,
            "solicitado_por": str(solicitado_por).strip(),
            "autorizado_por": str(autorizado_por).strip(),
        })

    with open(ARCHIVO, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_OC)
        w.writerows(filas)

    return len(filas)


def registrar_desde_orden_compra(
    *,
    oc_obj: Any,
    oc_numero: str,
    fecha_emision: Optional[str] = None
) -> int:
    """
    Convierte tu OrdenCompra a filas estándar y registra 1 fila por ítem.
    Retorna cantidad de filas escritas.
    """
    # Proveedor puede ser dict
    prov = getattr(oc_obj, "proveedor", {}) or {}
    if isinstance(prov, dict):
        proveedor_rs = (prov.get("razon_social") or prov.get("nombre") or "").strip()
    else:
        proveedor_rs = str(prov).strip()

    items_norm: List[Dict[str, Any]] = []
    for it in getattr(oc_obj, "items", []) or []:
        # ItemOC: descripcion, cantidad, precio_unitario
        desc = getattr(it, "descripcion", None)
        if desc is None and isinstance(it, dict):
            desc = it.get("descripcion") or it.get("item") or ""
        desc = (desc or "").strip()

        cant = getattr(it, "cantidad", None)
        if cant is None and isinstance(it, dict):
            cant = it.get("cantidad")

        pu = getattr(it, "precio_unitario", None)
        if pu is None:
            pu = getattr(it, "valor_unitario", None)
        if pu is None and isinstance(it, dict):
            pu = it.get("precio_unitario", it.get("valor_unitario"))

        items_norm.append({
            "item": desc,
            "cantidad": cant,
            "valor_unitario": pu,
        })

    return guardar_oc_items(
        oc_numero=oc_numero,
        centro_costo=getattr(oc_obj, "centro_costo", "") or "",
        proveedor=proveedor_rs,
        solicitado_por=getattr(oc_obj, "solicitante", "") or "",
        autorizado_por=getattr(oc_obj, "autoriza", "") or "",
        items=items_norm,
        fecha_emision=fecha_emision,
    )
