"""Zajedničke provjere ulaza i oblikovanje rezultata."""
from __future__ import annotations
import numpy as np
import pandas as pd

def directions(types, columns):
    """Vrati +1 za dobitne i -1 za troškovne kriterije."""
    if isinstance(types, dict):
        types = pd.Series(types)
    if not isinstance(types, pd.Series):
        types = pd.Series(types, index=columns)
    if set(types.index) != set(columns) or len(types) != len(columns):
        raise ValueError("Smjerovi moraju odgovarati svim nazivima kriterija.")
    types = types.reindex(columns)
    mapping = {'max': 1, '+': 1, 'benefit': 1, '1': 1, 'min': -1, '-': -1, 'cost': -1, '-1': -1}
    try:
        return types.map(lambda x: mapping[str(x).strip().lower()]).astype(int)
    except KeyError as exc:
        raise ValueError("Smjer kriterija mora biti max/min, +/-, benefit/cost.") from exc

def decision(matrix, types):
    if not isinstance(matrix, pd.DataFrame) or matrix.empty:
        raise ValueError("Potrebna je neprazna pandas DataFrame matrica odluke.")
    if matrix.index.has_duplicates or matrix.columns.has_duplicates or matrix.index.isna().any() or matrix.columns.isna().any():
        raise ValueError("Nazivi alternativa i kriterija moraju biti jedinstveni i neprazni.")
    try:
        x = matrix.apply(pd.to_numeric, errors='raise').astype(float)
    except (ValueError, TypeError) as exc:
        raise ValueError("Sve vrijednosti matrice odluke moraju biti brojevi.") from exc
    if not np.isfinite(x.to_numpy()).all():
        raise ValueError("Matrica odluke ne smije sadržavati prazne ili beskonačne vrijednosti.")
    return x, directions(types, x.columns)

def positive(matrix):
    if (matrix.to_numpy() <= 0).any():
        raise ValueError("Ova metoda zahtijeva strogo pozitivne vrijednosti matrice.")

def weights_series(weights, columns):
    if weights is None:
        raise ValueError("Nedostaju težine kriterija. Unesite weights ili ih izračunajte metodom za težine.")
    if isinstance(weights, dict):
        weights = pd.Series(weights)
    if not isinstance(weights, pd.Series):
        weights = pd.Series(weights, index=columns)
    if len(weights) != len(columns) or set(weights.index) != set(columns):
        raise ValueError("Nazivi težina moraju tačno odgovarati kriterijima.")
    w = weights.reindex(columns).astype(float)
    if not np.isfinite(w.to_numpy()).all() or (w < 0).any() or not np.isclose(w.sum(), 1, atol=1e-8):
        raise ValueError("Težine moraju biti nenegativne i zbir mora biti 1.")
    return w

def rank(scores, higher=True):
    return scores.rank(ascending=not higher, method='min').astype(int).rename('Rank')

def ranking_result(method, matrix, types, weights, scores, higher=True, **steps):
    scores = pd.Series(scores, index=matrix.index, name='Score')
    return {'method': method, 'task': 'ranking', 'input': matrix, 'types': types,
            'weights': weights, **steps, 'scores': scores, 'ranking': rank(scores, higher)}

def unit_interval(x, types):
    """Rastuća korisnost [0,1], za konstantan kriterij vrijednost 1."""
    lo, hi = x.min(), x.max()
    span = hi - lo
    y = x.copy()
    for c in x:
        y[c] = 1.0 if span[c] == 0 else ((x[c]-lo[c])/span[c] if types[c] == 1 else (hi[c]-x[c])/span[c])
    return y

def require_nonconstant(x, label='kriterij'):
    if (x.max() == x.min()).any():
        raise ValueError(f"Konstantan {label} onemogućava ovu formulu.")
