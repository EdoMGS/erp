"""Compatibility shim for legacy imports.

This module re-exports models from the installed 'client' app, which uses the
app label 'client_app' for migration and FK compatibility. Importers that use
``from client_app.models import ClientSupplier`` will receive the models defined
in ``client.models`` so there is a single source of truth.
"""

from client.models import (  # noqa: F401
    CityPostalCode,
    ClientActivityLog,
    ClientProfile,
    ClientSupplier,
)

__all__ = [
    "ClientSupplier",
    "ClientProfile",
    "CityPostalCode",
    "ClientActivityLog",
]
