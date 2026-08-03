"""
Shared rate limiter instance, kept in its own module to avoid circular imports
between main.py and the routers that need to apply @limiter.limit(...).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
