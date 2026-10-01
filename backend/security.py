"""
Security helper for the Student Marketplace.
Uses bcrypt for password hashing.
"""

import bcrypt

def hash_password(plain: str) -> str:
    """hash a plaintext password"""
    raw = plain.encode("utf-8")
    if len(raw) > 72:
        # bcrypt only uses the first 72 bytes; refuse instead of silently truncating
        raise ValueError("Password exceeds bcrypt's 72-byte limit.")
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=12)).decode("utf-8")