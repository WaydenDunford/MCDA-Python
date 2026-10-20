"""MACBETH kompatibilan LP za kvalitativne razlike kategorija 0..6.

Ograničenja: d(a,b)=v(a)-v(b); unutar kategorije razlika ≥1;
viša kategorija je ≥1 iznad svake niže. Sidra: najbolja=100, najgora=0.
Ovo je kanonska moguća skala, ne puni interaktivni M-MACBETH postupak.
"""
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from common import rank

CATEGORIES={'no':0,'none':0,'very weak':1,'weak':2,'moderate':3,'strong':4,'very strong':5,'extreme':6,
            'nikakva':0,'vrlo slaba':1,'slaba':2,'umjerena':3,'jaka':4,'vrlo jaka':5,'ekstremna':6}

def calculate(matrix,**kwargs):
    if not isinstance(matrix,pd.DataFrame) or matrix.shape[0]!=matrix.shape[1] or list(matrix.index)!=list(matrix.columns):
        raise ValueError('MACBETH zahtijeva kvadratnu tablicu kvalitativnih sudova.')
    names=list(matrix.index); n=len(names)
    if n<2: raise ValueError('MACBETH zahtijeva barem dvije opcije.')
    judgments=[]; order=[]
    for i in range(n):
        for j in range(i+1,n):
            a,b=matrix.iat[i,j],matrix.iat[j,i]
            if pd.notna(a) and pd.notna(b): raise ValueError('Unesite sud samo u jedan od dva simetrična polja.')
            if pd.isna(a) and pd.isna(b): raise ValueError('Nedostaje sud za par opcija.')
            raw=a if pd.notna(a) else b
            key=str(raw).strip().lower()
            cat=CATEGORIES.get(key)
            if cat is None:
                try: cat=int(raw)
                except (ValueError,TypeError): raise ValueError(f'Nepoznata MACBETH kategorija: {raw}')
            if cat not in range(7): raise ValueError('MACBETH kategorije su 0..6.')
            better,worse=(i,j) if pd.notna(a) else (j,i)
            judgments.append((better,worse,cat))
            if cat>0: order.append((better,worse))
    # Svaka pozitivna razlika bar 1; nulta razlika daje jednakost.
    ub=[]; bounds=[]
    for a,b,k in judgments:
        row=np.zeros(n); row[a]=-1; row[b]=1
        if k: ub.append(row); bounds.append(-1)
        else:
            ub.extend([row,-row]); bounds.extend([0,0])
    # Kategorije su globalno uređene: svaka viša razlika nadmašuje svaku nižu.
    for a,b,k in judgments:
        for c,d,h in judgments:
            if k>h:
                row=np.zeros(n); row[a]-=1; row[b]+=1; row[c]+=1; row[d]-=1
                ub.append(row); bounds.append(-1)
    # Minimizacija raspona uz proizvoljan redoslijed opcija.
    # Dodatne varijable su gornja (u) i donja (l) granica skale.
    augmented=[np.r_[row,0,0] for row in ub]
    for i in range(n):
        upper=np.zeros(n+2); upper[i]=1; upper[n]=-1
        lower=np.zeros(n+2); lower[i]=-1; lower[n+1]=1
        augmented.extend([upper,lower]); bounds.extend([0,0])
    objective=np.zeros(n+2); objective[n]=1; objective[n+1]=-1
    variable_bounds=[(None,None)]*(n+2); variable_bounds[0]=(0,0)
    lp=linprog(objective,A_ub=augmented,b_ub=bounds,bounds=variable_bounds,method='highs')
    if not lp.success: raise ValueError('MACBETH sudovi nisu konzistentni: LP nema dopušteno rješenje.')
    values=pd.Series(lp.x[:n],index=names)
    span=values.max()-values.min()
    scores=(((values-values.min())/span*100) if span>0 else values*0).rename('Score')
    differences=pd.DataFrame(scores.to_numpy()[:,None]-scores.to_numpy()[None,:],index=names,columns=names)
    return {'method':'macbeth','task':'ranking','input':matrix,'judgments':pd.DataFrame(judgments,columns=['better','worse','category']),
            'raw_scale':values,'difference_matrix':differences,'scores':scores,'ranking':rank(scores),
            'lp_status':lp.message}
