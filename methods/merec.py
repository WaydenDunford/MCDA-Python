"""MEREC (Keshavarz-Ghorabaee 2021): min/x za benefit, x/max za cost, log uklanjanje kriterija."""
import numpy as np
from common import positive

def calculate(matrix,types,**kwargs):
    positive(matrix)
    n=matrix.copy()
    for c in matrix:
        n[c]=matrix[c].min()/matrix[c] if types[c]==1 else matrix[c]/matrix[c].max()
    logs=np.abs(np.log(n)); k=len(matrix.columns)
    s=np.log1p(logs.sum(axis=1)/k)
    removed=matrix.copy()
    for c in matrix: removed[c]=np.log1p((logs.sum(axis=1)-logs[c])/k)
    effects=removed.sub(s,axis=0).abs().sum(axis=0)
    if effects.sum()<=0: raise ValueError('MEREC: efekti uklanjanja su nula.')
    return {'method':'merec','task':'weights','input':matrix,'types':types,
            'normalized':n,'absolute_log':logs,'performance':s,
            'removed_performance':removed,'removal_effect':effects,'weights':effects/effects.sum()}
