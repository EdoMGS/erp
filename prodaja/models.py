"""Backward compatibility layer delegating to new package-based models.

All real model definitions now live in prodaja/models/*.py modules.
Keep this file minimal to avoid duplicate model definitions and migration noise.
"""

from .models.invoice import *  # noqa: F401,F403
from .models.main import *  # noqa: F401,F403
from .models.quote import *  # noqa: F401,F403
from .models.work_order import *  # noqa: F401,F403
