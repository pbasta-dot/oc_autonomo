from .proveedores_repo import buscar, agregar, cargar_todos

PAGE_SIZE = 10

def pedir_texto(msg: str, requerido=True) -> str:
    while True:
        val = input(msg).strip()
        if val or not requerido:
            return val
        print("Este campo es obligatorio.")

def _campo(p: dict, *nombres, default=""):
    """
    Devuelve el primer campo existente (para compatibilidad con CSV antiguos).
    Ej: _campo(p, "persona_contacto", "contacto", "persona de contacto")
    """
    for n in nombres:
        if n in p and (p.get(n) is not None):
            return str(p.get(n, "")).strip()
    return default

def seleccionar_proveedor_antiguo():
    todos = cargar_todos()
    if not todos:
        print("\n⚠️ No hay proveedores cargados aún en proveedores.csv")
        print("Rellena proveedores.csv (carga masiva) o crea uno nuevo desde el sistema.\n")
        return None

    while True:
        q = input("\nBuscar (razón social / RUT / ciudad / giro / dirección / contacto) o 0 para volver: ").strip()
        if q == "0":
            return None

        resultados = buscar(q)
        if not resultados:
            print("No se encontraron resultados.")
            continue

        page = 0
        total = len(resultados)
        total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE

        while True:
            start = page * PAGE_SIZE
            end = min(start + PAGE_SIZE, total)
            page_items = resultados[start:end]

            print(f"\nResultados: {total} | Página {page+1}/{total_pages}")
            print("-" * 100)

            for i, p in enumerate(page_items, start=1):
                razon = _campo(p, "razon_social", "razon", "razon social")
                rut = _campo(p, "rut")
                ciudad = _campo(p, "ciudad")
                comuna = _campo(p, "comuna")
                contacto = _campo(p, "persona_contacto", "contacto", "persona de contacto", "persona_contacto ")
                print(f" {i}) {razon} | {rut} | {ciudad} | {comuna} | {contacto}")

            print("-" * 100)
            print("Opciones: [1-10]=Seleccionar | n=Siguiente | p=Anterior | b=Buscar nuevo | 0=Volver")
            cmd = input("Selecciona opción: ").strip().lower()

            if cmd == "0":
                return None

            if cmd == "b":
                break

            if cmd == "n":
                if page < total_pages - 1:
                    page += 1
                else:
                    print("Ya estás en la última página.")
                continue

            if cmd == "p":
                if page > 0:
                    page -= 1
                else:
                    print("Ya estás en la primera página.")
                continue

            if cmd.isdigit():
                idx = int(cmd)
                if 1 <= idx <= len(page_items):
                    elegido = page_items[idx - 1]
                    razon = _campo(elegido, "razon_social", "razon", "razon social")
                    rut = _campo(elegido, "rut")
                    print(f"\n✅ Seleccionado: {razon} ({rut})\n")
                    return elegido
                else:
                    print("Número fuera de rango para esta página.")
                continue

            print("Opción inválida.")

def crear_proveedor_nuevo():
    print("\n=== Crear proveedor nuevo ===")
    data = {}
    data["razon_social"] = pedir_texto("RAZÓN SOCIAL: ")
    data["rut"] = pedir_texto("RUT: ")
    data["giro"] = pedir_texto("GIRO: ", requerido=False)
    data["direccion"] = pedir_texto("DIRECCIÓN: ", requerido=False)
    data["comuna"] = pedir_texto("COMUNA: ", requerido=False)
    data["ciudad"] = pedir_texto("CIUDAD: ", requerido=False)
    data["telefono"] = pedir_texto("TELÉFONO: ", requerido=False)
    data["persona_contacto"] = pedir_texto("PERSONA DE CONTACTO: ", requerido=False)

    try:
        guardado = agregar(data)
        print(f"\n✅ Proveedor guardado con ID {guardado.get('id')}\n")
        return guardado
    except Exception as e:
        print(f"\n❌ No se pudo guardar: {e}\n")
        return None
