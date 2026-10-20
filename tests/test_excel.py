import pandas as pd
import pytest
from excel import load_data
from engine import run
from pathlib import Path

DATA=Path(__file__).resolve().parents[1]/'data'

def test_examples():
    d=load_data(DATA/'example.xlsx','saw')
    assert list(d['matrix'].index)==['Machine 1','Toyota','Supplier A']
    assert len(d['weights'])==3
    a=load_data(DATA/'ahp_example.xlsx','ahp',task='ranking')
    assert set(a['alternatives'])=={'C1','C2','C3'}
    hierarchy=run('ahp',**a,task='ranking')
    assert list(hierarchy['ranking'])==[1,2,3]
    assert load_data(DATA/'dematel_example.xlsx','dematel')['matrix'].shape==(3,3)
    assert load_data(DATA/'macbeth_example.xlsx','macbeth')['matrix'].shape==(3,3)

def test_missing_weights_and_separator(tmp_path):
    p=tmp_path/'x.xlsx'
    pd.DataFrame([['Alternative','C1','C2'],['A',1,2],[None,None,None],['B',2,3],
                  ['max/min','max','min']]).to_excel(p,index=False,header=False)
    d=load_data(p,'saw')
    assert 'weights' not in d and d['matrix'].shape==(2,2)

def test_duplicate_alternative(tmp_path):
    p=tmp_path/'x.xlsx'
    pd.DataFrame([['Alternative','C1'],['A',1],['A',2],['max/min','max']]).to_excel(p,index=False,header=False)
    with pytest.raises(ValueError,match='ponovljeni'): load_data(p,'saw')

def test_invalid_value_and_duplicate_criterion(tmp_path):
    p=tmp_path/'bad.xlsx'
    pd.DataFrame([['Alternative','C1','C2'],['A','text',2],['max/min','max','min']]).to_excel(p,index=False,header=False)
    with pytest.raises(ValueError,match='brojčana'): load_data(p,'saw')
    pd.DataFrame([['Alternative','C1','C1'],['A',1,2],['max/min','max','min']]).to_excel(p,index=False,header=False)
    with pytest.raises(ValueError,match='ponovljeni'): load_data(p,'saw')

def test_pairwise_fraction_and_orientation(tmp_path):
    p=tmp_path/'pair.xlsx'
    pd.DataFrame([[None,'C1','C2'],['C1',1,3],['C2','1/3',1]]).to_excel(p,index=False,header=False)
    x=load_data(p,'ahp')['matrix']
    assert x.loc['C2','C1']==pytest.approx(1/3)
    pd.DataFrame([[None,'C1','C2'],['C2',1,3],['C1','1/3',1]]).to_excel(p,index=False,header=False)
    with pytest.raises(ValueError,match='kvadratna'): load_data(p,'ahp')

def test_cilj_tezina_and_trailing_zero_templates(tmp_path):
    p=tmp_path/'podaci.xlsx'
    pd.DataFrame([
        [None,'Kriterij',None],
        ['Rd.broj','C1','C2'],
        [1,4,60],
        [2,2,190],
        [3,0,0],
        ['Cilj','+','-'],
        ['Težina (w)',.6,.4],
    ]).to_excel(p,index=False,header=False)
    with pytest.warns(UserWarning,match='samim nulama'):
        data=load_data(p,'saw')
    assert data['matrix'].shape==(2,2)
    assert list(data['matrix'].index)==['1','2']
    assert data['types'].to_dict()=={'C1':'max','C2':'min'}
    assert data['weights'].to_dict()=={'C1':.6,'C2':.4}
    assert load_data(p,'saw',skip_trailing_zero_rows=False)['matrix'].shape==(3,2)

def test_all_zero_row_and_column_anywhere_with_partial_zeros(tmp_path):
    p=tmp_path/'zeros.xlsx'
    pd.DataFrame([
        ['Alternative','C1','C2','C3'],
        ['A',0,0,5],
        ['Empty',0,0,0],
        ['B',4,0,0],
        ['Cilj','+','-', '+'],
        ['Težina (w)',.4,.2,.4],
    ]).to_excel(p,index=False,header=False)
    with pytest.warns(UserWarning) as captured:
        data=load_data(p,'saw')
    assert len(captured)==3  # red, kolona i ponovna normalizacija težina
    assert list(data['matrix'].index)==['A','B']
    assert list(data['matrix'].columns)==['C1','C3']
    assert data['matrix'].loc['A','C1']==0  # djelimične nule ostaju
    assert data['matrix'].loc['B','C3']==0
    assert data['types'].to_dict()=={'C1':'max','C3':'max'}
    assert data['weights'].to_dict()==pytest.approx({'C1':.5,'C3':.5})
    assert load_data(p,'saw',skip_all_zero=False)['matrix'].shape==(3,3)
