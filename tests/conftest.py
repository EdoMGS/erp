from __future__ import annotations

from hypothesis import settings

# CI profile with fewer examples to keep the suite fast.
settings.register_profile("ci", max_examples=150)
settings.load_profile("ci")
