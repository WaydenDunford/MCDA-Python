"""Promjena jedne težine uz proporcionalno skaliranje ostalih."""
import numpy as np
import pandas as pd
from engine import run
from common import weights_series
from rules import get_method_info

def analyze(method,matrix,types,weights,criterion,new_weight,**kwargs):
    """Ostale težine množe se faktorom (1-new)/(1-old)."""
    rule=get_method_info(method)
    if 'ranking' not in rule['tasks'] or not rule['requires_weights']:
        raise ValueError(f'{method} ne podržava vanjske težine za rangiranje.')
    w=weights_series(weights,matrix.columns)
    if criterion not in w: raise ValueError(f'Nepoznat kriterij: {criterion}')
    if not np.isfinite(new_weight) or not 0<=new_weight<=1: raise ValueError('Nova težina mora biti u [0,1].')
    old=w[criterion]; other=1-old
    if other==0 and new_weight<1: raise ValueError('Nije moguće raspodijeliti težinu: sve ostale početne težine su nula.')
    revised=w.copy()
    for c in revised.index:
        if c!=criterion: revised[c]=w[c]*(1-new_weight)/other if other else 0
    revised[criterion]=new_weight
    baseline=run(method,matrix=matrix,types=types,weights=w,**kwargs)
    changed=run(method,matrix=matrix,types=types,weights=revised,**kwargs)
    table=pd.DataFrame({'rank_before':baseline['ranking'],'rank_after':changed['ranking'],
                        'score_before':baseline['scores'],'score_after':changed['scores']})
    return {'method':'sensitivity','task':'sensitivity','criterion':criterion,
            'weights_before':w,'weights_after':revised,'comparison':table,
            'top_before':baseline['ranking'].idxmin(),'top_after':changed['ranking'].idxmin(),
            'top_changed':baseline['ranking'].idxmin()!=changed['ranking'].idxmin(),
            'baseline':baseline,'changed':changed}
