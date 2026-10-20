import pandas as pd
import pytest
from engine import run
from rules import list_methods,list_normalizations,get_method_info

X=pd.DataFrame({'C1':[1,2],'C2':[2,1]},index=['A','B'])
T={'C1':'max','C2':'min'}

def test_introspection():
    assert len(list_methods())==21
    assert 'ahp' in list_methods('weights')
    assert list_normalizations('topsis')==['vector']
    assert list_normalizations('entropy')==['sum','minmax']
    assert get_method_info('dematel')['input_type']=='influence'

def test_rejection():
    with pytest.raises(ValueError,match='Podržani zadaci'):
        run('saw',X,T,task='weights')
    with pytest.raises(ValueError,match='normalizaciju'):
        run('vikor',X,T,weights=[.5,.5],normalization='minmax')
    with pytest.raises(ValueError,match='Nedostaju težine'):
        run('saw',X,T)
    with pytest.raises(ValueError,match='Nazivi težina'):
        run('saw',X,T,weights={'C1':.5,'wrong':.5})
