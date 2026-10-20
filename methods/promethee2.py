"""PROMETHEE II: ponderisani parni preference P_j(d), pozitivni/negativni/neto tok."""
import numpy as np
import pandas as pd
from common import ranking_result

def calculate(matrix,types,weights,preference_functions=None,**kwargs):
    preference_functions=preference_functions or {c:{'type':'usual'} for c in matrix}
    if set(preference_functions)!=set(matrix.columns):
        raise ValueError('preference_functions mora definisati svaki kriterij.')
    pairwise={}; aggregate=np.zeros((len(matrix),len(matrix)))
    for c in matrix:
        spec=preference_functions[c]; kind=spec.get('type','usual')
        d=types[c]*(matrix[c].to_numpy()[:,None]-matrix[c].to_numpy()[None,:])
        if kind=='usual': p=(d>0).astype(float)
        elif kind=='u_shape': p=(d>spec['q']).astype(float)
        elif kind=='v_shape':
            scale=spec['p'];
            if scale<=0: raise ValueError('PROMETHEE p mora biti >0.')
            p=np.clip(d/scale,0,1)
        elif kind=='level':
            q,p0=spec['q'],spec['p']
            if not 0<=q<p0: raise ValueError('PROMETHEE zahtijeva 0<=q<p.')
            p=np.where(d<=q,0,np.where(d<=p0,0.5,1.0))
        elif kind=='linear':
            q,p0=spec['q'],spec['p']
            if not 0<=q<p0: raise ValueError('PROMETHEE zahtijeva 0<=q<p.')
            p=np.clip((d-q)/(p0-q),0,1)
        elif kind=='gaussian':
            s=spec['s']
            if s<=0: raise ValueError('PROMETHEE s mora biti >0.')
            p=np.where(d>0,1-np.exp(-d*d/(2*s*s)),0)
        else: raise ValueError(f'Nepoznata funkcija preferencije: {kind}')
        np.fill_diagonal(p,0)
        pairwise[c]=pd.DataFrame(p,index=matrix.index,columns=matrix.index)
        aggregate+=weights[c]*p
    agg=pd.DataFrame(aggregate,index=matrix.index,columns=matrix.index)
    den=max(len(matrix)-1,1); plus=agg.sum(axis=1)/den; minus=agg.sum(axis=0)/den
    net=plus-minus
    return ranking_result('promethee2',matrix,types,weights,net,
                          preference_functions=preference_functions,criterion_preferences=pairwise,
                          aggregated_preference=agg,positive_flow=plus,negative_flow=minus,net_flow=net)
