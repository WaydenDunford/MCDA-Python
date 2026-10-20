"""Pandas/konzolni prikaz bez promjene računske preciznosti."""
import pandas as pd

DECIMALS=6

def show_results(result,show_steps=True,decimals=DECIMALS):
    """Prikaži sve korake ili samo glavne pokazatelje."""
    keys=result.keys() if show_steps else [k for k in ('weights','scores','ranking','prominence','relation','group') if k in result]
    try:
        from IPython import get_ipython
        from IPython.display import display
        notebook=get_ipython() is not None and 'IPKernelApp' in get_ipython().config
    except ImportError: notebook=False
    with pd.option_context('display.precision',decimals):
        for key in keys:
            if key in ('method','task'): continue
            value=result[key]
            if notebook:
                print(f'\n{key}')
                display(value)
            else: print(f'\n{key}\n{value}')
