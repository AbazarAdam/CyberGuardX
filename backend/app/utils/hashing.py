"""
Hashing Utility
================
Single source of truth for email hashing.
Uses SHA-1 for compatibility with the Have I Been Pwned k-anonymity API.

**Important:** All modules that need to hash emails MUST import from here
rather than re-implementing the logic.
"""

import hashlib


def hash_email(email: str) -> str:
    """
    Normalise and SHA-1 hash an email address.

    Steps:
        1. Strip leading / trailing whitespace
        2. Convert to lowercase
        3. Return the SHA-1 hex digest

    Args:
        email: Raw email address string.

    Returns:
        40-character lowercase hex SHA-1 digest.
    """
    normalized = email.strip().lower()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()
