"""VIKOR (Opricovic): L1 S, L∞ R i kompromis Q; manji je bolji."""
import numpy as np
from common import ranking_result

def calculate(matrix,types,weights,v=0.5,**kwargs):
    if not 0<=v<=1: raise ValueError('v mora biti u [0,1].')
    best=matrix.max().where(types==1,matrix.min()); worst=matrix.min().where(types==1,matrix.max())
    span=(best-worst).abs()
    if (span==0).any(): raise ValueError('VIKOR ne prihvata konstantan kriterij.')
    gap=(matrix-best).abs().div(span,axis=1)
    terms=gap.mul(weights,axis=1); s=terms.sum(axis=1); r=terms.max(axis=1)
    def scale(z):
        return (z-z.min())/(z.max()-z.min()) if z.max()>z.min() else z*0
    q=v*scale(s)+(1-v)*scale(r)
    order=q.sort_values(kind='stable').index.tolist(); dq=1/(len(order)-1) if len(order)>1 else 0
    advantage=len(order)<2 or q[order[1]]-q[order[0]]>=dq-1e-12
    stability=order[0] in {s.idxmin(),r.idxmin()}
    compromise=[order[0]] if advantage and stability else [a for a in order if q[a]-q[order[0]]<dq+1e-12]
    return ranking_result('vikor',matrix,types,weights,q,higher=False,
                          best=best,worst=worst,gap=gap,weighted_gap=terms,S=s,R=r,Q=q,
                          v=v,acceptable_advantage=advantage,acceptable_stability=stability,
                          compromise_solution=compromise)
