"""CODAS: euklidska i taksist udaljenost od anti-ideala; prag τ."""
import numpy as np
import pandas as pd
from common import ranking_result
from normalizations import normalize

def calculate(matrix,types,weights,tau=0.02,**kwargs):
    if tau<0: raise ValueError('tau mora biti nenegativan.')
    n=normalize('max',matrix,types); weighted=n.mul(weights,axis=1)
    anti=weighted.min(); diff=weighted-anti
    e=np.sqrt((diff**2).sum(axis=1)); t=diff.abs().sum(axis=1)
    ed=e.to_numpy()[:,None]-e.to_numpy()[None,:]
    td=t.to_numpy()[:,None]-t.to_numpy()[None,:]
    h=ed+(np.abs(ed)>=tau)*td
    preference=pd.DataFrame(h,index=matrix.index,columns=matrix.index)
    return ranking_result('codas',matrix,types,weights,preference.sum(axis=1),
                          normalized=n,weighted=weighted,anti_ideal=anti,
                          euclidean=e,taxicab=t,relative_assessment=preference,tau=tau)
