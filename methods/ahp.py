"""Saaty AHP: Perronov svojstveni vektor pozitivne recipročne matrice."""
import numpy as np
import pandas as pd
from common import rank

RI={1:0,2:0,3:.58,4:.90,5:1.12,6:1.24,7:1.32,8:1.41,9:1.45,10:1.49,
    11:1.51,12:1.48,13:1.56,14:1.57,15:1.59}

def priority(matrix):
    if not isinstance(matrix,pd.DataFrame) or matrix.shape[0]!=matrix.shape[1] or list(matrix.index)!=list(matrix.columns):
        raise ValueError('AHP zahtijeva kvadratnu matricu s jednakim redoslijedom naziva redova i kolona.')
    a=matrix.astype(float).to_numpy(); size=len(a)
    if not np.isfinite(a).all() or (a<=0).any() or not np.allclose(np.diag(a),1,atol=1e-7) or not np.allclose(a*a.T,1,atol=1e-6):
        raise ValueError('AHP matrica mora biti pozitivna, recipročna i imati dijagonalu 1.')
    vals,vecs=np.linalg.eig(a)
    pos=np.argmax(vals.real); lam=vals[pos]
    if abs(lam.imag)>1e-8: raise ValueError('AHP: glavna svojstvena vrijednost nije realna.')
    vector=vecs[:,pos].real
    if vector.sum()<0: vector=-vector
    if (vector<=0).any(): raise ValueError('AHP: glavni svojstveni vektor nije pozitivan.')
    p=pd.Series(vector/vector.sum(),index=matrix.index,name='Priority')
    ci=(lam.real-size)/(size-1) if size>1 else 0
    ri=RI.get(size)
    cr=ci/ri if ri else (0 if size<=2 else None)
    return {'pairwise':matrix,'normalized':matrix.div(matrix.sum(axis=0),axis=1),
            'principal_eigenvalue':float(lam.real),'principal_eigenvector':pd.Series(vector,index=matrix.index),
            'priorities':p,'lambda_max':float(lam.real),'CI':float(ci),'RI':ri,'CR':cr,
            'consistent':None if cr is None else bool(cr<0.1)}

def calculate(matrix,task='weights',alternatives=None,**kwargs):
    criteria=priority(matrix)
    result={'method':'ahp','task':task,'input':matrix,**criteria,'weights':criteria['priorities']}
    if task=='ranking':
        if not isinstance(alternatives,dict) or set(alternatives)!=set(matrix.index):
            raise ValueError('AHP ranking zahtijeva alternatives={kriterij: recipročna matrica alternativa}.')
        local={c:priority(alternatives[c]) for c in matrix.index}
        names=next(iter(local.values()))['priorities'].index
        if any(list(x['priorities'].index)!=list(names) for x in local.values()):
            raise ValueError('Matrice alternativa moraju imati iste alternative istim redoslijedom.')
        local_matrix=pd.DataFrame({c:local[c]['priorities'] for c in matrix.index})
        scores=local_matrix.dot(criteria['priorities']).rename('Score')
        result.update(alternative_comparisons=local,local_priorities=local_matrix,
                      scores=scores,ranking=rank(scores))
    return result
