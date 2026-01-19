# config.py (raíz del proyecto)
from pathlib import Path
import sys


def _resource_dir() -> Path:
    """
    Base para LEER recursos (templates, etc.)
    - Normal: carpeta donde está config.py
    - PyInstaller: sys._MEIPASS (recursos empaquetados)
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def _run_dir() -> Path:
    """
    Base para ESCRIBIR archivos (outputs, data)
    - Normal: carpeta del proyecto
    - PyInstaller: carpeta del ejecutable
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


# Bases
RESOURCE_DIR = _resource_dir()
RUN_DIR = _run_dir()

# Directorios
TEMPLATES_DIR = RESOURCE_DIR / "templates"

# ✅ DATA debe escribirse junto al RUN_DIR (no en _MEIPASS)
DATA_DIR = RUN_DIR / "data"
OUTPUTS_DIR = RUN_DIR / "outputs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Archivos
PLANTILLA_OC_XLSX = TEMPLATES_DIR / "OC_BASE.xlsx"

# ✅ CSVs en RUN_DIR/data
PROVEEDORES_CSV = DATA_DIR / "proveedores.csv"
OCS_DETALLE_CSV = DATA_DIR / "ocs_detalle.csv"  # nombre estándar y en minúsculas

# Parámetros app
EMPRESAS = {
    "1": {
        "nombre": "Red Nacional de Servicios Integrales SpA",
        "rut": "76.279.333-4",
        "giro": "Servicios de ambulancia y asistencia",
        "direccion": "Tu dirección empresa 1",
        "correo":"PROVEEDORES@REST911.CL (envío de facturas para el pago).",
    },
    
    "2": {
        "nombre": "Rest911 (Otra Razón Social)",
        "rut": "75.269.444-4",
        "giro": "Otro giro",
        "direccion": "Tu dirección empresa 2",
        "correo":"PROVEEDORES@REST911.CL (envío de facturas para el pago)."
    },
}

IVA_TASA = 0.19

APP_NOMBRE = "Sistema OC - Autónomo"

ENTREGA_PREDEFINIDA = {
    "nombre": "Pablo Basta",
    "telefono": "+56 9 XXXXXXXX",
    "correo": "pbasta@rest911.cl",
}

CONDICION_PAGO_DEFAULT = "Transferencia"


def validar_config() -> None:
    """
    Validamos SOLO recursos que deben existir (plantillas).
    Los CSV NO se validan porque el sistema los crea automáticamente.
    """
    errores = []
    if not PLANTILLA_OC_XLSX.exists():
        errores.append(f"No se encontró plantilla: {PLANTILLA_OC_XLSX.resolve()}")
    if errores:
        raise FileNotFoundError("\n".join(errores))


if __name__ == "__main__":
    print("RESOURCE_DIR:", RESOURCE_DIR)
    print("RUN_DIR:", RUN_DIR)
    print("TEMPLATES_DIR:", TEMPLATES_DIR)
    print("DATA_DIR:", DATA_DIR)
    print("OUTPUTS_DIR:", OUTPUTS_DIR)
    print("PLANTILLA_OC_XLSX:", PLANTILLA_OC_XLSX)
    print("PROVEEDORES_CSV:", PROVEEDORES_CSV)
    print("OCS_DETALLE_CSV:", OCS_DETALLE_CSV)
    validar_config()
    print("✅ Config OK")
