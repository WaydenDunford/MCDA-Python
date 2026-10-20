"""DEMATEL: N=X/s, s=max(max row-sum,max column-sum); T=N(I-N)^-1."""
import numpy as np
import pandas as pd

def calculate(matrix,**kwargs):
    if not isinstance(matrix,pd.DataFrame) or matrix.shape[0]!=matrix.shape[1] or list(matrix.index)!=list(matrix.columns):
        raise ValueError('DEMATEL zahtijeva kvadratnu matricu s istim faktorima u redovima i kolonama.')
    x=matrix.astype(float)
    if not np.isfinite(x.to_numpy()).all() or (x.to_numpy()<0).any() or not np.allclose(np.diag(x),0):
        raise ValueError('DEMATEL matrica mora biti nenegativna s nultom dijagonalom.')
    scale=max(x.sum(axis=0).max(),x.sum(axis=1).max())
    if scale<=0: raise ValueError('DEMATEL zahtijeva barem jedan pozitivan uticaj.')
    n=x/scale
    if max(abs(np.linalg.eigvals(n.to_numpy())))>=1-1e-12:
        raise ValueError('DEMATEL: spektralni radijus normalizirane matrice mora biti <1.')
    t=pd.DataFrame(np.linalg.solve(np.eye(len(n))-n.to_numpy(),n.to_numpy()),index=x.index,columns=x.columns)
    d=t.sum(axis=1); r=t.sum(axis=0)
    r.index=d.index
    return {'method':'dematel','task':'relationships','input':x,'normalized':n,
            'total_relation':t,'D':d,'R':r,'prominence':d+r,'relation':d-r,
            'group':(d-r).map(lambda z:'cause' if z>0 else ('effect' if z<0 else 'neutral')),
            'scale':scale}
