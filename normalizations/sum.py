"""Omjerni oblik: x/sum(x) za max, (1/x)/sum(1/x) za min; x>0."""
from common import decision, positive

def normalize(matrix, types):
    x,t = decision(matrix, types); positive(x)
    return x.apply(lambda c: c/c.sum() if t[c.name] == 1 else (1/c)/(1/c).sum())
