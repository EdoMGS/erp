from .jls_rates import get_local_rate, LocalRate  # noqa: F401
from .payroll_tax import compute_local_income_tax, LocalTaxComputation  # noqa: F401

__all__ = [
    'get_local_rate',
    'LocalRate',
    'compute_local_income_tax',
    'LocalTaxComputation',
    'PayrollCalculator',
    'EvaluacijaService',
]


class _Deferred:
    def __init__(self, target_name):
        self._target_name = target_name
        self._resolved = None

    def _resolve(self):
        if self._resolved is None:
            from .. import services as _legacy

            self._resolved = getattr(_legacy, self._target_name)
        return self._resolved

    def __getattr__(self, item):
        return getattr(self._resolve(), item)

    def __call__(self, *a, **kw):  # if class is instantiated
        return self._resolve()(*a, **kw)


# Proxies to avoid import-time circular reference
PayrollCalculator = _Deferred('PayrollCalculator')  # type: ignore
EvaluacijaService = _Deferred('EvaluacijaService')  # type: ignore
