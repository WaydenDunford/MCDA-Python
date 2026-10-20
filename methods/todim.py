"""TODIM: relativne težine prema referentnom kriteriju i teorija perspektive."""
import numpy as np
import pandas as pd
from common import ranking_result,unit_interval

def calculate(matrix,types,weights,theta=1.0,**kwargs):
    if theta<=0: raise ValueError('TODIM theta mora biti >0.')
    n=unit_interval(matrix,types)
    ref=weights.idxmax()
    if weights[ref]==0: raise ValueError('TODIM zahtijeva pozitivnu težinu.')
    relative=weights/weights[ref]; total=relative.sum()
    contributions={}; dominance=np.zeros((len(matrix),len(matrix)))
    for c in matrix:
        d=n[c].to_numpy()[:,None]-n[c].to_numpy()[None,:]
        gain=np.sqrt(np.maximum(d,0)*relative[c]/total)
        loss=-np.sqrt(np.maximum(-d,0)*total/relative[c])/theta if relative[c]>0 else np.zeros_like(d)
        p=np.where(d>=0,gain,loss)
        contributions[c]=pd.DataFrame(p,index=matrix.index,columns=matrix.index)
        dominance+=p
    dom=pd.DataFrame(dominance,index=matrix.index,columns=matrix.index)
    totals=dom.sum(axis=1)
    scores=(totals-totals.min())/(totals.max()-totals.min()) if totals.max()>totals.min() else totals*0
    return ranking_result('todim',matrix,types,weights,scores,normalized=n,reference=ref,
                          relative_weights=relative,criterion_dominance=contributions,
                          dominance=dom,total_dominance=totals,theta=theta)
