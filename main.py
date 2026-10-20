"""Primjer lokalnog pokretanja: python main.py --method saw --file data/example.xlsx."""
import argparse
from excel import load_data
from engine import run
from display import show_results
from export import export_excel

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--method',default='saw')
    parser.add_argument('--task')
    parser.add_argument('--file',default='data/example.xlsx')
    parser.add_argument('--sheet')
    parser.add_argument('--normalization')
    parser.add_argument('--output',default='results/output.xlsx')
    parser.add_argument('--brief',action='store_true')
    args=parser.parse_args()
    data=load_data(args.file,args.method,task=args.task,sheet=args.sheet)
    result=run(args.method,task=args.task,normalization=args.normalization,**data)
    show_results(result,show_steps=not args.brief)
    print(f'\nSačuvano: {export_excel(result,args.output)}')

if __name__=='__main__': main()
