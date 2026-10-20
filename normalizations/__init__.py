"""Šest eksplicitnih transformacija kriterija."""
from importlib import import_module

def normalize(name, matrix, types, **kwargs):
    if name not in {'max','minmax','sum','vector','nonlinear','ln'}:
        raise ValueError(f"Nepoznata normalizacija: {name}")
    return import_module(f'normalizations.{name}').normalize(matrix, types, **kwargs)
