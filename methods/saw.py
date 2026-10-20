"""SAW: aditivna korisnost Σ w_j r_ij; navedena vanjska normalizacija."""
from common import ranking_result
from normalizations import normalize

def calculate(matrix,types,weights,normalization=None,task=None,**kwargs):
    name=normalization or 'max'
    n=normalize(name,matrix,types,**kwargs)
    v=n.mul(weights,axis=1)
    return ranking_result('saw',matrix,types,weights,v.sum(axis=1),
                          normalization=name,normalized=n,weighted=v)
