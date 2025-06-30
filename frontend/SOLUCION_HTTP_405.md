# Instrucciones para corregir el error HTTP 405 en FastAPI

## Pasos para solucionar el problema:

### 1. Verificar que FastAPI esté corriendo
Ejecutar en la terminal desde la carpeta raíz del proyecto:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Verificar acceso a la documentación
Abrir en el navegador: `http://localhost:8000/docs`
- Si no carga, el problema es que FastAPI no está corriendo correctamente
- Si carga, verificar que aparezcan las rutas de autenticación

### 3. Configurar CORS en api/main.py

**IMPORTANTE**: Agregar CORS ANTES de incluir los routers:

```python
import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # AGREGAR ESTA LÍNEA
from database.mysql_connection import MySQLConnection
# ... resto de imports

app = FastAPI()

# AGREGAR CORS AQUÍ - ANTES DE INCLUIR ROUTERS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción cambiar por dominios específicos
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize the database connection
db = MySQLConnection(
    host        = os.getenv("MYSQL_HOST"),
    port        = 3306,
    user        = "root",
    password    = "root",
    database    = "cine"
)

@app.get("/")
def read_root():
    return {"message": "Cine API"}

# Resto de los routers...
app.include_router(auth_routes, prefix="/auth")
# etc...
```

### 4. Corregir rutas GET que tienen Body()

En cada archivo de rutas (movies.py, theaters.py, etc.), cambiar:

```python
# ANTES (causa error 405):
@router.get("/all")
async def get_all_movies(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):

# DESPUÉS:
@router.get("/all")
async def get_all_movies(
    current_user: dict = Depends(current_user_dep)
):
    return get_all_movies_controller({})
```

### 5. Instalar dependencias de CORS si no están instaladas
```bash
pip install "fastapi[all]"
```

### 6. Reiniciar el servidor
Después de hacer los cambios, reiniciar FastAPI:
```bash
# Ctrl+C para parar
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Probar en el frontend
1. Usar el botón "🔍 Probar Endpoints" para verificar conectividad
2. Si los endpoints funcionan, intentar login normal
3. Si no funcionan, usar el botón "🧪 Modo Mock" para probar con datos simulados

## Verificación paso a paso:

1. **Servidor corriendo**: `http://localhost:8000` debe mostrar `{"message": "Cine API"}`
2. **Documentación accesible**: `http://localhost:8000/docs` debe cargar la interfaz de Swagger
3. **CORS configurado**: No debe haber errores de CORS en la consola del navegador
4. **Rutas corregidas**: Las rutas GET no deben tener Body() en los parámetros

## Si nada funciona:
Usar el modo mock temporal para probar el frontend mientras corriges el backend:
- Hacer clic en "🧪 Modo Mock" en la pantalla de login
- Usar credenciales: usuario `admin`, contraseña `123456`
