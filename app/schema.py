"""Esquema de datos de la factura extraída.

Este es el contrato que separa la etapa de IA (que solo llena estos campos)
de la etapa de validación (que decide qué hacer con ellos). Ningún dato sale
de este proceso sin pasar por este esquema.

Cada campo tiene una descripción en español (visible en /docs) para que la
página de documentación se entienda sin necesidad de leer el código.
"""
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LineaFactura(BaseModel):
    descripcion: str = Field(description="Qué se cobra en esta línea, tal como aparece en la factura")
    cantidad: Decimal = Field(description="Cuántas unidades de este ítem se facturaron")
    precio_unitario: Decimal = Field(description="Precio de una sola unidad de este ítem")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "descripcion": "Licencia de software anual",
                "cantidad": "1",
                "precio_unitario": "1200.00",
            }
        }
    )


class Factura(BaseModel):
    proveedor_nit: str = Field(description="Número de identificación fiscal (NIT) de quien emite la factura")
    fecha_emision: str = Field(description="Fecha en la que se emitió la factura, formato AAAA-MM-DD")
    total: Decimal = Field(description="Valor total de la factura, tal como aparece impreso en el documento")
    lineas: list[LineaFactura] = Field(
        default_factory=list, description="Cada uno de los ítems o servicios facturados, con cantidad y precio"
    )
    confianza: float = Field(
        ge=0.0,
        le=1.0,
        description="Qué tan segura está la etapa de extracción de estos datos, en una escala de 0 (nada segura) a 1 (totalmente segura)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "proveedor_nit": "900123456-7",
                "fecha_emision": "2026-07-15",
                "total": "2050.00",
                "lineas": [
                    {"descripcion": "Licencia de software anual", "cantidad": "1", "precio_unitario": "1200.00"},
                    {"descripcion": "Soporte técnico premium", "cantidad": "3", "precio_unitario": "150.00"},
                ],
                "confianza": 0.95,
            }
        }
    )

    @field_validator("proveedor_nit")
    @classmethod
    def nit_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("proveedor_nit no puede estar vacío")
        return v.strip()

    @field_validator("total", "confianza", mode="before")
    @classmethod
    def numero_valido(cls, v):
        try:
            return v
        except InvalidOperation as exc:
            raise ValueError("valor numérico inválido") from exc


class ResultadoExtraccion(BaseModel):
    documento_id: int = Field(description="Número consecutivo con el que quedó guardado este documento")
    factura: Factura = Field(description="Los datos que se lograron extraer de la factura")
    decision: str = Field(
        description="Qué se hace con este resultado: 'AUTO_APROBADO' si todo cuadró, o 'A_REVISION_HUMANA' si algo necesita que una persona lo revise. Esta decisión siempre la toma una regla fija, nunca la IA."
    )
    motivo: str = Field(description="Explicación en texto de por qué se tomó esa decisión")
    modo: str = Field(
        description="Cómo se hizo la extracción: 'mock' (reglas simples, sin costo) o 'claude' (modelo de IA real, solo si se configuró una clave)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "documento_id": 1,
                "factura": Factura.model_config["json_schema_extra"]["example"],
                "decision": "AUTO_APROBADO",
                "motivo": "confianza y cuadre de cifras dentro de los umbrales",
                "modo": "mock",
            }
        }
    )
