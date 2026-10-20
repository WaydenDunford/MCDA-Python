"""Zavadskas–Turskis logaritamska normalizacija.

Dobit: ln(x)/Σln(x). Trošak: [1-ln(x)/Σln(x)]/(m-1).
Ovdje se zahtijeva x>1 i m>1 da obje transformacije budu nenegativne.
"""
import numpy as np
from common import decision

def normalize(matrix, types):
    x,t = decision(matrix, types)
    if len(x)<2 or (x.to_numpy()<=1).any():
        raise ValueError('Logaritamska normalizacija zahtijeva barem dvije alternative i sve x>1.')
    out=x.copy()
    for c in x:
        z=np.log(x[c]); p=z/z.sum()
        out[c]=p if t[c]==1 else (1-p)/(len(x)-1)
    return out
