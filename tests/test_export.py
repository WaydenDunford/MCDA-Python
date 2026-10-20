from pathlib import Path
import pandas as pd
import nbformat
from engine import run
from excel import load_data
from export import export_excel
from comparison import compare
from sensitivity import analyze
import pytest

ROOT=Path(__file__).resolve().parents[1]

def test_export(tmp_path):
    d=load_data(ROOT/'data/example.xlsx','saw')
    r=run('saw',**d,normalization='minmax')
    p=export_excel(r,tmp_path/'result.xlsx')
    book=pd.ExcelFile(p)
    assert {'input','normalized','weighted','scores','ranking'}<=set(book.sheet_names)
    scores=pd.read_excel(p,sheet_name='scores',index_col=0)
    assert abs(scores.loc['Toyota','Score']-r['scores']['Toyota'])<1e-6
    a=run('ahp',**load_data(ROOT/'data/ahp_example.xlsx','ahp'))
    ahp_book=pd.ExcelFile(export_excel(a,tmp_path/'ahp.xlsx'))
    assert {'pairwise','normalized','principal_eigenvector','priorities','CR'}<=set(ahp_book.sheet_names)

def test_notebook_valid():
    nb=nbformat.read(ROOT/'notebooks/MCDA_Colab.ipynb',as_version=4)
    nbformat.validate(nb)
    for cell in nb.cells:
        if cell.cell_type=='code': compile(cell.source,'notebook','exec')

def test_comparison_sensitivity_and_source_guard(tmp_path):
    d=load_data(ROOT/'data/example.xlsx','saw')
    c=compare(['saw','topsis','vikor','waspas'],d['matrix'],d['types'],d['weights'])
    assert c['ranks'].shape==(3,4)
    assert not c['errors']
    export_excel(c,tmp_path/'comparison.xlsx')
    s=analyze('saw',d['matrix'],d['types'],d['weights'],'C1',.5)
    assert s['weights_after'].sum()==pytest.approx(1)
    export_excel(s,tmp_path/'sensitivity.xlsx')
    with pytest.raises(ValueError,match='prepisati'):
        export_excel(run('saw',**d),ROOT/'data/example.xlsx')
