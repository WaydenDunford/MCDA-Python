"""MOORA ratio system: vektorski normalizirani benefit minus cost ponderisani zbirovi."""
import numpy as np
from common import ranking_result

def calculate(matrix,types,weights,**kwargs):
    den=np.sqrt((matrix**2).sum())
    if (den==0).any(): raise ValueError('MOORA zahtijeva nenultu vektorsku normu svakog kriterija.')
    n=matrix.div(den,axis=1); v=n.mul(weights,axis=1)
    contribution=v.mul(types,axis=1)
    return ranking_result('moora',matrix,types,weights,contribution.sum(axis=1),
                          normalized=n,weighted=v,signed_contribution=contribution,
                          benefit_sum=v.loc[:,types==1].sum(axis=1),cost_sum=v.loc[:,types==-1].sum(axis=1))
