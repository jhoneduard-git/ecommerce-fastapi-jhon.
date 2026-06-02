from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt  # Asegúrate de tener instalada la librería pyjwt

# ==========================================
# 🔑 CONFIGURACIÓN Y CONSTANTES DEL JWT
# ==========================================
# Puedes cambiar esta clave secreta por cualquier texto largo en el futuro
SECRET_KEY = "mi_llave_secreta_super_segura_para_el_ecommerce"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de Passlib para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==========================================
# 🛡️ FUNCIONES PARA CONTRASEÑAS (BCRYPT)
# ==========================================
def get_password_hash(password: str) -> str:
    """Recibe la contraseña limpia y la devuelve encriptada (Hash)"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña limpia con el Hash de la DB"""
    return pwd_context.verify(plain_password, hashed_password)


# ==========================================
# 🎫 FUNCIÓN PARA GENERAR EL TOKEN JWT
# ==========================================
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Genera un token JWT firmado y con tiempo de expiración"""
    to_encode = data.copy()
    
    # Si pasamos un tiempo específico lo usa, si no, usa los 30 minutos por defecto
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    # Añadimos la fecha de expiración al cuerpo (payload) del token
    to_encode.update({"exp": expire})
    
    # Creamos y firmamos el JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt