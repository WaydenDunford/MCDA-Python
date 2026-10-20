"""CRITIC: min-max, populacijska σ, Pearson korelacije, C_j=σ_j Σ(1-r_jk)."""
import numpy as np
from common import unit_interval

def calculate(matrix,types,**kwargs):
    n=unit_interval(matrix,types)
    sd=n.std(ddof=0)
    corr=n.corr().fillna(0)
    for criterion in corr.index:
        corr.loc[criterion,criterion]=1
    conflict=(1-corr).sum(axis=1)
    information=sd*conflict
    if information.sum()<=0: raise ValueError('CRITIC: nema kontrasta; težine nisu određene.')
    return {'method':'critic','task':'weights','input':matrix,'types':types,
            'normalized':n,'standard_deviation':sd,'correlation':corr,
            'conflict':conflict,'information':information,'weights':information/information.sum()}
