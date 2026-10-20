"""ARAS: omjer rezultata prema idealnoj alternativi, sum normalizacija proširene matrice."""
import pandas as pd
from common import ranking_result, positive

def calculate(matrix,types,weights,**kwargs):
    positive(matrix)
    ideal=matrix.max().where(types==1,matrix.min())
    extended=pd.concat([pd.DataFrame([ideal],index=['Ideal']),matrix])
    transformed=extended.copy()
    for c in extended:
        if types[c]==-1: transformed[c]=1/extended[c]
    n=transformed.div(transformed.sum(axis=0),axis=1)
    weighted=n.mul(weights,axis=1); sums=weighted.sum(axis=1)
    scores=sums.drop('Ideal')/sums['Ideal']
    return ranking_result('aras',matrix,types,weights,scores,ideal=ideal,
                          extended=extended,transformed=transformed,normalized=n,
                          weighted=weighted,optimality=sums)
