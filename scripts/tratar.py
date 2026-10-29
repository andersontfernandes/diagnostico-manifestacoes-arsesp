"""Limpa, padroniza e agrega os CSV da Arsesp nas bases usadas pelo painel.

Uso: python scripts/tratar.py dados/brutos dados/processados
Gera: mensal.json, anual.json, municipios_2023.json, regional.json, apuracao.json
"""
import csv, json, sys, statistics as st, unicodedata
from collections import Counter, defaultdict
RAW, OUT = sys.argv[1], sys.argv[2]
M={'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}
CAT={'ReclQualAgua':'Qualidade da água','ReclVazAgua':'Vazamento de água','ReclCav':'Cavalete / hidrômetro',
 'ReclFAPP':'Falta de água / pouca pressão','ReclValorConta':'Valor da conta','ReclServEsg':'Serviços de esgoto',
 'ReclRepos':'Reposição de pavimento','SolicVistoria':'Vistoria','SolicCarroTq':'Caminhão-tanque',
 'SolicServLig':'Serviços de ligação','SolicServCom':'Serviços comerciais','SolicServComConAgua':'Serv. comerciais c/ conta de água',
 'NumSolicEstProj':'Estudos de projeto','OUTROS':'Outros'}
REG=[('ALTO PARANAPANEMA','RA'),('B PARANAPANEMA','RB'),('BAIXO PARANAPANEMA','RB'),('B. PARANAP','RB'),('PARDO E GRANDE','RG'),
 ('CAPIVARI','RJ'),('MEDIO TIETE','RM'),('LITORAL NORTE','RN'),('L. NORTE','RN'),('RIBEIRA','RR'),('BAIXADA','RS'),
 ('B TIETE','RT'),('BAIXO TIETE','RT'),('VALE DO PARA','RV'),('V. PARAIBA','RV'),('CENTRO','MC'),('LESTE','ML'),('NORTE','MN'),('OESTE','MO'),('SUL','MS')]
REGNAME={'RA':'Alto Paranapanema','RB':'Baixo Paranapanema','RG':'Pardo e Grande','RJ':'Capivari/Jundiaí','RM':'Médio Tietê',
 'RN':'Litoral Norte','RR':'Vale do Ribeira','RS':'Baixada Santista','RT':'Baixo Tietê e Grande','RV':'Vale do Paraíba',
 'MC':'Metropolitana Centro','ML':'Metropolitana Leste','MN':'Metropolitana Norte','MO':'Metropolitana Oeste','MS':'Metropolitana Sul'}
def strip(s): return ''.join(c for c in unicodedata.normalize('NFD',s.upper()) if unicodedata.category(c)!='Mn')
def un_code(u):
    u=strip(u.strip())
    if len(u)>=2 and u[:2] in REGNAME and (len(u)==2 or u[2]==' '): return u[:2]
    for k,c in REG:
        if k in u: return c
    return None
issues=[]; kpi={}
data={}
for tipo,fn in [('Reclamações','REG_SAN_SGFCI-RECLAMACOES.csv'),('Solicitações','REG_SAN_SGFCI-SOLICITACOES.csv')]:
    rows=list(csv.DictReader(open(f'{RAW}/{fn}',encoding='latin1',newline=''),delimiter=';'))
    n0=len(rows)
    blank=[r for r in rows if not r['COD_IBGE']]; rows=[r for r in rows if r['COD_IBGE']]
    seen=set(); dedup=[]; ndup=0
    for r in rows:
        t=tuple(r.values())
        if t in seen: ndup+=1; continue
        seen.add(t); dedup.append(r)
    rows=dedup
    cats=[c for c in rows[0] if c in CAT]
    for r in rows:
        p=r['DATA'].split(', ')[-1].split(' de '); r['mes']=f"{p[2]}-{M[p[1]]:02d}"
    data[tipo]=(rows,cats)
    kpi[tipo]=dict(brutas=n0,brancas=len(blank),dup=ndup,validas=len(rows))
rows_r,_=data['Reclamações']
# names & modal regional per municipality
names=defaultdict(Counter); munreg=defaultdict(Counter); conc={}
for tipo in data:
    for r in data[tipo][0]:
        names[r['COD_IBGE']][r['MUNICIPIO']]+=1
        c=un_code(r['UN'])
        if c: munreg[r['COD_IBGE']][c]+=1
        conc[r['COD_IBGE']]=r['CONCESSIONARIA']
def nome(c): return max(names[c].items(),key=lambda kv:(kv[0].isupper(),kv[1]))[0].upper()
nvar=sum(1 for c in names if len(names[c])>1)
def regional(r):
    if r['CONCESSIONARIA']!='Sabesp': return 'Outras concessionárias'
    c=un_code(r['UN']) or (munreg[r['COD_IBGE']].most_common(1)[0][0] if munreg[r['COD_IBGE']] else None)
    return f"{c} · {REGNAME[c]}" if c else 'Não identificada'
nunvar=len({r['UN'] for t in data for r in data[t][0]})
# monthly
mensal=[]; anual=[]
for tipo,(rows,cats) in data.items():
    bym=defaultdict(list)
    for r in rows: bym[r['mes']].append(r)
    for c in cats:
        series=[]
        for m in sorted(bym):
            rs=bym[m]; vals=[float(r[c]) for r in rs if r[c].strip()]
            series.append(dict(tipo=tipo,categoria=CAT[c],mes=m,total=round(sum(vals)),informantes=len(vals),linhas=len(rs)))
        med=st.median([s['total'] for s in series if s['informantes']>=0.5*s['linhas']] or [0])
        for s in series:
            if s['informantes']<0.5*s['linhas']: s['situacao']='Lacuna de preenchimento'
            elif med>0 and s['total']>5*med: s['situacao']='Valor atípico'
            elif s['mes']>='2024-01' and tipo=='Reclamações': s['situacao']='Mudança de patamar'
            else: s['situacao']='Regular'
        mensal+=series
mensal_out=[{k:s[k] for k in ('tipo','categoria','mes','total','informantes','situacao')} for s in mensal]
for tipo in data:
    for cat in dict.fromkeys(s['categoria'] for s in mensal if s['tipo']==tipo):
        for y in ['2021','2022','2023','2024']:
            ss=[s for s in mensal if s['tipo']==tipo and s['categoria']==cat and s['mes'].startswith(y)]
            anual.append(dict(tipo=tipo,categoria=cat,ano=int(y),total=sum(s['total'] for s in ss),meses_regulares=sum(s['situacao']=='Regular' for s in ss)))
# municipal 2023 (reclamações)
rcats=data['Reclamações'][1]
mun=defaultdict(lambda: defaultdict(float)); munrg={}
for r in rows_r:
    if not r['mes'].startswith('2023'): continue
    k=r['COD_IBGE']
    for c in rcats: mun[k][c]+=float(r[c] or 0)
    munrg.setdefault(k,regional(r) if r['CONCESSIONARIA']!='Sabesp' or un_code(r['UN']) else None)
municipios=[]
for k,v in mun.items():
    rg=munrg[k]
    if k=='3550308': rg='São Paulo (capital) · várias UNs'
    elif not rg: rg=regional({'CONCESSIONARIA':conc[k],'UN':'','COD_IBGE':k})
    d=dict(cod_ibge=k,municipio=nome(k),regional=rg,concessionaria=conc[k])
    for c in rcats: d[CAT[c]]=round(v[c])
    d['total']=round(sum(v.values())); municipios.append(d)
municipios.sort(key=lambda d:-d['total'])
# regional annual 2021-2023 (reclamações)
reg=defaultdict(float); regm=defaultdict(set)
for r in rows_r:
    y=r['mes'][:4]
    if y=='2024': continue
    g=regional(r); reg[(g,int(y))]+=sum(float(r[c] or 0) for c in rcats); regm[(g,int(y))].add(r['COD_IBGE'])
regional_rows=[dict(regional=g,ano=y,total=round(t),municipios=len(regm[(g,y)])) for (g,y),t in sorted(reg.items())]
# 2024 H2 misalignment test
H1=('01','02','03','04','05','06')
def halves(y):
    a=defaultdict(float);b=defaultdict(float)
    for r in rows_r:
        if r['mes'][:4]!=y: continue
        (a if r['mes'][5:] in H1 else b)[r['COD_IBGE']]+=float(r['ReclVazAgua'] or 0)
    ks=[k for k in a if k in b]; return st.correlation([a[k] for k in ks],[b[k] for k in ks])
c23,c24=halves('2023'),halves('2024')
kr,ks=kpi['Reclamações'],kpi['Solicitações']
apur=[
 dict(id='linhas_brutas',etapa='Ingestão',problema='Linhas lidas (cada arquivo)',afetados=kr['brutas'],tratamento='Arquivos CSV em Latin-1, separador ";".'),
 dict(id='linhas_vazias',etapa='Limpeza',problema='Linhas sem município, data ou valores',afetados=kr['brancas']+ks['brancas'],tratamento='Removidas (soma dos dois arquivos).'),
 dict(id='duplicadas',etapa='Limpeza',problema='Linhas idênticas repetidas',afetados=kr['dup']+ks['dup'],tratamento='Mantida uma cópia.'),
 dict(id='linhas_validas',etapa='Limpeza',problema='Linhas válidas de reclamações',afetados=kr['validas'],tratamento='Base para todas as análises de reclamações.'),
 dict(id='municipios',etapa='Padronização',problema='Municípios distintos (código IBGE)',afetados=len(names),tratamento='Código IBGE usado como chave; nome mais frequente em maiúsculas.'),
 dict(id='nomes_variantes',etapa='Padronização',problema='Municípios com mais de uma grafia',afetados=nvar,tratamento='Ex.: "Aspásia" e "ASPASIA" unificados pelo código IBGE.'),
 dict(id='un_variantes',etapa='Padronização',problema='Grafias distintas da unidade de negócio',afetados=nunvar,tratamento='Reduzidas a 15 unidades regionais da Sabesp + outras concessionárias.'),
 dict(id='data_texto',etapa='Padronização',problema='Meses com data escrita por extenso',afetados=48,tratamento='"sábado, 1 de maio de 2021" convertido para 2021-05.'),
 dict(id='multi_un',etapa='Agregação',problema='Meses em que um município aparece em várias linhas',afetados=sum(1 for v in Counter((r['COD_IBGE'],r['mes']) for r in rows_r).values() if v>1),tratamento='São Paulo e Guarujá vêm divididos por unidade; valores somados por município e mês.'),
 dict(id='lacunas',etapa='Cobertura',problema='Combinações mês × categoria com menos de 50% de preenchimento',afetados=sum(s['situacao']=='Lacuna de preenchimento' for s in mensal),tratamento='Marcadas como lacuna; ex.: reposição de pavimento jul–dez/2022, qualidade da água a partir de jul/2023.'),
 dict(id='atipicos',etapa='Cobertura',problema='Combinações mês × categoria acima de 5× a mediana',afetados=sum(s['situacao']=='Valor atípico' for s in mensal),tratamento='Marcadas como atípicas; concentradas em solicitações de jul–dez/2021.'),
 dict(id='corr_2023',etapa='Consistência',problema='Correlação municipal 1º × 2º semestre de 2023 (×1000)',afetados=round(c23*1000),tratamento='Referência: municípios mantêm o mesmo patamar entre semestres.'),
 dict(id='corr_2024',etapa='Consistência',problema='Correlação municipal 1º × 2º semestre de 2024 (×1000)',afetados=round(c24*1000),tratamento='Valores de jul–dez/2024 não correspondem aos municípios. Usados só no total estadual.'),
]
for name,obj in [('mensal',mensal_out),('anual',anual),('municipios_2023',municipios),('regional',regional_rows),('apuracao',apur)]:
    json.dump(obj,open(f'{OUT}/{name}.json','w'),ensure_ascii=False)
    print(name,len(obj))
print(kpi, c23, c24)
print(municipios[:3]); print([a for a in anual if a['ano']==2023 and a['tipo']=='Reclamações'])
print(Counter(s['situacao'] for s in mensal))
print(sorted({r['regional'] for r in regional_rows}))
