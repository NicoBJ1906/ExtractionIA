# Requisitos no funcionales asumidos para el MVP

| Requisito | Decisión en el MVP | Cómo escalaría (Opción B de la propuesta) |
|---|---|---|
| Concurrencia | Un proceso `uvicorn`, SQLite | Colas + workers horizontales, Postgres |
| Costo de IA | Modo mock por defecto; Claude solo si se exporta una clave | Enrutamiento de modelos por confianza, caché de prompt, Batch API |
| Disponibilidad | Sin objetivo formal (demo local) | SLO explícito, reintentos, cola de mensajes fallidos |
| Seguridad de datos | Sin PII real (factura sintética de ejemplo) | Enmascarado de PII antes de salir a un proveedor externo |
| Multi-tenant | No aplica (un solo usuario local) | Partición dura por `tenant_id` en base de datos y caché |
| Auditabilidad | Cada documento guarda decisión + motivo en SQLite | Bitácora inmutable, trazabilidad completa por documento |

El MVP prioriza que cualquier persona pueda instalarlo y probarlo en minutos, sin credenciales ni infraestructura adicional, manteniendo el mismo contrato de datos y la misma separación entre IA (extracción) y reglas (validación) que tendría la versión de producción.
