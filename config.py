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
    }
}


IVA_TASA = 0.19
APP_NOMBRE = "Sistema OC - Autónomo"

# Plantilla Excel (debe existir en la raíz del proyecto)
PLANTILLA_OC_XLSX = "OC BASE.xlsx"

# Registro predefinido de entrega (sin dirección, como indicaste)
ENTREGA_PREDEFINIDA = {
    "nombre": "Pablo Basta",
    "telefono": "+56 9 XXXXXXXX",
    "correo": "pbasta@rest911.cl",
    # dirección NO obligatoria: no la usaremos por defecto
}

# Condición de pago por defecto (se escribe en C17)
CONDICION_PAGO_DEFAULT = "Transferencia"

