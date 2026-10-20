import numpy as np
import pandas as pd
import pytest
from engine import run
from rules import RULES

X=pd.DataFrame({'C1':[2.,4.,3.],'C2':[4.,2.,3.]},index=['A','B','C'])
T={'C1':'max','C2':'min'}
W={'C1':.5,'C2':.5}

def test_saw_reference():
    r=run('saw',X,T,W,normalization='max')
    assert np.allclose(r['scores'],[.5,1,17/24])
    assert list(r['ranking'])==[3,1,2]
    assert np.allclose(r['weighted'].loc['A'],[.25,.25])

def test_entropy_sum_matches_excel_reference():
    x=pd.DataFrame({'C1':[30,100,50,300], 'C2':[.1,.7,1,2],
                    'C3':[1,1,2,3], 'C4':[20,40,10,35]},
                   index=['1','2','3','4'])
    types={'C1':'min','C2':'min','C3':'max','C4':'min'}
    result=run('entropy',x,types,normalization='sum')
    assert result['normalization']=='sum'
    assert np.allclose(result['proportions'].loc['1'],
                       [.5,.7734806629834254,1/7, .2456140350877192])
    assert np.allclose(result['weights'],
                       [.2155062172636474,.5476167967109513,
                        .09643205471164833,.14044493131375285])
    assert not np.allclose(result['weights'],run('entropy',x,types)['weights'])
    assert np.allclose(run('entropy',x,types,normalization='minmax')['weights'],
                       run('entropy',x,types)['weights'])

def test_topsis_reference():
    r=run('topsis',X.iloc[:2],T,W,normalization='vector')
    assert np.allclose(r['scores'],[0,1])
    assert np.allclose(r['positive_ideal'],[.5*4/np.sqrt(20),.5*2/np.sqrt(20)])

def test_waspas_endpoints_and_vikor_best():
    a=run('waspas',X,T,W,lambda_=1)
    b=run('waspas',X,T,W,lambda_=0)
    assert np.allclose(a['scores'],a['weighted_sum'])
    assert np.allclose(b['scores'],b['weighted_product'])
    v=run('vikor',X,T,W)
    assert v['S']['B']==pytest.approx(0)
    assert v['R']['B']==pytest.approx(0)
    assert v['Q']['B']==pytest.approx(0)

def test_ahp_consistent():
    x=pd.DataFrame([[1,2,4],[.5,1,2],[.25,.5,1]],index=list('ABC'),columns=list('ABC'))
    r=run('ahp',x,task='weights')
    assert np.allclose(r['weights'],[4/7,2/7,1/7])
    assert r['CR']==pytest.approx(0,abs=1e-12)
    assert r['lambda_max']==pytest.approx(3)

def test_dematel_analytic():
    x=pd.DataFrame([[0,1],[0,0]],index=['A','B'],columns=['A','B'])
    r=run('dematel',x)
    assert np.allclose(r['total_relation'],x)
    assert list(r['group'])==['cause','effect']

def test_macbeth_order():
    x=pd.DataFrame([[None,'moderate','strong'],[None,None,'weak'],[None,None,None]],
                   index=list('ABC'),columns=list('ABC'))
    r=run('macbeth',x)
    assert list(r['ranking'])==[1,2,3]
    assert r['scores']['A']==pytest.approx(100)
    assert r['scores']['C']==pytest.approx(0)
    swapped=x.loc[['C','A','B'],['C','A','B']]
    # Sudovi se po permutaciji mogu naći i ispod dijagonale.
    reordered=run('macbeth',swapped)
    assert reordered['scores']['A']==pytest.approx(100)
    assert reordered['scores']['C']==pytest.approx(0)

@pytest.mark.parametrize('method',[m for m,r in RULES.items() if r['input_type']=='decision'])
def test_all_decision_methods_invariants(method):
    rule=RULES[method]
    example=X.copy()
    if method=='critic': example.loc['C','C2']=4
    args={'matrix':example,'types':T}
    if rule['requires_weights']: args['weights']=W
    r=run(method,**args)
    assert r['method']==method
    if 'weights' in r: assert r['weights'].sum()==pytest.approx(1)
    if 'ranking' in r:
        assert set(r['ranking'])=={1,2,3}
        assert np.isfinite(r['scores']).all()
        assert r['ranking']['B']==1  # B Pareto dominira A i C u testnoj matrici.
