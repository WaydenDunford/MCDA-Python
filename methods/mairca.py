"""MAIRCA: jednaka početna preferencija P=1/m, teorijska-realna ocjena i ukupni jaz."""
from common import ranking_result,unit_interval

def calculate(matrix,types,weights,**kwargs):
    n=unit_interval(matrix,types)
    theoretical=n*0+weights/len(matrix)
    real=theoretical*n; gap=theoretical-real
    return ranking_result('mairca',matrix,types,weights,gap.sum(axis=1),higher=False,
                          normalized=n,initial_preference=1/len(matrix),
                          theoretical=theoretical,real=real,gap=gap)
