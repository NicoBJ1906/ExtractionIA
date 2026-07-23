# Extracción documental — MVP

Implementación funcional del caso de uso prioritario de la propuesta técnica adjunta: **extracción automática de información desde documentos** (facturas en PDF), con IA acotada a una sola etapa y una capa de reglas determinista que decide si el resultado se aprueba solo o pasa a revisión humana.

Este proyecto es la puesta en escena de la Opción A (MVP low-cost) descrita en el documento — un solo servicio, sin colas ni bases de datos gestionadas, pensado para instalarse y probarse en minutos.

> 📋 **¿Primera vez viendo este proyecto?** Sigue [`MANUAL_DE_PRUEBA.md`](MANUAL_DE_PRUEBA.md) — instrucciones paso a paso, sin asumir experiencia previa.

## Arquitectura

```
PDF ──▶ ocr.py ──▶ extractor.py ──▶ validation.py ──▶ storage.py
        (texto)     (IA: llena       (reglas: decide     (SQLite)
                      el esquema)      si se aprueba)
```

La IA solo interviene en `extractor.py`. La decisión de auto-aprobar o enviar a revisión humana la toma siempre `validation.py`, con reglas fijas (cuadre de cifras, umbral de confianza, campos obligatorios) — nunca el modelo de lenguaje.

Detalle funcional completo en [`aidlc-docs/functional-design.md`](aidlc-docs/functional-design.md).

## Instalación

Requiere Python 3.11+.

```bash
git clone https://github.com/NicoBJ1906/ExtractionIA.git
cd ExtractionIA
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
```

## Cómo probarlo

**No se necesita ninguna clave de API.** Por defecto el servicio corre en modo mock (extracción por reglas simples sobre el texto, sin costo y sin llamadas externas):

```bash
python scripts/generar_muestra.py
uvicorn app.main:app --reload
```

Luego abre en el navegador:

```
http://localhost:8000
```

Esa es la interfaz visual del proyecto: arrastra o selecciona el PDF de ejemplo (`samples/factura_ejemplo.pdf`), procésalo, y verás los datos extraídos junto con la decisión (aprobado o a revisión humana) y el historial de documentos procesados.

También hay documentación técnica interactiva (Swagger) en `http://localhost:8000/docs`, y una alternativa por terminal:

```bash
curl -F "file=@samples/factura_ejemplo.pdf" http://localhost:8000/extraer
curl http://localhost:8000/documentos
```

### Opcional: ver la extracción con Claude real
Si quieres ver la etapa de IA usando un modelo real en vez del modo mock, exporta tu propia clave antes de levantar el servicio:

```bash
export ANTHROPIC_API_KEY=tu-propia-clave      # Windows: set ANTHROPIC_API_KEY=...
uvicorn app.main:app --reload
```

El resto del pipeline (validación, decisión, persistencia) es idéntico en ambos modos.

## Pruebas automatizadas

```bash
python -m pytest tests/ -v
```

## Qué se simplificó a propósito
Este es un MVP, no la versión de producción. La propuesta técnica adjunta describe en su Parte 2.5 una segunda variante escalable (colas, Postgres, multi-tenant, enrutamiento de modelos) que no se implementa aquí — el objetivo de este repositorio es demostrar el razonamiento de arquitectura (IA acotada + validación determinista) de forma instalable y verificable, no replicar la infraestructura completa. Detalle en [`aidlc-docs/nfr.md`](aidlc-docs/nfr.md).
