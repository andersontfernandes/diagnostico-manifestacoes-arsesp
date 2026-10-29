"""Perfil rápido dos CSV: colunas, vazios, categorias e somas.

Uso: python scripts/perfil.py dados/brutos/REG_SAN_SGFCI-RECLAMACOES.csv dados/brutos/REG_SAN_SGFCI-SOLICITACOES.csv
"""
import csv, sys
from collections import Counter
for f in sys.argv[1:]:
    rows=list(csv.DictReader(open(f,encoding='latin1',newline=''),delimiter=';'))
    cols=rows[0].keys()
    print('=====',f.split('/')[-1],len(rows))
    for c in cols:
        v=[r[c] for r in rows]; empty=sum(1 for x in v if x in ('',None))
        print(f'{c:22} empty={empty:6} uniq={len(set(v)):6} ex={list(dict.fromkeys(v))[:3]}')
    for c in ['ANO_RELATORIO','CONCESSIONARIA','UN']:
        print(c, dict(sorted(Counter(r[c] for r in rows).items())))
    k=Counter((r['COD_IBGE'],r['DATA'],r['CONCESSIONARIA']) for r in rows)
    print('dup keys', sum(n-1 for n in k.values() if n>1))
    for c in cols:
        if c.startswith(('Recl','Solic','Num','OUTROS')):
            tot=0;bad=Counter();neg=0;mx=0
            for r in rows:
                x=r[c].strip()
                if not x: continue
                try: n=float(x.replace(',','.'))
                except: bad[x]+=1; continue
                tot+=n; neg+=n<0; mx=max(mx,n)
            print(f'  {c:22} sum={tot:10.0f} max={mx} neg={neg} nonnum={dict(bad.most_common(4))}')
    print('DATA samples', Counter(r['DATA'].split(', ')[-1].split(' de ')[-1] for r in rows))
