import numpy as np
import pandas as pd
import pytest
from normalizations import normalize

X=pd.DataFrame({'B':[2.,4.],'C':[4.,2.]},index=['A','B'])
T={'B':'max','C':'min'}

@pytest.mark.parametrize('name,expected',[
    ('max',[[.5,.5],[1,1]]),
    ('minmax',[[0,0],[1,1]]),
    ('sum',[[1/3,1/3],[2/3,2/3]]),
    ('vector',[[2/np.sqrt(20),.25/np.sqrt(.25**2+.5**2)],
               [4/np.sqrt(20),.5/np.sqrt(.25**2+.5**2)]]),
    ('nonlinear',[[.25,.25],[1,1]]),
])
def test_manual(name,expected):
    assert np.allclose(normalize(name,X,T),expected)

def test_logarithmic():
    y=normalize('ln',X,T)
    p=np.log(2)/(np.log(2)+np.log(4))
    assert np.allclose(y.iloc[0],[p,1-(1-p)])
    assert np.allclose(y.sum(),1)

def test_invalid():
    with pytest.raises(ValueError): normalize('max',X-2,T)
    with pytest.raises(ValueError): normalize('ln',X/2,T)
