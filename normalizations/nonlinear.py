"""Potencijalna nelinearna normalizacija (Zavadskas/Turskis): (x/max)^p, (min/x)^p; x>0, p>0."""
import numpy as np
from common import decision, positive

def normalize(matrix, types, p=2.0):
    if not np.isfinite(p) or p <= 0: raise ValueError('p mora biti pozitivan konačan broj.')
    x,t = decision(matrix, types); positive(x)
    return x.apply(lambda c: (c/c.max() if t[c.name] == 1 else c.min()/c)**p)
