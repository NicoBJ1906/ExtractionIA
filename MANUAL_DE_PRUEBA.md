# Manual de instalación y prueba

Esta guía asume que no conoces el proyecto y lo estás probando por primera vez, como si acabaras de recibir la entrega de una prueba técnica. Sigue los pasos en orden.

## Requisitos previos

- **Python 3.11 o superior** instalado. Para comprobarlo, abre una terminal y escribe:
  ```
  python --version
  ```
  Si ves algo como `Python 3.12.10`, estás listo. Si dice "no se reconoce el comando", necesitas instalar Python desde [python.org](https://www.python.org/downloads/) antes de continuar.

- No necesitas ninguna clave de API, ninguna cuenta ni ningún servicio externo. Todo corre en tu computador.

## Paso 1 — Obtener el proyecto

Si lo descargaste como `.zip`: descomprímelo en cualquier carpeta y abre una terminal dentro de esa carpeta (`ExtractionIA/`).

Si lo vas a clonar desde GitHub:
```bash
git clone https://github.com/NicoBJ1906/ExtractionIA.git
cd ExtractionIA
```

## Paso 2 — Crear un entorno aislado (virtual environment)

Un "entorno virtual" es una carpeta separada donde se instalan las librerías que este proyecto necesita, sin mezclarlas con nada más de tu computador. Se crea una sola vez:

```bash
python -m venv venv
```

Esto crea una carpeta llamada `venv/` dentro del proyecto. No borra ni toca nada de tu sistema.

## Paso 3 — Activar el entorno

Cada vez que quieras trabajar en el proyecto, primero "entras" al entorno:

**Windows (CMD o Git Bash):**
```
venv\Scripts\activate
```

**macOS / Linux:**
```
source venv/bin/activate
```

Sabrás que funcionó porque al inicio de la línea de tu terminal va a aparecer `(venv)`.

## Paso 4 — Instalar las dependencias

Con el entorno ya activado:

```bash
pip install -r requirements.txt
```

Esto va a tardar uno o dos minutos la primera vez — está descargando e instalando las librerías que usa el proyecto (FastAPI, Pydantic, etc.). Vas a ver mucho texto pasar; es normal.

## Paso 5 — Generar una factura de ejemplo

El proyecto necesita un PDF de prueba. Ya viene uno incluido en `samples/factura_ejemplo.pdf`, pero si quieres generarlo de nuevo (o no existe):

```bash
python scripts/generar_muestra.py
```

Deberías ver: `Generado: .../samples/factura_ejemplo.pdf`

## Paso 6 — Levantar el servicio

```bash
uvicorn app.main:app --reload
```

Vas a ver algo como:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

**Deja esta terminal abierta** — el servicio se queda corriendo ahí. Si la cierras, el servicio se apaga.

## Paso 7 — Probarlo desde el navegador (la forma más fácil)

Abre en tu navegador:
```
http://localhost:8000/docs
```

Vas a ver una página con la lista de operaciones disponibles (`/extraer`, `/documentos`, `/salud`). Para probar la extracción:

1. Haz clic en `POST /extraer`.
2. Haz clic en el botón "Try it out".
3. En el campo de archivo, selecciona `samples/factura_ejemplo.pdf` (está dentro de la carpeta del proyecto).
4. Haz clic en "Execute".
5. Más abajo va a aparecer la respuesta: los datos que se extrajeron de la factura (NIT, fecha, total, líneas) y al final la decisión: `"decision":"AUTO_APROBADO"`.

## Paso 8 — Probarlo desde la terminal (alternativa)

Abre una **segunda terminal** (deja la primera corriendo el servicio) y ejecuta:

```bash
curl -F "file=@samples/factura_ejemplo.pdf" http://localhost:8000/extraer
```

Vas a recibir la misma respuesta, en formato de texto (JSON).

Para ver el historial de todo lo que has procesado:
```bash
curl http://localhost:8000/documentos
```

## Paso 9 — Correr las pruebas automatizadas (opcional)

Para confirmar que la lógica de validación funciona correctamente:

```bash
python -m pytest tests/ -v
```

Deberías ver 5 pruebas, todas en verde (`PASSED`).

## Cómo detener el servicio

Vuelve a la terminal donde corre `uvicorn` y presiona `Ctrl + C`.

## Problemas comunes

| Problema | Solución |
|---|---|
| `python` no se reconoce como comando | Instala Python desde python.org y reinicia la terminal |
| `Address already in use` / el puerto 8000 ya está ocupado | Usa otro puerto: `uvicorn app.main:app --reload --port 8001` (y ajusta la URL en los pasos siguientes) |
| No aparece `(venv)` después de activar | En Windows, si usas PowerShell en vez de CMD, el comando es `venv\Scripts\Activate.ps1`; si da error de permisos, usa CMD o Git Bash en su lugar |
| Error al instalar `pypdf` o similar | Verifica que estés usando Python 3.11 o superior (`python --version`) |

## ¿Y si quiero ver la extracción con IA real en vez del modo simulado?

Por defecto todo corre en modo simulado (sin costo, sin clave). Si quieres ver la extracción hecha por un modelo de IA real (Claude), define tu propia clave antes del Paso 6:

```bash
set ANTHROPIC_API_KEY=tu-propia-clave      # Windows CMD
export ANTHROPIC_API_KEY=tu-propia-clave   # Git Bash / macOS / Linux
```

Y luego levanta el servicio normalmente (Paso 6). El resto del comportamiento es idéntico.
