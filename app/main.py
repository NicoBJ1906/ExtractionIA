"""Servicio de extracción documental — MVP.

Orquesta las etapas del pipeline descrito en la propuesta técnica:
  1. Lectura del PDF (ocr.py, determinista)
  2. Extracción de campos (extractor.py, única etapa con IA)
  3. Validación y decisión de autonomía (validation.py, determinista)
  4. Persistencia (storage.py)

La decisión de aprobar o enviar a revisión humana nunca la toma el modelo:
la toma siempre validation.decidir().
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile

from app import extractor, ocr, storage, validation
from app.schema import ResultadoExtraccion


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.inicializar_db()
    yield


app = FastAPI(
    title="Extracción documental — MVP",
    description="Convierte facturas en PDF a datos estructurados y validados.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.post("/extraer", response_model=ResultadoExtraccion)
async def extraer_documento(file: UploadFile = File(...)):
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")

    contenido = await file.read()

    import io

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


@app.get("/documentos")
def documentos():
    return storage.listar_documentos()
