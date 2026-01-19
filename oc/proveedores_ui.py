from __future__ import annotations

from typing import Any, Dict, List

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
    base = f"{rs} | {rut}"
    extra = " | ".join([x for x in [giro, f"{comuna}, {ciudad}".strip(", ")] if x])
    return f"{base} | {extra}" if extra else base

def _input_obligatorio(msg: str) -> str:
    while True:
        v = input(msg).strip()
        if v:
            return v
        print("⚠️ Campo obligatorio.")

def _input_opcional(msg: str) -> str:
    return input(msg).strip()

def _elegir_indice(max_n: int) -> int:
    while True:
        raw = input("Selecciona un número: ").strip()
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= max_n:
                return n - 1
        print("⚠️ Selección inválida.")

def _seleccionar_proveedor_existente() -> Dict[str, str]:
    proveedores = proveedores_repo.cargar_todos()
    if not proveedores:
        print("No hay proveedores registrados. Debes crear uno nuevo.")
        return _crear_proveedor_nuevo()

    q = input("Buscar (Razón Social o RUT) [Enter para listar todos]: ").strip().lower()

    if q:
        filtrados: List[Dict[str, str]] = []
        for p in proveedores:
            rs = _norm(p.get("razon_social")).lower()
            rut = _norm(p.get("rut")).lower()
            if q in rs or q in rut:
                filtrados.append(p)
    else:
        filtrados = proveedores

    if not filtrados:
        print("No se encontraron coincidencias. Se creará un proveedor nuevo.")
        return _crear_proveedor_nuevo()

    print("\nProveedores disponibles:")
    for i, p in enumerate(filtrados, start=1):
        print(f" {i}) {_formatear(p)}")

    idx = _elegir_indice(len(filtrados))
    elegido = filtrados[idx]
    return {k: _norm(v) for k, v in elegido.items()}

def _crear_proveedor_nuevo() -> Dict[str, str]:
    print("\n=== Crear proveedor nuevo ===")
    data: Dict[str, str] = {}

    data["razon_social"] = _input_obligatorio("Razón social: ")
    data["rut"] = _input_obligatorio("RUT: ")

    data["giro"] = _input_opcional("Giro: ")
    data["direccion"] = _input_opcional("Dirección: ")
    data["comuna"] = _input_opcional("Comuna: ")
    data["ciudad"] = _input_opcional("Ciudad: ")
    data["telefono"] = _input_opcional("Teléfono: ")
    data["persona_contacto"] = _input_opcional("Persona contacto: ")

    # Guardar con control de errores (RUT duplicado / campos obligatorios)
    try:
        creado = proveedores_repo.agregar(data)
    except ValueError as e:
        print(f"❌ No se pudo crear proveedor: {e}")
        print("👉 Intenta nuevamente.\n")
        return _crear_proveedor_nuevo()

    print(f"✅ Proveedor creado: {_formatear(creado)}")
    return {k: _norm(v) for k, v in creado.items()}


    print(f"✅ Proveedor creado: {_formatear(creado)}")
    return {k: _norm(v) for k, v in creado.items()}

def buscar_y_seleccionar_proveedor() -> Dict[str, str]:
    """
    Mantiene el mismo nombre que usas en flow.py, pero ahora pregunta:
    - 1) Proveedor antiguo (seleccionar)
    - 2) Proveedor nuevo (crear)
    """
    while True:
        print("\n¿El proveedor es nuevo o antiguo?")
        print(" 1) Antiguo (ya registrado)")
        print(" 2) Nuevo (registrar ahora)")
        op = input("Opción (1/2): ").strip()

        if op == "1":
            return _seleccionar_proveedor_existente()
        if op == "2":
            return _crear_proveedor_nuevo()

        print("⚠️ Opción inválida. Ingresa 1 o 2.")
