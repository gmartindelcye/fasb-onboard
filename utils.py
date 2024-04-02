from passlib.context import CryptContext
from settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


if __name__ == "__main__":
    password = 'secret'
    hash_password = get_password_hash(password)
    print(f"password: {password} hash_password: {hash_password}")
    check = verify_password(password, hash_password)
    print(f"check: {check}")