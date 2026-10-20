"""Centralni dispečer; formule su isključivo u modulima metoda."""
from importlib import import_module
from rules import validate_request
from common import decision, weights_series

def run(method, matrix=None, types=None, weights=None, normalization=None, task=None, source_path=None, **kwargs):
    """Pokreni metodu uz validaciju strukture, smjerova i težina."""
    method=method.lower().replace(' ', '')
    rule,task=validate_request(method, task, normalization)
    if rule['input_type']=='decision':
        matrix,types=decision(matrix,types)
        if rule['requires_weights']:
            weights=weights_series(weights,matrix.columns)
    else:
        if types is not None or weights is not None:
            raise ValueError(f'{method.upper()} koristi {rule["input_type"]} ulaz; types/weights nisu primjenjivi.')
        if matrix is None: raise ValueError(f'Nedostaje {rule["input_type"]} matrica.')
    module=import_module(f'methods.{method}')
    result=module.calculate(matrix=matrix,types=types,weights=weights,
                            normalization=normalization,task=task,**kwargs)
    if source_path is not None: result['source_path']=source_path
    return result
