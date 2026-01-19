from __future__ import annotations

import csv
import os
from datetime import date
from typing import Any, Dict, List, Optional

from config import OCS_DETALLE_CSV, IVA_TASA  # Path + tasa IVA desde config.py

ARCHIVO = str(OCS_DETALLE_CSV)

CAMPOS_OC = [
    "fecha",
    "oc",
    "centro_costo",
    "proveedor",
    "item",
    "cantidad",
    "valor_unitario",
    "con_iva",
    "total",
    "solicitado_por",
]


def _asegurar_salto_linea_final() -> None:
    """
    Si el archivo existe y NO termina con salto de línea,
    agregamos un '\n' para que el siguiente registro no se pegue al header.
    """
    if not os.path.exists(ARCHIVO):
        return

    try:
        with open(ARCHIVO, "rb") as f:
            data = f.read()
        if not data:
            return
        if not (data.endswith(b"\n") or data.endswith(b"\r\n")):
            with open(ARCHIVO, "ab") as f:
                f.write(b"\n")
    except Exception:
        # si falla, no bloqueamos el flujo
        pass


def asegurar_archivo() -> None:
    folder = os.path.dirname(ARCHIVO)
    if folder:
        os.makedirs(folder, exist_ok=True)

    if not os.path.exists(ARCHIVO):
        with open(ARCHIVO, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS_OC)
            w.writeheader()

    # clave: garantiza que el header quede separado de la primera fila
    _asegurar_salto_linea_final()


def _to_float(x: Any) -> float:
    """
    Acepta: 25000 | "25.000" | "25,000" | "25.000,50" | "10,5"
    """
    if x is None:
        return 0.0
    s = str(x).strip().replace(" ", "")
    if not s:
        return 0.0

    if "," in s and "." in s and s.rfind(",") > s.rfind("."):
        s = s.replace(".", "").replace(",", ".")
    elif "," in s and "." in s:
        s = s.replace(",", "")
    elif "," in s and "." not in s and s.count(",") == 1:
        s = s.replace(",", ".")
    elif "." in s and s.count(".") == 1:
        left, right = s.split(".")
        if left.isdigit() and right.isdigit() and len(right) == 3:
            s = left + right

    return float(s)


def _to_bool_con_iva(v: Any, default: bool = True) -> bool:
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("s", "si", "sí", "true", "1", "con", "con iva", "iva", "y", "yes"):
        return True
    if s in ("n", "no", "false", "0", "sin", "sin iva"):
        return False
    return default


def guardar_oc_items(
    *,
    oc_numero: str,
    centro_costo: str,
    proveedor: str,
    solicitado_por: str,
    items: List[Dict[str, Any]],
    fecha_emision: Optional[str] = None,
) -> int:
    """
    items = [
        {"item": "Filtro aceite", "cantidad": 2, "valor_unitario": 4500, "con_iva": True},
        ...
    ]
    Guarda 1 fila por item.
    """
    asegurar_archivo()

    if fecha_emision is None:
        fecha_emision = date.today().isoformat()

    filas: List[Dict[str, Any]] = []

    for it in items:
        cantidad = _to_float(it.get("cantidad"))
        valor_unitario = _to_float(it.get("valor_unitario"))
        neto_item = round(cantidad * valor_unitario, 2)

        con_iva = _to_bool_con_iva(it.get("con_iva"), default=True)
        if con_iva:
            total_item = round(neto_item * (1.0 + float(IVA_TASA)), 2)
        else:
            total_item = neto_item

        filas.append({
            "fecha": fecha_emision,
            "oc": (oc_numero or "").strip(),
            "centro_costo": (centro_costo or "").strip(),
            "proveedor": (proveedor or "").strip(),
            "item": (str(it.get("item", "")) or "").strip(),
            "cantidad": cantidad,
            "valor_unitario": valor_unitario,
            "con_iva": "SI" if con_iva else "NO",
            "total": total_item,
            "solicitado_por": (solicitado_por or "").strip(),
        })

    # por si algo volvió a dejar el archivo sin \n
    _asegurar_salto_linea_final()

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
    Toma OrdenCompra y registra items en el histórico.
    - Si oc_obj.con_iva no existe, asume True.
    """
    prov = getattr(oc_obj, "proveedor", {}) or {}
    if isinstance(prov, dict):
        proveedor_rs = (prov.get("razon_social") or prov.get("nombre") or "").strip()
    else:
        proveedor_rs = str(prov).strip()

    con_iva_oc = _to_bool_con_iva(getattr(oc_obj, "con_iva", None), default=True)

    items_norm: List[Dict[str, Any]] = []
    for it in getattr(oc_obj, "items", []) or []:
        desc = getattr(it, "descripcion", "") or ""
        cant = getattr(it, "cantidad", 0)
        pu = getattr(it, "precio_unitario", 0)

        items_norm.append({
            "item": desc,
            "cantidad": cant,
            "valor_unitario": pu,
            "con_iva": con_iva_oc,
        })

    return guardar_oc_items(
        oc_numero=oc_numero,
        centro_costo=getattr(oc_obj, "centro_costo", "") or "",
        proveedor=proveedor_rs,
        solicitado_por=getattr(oc_obj, "solicitante", "") or "",
        items=items_norm,
        fecha_emision=fecha_emision,
    )
