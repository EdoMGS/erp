"""Backward compatibility layer delegating to new package-based models.

All real model definitions now live in prodaja/models/main.py.
Keep this file minimal to avoid duplicate model definitions and migration noise.
Remove once all imports updated to use prodaja.models.* directly from the package.
"""

from .models.main import *  # noqa: F401,F403
