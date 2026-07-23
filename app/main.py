"""Servicio de extracción documental — MVP.

Orquesta las etapas del pipeline descrito en la propuesta técnica:
  1. Lectura del PDF (ocr.py, determinista)
  2. Extracción de campos (extractor.py, única etapa con IA)
  3. Validación y decisión de autonomía (validation.py, determinista)
  4. Persistencia (storage.py)

La decisión de aprobar o enviar a revisión humana nunca la toma el modelo:
la toma siempre validation.decidir().
"""
import io
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile

from app import extractor, ocr, storage, validation
from app.schema import ResultadoExtraccion

TAGS_METADATA = [
    {
        "name": "Extracción de facturas",
        "description": (
            "Sube una factura en PDF y el sistema la convierte en datos estructurados. "
            "Una sola etapa usa Inteligencia Artificial (extraer los datos); la decisión "
            "de aprobar el resultado siempre la toma una regla fija, nunca la IA."
        ),
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.inicializar_db()
    yield


app = FastAPI(
    title="Extracción documental — MVP",
    description=(
        "Convierte facturas en PDF a datos estructurados y validados. "
        "Es la puesta en escena de la propuesta técnica: extracción con IA acotada "
        "a una sola etapa, más una capa de reglas fijas que decide si el resultado "
        "se aprueba solo o pasa a revisión humana."
    ),
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
)


@app.get(
    "/salud",
    tags=["Extracción de facturas"],
    summary="Verificar que el servicio está encendido",
    description="No hace nada más que confirmar que el servicio está arriba y respondiendo.",
    response_description="Un mensaje simple confirmando que todo está bien.",
)
def salud():
    return {"estado": "ok"}


@app.post(
    "/extraer",
    response_model=ResultadoExtraccion,
    tags=["Extracción de facturas"],
    summary="Subir una factura en PDF y extraer sus datos",
    description=(
        "Recibe un archivo PDF de una factura. Internamente hace cuatro cosas en orden: "
        "(1) lee el texto del PDF, (2) usa IA (o el modo simulado, si no hay clave configurada) "
        "para llenar los datos —NIT, fecha, total, líneas—, (3) revisa esos datos con reglas fijas "
        "para decidir si se aprueban solos o necesitan revisión humana, y (4) guarda el resultado. "
        "Devuelve los datos extraídos junto con esa decisión y el motivo."
    ),
    response_description="Los datos extraídos de la factura, más la decisión (aprobado o a revisión) y por qué.",
)
async def extraer_documento(
    file: UploadFile = File(..., description="El archivo PDF de la factura a procesar"),
):
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")

    contenido = await file.read()

    try:
        texto = ocr.texto_desde_pdf(io.BytesIO(contenido))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    factura, modo = extractor.extraer(texto)
    decision, motivo = validation.decidir(factura)

    factura_dict = factura.model_dump(mode="json")
    documento_id = storage.guardar_documento(file.filename, factura_dict, decision, motivo, modo)

    return ResultadoExtraccion(
        documento_id=documento_id,
        factura=factura,
        decision=decision,
        motivo=motivo,
        modo=modo,
    )


@app.get(
    "/documentos",
    tags=["Extracción de facturas"],
    summary="Ver el historial de documentos procesados",
    description="Lista todos los documentos que se han enviado a /extraer, más recientes primero, con su decisión.",
    response_description="Una lista de documentos procesados, con su decisión y fecha.",
)
def documentos():
    return storage.listar_documentos()
