"""Klasični TOPSIS: vektorska normalizacija sirovih x, pa benefit/cost ideali."""
import numpy as np
from common import ranking_result

def calculate(matrix,types,weights,normalization=None,**kwargs):
    norm=np.sqrt((matrix**2).sum(axis=0))
    if (norm==0).any(): raise ValueError('TOPSIS ne prihvata kriterij s nultom vektorskom normom.')
    n=matrix.div(norm,axis=1); v=n.mul(weights,axis=1)
    ideal_plus=v.max().where(types==1,v.min()); ideal_minus=v.min().where(types==1,v.max())
    dp=np.sqrt(((v-ideal_plus)**2).sum(axis=1)); dm=np.sqrt(((v-ideal_minus)**2).sum(axis=1))
    den=dp+dm
    if (den==0).any(): raise ValueError('TOPSIS: pozitivni i negativni ideal su identični.')
    return ranking_result('topsis',matrix,types,weights,dm/den,normalization='vector',
                          normalized=n,weighted=v,positive_ideal=ideal_plus,negative_ideal=ideal_minus,
                          distance_positive=dp,distance_negative=dm)
