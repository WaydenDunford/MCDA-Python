"""EDAS: pozitivna/negativna udaljenost od srednje vrijednosti; aritmetička sredina >0."""
from common import ranking_result,positive

def calculate(matrix,types,weights,**kwargs):
    positive(matrix)
    average=matrix.mean(); pda=matrix.copy(); nda=matrix.copy()
    for c in matrix:
        d=(matrix[c]-average[c])/average[c]*types[c]
        pda[c]=d.clip(lower=0); nda[c]=(-d).clip(lower=0)
    sp=pda.mul(weights,axis=1).sum(axis=1); sn=nda.mul(weights,axis=1).sum(axis=1)
    if sp.max()==0 and sn.max()==0: raise ValueError('EDAS: sve alternative su jednake.')
    nsp=sp/sp.max() if sp.max()>0 else sp*0
    nsn=1-sn/sn.max() if sn.max()>0 else sn*0+1
    return ranking_result('edas',matrix,types,weights,(nsp+nsn)/2,
                          average=average,PDA=pda,NDA=nda,SP=sp,SN=sn,NSP=nsp,NSN=nsn)
