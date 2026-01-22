import hashlib

def make_email_hash(email: str) -> bytes:
    return hashlib.sha256(email.encode()).digest()