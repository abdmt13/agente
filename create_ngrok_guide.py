from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUTPUT = r"C:\Users\USER\Documents\agente\Guia_para_iniciar_y_detener_la_aplicacion_con_ngrok.docx"


def set_cell_margins(cell, top=100, start=120, bottom=100, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def shade(element, color):
    props = element.get_or_add_pPr() if element.tag.endswith("}p") else element.get_or_add_tcPr()
    shd = props.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        props.append(shd)
    shd.set(qn("w:fill"), color)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_code(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.left_indent = Inches(0.22)
    p.paragraph_format.right_indent = Inches(0.22)
    p.paragraph_format.keep_together = True
    shade(p._p, "F2F4F7")
    for i, line in enumerate(text.splitlines()):
        if i:
            p.add_run().add_break()
        run = p.add_run(line)
        run.font.name = "Consolas"
        run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:ascii"), "Consolas")
        run._element.rPr.rFonts.set(qn("w:hAnsi"), "Consolas")
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(31, 41, 55)
    return p


def add_step(doc, number, title, explanation, command=None):
    p = doc.add_paragraph(style="Heading 2")
    p.paragraph_format.keep_with_next = True
    p.add_run(f"{number}  {title}")
    body = doc.add_paragraph(explanation)
    body.paragraph_format.space_after = Pt(4 if command else 9)
    if command:
        add_code(doc, command)


doc = Document()
section = doc.sections[0]
section.top_margin = Inches(0.72)
section.bottom_margin = Inches(0.68)
section.left_margin = Inches(0.78)
section.right_margin = Inches(0.78)

styles = doc.styles
styles["Normal"].font.name = "Aptos"
styles["Normal"]._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
styles["Normal"]._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
styles["Normal"].font.size = Pt(10.5)
styles["Normal"].font.color.rgb = RGBColor(31, 41, 55)
styles["Normal"].paragraph_format.space_after = Pt(6)
styles["Normal"].paragraph_format.line_spacing = 1.08

title_style = styles["Title"]
title_style.font.name = "Aptos Display"
title_style._element.rPr.rFonts.set(qn("w:ascii"), "Aptos Display")
title_style._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos Display")
title_style.font.size = Pt(26)
title_style.font.bold = True
title_style.font.color.rgb = RGBColor(0, 0, 0)
title_style.paragraph_format.space_after = Pt(8)

for style_name, size in (("Heading 1", 16), ("Heading 2", 12)):
    st = styles[style_name]
    st.font.name = "Aptos Display"
    st._element.rPr.rFonts.set(qn("w:ascii"), "Aptos Display")
    st._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos Display")
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = RGBColor(0, 0, 0)
    st.paragraph_format.space_before = Pt(12 if style_name == "Heading 1" else 8)
    st.paragraph_format.space_after = Pt(5)

title = doc.add_paragraph(style="Title")
title.add_run("Guía para iniciar y detener la aplicación con ngrok")
intro = doc.add_paragraph(
    "Esta guía permite ejecutar localmente el chatbot Node, el panel FastAPI y el proxy que los publica mediante ngrok. "
    "Los archivos de la aplicación no se modifican al seguir estos pasos."
)
intro.paragraph_format.space_after = Pt(10)

p = doc.add_paragraph()
r = p.add_run("Carpeta de trabajo  ")
r.bold = True
p.add_run(r"C:\Users\USER\Documents\agente")
p.paragraph_format.space_after = Pt(12)

doc.add_heading("Mapa de servicios", level=1)
table = doc.add_table(rows=1, cols=3)
table.autofit = False
table.columns[0].width = Inches(1.55)
table.columns[1].width = Inches(1.0)
table.columns[2].width = Inches(4.35)
headers = ["Servicio", "Puerto", "Función"]
for i, text in enumerate(headers):
    cell = table.rows[0].cells[i]
    cell.text = text
    shade(cell._tc, "1F4E78")
    set_cell_margins(cell)
    for run in cell.paragraphs[0].runs:
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
set_repeat_table_header(table.rows[0])
rows = [
    ("Chatbot Node", "3000", "Interfaz pública y ruta /api/chat"),
    ("FastAPI", "8000", "Panel /personal, documentación /docs y API /api/v1"),
    ("Proxy local", "8080", "Reúne ambos servicios antes de enviarlos a ngrok"),
    ("Inspector ngrok", "4040", "Muestra el estado local del túnel mientras ngrok está activo"),
]
for row_index, values in enumerate(rows):
    cells = table.add_row().cells
    for i, value in enumerate(values):
        cells[i].text = value
        set_cell_margins(cells[i])
        if row_index % 2:
            shade(cells[i]._tc, "F4F7FA")
        cells[i].vertical_alignment = 1
        cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 1 else WD_ALIGN_PARAGRAPH.LEFT

doc.add_heading("Detener la aplicación", level=1)
doc.add_paragraph(
    "Ejecuta el siguiente bloque en PowerShell. Detiene ngrok y únicamente los procesos que estén escuchando en los puertos de esta solución."
)
add_code(doc, """Set-Location C:\\Users\\USER\\Documents\\agente
Stop-Process -Name ngrok -Force -ErrorAction SilentlyContinue

$ports = 3000, 8000, 8080
Get-NetTCPConnection -State Listen |
  Where-Object LocalPort -In $ports |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object { Stop-Process -Id $_ -Force }""")
doc.add_paragraph(
    "Si PowerShell indica acceso denegado, abre PowerShell como administrador y repite el bloque."
)

doc.add_heading("Iniciar la aplicación", level=1)
doc.add_paragraph(
    "Abre cuatro terminales de PowerShell. En cada una, entra primero en la carpeta del proyecto y luego ejecuta el comando indicado. "
    "Mantén abiertas las cuatro terminales mientras la aplicación deba permanecer disponible."
)

add_step(doc, 1, "Iniciar el chatbot Node", "Carga el archivo .env, conecta la base de datos y publica el chatbot en el puerto 3000.",
         """Set-Location C:\\Users\\USER\\Documents\\agente
npm start""")
add_step(doc, 2, "Iniciar FastAPI", "Publica el panel administrativo y la API en la dirección local 127.0.0.1 y el puerto 8000.",
         """Set-Location C:\\Users\\USER\\Documents\\agente
.\\.venv\\Scripts\\python.exe -m uvicorn src.presentation.main:app --host 127.0.0.1 --port 8000""")
add_step(doc, 3, "Iniciar el proxy local", "El proxy envía el chatbot a Node y las rutas administrativas a FastAPI.",
         """Set-Location C:\\Users\\USER\\Documents\\agente
node .ngrok-dual-proxy.mjs""")
add_step(doc, 4, "Iniciar ngrok", "ngrok publica el proxy del puerto 8080. Copia la dirección HTTPS que aparece en la terminal.",
         """Set-Location C:\\Users\\USER\\Documents\\agente
ngrok http 8080""")

doc.add_heading("Rutas públicas", level=1)
doc.add_paragraph("Sustituye URL_PUBLICA por la dirección HTTPS que muestre ngrok.")
routes = doc.add_table(rows=1, cols=2)
routes.autofit = False
routes.columns[0].width = Inches(2.65)
routes.columns[1].width = Inches(4.25)
for i, text in enumerate(("Dirección", "Contenido")):
    cell = routes.rows[0].cells[i]
    cell.text = text
    shade(cell._tc, "1F4E78")
    set_cell_margins(cell)
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in cell.paragraphs[0].runs:
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
set_repeat_table_header(routes.rows[0])
for idx, values in enumerate((
    ("https://URL_PUBLICA/", "Chatbot público"),
    ("https://URL_PUBLICA/personal", "Panel administrativo"),
    ("https://URL_PUBLICA/docs", "Documentación Swagger de FastAPI"),
    ("https://URL_PUBLICA/api/v1", "API de FastAPI"),
)):
    cells = routes.add_row().cells
    for i, value in enumerate(values):
        cells[i].text = value
        set_cell_margins(cells[i])
        if idx % 2:
            shade(cells[i]._tc, "F4F7FA")

doc.add_heading("Comprobar que todo funciona", level=1)
doc.add_paragraph("Ejecuta estas solicitudes locales antes de compartir la dirección pública:")
add_code(doc, """Invoke-WebRequest http://127.0.0.1:3000 -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:8000/personal -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:8080 -UseBasicParsing""")
doc.add_paragraph("Cada comando debe mostrar StatusCode 200.")

doc.add_heading("Solución de problemas", level=1)
issues = [
    ("EADDRINUSE en el puerto 3000", "Ya existe una copia de Node. Ejecuta primero la sección Detener la aplicación y vuelve a iniciar los servicios."),
    ("Modo demostración", "Comprueba que GEMINI_API_KEY tenga una clave válida en .env. No compartas ni confirmes ese archivo en Git."),
    ("Gemini no responde", "Verifica GEMINI_MODEL=gemini-3.8-flash y GEMINI_THINKING_LEVEL=low, después reinicia Node."),
    ("ngrok muestra una advertencia", "En el plan gratuito, cada navegador puede ver una pantalla de advertencia una vez por endpoint. Continúa únicamente si reconoces la dirección."),
    ("502 Bad Gateway", "Confirma que los puertos 3000, 8000 y 8080 respondan localmente antes de reiniciar ngrok."),
]
for title_text, explanation in issues:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    lead = p.add_run(f"{title_text}. ")
    lead.bold = True
    p.add_run(explanation)

doc.add_heading("Notas de seguridad", level=1)
for item in (
    "La URL de ngrok es pública mientras el proceso esté activo.",
    "No publiques el archivo .env ni compartas las claves de Gemini o ngrok.",
    "Protege las rutas administrativas antes de usar esta configuración como servicio permanente.",
    "Para cortar inmediatamente el acceso público, ejecuta Stop-Process -Name ngrok -Force.",
):
    doc.add_paragraph(item, style="List Bullet")

for sec in doc.sections:
    footer = sec.footer
    footer_p = footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer_p.add_run("Guía operativa local")
    footer_run.font.name = "Aptos"
    footer_run.font.size = Pt(8)
    footer_run.font.color.rgb = RGBColor(107, 114, 128)

doc.core_properties.title = "Guía para iniciar y detener la aplicación con ngrok"
doc.core_properties.subject = "Procedimiento local para Node FastAPI proxy y ngrok"
doc.core_properties.author = ""
doc.save(OUTPUT)
print(OUTPUT)
