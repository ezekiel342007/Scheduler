from passlib.hash import pbkdf2_sha256

def get_hashed_password(password: str) -> str:
    return pbkdf2_sha256.hash(str(password))

def verify_password(password: str, hashed_password: str) -> bool:
    return pbkdf2_sha256.verify(str(password), hashed_password)
