# oc/proveedores_ui.py
from __future__ import annotations

from typing import Dict, List, Any

from oc import proveedores_repo


CAMPOS_STD = [
    "razon_social",
    "rut",
    "giro",
    "direccion",
    "comuna",
    "ciudad",
    "telefono",
    "persona_contacto",
]


def _norm(s: Any) -> str:
    return ("" if s is None else str(s)).strip()


def _formatear(p: Dict[str, str]) -> str:
    rs = _norm(p.get("razon_social"))
    rut = _norm(p.get("rut"))
    giro = _norm(p.get("giro"))
    comuna = _norm(p.get("comuna"))
    ciudad = _norm(p.get("ciudad"))
    return f"{rs} | {rut} | {giro} | {comuna}/{ciudad}"


def _estandarizar(p: Dict[str, Any]) -> Dict[str, str]:
    # Asegura que devolvemos siempre las llaves que Excel espera
    out = {k: "" for k in CAMPOS_STD}
    for k in CAMPOS_STD:
        if k in p and p[k] is not None:
            out[k] = _norm(p[k])

    # alias por si vienen con otros nombres
    if not out["razon_social"]:
        out["razon_social"] = _norm(p.get("nombre", ""))

    if not out["persona_contacto"]:
        out["persona_contacto"] = _norm(p.get("contacto", ""))

    return out


def _buscar(query: str) -> List[Dict[str, str]]:
    """
    Intenta usar búsqueda avanzada si existe.
    Si no, usa búsqueda simple con contains.
    """
    query = _norm(query)
    todos = proveedores_repo.cargar_todos()

    # 1) Búsqueda avanzada (si existe en tu repo)
    if hasattr(proveedores_repo, "buscar_avanzado"):
        try:
            res = proveedores_repo.buscar_avanzado(query)
            return [_estandarizar(p) for p in res]
        except Exception:
            pass

    # 2) Búsqueda simple fallback
    if not query:
        return [_estandarizar(p) for p in todos]

    q = query.lower()
    filtrados = []
    for p in todos:
        texto = " ".join([_norm(p.get(k, "")) for k in CAMPOS_STD]).lower()
        if q in texto:
            filtrados.append(_estandarizar(p))

    return filtrados


def buscar_y_seleccionar_proveedor() -> Dict[str, str]:
    """
    UI de consola para buscar y seleccionar proveedor.
    Devuelve un dict estandarizado.
    """
    print("\n=== Buscar proveedor ===")
    print("Tip: puedes buscar por razón social / rut / giro / comuna.\n")

    while True:
        query = input("Buscar (Enter para listar todos, 0 para cancelar): ").strip()
        if query == "0":
            return {}

        resultados = _buscar(query)

        if not resultados:
            print("❌ No se encontraron proveedores. Intenta con otra búsqueda.\n")
            continue

        # Mostrar top 20
        max_show = 20
        print("\nResultados:")
        for i, p in enumerate(resultados[:max_show], start=1):
            print(f"{i}) {_formatear(p)}")

        if len(resultados) > max_show:
            print(f"... mostrando {max_show} de {len(resultados)} resultados")

        sel = input("\nSelecciona número (Enter para buscar otra vez): ").strip()
        if not sel:
            print("")
            continue

        try:
            n = int(sel)
            if 1 <= n <= min(len(resultados), max_show):
                return resultados[n - 1]
        except Exception:
            pass

        print("⚠️ Selección inválida.\n")
