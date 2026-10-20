"""PSI: min/max omjer, odstupanja od sredine, Ω=1-Σ(r-r̄)^2, ψ=Ω/ΣΩ."""
from common import positive,ranking_result
from normalizations import normalize

def calculate(matrix,types,task='ranking',**kwargs):
    positive(matrix)
    n=normalize('max',matrix,types)
    mean=n.mean(); variation=((n-mean)**2).sum(axis=0)
    preference=1-variation
    if (preference<0).any() or preference.sum()<=0:
        raise ValueError('PSI: preferencijske vrijednosti nisu nenegativne; varijanta nije primjenjiva.')
    weights=preference/preference.sum()
    steps=dict(normalized=n,mean=mean,variation=variation,preference=preference)
    if task=='weights':
        return {'method':'psi','task':'weights','input':matrix,'types':types,**steps,'weights':weights}
    weighted=n.mul(weights,axis=1)
    return ranking_result('psi',matrix,types,weights,weighted.sum(axis=1),**steps,weighted=weighted)
