# Configuración CORS para el Backend

Para que el frontend pueda comunicarse correctamente con la API FastAPI, es necesario configurar CORS (Cross-Origin Resource Sharing) en el backend.

## Archivo a modificar: `api/main.py`

Agregar las siguientes líneas al archivo principal de la API:

```python
from fastapi.middleware.cors import CORSMiddleware

# ... código existente ...

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:3000", "http://localhost:8080", "*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ... resto del código ...
```

## Instalación de dependencia

Si no está instalada, ejecutar:

```bash
pip install fastapi[all]
```

## Configuración de desarrollo vs producción

### Desarrollo
```python
allow_origins=["*"]  # Permite cualquier origen (solo para desarrollo)
```

### Producción
```python
allow_origins=["https://tu-dominio.com", "https://www.tu-dominio.com"]  # Especificar dominios exactos
```

## Comandos para ejecutar el sistema completo

### 1. Iniciar el backend (en la carpeta raíz del proyecto)
```bash
# Con uvicorn directamente
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# O con docker-compose (si está configurado)
docker-compose up
```

### 2. Abrir el frontend
```bash
# Opción 1: Abrir directamente el archivo HTML
# Navegar a la carpeta frontend y abrir index.html en el navegador

# Opción 2: Usar un servidor HTTP simple (recomendado)
cd frontend
python -m http.server 3000

# O con Node.js
npx http-server -p 3000
```

## Verificación de conexión

1. Abrir el navegador en `http://localhost:3000` (frontend)
2. La API debe estar disponible en `http://localhost:8000`
3. Verificar en la consola del navegador (F12) si hay errores de CORS
4. Si aparece el indicador naranja "MODO DESARROLLO", significa que la API no está disponible y se está usando el modo mock

## URLs de prueba

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Base**: http://localhost:8000

## Credenciales de prueba (modo mock)

- **Usuario**: admin
- **Contraseña**: 123456

(En producción, usar las credenciales configuradas en la base de datos)
