"""Shannonova entropija: odabrana transformacija, P=z/Σz, e=-Σp ln p/ln m."""
import numpy as np
from common import unit_interval
from normalizations import normalize

def calculate(matrix,types,normalization=None,**kwargs):
    if len(matrix)<2: raise ValueError('Entropija zahtijeva barem dvije alternative.')
    name=normalization or 'minmax'
    z=unit_interval(matrix,types) if name=='minmax' else normalize(name,matrix,types)
    if (z.sum()==0).any(): raise ValueError('Entropija: kriterij ima nulti zbir.')
    p=z.div(z.sum(axis=0),axis=1)
    term=p.where(p>0,1)
    entropy=-(p*np.log(term)).sum(axis=0)/np.log(len(matrix))
    diversity=1-entropy
    if diversity.sum()<=0: raise ValueError('Entropija: nema informacijske raznolikosti.')
    return {'method':'entropy','task':'weights','input':matrix,'types':types,
            'normalization':name,
            'transformed':z,'proportions':p,'entropy':entropy,
            'diversification':diversity,'weights':diversity/diversity.sum()}
