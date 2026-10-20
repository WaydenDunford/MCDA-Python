"""Čitanje odluka, recipročnih parova, uticaja i kvalitativnih sudova iz Excela."""
from fractions import Fraction
import re
import unicodedata
import warnings
import numpy as np
import pandas as pd
from rules import validate_request
from common import directions

def _numeric(v, fraction=False):
    if fraction and isinstance(v,str) and '/' in v:
        try: return float(Fraction(v.strip()))
        except (ValueError,ZeroDivisionError) as exc: raise ValueError(f'Neispravan razlomak: {v}') from exc
    try: return float(v)
    except (TypeError,ValueError) as exc: raise ValueError(f'Neispravna brojčana vrijednost: {v}') from exc

def _rows(path,sheet=0):
    raw=pd.read_excel(path,sheet_name=sheet,header=None,dtype=object,engine='openpyxl')
    return raw.dropna(how='all').dropna(axis=1,how='all').reset_index(drop=True)

def _label(v):
    return '' if pd.isna(v) else str(v).strip()

def _metadata_key(label):
    """Ujednači nazive metapodataka, uključujući č/ć/ž i oznaku (w)."""
    ascii_label=''.join(c for c in unicodedata.normalize('NFKD',label.lower())
                        if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]','',ascii_label)

def _unique(names,what):
    if not all(names) or len(set(names))!=len(names):
        raise ValueError(f'{what}: prazni ili ponovljeni nazivi.')

def load_decision_matrix(path,sheet=0,skip_trailing_zero_rows=True):
    raw=_rows(path,sheet)
    header=None
    for i,row in raw.iterrows():
        labels=[_label(v) for v in row.iloc[1:]]
        if len(labels)>0 and all(re.fullmatch(r'C\d+',x,re.I) for x in labels):
            header=i; break
    if header is None: raise ValueError('Nije pronađen red zaglavlja s kriterijima C1, C2, ...')
    cols=[_label(v) for v in raw.iloc[header,1:]]; _unique(cols,'Kriteriji')
    records=[]; names=[]; t=None; w=None
    for i in range(header+1,len(raw)):
        row=raw.iloc[i]; label=_label(row.iloc[0]); values=row.iloc[1:].tolist()
        if not label and all(pd.isna(v) for v in values): continue
        key=_metadata_key(label)
        if key in {'maxmin','types','directions','cilj','goal','objective'}:
            if t is not None: raise ValueError('Više redova max/min.')
            t=pd.Series(values,index=cols); continue
        if key in {'weights','weight','tezine','tezina','tezinaw'}:
            if w is not None: raise ValueError('Više redova weights.')
            w=pd.Series([_numeric(v) for v in values],index=cols); continue
        if t is not None or w is not None:
            raise ValueError(f'Red {label} iza metapodataka nije dozvoljen.')
        if not label: raise ValueError('Alternativa ima prazan naziv.')
        names.append(label); records.append([_numeric(v) for v in values])
    if skip_trailing_zero_rows:
        skipped=[]
        while len(records)>1 and all(value==0 for value in records[-1]):
            records.pop(); skipped.append(names.pop())
        if skipped:
            warnings.warn('Preskočeni završni redovi sa samim nulama (prazni predlošci): '
                          + ', '.join(reversed(skipped)) + '. Za zadržavanje koristite '
                          'skip_trailing_zero_rows=False.',UserWarning,stacklevel=2)
    _unique(names,'Alternative')
    if t is None: raise ValueError('Nedostaje red smjera kriterija (max/min ili Cilj).')
    if not records: raise ValueError('Nema alternativa u matrici.')
    d=directions(t,cols)
    x=pd.DataFrame(records,index=names,columns=cols)
    if not np.isfinite(x.to_numpy()).all(): raise ValueError('Matrica sadrži NaN/inf.')
    result={'matrix':x,'types':d.map({1:'max',-1:'min'})}
    if w is not None: result['weights']=w
    return result

def _square(path,sheet=0,fraction=False):
    raw=_rows(path,sheet)
    # Traži zaglavlje čiji su nazivi identični nazivima redova.
    for start in range(len(raw)):
        names=[_label(v) for v in raw.iloc[start,1:]]
        if not names or not all(names) or len(set(names))!=len(names): continue
        if len(raw)<start+1+len(names): continue
        rows=[_label(v) for v in raw.iloc[start+1:start+1+len(names),0]]
        if rows==names:
            vals=raw.iloc[start+1:start+1+len(names),1:].copy()
            vals.index=names; vals.columns=names
            if fraction:
                vals=vals.map(lambda v:_numeric(v,True))
            return vals
    raise ValueError('Potrebna je kvadratna matrica: nazivi redova i kolona moraju biti jednaki i u istom redoslijedu.')

def load_pairwise_matrix(path,sheet=0):
    from methods.ahp import priority
    x=_square(path,sheet,True); priority(x)
    return {'matrix':x}

def load_influence_matrix(path,sheet=0):
    from methods.dematel import calculate
    x=_square(path,sheet,True); calculate(x)
    return {'matrix':x}

def load_judgment_matrix(path,sheet=0):
    x=_square(path,sheet,False)
    return {'matrix':x}

def load_data(path,method,task=None,sheet=None,skip_trailing_zero_rows=True):
    """Izaberi Excel strukturu na osnovu metode, nikada prema nazivu alternativa."""
    rule,_=validate_request(method,task)
    kind=rule['input_type']; sheet=0 if sheet is None else sheet
    if kind=='decision': result=load_decision_matrix(path,sheet,skip_trailing_zero_rows)
    elif kind=='pairwise':
        result=load_pairwise_matrix(path,sheet)
        if task=='ranking':
            book=pd.ExcelFile(path,engine='openpyxl')
            names=result['matrix'].index
            missing=[c for c in names if c not in book.sheet_names]
            if missing: raise ValueError(f'Nedostaju AHP listovi alternativa: {missing}')
            result['alternatives']={c:load_pairwise_matrix(path,c)['matrix'] for c in names}
    elif kind=='influence': result=load_influence_matrix(path,sheet)
    else: result=load_judgment_matrix(path,sheet)
    result['source_path']=str(path)
    return result
