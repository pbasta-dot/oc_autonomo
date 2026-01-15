# config.py (raíz del proyecto)
from pathlib import Path
import sys

def _base_dir() -> Path:
    """
    - En modo normal (python app.py): raíz = carpeta donde está config.py
    - En modo exe (PyInstaller): raíz = carpeta del ejecutable (sys._MEIPASS / dist folder)
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # En PyInstaller, los recursos se extraen a _MEIPASS
        # pero para outputs conviene usar la carpeta del exe
        return Path(sys._MEIPASS)  # recursos empaquetados
    return Path(__file__).resolve().parent

# BASE para encontrar recursos empaquetados
RESOURCE_DIR = _base_dir()

# BASE para escribir outputs (junto al exe o junto al proyecto)
if getattr(sys, "frozen", False):
    RUN_DIR = Path(sys.executable).resolve().parent
else:
    RUN_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = RESOURCE_DIR / "templates"
DATA_DIR = RESOURCE_DIR / "data"
OUTPUTS_DIR = RUN_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

PLANTILLA_OC_XLSX = TEMPLATES_DIR / "OC_BASE.xlsx"
PROVEEDORES_CSV = DATA_DIR / "proveedores.csv"

EMPRESAS = {
    "1": {
        "nombre": "Red Nacional de Servicios Integrales SpA",
        "rut": "76.279.333-4",
        "giro": "Servicios de ambulancia y asistencia",
        "direccion": "Tu dirección empresa 1",
    },
    "2": {
        "nombre": "Rest911 (Otra Razón Social)",
        "rut": "75.269.444-4",
        "giro": "Otro giro",
        "direccion": "Tu dirección empresa 2",
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
    errores = []
    if not PLANTILLA_OC_XLSX.exists():
        errores.append(f"No se encontró plantilla: {PLANTILLA_OC_XLSX.resolve()}")
    if not PROVEEDORES_CSV.exists():
        errores.append(f"No se encontró proveedores: {PROVEEDORES_CSV.resolve()}")
    if errores:
        raise FileNotFoundError("\n".join(errores))

if __name__ == "__main__":
    print("RESOURCE_DIR:", RESOURCE_DIR)
    print("RUN_DIR:", RUN_DIR)
    print("PLANTILLA_OC_XLSX:", PLANTILLA_OC_XLSX)
    print("PROVEEDORES_CSV:", PROVEEDORES_CSV)
    print("OUTPUTS_DIR:", OUTPUTS_DIR)
    validar_config()
    print("✅ Config OK")
