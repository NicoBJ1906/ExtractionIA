# Diseño funcional

## Endpoints

### `POST /extraer`
Recibe un PDF (`multipart/form-data`, campo `file`) y devuelve el resultado de procesarlo por las cuatro etapas del pipeline.

**Entrada:** un archivo PDF.

**Salida (200):**
```json
{
  "documento_id": 1,
  "factura": {
    "proveedor_nit": "900123456-7",
    "fecha_emision": "2026-07-15",
    "total": "2050.00",
    "lineas": [{ "descripcion": "...", "cantidad": "1", "precio_unitario": "1200.00" }],
    "confianza": 0.95
  },
  "decision": "AUTO_APROBADO",
  "motivo": "confianza y cuadre de cifras dentro de los umbrales",
  "modo": "mock"
}
```

**Errores:**
- `400` si el archivo no es un PDF.
- `422` si no se pudo leer texto del PDF (ver nota de OCR abajo).

### `GET /documentos`
Lista los documentos procesados (id, archivo, decisión, motivo, modo, fecha), más recientes primero. Sustituye a una cola de revisión real, que en producción tendría una interfaz dedicada para aprobar/corregir.

### `GET /salud`
Chequeo simple de disponibilidad.

## Contrato entre etapas
`ocr.py` → texto plano → `extractor.py` → objeto `Factura` (Pydantic) → `validation.py` → `(decision, motivo)` → `storage.py`. Cada etapa solo conoce la forma de datos que le entrega la anterior — permite reemplazar cualquiera (p. ej. cambiar el extractor mock por Claude, o el OCR por un servicio real) sin tocar las demás.

## Qué se dejó fuera del MVP a propósito
- **OCR de imagen real** (Azure Document Intelligence / Textract): el MVP solo lee PDFs con capa de texto. Un PDF escaneado sin texto devuelve `422` con un mensaje explícito de qué haría falta.
- **Cola de revisión humana con interfaz:** `GET /documentos` expone la lista; una interfaz de aprobar/corregir en un clic es una capa de presentación adicional, no un cambio de arquitectura.
- **Multi-tenant, colas, Postgres:** corresponden a la variante escalable (Opción B) descrita en la propuesta técnica, no a este MVP.
