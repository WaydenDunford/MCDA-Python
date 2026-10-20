"""Omjer prema najboljoj vrijednosti: x/max(x) za max, min(x)/x za min; x>0."""
from common import decision, positive

def normalize(matrix, types):
    x, t = decision(matrix, types); positive(x)
    return x.apply(lambda c: c/c.max() if t[c.name] == 1 else c.min()/c)
