# Corrección de Errores HTTP 405 - Backend API

## Problema
Error HTTP 405 "Method Not Allowed" al hacer peticiones a la API.

## Causa
Las rutas están definidas con `@router.get()` pero esperan un `Body(...)`, lo cual es inconsistente porque las peticiones GET no pueden tener body.

## Solución

### Archivos a corregir en el backend:

#### 1. `api/routes/movies.py`
```python
# CAMBIAR ESTO:
@router.get("/all")
async def get_all_movies(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):

# POR ESTO (eliminar el Body para GET):
@router.get("/all")
async def get_all_movies(
    current_user: dict = Depends(current_user_dep)
):
    return get_all_movies_controller({})  # Pasar diccionario vacío
```

#### 2. `api/routes/theaters.py`
```python
# CAMBIAR:
@router.get("/all")
async def get_all_theaters(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):

# POR:
@router.get("/all")
async def get_all_theaters(
    current_user: dict = Depends(current_user_dep)
):
    return get_all_theaters_controller({})
```

#### 3. `api/routes/showtimes.py`
```python
# CAMBIAR:
@router.get("/all")
async def get_all_showtimes(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):

# POR:
@router.get("/all")
async def get_all_showtimes(
    current_user: dict = Depends(current_user_dep)
):
    return get_all_showtimes_controller({})
```

#### 4. `api/routes/reserved_seats.py`
```python
# CAMBIAR:
@router.get("/all")
async def get_all_reserved_seats(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):

# POR:
@router.get("/all")
async def get_all_reserved_seats(
    current_user: dict = Depends(current_user_dep)
):
    return get_all_reserved_seats_controller({})
```

#### 5. `api/routes/sales.py`
```python
# CAMBIAR:
@router.get("/all")
async def get_all_sales(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):

# POR:
@router.get("/all")
async def get_all_sales(
    current_user: dict = Depends(current_user_dep)
):
    return get_all_sales_controller({})
```

## Regla general

- **Rutas GET**: No deben tener `Body(...)`, usar query parameters o path parameters si necesitan datos
- **Rutas POST/PUT/DELETE**: Pueden tener `Body(...)` para recibir datos en el cuerpo de la petición

## Configuración CORS adicional

Asegúrate de que tu archivo `api/main.py` tenga esta configuración CORS:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS ANTES de incluir los routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En desarrollo
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ... resto de tu código con los routers
```

## Verificación

Después de hacer estos cambios:

1. Reinicia el servidor FastAPI
2. Ve a `http://localhost:8000/docs`
3. Verifica que las rutas `/movies/all`, `/theaters/all`, etc. aparezcan como GET sin body
4. Prueba el login desde el frontend

## Frontend ya corregido

El frontend ahora está configurado para usar GET sin body para las rutas `/all`.
