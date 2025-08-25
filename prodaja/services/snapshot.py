from __future__ import annotations

from typing import Any

from ..models.quote import EstimSnapshot


def snapshot_as_dict(snapshot: EstimSnapshot) -> dict[str, Any]:
    """Serialize EstimSnapshot to the dict shape used for hashing and API responses."""
    return {
        "input": snapshot.input_data,
        "breakdown": snapshot.breakdown,
        "norms_version": snapshot.norms_version,
        "price_list_version": snapshot.price_list_version,
        "rounding_policy": snapshot.rounding_policy,
    }
