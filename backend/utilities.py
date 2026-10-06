"""
Utilities helper for the Student Marketplace.
"""

import os

def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing environment variable {name}. Define it in your .env file."
        )
    return value
