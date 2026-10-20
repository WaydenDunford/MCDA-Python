"""MABAC: pomaknuta min-max korisnost, geometrijska granična aproksimacija."""
import numpy as np
from common import ranking_result,unit_interval

def calculate(matrix,types,weights,**kwargs):
    n=unit_interval(matrix,types); v=(n+1).mul(weights,axis=1)
    border=np.exp(np.log(v.replace(0,np.nan)).mean(axis=0)).fillna(0)
    distance=v-border
    return ranking_result('mabac',matrix,types,weights,distance.sum(axis=1),
                          normalized=n,weighted_shifted=v,border=border,distance=distance)
