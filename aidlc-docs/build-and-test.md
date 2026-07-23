# Cómo se construyó y probó

## Construcción
Servicio único en FastAPI, cuatro módulos con una responsabilidad cada uno (`ocr.py`, `extractor.py`, `validation.py`, `storage.py`), orquestados por `main.py`. Sin dependencias de infraestructura externa (sin Docker, sin base de datos gestionada) para que la instalación sea `pip install` + un comando.

## Pruebas

```bash
python -m pytest tests/ -v
```

Cubren la parte que más importa auditar: la regla determinista de `validation.py` (cuándo se auto-aprueba una factura y cuándo se envía a revisión humana), incluyendo los cuatro motivos de rechazo: confianza baja, cifras que no cuadran, ausencia de líneas y NIT no identificado.

## Prueba manual de punta a punta

```bash
python scripts/generar_muestra.py      # genera samples/factura_ejemplo.pdf
uvicorn app.main:app --reload          # levanta el servicio
curl -F "file=@samples/factura_ejemplo.pdf" http://localhost:8000/extraer
curl http://localhost:8000/documentos
```

Sin `ANTHROPIC_API_KEY` definida, corre en modo mock. Exportando la variable, la extracción la hace Claude (`claude-haiku-4-5`) con salidas estructuradas — el resto del pipeline (validación, decisión, persistencia) es exactamente el mismo código.
