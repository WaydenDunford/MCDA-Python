"""MARCOS: ideal/anti-ideal, omjerna normalizacija i izvorna kompromisna funkcija."""
import numpy as np
import pandas as pd
from common import ranking_result,positive

def calculate(matrix,types,weights,**kwargs):
    positive(matrix)
    ideal=matrix.max().where(types==1,matrix.min())
    anti=matrix.min().where(types==1,matrix.max())
    ext=pd.concat([pd.DataFrame([anti],index=['AntiIdeal']),matrix,pd.DataFrame([ideal],index=['Ideal'])])
    n=ext.copy()
    for c in ext:
        n[c]=ext[c]/ideal[c] if types[c]==1 else ideal[c]/ext[c]
    weighted=n.mul(weights,axis=1); s=weighted.sum(axis=1)
    km=s.loc[matrix.index]/s['AntiIdeal']; kp=s.loc[matrix.index]/s['Ideal']
    fm=kp/(km+kp); fp=km/(km+kp)
    utility=(km+kp)/(1+(1-fp)/fp+(1-fm)/fm)
    return ranking_result('marcos',matrix,types,weights,utility,
                          ideal=ideal,anti_ideal=anti,extended=ext,normalized=n,weighted=weighted,
                          S=s,K_minus=km,K_plus=kp,f_minus=fm,f_plus=fp)
