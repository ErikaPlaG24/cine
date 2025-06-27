#   Módulo de Utilidades para Hashing de Contraseñas
#   
#   Proporciona funciones para:
#   - Generar hash seguro de contraseñas usando bcrypt
#   - Configuración personalizada del algoritmo de hashing
#   
#   Dependencias:
#   - passlib: Para operaciones de hashing seguro
#   - bcrypt: Para operaciones de hashing y verificación de contraseñas

import bcrypt

# =============================================================================
# FUNCIONES DE HASHING
# =============================================================================

def hash_password(password: str) -> bytes:
    """
    Genera un hash seguro de una contraseña utilizando bcrypt.

    Args:
        password (str): Contraseña en texto plano a hashear

    Returns:
        bytes: Contraseña hasheada en formato seguro

    Example:
        >>> hashed = hash_password("mi_contraseña_secreta")
        >>> verify_password("mi_contraseña_secreta", hashed)
        True
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """
    Verifica si la contraseña proporcionada coincide con el hash almacenado.

    Args:
        plain_password (str): Contraseña en texto plano a verificar
        hashed_password (bytes): Contraseña hasheada

    Returns:
        bool: True si la contraseña coincide, False en caso contrario

    Example:
        >>> hashed = hash_password("mi_contraseña_secreta")
        >>> verify_password("mi_contraseña_secreta", hashed)
        True
    """
    password_byte_enc = plain_password.encode('utf-8')
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password)


#print(f"Your hasshed password is: {hash_password('root')}")