"""WASPAS: λ Σ w_j r_ij + (1-λ) Π r_ij^w_j, omjerna max normalizacija."""
import numpy as np
from common import ranking_result
from normalizations import normalize

def calculate(matrix,types,weights,lambda_=0.5,**kwargs):
    if not 0<=lambda_<=1: raise ValueError('lambda_ mora biti u [0,1].')
    n=normalize('max',matrix,types)
    ws=n.mul(weights,axis=1).sum(axis=1)
    wp=np.exp(np.log(n).mul(weights,axis=1).sum(axis=1))
    return ranking_result('waspas',matrix,types,weights,lambda_*ws+(1-lambda_)*wp,
                          normalized=n,weighted_sum=ws,weighted_product=wp,lambda_=lambda_)
