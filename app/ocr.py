"""Lectura de texto desde el PDF de entrada.

Etapa determinista de pre-proceso: no interpreta el contenido, solo lo convierte
a texto plano para que la siguiente etapa (extracción) trabaje sobre algo uniforme,
sin importar si el PDF vino de un correo, una carga manual o un escaneo con capa
de texto ya reconocida.
"""
from pypdf import PdfReader


def texto_desde_pdf(ruta_o_bytes) -> str:
    lector = PdfReader(ruta_o_bytes)
    partes = [pagina.extract_text() or "" for pagina in lector.pages]
    texto = "\n".join(partes).strip()
    if not texto:
        raise ValueError(
            "No se pudo leer texto del PDF. En producción, este caso activaría "
            "un OCR de imagen (p. ej. Azure Document Intelligence / AWS Textract) "
            "antes de enviarlo a revisión humana."
        )
    return texto
