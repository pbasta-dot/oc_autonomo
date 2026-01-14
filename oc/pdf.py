import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def money(v: float) -> str:
    return f"{v:,.0f}".replace(",", ".")

def generar_pdf_oc(oc, output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{oc.numero}.pdf")

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "ORDEN DE COMPRA")
    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"N°: {oc.numero}")
    c.drawString(300, y, f"Fecha: {oc.fecha.strftime('%d-%m-%Y %H:%M')}")
    y -= 20

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Empresa emisora")
    y -= 15
    c.setFont("Helvetica", 10)
    c.drawString(50, y, oc.empresa_emisora["nombre"]); y -= 14
    c.drawString(50, y, f"RUT/ID: {oc.empresa_emisora['rut']}"); y -= 14
    c.drawString(50, y, f"Dirección: {oc.empresa_emisora['direccion']}"); y -= 14
    c.drawString(50, y, f"Contacto: {oc.empresa_emisora['correo']} | {oc.empresa_emisora['telefono']}")
    y -= 25

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Cliente")
    y -= 15
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Nombre: {oc.cliente_nombre}"); y -= 14
    c.drawString(50, y, f"Centro de costo: {oc.centro_costo}"); y -= 14
    c.drawString(50, y, f"Condición: {'Con IVA' if oc.con_iva else 'Sin IVA'}")
    y -= 25

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Cant.")
    c.drawString(90, y, "Descripción")
    c.drawString(400, y, "V. Unit")
    c.drawString(470, y, "Total")
    y -= 10
    c.line(50, y, 545, y)
    y -= 15

    c.setFont("Helvetica", 10)
    for it in oc.items:
        if y < 120:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)

        c.drawString(50, y, str(it.cantidad))
        c.drawString(90, y, it.descripcion[:45])
        c.drawRightString(455, y, money(it.valor_unitario))
        c.drawRightString(545, y, money(it.total_linea))
        y -= 14

    y -= 10
    c.line(350, y, 545, y)
    y -= 18

    c.setFont("Helvetica-Bold", 10)
    c.drawString(350, y, "Subtotal:")
    c.drawRightString(545, y, money(oc.subtotal))
    y -= 14
    c.drawString(350, y, "IVA:")
    c.drawRightString(545, y, money(oc.iva))
    y -= 14
    c.drawString(350, y, "TOTAL:")
    c.drawRightString(545, y, money(oc.total))

    c.save()
    return filename
