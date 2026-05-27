from passlib.context import CryptContext

# Configuramos passlib para que use el algoritmo bcrypt para cifrar
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Recibe la contraseña limpia y la devuelve encriptada (Hash)
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Compara una contraseña limpia con el Hash de la DB para ver si coinciden
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)