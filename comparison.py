"""Upoređivanje rangova bez miješanja različitih skala ocjena."""
import pandas as pd
from engine import run

def compare(methods,matrix,types,weights,parameters=None):
    """parameters={metoda: argumenti}; greške se navode, bez tihih zamjena."""
    parameters=parameters or {}; ranks={}; scores={}; errors={}; results={}
    for method in methods:
        try:
            result=run(method,matrix=matrix,types=types,weights=weights,
                       **parameters.get(method,{}))
            ranks[method]=result['ranking']; scores[method]=result['scores']; results[method]=result
        except (ValueError,TypeError,KeyError) as exc: errors[method]=str(exc)
    rank_table=pd.DataFrame(ranks); score_table=pd.DataFrame(scores)
    return {'method':'comparison','task':'comparison','ranks':rank_table,
            'scores':score_table,'spearman':rank_table.corr(method='spearman'),
            'errors':errors,'results':results}
