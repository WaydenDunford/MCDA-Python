"""Afina min-max korisnost; konstantan stupac ima korisnost 1 za sve."""
from common import decision, unit_interval

def normalize(matrix, types):
    x,t = decision(matrix, types)
    return unit_interval(x,t)
