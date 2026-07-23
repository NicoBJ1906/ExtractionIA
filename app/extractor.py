"""Única etapa del pipeline que usa IA: convertir texto de un documento en campos
estructurados de una factura.

Dos modos, misma forma de salida:
- Modo mock (por defecto, sin costo, sin clave): reglas simples sobre el texto.
  Sirve para instalar y probar el proyecto sin depender de ningún proveedor externo.
- Modo Claude (si se exporta ANTHROPIC_API_KEY): extracción real con salidas
  estructuradas, restringida al mismo esquema. La IA nunca decide si el resultado
  se aprueba; eso lo hace la capa de validación (ver validation.py).
"""
import json
import os
import re
from decimal import Decimal, InvalidOperation

from app.schema import Factura

MODELO = "claude-haiku-4-5"

ESQUEMA_FACTURA = {
    "type": "object",
    "properties": {
        "proveedor_nit": {"type": "string", "description": "NIT o identificador fiscal del proveedor"},
        "fecha_emision": {"type": "string", "description": "Fecha en formato ISO-8601 (AAAA-MM-DD)"},
        "total": {"type": "number", "description": "Valor total de la factura"},
        "confianza": {"type": "number", "description": "Confianza del extractor, entre 0 y 1"},
        "lineas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "descripcion": {"type": "string"},
                    "cantidad": {"type": "number"},
                    "precio_unitario": {"type": "number"},
                },
                "required": ["descripcion", "cantidad", "precio_unitario"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["proveedor_nit", "fecha_emision", "total", "confianza", "lineas"],
    "additionalProperties": False,
}

PROMPT_SISTEMA = (
    "Extraes datos de facturas a partir de su texto plano. Devuelve solo los campos "
    "pedidos por el esquema. Si un campo no aparece en el texto, no lo inventes: usa "
    "un valor vacío o razonable y baja el valor de 'confianza' en consecuencia."
)


def extraer(texto: str) -> tuple[Factura, str]:
    """Devuelve (factura, modo) donde modo es 'claude' o 'mock'."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return _extraer_con_claude(texto), "claude"
    return _extraer_mock(texto), "mock"


def _extraer_con_claude(texto: str) -> Factura:
    import anthropic

    cliente = anthropic.Anthropic()
    respuesta = cliente.messages.create(
        model=MODELO,
        max_tokens=1024,
        system=PROMPT_SISTEMA,
        output_config={"format": {"type": "json_schema", "schema": ESQUEMA_FACTURA}},
        messages=[{"role": "user", "content": texto}],
    )
    datos = json.loads(respuesta.content[0].text)
    return Factura(**datos)


def _extraer_mock(texto: str) -> Factura:
    """Extractor sin IA: reglas simples sobre el texto, misma forma de salida.

    No pretende ser un extractor de producción — su único propósito es que el
    proyecto se pueda instalar y probar de punta a punta sin ninguna clave de API.
    """
    nit = _buscar(r"NIT[:\s]*([\d\.\-]+)", texto) or "NO_ENCONTRADO"
    fecha = _buscar(r"(\d{4}-\d{2}-\d{2})", texto) or "1970-01-01"
    total_str = _buscar(r"TOTAL[:\s]*\$?\s*([\d\.,]+)", texto, flags=re.IGNORECASE)
    total = _a_decimal(total_str) if total_str else Decimal("0")

    lineas = []
    for match in re.finditer(
        r"^(?P<desc>.+?)\s+(?P<cant>\d+)\s+x\s+\$?(?P<precio>[\d\.,]+)$",
        texto,
        flags=re.MULTILINE,
    ):
        lineas.append(
            {
                "descripcion": match.group("desc").strip(),
                "cantidad": _a_decimal(match.group("cant")),
                "precio_unitario": _a_decimal(match.group("precio")),
            }
        )

    confianza = 0.95 if (nit != "NO_ENCONTRADO" and total_str and lineas) else 0.4
    return Factura(
        proveedor_nit=nit,
        fecha_emision=fecha,
        total=total,
        lineas=lineas,
        confianza=confianza,
    )


def _buscar(patron: str, texto: str, flags: int = 0) -> str | None:
    m = re.search(patron, texto, flags)
    return m.group(1) if m else None


def _a_decimal(valor: str) -> Decimal:
    """Interpreta números en formato US: la coma es separador de miles, el punto es decimal."""
    limpio = valor.replace(",", "")
    try:
        return Decimal(limpio)
    except InvalidOperation:
        return Decimal("0")
