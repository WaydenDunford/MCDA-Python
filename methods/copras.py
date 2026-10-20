"""COPRAS: sum normalizacija i relativna značajnost Q_i=S+_i+(ΣS-_i)/(S-_i Σ1/S-_i)."""
import numpy as np
from common import ranking_result,positive

def calculate(matrix,types,weights,**kwargs):
    positive(matrix)
    n=matrix.div(matrix.sum(axis=0),axis=1); weighted=n.mul(weights,axis=1)
    benefit=weighted.loc[:,types==1].sum(axis=1); cost=weighted.loc[:,types==-1].sum(axis=1)
    if (types==-1).any():
        if (cost<=0).any(): raise ValueError('COPRAS zahtijeva pozitivne troškovne zbirove.')
        q=benefit+cost.sum()/(cost*(1/cost).sum())
    else: q=benefit
    return ranking_result('copras',matrix,types,weights,q,
                          normalized=n,weighted=weighted,benefit_sum=benefit,cost_sum=cost,
                          relative_significance=q,utility_percent=100*q/q.max())
