"""Izvoz svakog numeričkog koraka u zaseban Excel list."""
from pathlib import Path
import re
import pandas as pd
from openpyxl.utils import get_column_letter

def _sheet_name(name,used):
    base=re.sub(r'[\\/*?:\[\]]','_',str(name))[:31] or 'Result'
    result=base; i=2
    while result.lower() in used:
        suffix=f'_{i}'; result=base[:31-len(suffix)]+suffix; i+=1
    used.add(result.lower()); return result

def _flatten(prefix,value):
    if isinstance(value,dict):
        for key,item in value.items():
            yield from _flatten(f'{prefix}_{key}' if prefix else str(key),item)
    elif isinstance(value,pd.DataFrame): yield prefix,value
    elif isinstance(value,pd.Series): yield prefix,value.to_frame()
    elif isinstance(value,(list,tuple)):
        yield prefix,pd.DataFrame({'value':list(value)})
    else: yield prefix,pd.DataFrame({'value':[value]})

def export_excel(result,path,decimals=6):
    """Sačuvaj sve relevantne rezultate; postojeći ulazni Excel ne mijenja."""
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    if 'source_path' in result and path.resolve()==Path(result['source_path']).resolve():
        raise ValueError('Izlazni Excel ne smije prepisati izvorni Excel fajl.')
    used=set()
    with pd.ExcelWriter(path,engine='openpyxl') as writer:
        for key,value in result.items():
            if key in {'method','task','source_path'}: continue
            for name,frame in _flatten(key,value):
                sheet=_sheet_name(name,used)
                frame.to_excel(writer,sheet_name=sheet,float_format=f'%.{decimals}f')
                ws=writer.sheets[sheet]; ws.freeze_panes='B2'
                for col in ws.columns:
                    width=min(45,max(12,max(len(str(cell.value or '')) for cell in col)+2))
                    ws.column_dimensions[get_column_letter(col[0].column)].width=width
    return path
