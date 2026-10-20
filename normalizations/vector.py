"""Vektorska korisnost: x/||x|| za max, (1/x)/||1/x|| za min; x>0."""
import numpy as np
from common import decision, positive

def normalize(matrix, types):
    x,t = decision(matrix, types); positive(x)
    return x.apply(lambda c: (c if t[c.name] == 1 else 1/c)/np.linalg.norm(c if t[c.name] == 1 else 1/c))
