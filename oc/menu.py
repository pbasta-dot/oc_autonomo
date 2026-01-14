from .flow import crear_oc, pedir_opcion, FLOW_VERSION
from .excel import generar_excel_oc

def menu_principal(usuario: str):
    while True:
        print("====== SISTEMA OC ======")
        print(f"Usuario: {usuario}")
        print(f"Flow: {FLOW_VERSION}")  # <- CONFIRMACIÓN VISUAL
        print("1) Generar Draft OC (Excel)")
        print("0) Salir")

        op = pedir_opcion("Opción: ", {"0", "1"})
        if op == "0":
            print("Saliendo...")
            return

        if op == "1":
            oc = crear_oc()
            if oc is None:
                print("Volviendo al menú...\n")
                continue

            path = generar_excel_oc(oc)
            print(f"\n✅ Draft generado: {oc.numero}")
            print(f"📄 Excel generado en: {path}\n")
