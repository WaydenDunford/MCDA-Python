"""Jedino mjesto za pravila kompatibilnosti i pregled dostupnih metoda."""
from copy import deepcopy

_RANK = 'aras codas copras edas mabac mairca marcos moora promethee2 saw todim topsis vikor waspas'.split()
_WEIGHT = 'critic entropy merec'.split()
RULES = {m: dict(tasks=['ranking'], input_type='decision', requires_weights=True,
                 computes_weights=False, normalizations=[], native_normalization=True,
                 required_parameters=[], output='ranking') for m in _RANK}
RULES.update({m: dict(tasks=['weights'], input_type='decision', requires_weights=False,
                      computes_weights=True, normalizations=[], native_normalization=True,
                      required_parameters=[], output='weights') for m in _WEIGHT})
RULES['saw'].update(normalizations=['max','minmax','sum','vector','nonlinear'], native_normalization=False)
RULES['entropy'].update(normalizations=['sum','minmax'])
RULES['topsis'].update(normalizations=['vector'], native_normalization=False)
RULES['ahp'] = dict(tasks=['weights','ranking'], input_type='pairwise', requires_weights=False,
                    computes_weights=True, normalizations=[], native_normalization=True,
                    required_parameters=[], output='weights/ranking')
RULES['dematel'] = dict(tasks=['relationships'], input_type='influence', requires_weights=False,
                        computes_weights=False, normalizations=[], native_normalization=True,
                        required_parameters=[], output='relationships')
RULES['macbeth'] = dict(tasks=['ranking'], input_type='judgment', requires_weights=False,
                        computes_weights=False, normalizations=[], native_normalization=True,
                        required_parameters=[], output='ranking')
RULES['psi'] = dict(tasks=['weights','ranking'], input_type='decision', requires_weights=False,
                    computes_weights=True, normalizations=[], native_normalization=True,
                    required_parameters=[], output='weights/ranking')
RULES['promethee2']['required_parameters']=['preference_functions']
RULES['todim']['required_parameters']=['theta']
RULES['macbeth']['required_parameters']=['judgments']

def list_methods(task=None):
    """Metode, opciono filtrirane prema zadatku."""
    return sorted(m for m,r in RULES.items() if task is None or task in r['tasks'])

def get_method_info(method):
    if method not in RULES: raise ValueError(f'Nepoznata metoda: {method}')
    return deepcopy(RULES[method])

def list_normalizations(method):
    return get_method_info(method)['normalizations'][:]

def validate_request(method, task=None, normalization=None):
    r=get_method_info(method)
    task=task or ('weights' if method=='ahp' else ('ranking' if 'ranking' in r['tasks'] else r['tasks'][0]))
    if task not in r['tasks']:
        raise ValueError(f"{method.upper()} ne podržava zadatak {task}. Podržani zadaci: {', '.join(r['tasks'])}")
    if normalization is not None and normalization not in r['normalizations']:
        choices=', '.join(r['normalizations']) or 'samo ugrađena normalizacija'
        raise ValueError(f"{method.upper()} ne podržava normalizaciju {normalization}. Dostupno: {choices}")
    return r,task
