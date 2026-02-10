import hashlib


def hash_email(email: str) -> str:
    normalized = email.strip().lower()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()
