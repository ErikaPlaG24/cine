#   Módulo de Autenticación JWT
#   
#   Proporciona funcionalidades para:
#   - Hash y verificación de contraseñas
#   - Generación de tokens JWT (access y refresh)
#   - Decodificación y validación de tokens
#   
#   Dependencias:
#   - passlib: Para hashing de contraseñas (bcrypt)
#   - python-jose: Para operaciones con JWT
#   - python-dotenv: Para manejo de variables de entorno

from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from fastapi import HTTPException

# =============================================================================
# CONFIGURACIÓN INICIAL
# =============================================================================

# Cargar variables de entorno desde archivo .env
load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(__file__), 
        '..', 
        '.env'
    )
)

# Contexto para hashing de contraseñas
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)

# Constantes de configuración
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15)
)
REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 30)
)

# =============================================================================
# FUNCIONES DE HASH DE CONTRASEÑAS
# =============================================================================

def verify_password(
    plain_password: str, 
    hashed_password: str
) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su versión hasheada.
    
    Args:
        plain_password (str): Contraseña en texto plano
        hashed_password (str): Contraseña hasheada
        
    Returns:
        bool: True si coinciden, False en caso contrario
    """
    return pwd_context.verify(
        plain_password, 
        hashed_password
    )

# =============================================================================
# FUNCIONES DE GENERACIÓN DE TOKENS
# =============================================================================

def create_access_token(
    data: dict, 
    expires_delta: timedelta = None
) -> str:
    """
    Genera un token JWT de acceso.
    
    Args:
        data (dict): Datos a incluir en el token
        expires_delta (timedelta, optional): Tiempo de expiración personalizado
        
    Returns:
        str: Token JWT firmado
    """
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + (
        expires_delta or 
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    to_encode.update({
        "exp": expire, 
        "iat": now
    })
    
    return jwt.encode(
        to_encode, 
        JWT_SECRET_KEY, 
        algorithm="HS512"
    )

def create_refresh_token(
    data: dict, 
    expires_delta: timedelta = None
) -> str:
    """
    Genera un token JWT de refresh.
    
    Args:
        data (dict): Datos a incluir en el token
        expires_delta (timedelta, optional): Tiempo de expiración personalizado
        
    Returns:
        str: Token JWT firmado
    """
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + (
        expires_delta or 
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    to_encode.update({
        "exp": expire, 
        "iat": now
    })
    
    return jwt.encode(
        to_encode, 
        JWT_REFRESH_SECRET_KEY, 
        algorithm="HS512"
    )

# =============================================================================
# FUNCIONES DE VALIDACIÓN DE TOKENS
# =============================================================================

def decode_token(
    token: str, 
    secret_key: str
) -> dict:
    """
    Decodifica y valida un token JWT.
    
    Args:
        token (str): Token JWT a validar
        secret_key (str): Clave secreta para verificar la firma
        
    Returns:
        dict: Payload del token si es válido
        
    Raises:
        HTTPException: Si el token está expirado o es inválido
    """
    try:
        payload = jwt.decode(
            token, 
            secret_key, 
            algorithms=["HS512"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, 
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401, 
            detail="Invalid token"
        )

def get_token_expiration(token: str) -> datetime:
    """
    Obtiene la fecha de expiración (exp) de un token JWT.

    Args:
        token (str): Token JWT

    Returns:
        datetime: Fecha y hora de expiración del token

    Raises:
        HTTPException: Si el token es inválido o no contiene 'exp'
    """
    try:
        # Decodifica sin verificar expiración ni firma
        payload = jwt.get_unverified_claims(token)
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=400,
                detail="Token does not contain expiration"
            )
        return datetime.utcfromtimestamp(exp)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid token"
        )

def get_current_user(token:str) -> dict:
    """
    Obtiene el usuario actual a partir del token JWT.

    Args:
        token (str): Token JWT

    Returns:
        dict: Información del usuario

    Raises:
        HTTPException: Si el token es inválido o no contiene 'username'
    """
    payload = decode_token(token, JWT_SECRET_KEY)
    username = payload.get("username")
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Token does not contain username"
        )
    return {"username": username, "role": payload.get("role")}