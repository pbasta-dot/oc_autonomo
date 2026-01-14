import csv
import os
import re

ARCHIVO = "proveedores.csv"

CAMPOS = [
    "id",
    "razon_social",
    "rut",
    "giro",
    "direccion",
    "comuna",
    "ciudad",
    "telefono",
    "persona_contacto",
]

def asegurar_archivo():
    if not os.path.exists(ARCHIVO):
        with open(ARCHIVO, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS)
            w.writeheader()

def cargar_todos():
    asegurar_archivo()
    data = []
    with open(ARCHIVO, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            data.append({k: (v or "").strip() for k, v in row.items()})
    return data

def _normalizar(s: str) -> str:
    return (s or "").strip().lower()

def normalizar_rut(rut: str) -> str:
    """
    Normaliza rut para búsqueda:
    - elimina puntos, espacios y guiones
    - deja k en minúscula
    Ej: 76.123.456-7 -> 761234567
        12.345.678-K -> 12345678k
    """
    r = (rut or "").strip().lower()
    r = re.sub(r"[^0-9k]", "", r)  # deja solo números y k
    return r

def buscar(query: str):
    q_raw = (query or "").strip()
    if not q_raw:
        return []

    q = _normalizar(q_raw)
    q_rut = normalizar_rut(q_raw)

    todos = cargar_todos()
    resultados = []

    for p in todos:
        # Texto “full” para búsqueda amplia
        full = " | ".join([
            p.get("razon_social", ""),
            p.get("rut", ""),
            p.get("giro", ""),
            p.get("direccion", ""),
            p.get("comuna", ""),
            p.get("ciudad", ""),
            p.get("telefono", ""),
            p.get("persona_contacto", ""),
        ])
        full_norm = _normalizar(full)

        # Comparación por rut normalizado (para soportar puntos/guión)
        p_rut_norm = normalizar_rut(p.get("rut", ""))

        if q in full_norm or (q_rut and q_rut == p_rut_norm) or (q_rut and q_rut in p_rut_norm):
            resultados.append(p)

    # Ranking simple: empieza por “razon_social” o rut primero
    def score(p):
        rs = _normalizar(p.get("razon_social", ""))
        rutn = normalizar_rut(p.get("rut", ""))
        s = 0
        if rs.startswith(q):
            s += 3
        if q_rut and rutn.startswith(q_rut):
            s += 3
        if q in rs:
            s += 2
        if q in _normalizar(p.get("ciudad", "")):
            s += 1
        return -s  # menor es mejor en sort

    resultados.sort(key=score)
    return resultados

def _siguiente_id(todos: list[dict]) -> int:
    max_id = 0
    for p in todos:
        try:
            max_id = max(max_id, int(p.get("id") or 0))
        except ValueError:
            pass
    return max_id + 1

def existe_rut(rut: str) -> bool:
    r = normalizar_rut(rut)
    if not r:
        return False
    for p in cargar_todos():
        if normalizar_rut(p.get("rut")) == r:
            return True
    return False

def agregar(proveedor: dict) -> dict:
    asegurar_archivo()
    todos = cargar_todos()

    proveedor = {k: (proveedor.get(k, "") or "").strip() for k in CAMPOS}

    if not proveedor["razon_social"]:
        raise ValueError("RAZÓN SOCIAL es obligatoria")
    if not proveedor["rut"]:
        raise ValueError("RUT es obligatorio")

    if existe_rut(proveedor["rut"]):
        raise ValueError("Ya existe un proveedor con ese RUT")

    proveedor["id"] = str(_siguiente_id(todos))

    with open(ARCHIVO, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writerow(proveedor)

    return proveedor
