from __future__ import annotations

from typing import Any, Callable
import inspect
import os
from datetime import datetime

import config

from oc.excel import generar_excel_oc

# PDF opcional
try:
    from oc.pdf import generar_pdf_oc
except Exception:
    generar_pdf_oc = None  # type: ignore

from .oc_repo import registrar_desde_orden_compra
from config import OCS_DETALLE_CSV


# =====================================================
# Helpers UX
# =====================================================
def _line():
    print("-" * 60)


def _title(text: str):
    _line()
    print(f"🧾 {text}")
    _line()


def _confirm(msg: str) -> bool:
    while True:
        r = input(f"{msg} (S/N): ").strip().lower()
        if r in ("s", "si", "sí"):
            return True
        if r in ("n", "no"):
            return False
        print("❌ Respuesta inválida. Usa S o N.")


def _fmt_money(value):
    try:
        return f"${int(round(float(value))):,}".replace(",", ".")
    except Exception:
        return "-"


def _get_dict(obj: Any, attr: str, default=None):
    v = getattr(obj, attr, None)
    if v is None:
        return default if default is not None else {}
    return v


# =====================================================
# Detectar función correcta en oc.flow
# =====================================================
def _resolver_funcion_creacion_oc() -> Callable:
    import oc.flow as flow  # import local para evitar problemas circulares

    candidatos_por_nombre = [
        "crear_orden_compra",
        "crear_oc",
        "nueva_oc",
        "nuevo_oc",
        "flujo_oc",
        "flujo_creacion_oc",
        "crear",
        "run",
        "main",
    ]

    for name in candidatos_por_nombre:
        fn = getattr(flow, name, None)
        if callable(fn):
            return fn

    callables = []
    for name, obj in vars(flow).items():
        if name.startswith("_"):
            continue
        if callable(obj):
            try:
                sig = inspect.signature(obj)
                if 0 <= len(sig.parameters) <= 2:
                    callables.append((name, obj))
            except Exception:
                continue

    if len(callables) == 1:
        return callables[0][1]

    if len(callables) > 1:
        nombres = ", ".join(n for n, _ in callables)
        raise ImportError(
            "No pude identificar automáticamente la función de creación de OC en oc/flow.py.\n"
            f"Encontré varias funciones candidatas: {nombres}\n"
            "Solución: renombra la principal a 'crear_orden_compra' o dime cuál usar."
        )

    raise ImportError(
        "No encontré ninguna función para crear una OC en oc/flow.py.\n"
        "Asegúrate de tener una función pública (no empezando con _) que construya y devuelva la OrdenCompra."
    )


def _crear_oc(usuario: Any) -> Any:
    fn = _resolver_funcion_creacion_oc()
    sig = inspect.signature(fn)
    if len(sig.parameters) == 0:
        return fn()
    return fn(usuario)


# =====================================================
# Resumen visual
# =====================================================
def _mostrar_resumen_oc(oc: Any):
    _title("Resumen Orden de Compra")

    empresa = _get_dict(oc, "empresa", {})
    proveedor = _get_dict(oc, "proveedor", {})

    print("🏢 Empresa")
    print(f"   Nombre : {empresa.get('nombre', empresa.get('razon_social', '-'))}")
    print(f"   RUT    : {empresa.get('rut', '-')}")
    print()

    print("🏭 Proveedor")
    print(f"   Razón  : {proveedor.get('razon_social', proveedor.get('nombre', '-'))}")
    print(f"   RUT    : {proveedor.get('rut', '-')}")
    print()

    items = getattr(oc, "items", []) or []
    print(f"📦 Ítems ({len(items)})")

    for i, item in enumerate(items, start=1):
        if isinstance(item, dict):
            desc = item.get("descripcion") or item.get("nombre") or item.get("detalle") or "-"
            cant = item.get("cantidad", "-")
            precio = _fmt_money(item.get("precio_unitario"))
            subtotal = _fmt_money(item.get("subtotal"))
        else:
            desc = getattr(item, "descripcion", None) or getattr(item, "nombre", None) or getattr(item, "detalle", None) or "-"
            cant = getattr(item, "cantidad", "-")
            precio = _fmt_money(getattr(item, "precio_unitario", None))
            subtotal = _fmt_money(getattr(item, "subtotal", None))

        print(f"   {i}. {desc}")
        print(f"      Cantidad: {cant} | Precio: {precio} | Subtotal: {subtotal}")

    _line()
    print(f"💰 Neto : {_fmt_money(getattr(oc, 'neto', None))}")
    print(f"💰 IVA  : {_fmt_money(getattr(oc, 'iva', None))}")
    print(f"💰 Total: {_fmt_money(getattr(oc, 'total', None))}")
    _line()
    print(f"📄 Condición de pago: {getattr(config, 'CONDICION_PAGO_DEFAULT', '-')}")
    _line()


# =====================================================
# Menú principal
# =====================================================
def menu_principal(usuario):
    while True:
        _title(getattr(config, "APP_NOMBRE", "OC_Autonomo"))

        print("1️⃣  Crear nueva Orden de Compra")
        print("2️⃣  Salir")
        _line()

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            try:
                oc = _crear_oc(usuario)
                _mostrar_resumen_oc(oc)

                if not _confirm("¿Confirmar generación de la Orden de Compra?"):
                    print("⚠️  Operación cancelada por el usuario.")
                    input("Presiona ENTER para continuar...")
                    continue

                # 1) Excel
                excel_path = generar_excel_oc(oc)
                print(f"✅ Excel generado: {excel_path}")

                # 2) PDF (opcional)
                pdf_path = None
                if generar_pdf_oc is not None:
                    try:
                        pdf_path = generar_pdf_oc(excel_path)
                        print(f"📄 PDF generado: {pdf_path}")
                    except Exception as e:
                        print(f"⚠️  No se pudo generar PDF (opcional): {e}")

                # 3) OC numero para histórico
                if pdf_path:
                    oc_numero = os.path.splitext(os.path.basename(pdf_path))[0]
                else:
                    oc_numero = datetime.now().strftime("OC-%Y%m%d-%H%M%S")

                # 4) Registrar histórico (NO silencioso)
                print("🧪 DEBUG: registrando histórico...")
                print(f"🧪 DEBUG: oc_numero = {oc_numero}")
                print(f"🧪 DEBUG: items = {len(getattr(oc, 'items', []) or [])}")
                print(f"🧪 DEBUG: archivo destino = {OCS_DETALLE_CSV}")

                filas = registrar_desde_orden_compra(oc_obj=oc, oc_numero=oc_numero)
                print(f"✅ Histórico OK: {filas} filas agregadas en {OCS_DETALLE_CSV}")

                # Confirmación dura: imprimir últimas líneas
                try:
                    with open(OCS_DETALLE_CSV, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    print("🧾 Últimas líneas CSV:")
                    for l in lines[-min(5, len(lines)):]:
                        print("   " + l.strip())
                except Exception as e:
                    print(f"⚠️ DEBUG: no pude leer el CSV para confirmar: {e}")

                print("🎉 Orden de Compra generada exitosamente.")
                input("Presiona ENTER para volver al menú...")

            except Exception as e:
                _line()
                print("❌ Error en el flujo")
                print(str(e))
                _line()
                input("Presiona ENTER para continuar...")

        elif opcion == "2":
            print("👋 Saliendo del sistema. Hasta luego.")
            break

        else:
            print("❌ Opción inválida.")
            input("Presiona ENTER para intentar nuevamente...")
