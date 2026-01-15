from openpyxl import load_workbook
from pathlib import Path
from datetime import datetime

from config import PLANTILLA_OC_XLSX


def generar_excel_oc(oc):
    """
    Genera el Excel de Orden de Compra desde la plantilla base
    """
    plantilla = Path(PLANTILLA_OC_XLSX)

    if not plantilla.exists():
        raise FileNotFoundError(f"No existe la plantilla: {plantilla}")

    wb = load_workbook(plantilla)
    ws = wb.active

    # --- prueba mínima ---
    ws["A1"] = "OC GENERADA CORRECTAMENTE"

    output = Path("outputs")
    output.mkdir(exist_ok=True)

    nombre = f"DRAFT-{datetime.now().strftime('%Y%m%d-%H%M%S')}.xlsx"
    destino = output / nombre

    wb.save(destino)

    return str(destino)
