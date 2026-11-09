"""Aggregate questionnaire usability; private inputs must remain outside Git."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import date, datetime
import hashlib
import html
import json
import math
from pathlib import Path
import re
import subprocess
import unicodedata

F1 = ['Muito difícil', 'Difícil', 'Fácil', 'Muito fácil']
EDUCATION = ['Ensino fundamental incompleto', 'Ensino fundamental completo',
             'Ensino médio incompleto', 'Ensino médio completo',
             'Ensino superior incompleto', 'Ensino superior completo', 'Pós-graduação']
CORRECT = 'Dor física, cansaço ou tensão dentro ou ao redor dos olhos ou da cabeça'
THEMES = {
 'instrucoes_exemplo': 'Instruções ou exemplo inicial',
 'alternativas_resposta': 'Alternativas de resposta e categorias ausentes',
 'clareza_linguagem': 'Clareza, abstração ou conectivos',
 'contexto_memoria': 'Contexto, memória ou aplicabilidade das situações',
 'exemplos_visuais': 'Sugestão de exemplos visuais',
 'extensao_cansaco': 'Extensão ou cansaço no preenchimento',
 'navegacao': 'Navegação e avanço de tela',
 'facilidade_explicita': 'Facilidade ou clareza explicitamente elogiada',
 'sociodemografico_inclusao': 'Categorias sociodemográficas, inclusão ou cobertura',
 'recrutamento': 'Informações do convite',
}
ALLOWED = {'TR1', 'F1', 'F2', 'QS2', 'QS8'}

def norm(text):
    return ' '.join(unicodedata.normalize('NFC', str(text or '')).split()).casefold()

def wilson(k, n):
    if not n: return None
    z = 1.959963984540054
    p = k/n; den = 1+z*z/n
    mid = (p+z*z/(2*n))/den
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [mid-half, mid+half]

def age_at(birth, submitted):
    # Explicit formats only; never silently swap month/day or use today's date.
    raw = str(birth or '').strip()
    b = None
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ'):
        try: b = datetime.strptime(raw, fmt).date(); break
        except ValueError: pass
    if b is None: return None, 'birth_unparsed'
    try: s = datetime.fromisoformat(str(submitted).replace('Z','+00:00')).date()
    except ValueError: return None, 'submission_unparsed'
    age = s.year-b.year-((s.month,s.day)<(b.month,b.day))
    if b>s or age>120: return None, 'age_implausible'
    return age, 'valid'

def answer_index(row):
    out = {}
    for a in row.get('answers', []):
        c = a.get('caption')
        if c in ALLOWED: out.setdefault(c, []).append(a)
    return out

def choice(index, caption):
    entries = index.get(caption, [])
    if len(entries)!=1: return None
    values = entries[0].get('selected_option_texts') or []
    return values[0] if len(values)==1 and isinstance(values[0], str) else None

def f2_status(text):
    t=norm(text)
    if not t: return 'ausente'
    if t in {'n/a','n a','na','n/3'}: return 'marcador_na'
    if t in {'nenhum','nenhuma','não','nao','nada','nada declarar.','nada a declarar.',
             'não tenho observações a fazer no momento','nenhuma observação a ser feita.',
             'nenhuma observação','nada a observa','ndn','não tenho','nao tenho'}:
        return 'sem_observacao_explicita'
    if t in {'aaa','observação','nenh','não possu'}: return 'sem_conteudo_interpretavel'
    return 'comentario_com_conteudo'

def analyze(payload, review=None):
    rows=payload['data']['submissions']
    ids=[r['submission_id'] for r in rows]
    if len(ids)!=len(set(ids)): raise ValueError('Duplicate submission identifiers; resolve privately before aggregation.')
    labels=(review or {}).get('labels_by_submission_id', {})
    known={str(x) for x in ids}
    if set(labels)-known: raise ValueError('Review references unknown submissions.')
    exclusions=Counter(); f1=Counter(); edu=Counter(); ages=[]; age_status=Counter(); f2=Counter(); themes=Counter()
    cross_edu={e:Counter() for e in EDUCATION}
    bins=[(0,17),(18,29),(30,44),(45,59),(60,120)]
    cross_age={f'{lo}–{hi}':Counter() for lo,hi in bins}
    matched=set(); eligible=0; period=[]
    for r in rows:
        idx=answer_index(r)
        tr=choice(idx,'TR1')
        if tr is None: exclusions['TR1 ausente ou inconsistente']+=1; continue
        if norm(tr)!=norm(CORRECT): exclusions['TR1 incorreta']+=1; continue
        eligible+=1
        try: period.append(datetime.fromisoformat(r['submitted_at'].replace('Z','+00:00')).date().isoformat())
        except (ValueError,KeyError): pass
        raw=choice(idx,'F1'); valid={norm(x):x for x in F1}
        f=valid.get(norm(raw), 'Prefiro não responder' if norm(raw)=='prefiro não responder' else 'Ausente/inconsistente')
        f1[f]+=1
        e=next((x for x in EDUCATION if norm(x)==norm(choice(idx,'QS8'))),None)
        e=e or ('Prefiro não responder' if norm(choice(idx,'QS8'))=='prefiro não responder' else 'Ausente/inconsistente')
        edu[e]+=1
        if e in cross_edu: cross_edu[e][f]+=1
        births=idx.get('QS2',[])
        a,reason=age_at(births[0].get('text_response') if len(births)==1 else '',r.get('submitted_at',''))
        age_status[reason]+=1
        if a is not None:
            ages.append(a)
            for lo,hi in bins:
                if lo<=a<=hi: cross_age[f'{lo}–{hi}'][f]+=1; break
        entries=idx.get('F2',[])
        status=f2_status(entries[0].get('text_response') if len(entries)==1 else '')
        f2[status]+=1
        labs=labels.get(str(r['submission_id']),[])
        if len(labs)!=len(set(labs)) or set(labs)-THEMES.keys(): raise ValueError('Invalid review labels.')
        if labs:
            if status!='comentario_com_conteudo': raise ValueError('Review labels require a substantive comment.')
            themes.update(labs); matched.add(str(r['submission_id']))
    if set(labels)-matched: raise ValueError('Review includes excluded submissions.')
    import numpy as np
    n=sum(f1[c] for c in F1); difficult=f1[F1[0]]+f1[F1[1]]
    hist=[{'from':lo,'to_exclusive':lo+10,'n':sum(lo<=a<lo+10 for a in ages)} for lo in range(0,121,10)]
    stats=None if not ages else {k:float(v) for k,v in zip(['minimum','q25','median','q75','maximum'],np.percentile(ages,[0,25,50,75,100]))}
    return {'protocol':'usability-tr1-v1','total_submissions':len(rows),'eligible':eligible,
      'exclusions':dict(exclusions),'collection_period':[min(period),max(period)] if period else None,
      'f1':{c:f1[c] for c in F1+['Prefiro não responder','Ausente/inconsistente']},
      'difficulty':{'n':difficult,'denominator':n,'proportion':difficult/n if n else None,'wilson95':wilson(difficult,n)},
      'education':{e:edu[e] for e in EDUCATION+['Prefiro não responder','Ausente/inconsistente']},
      'age':{'status':dict(age_status),'n':len(ages),'summary':stats,'histogram_10_years':hist},
      'f1_by_education':{e:{c:v[c] for c in F1+['Prefiro não responder','Ausente/inconsistente']} for e,v in cross_edu.items()},
      'f1_by_age_band':{e:{c:v[c] for c in F1+['Prefiro não responder','Ausente/inconsistente']} for e,v in cross_age.items()},
      'f2':{'status':dict(f2),'review_completed':review is not None,'comments_tagged':len(matched),
            'themes':{k:themes[k] for k in THEMES},'method':'Leitura interpretativa pelo assistente de IA, única, com codificação conservadora multirrótulo, sem inferência clínica ou validação humana independente.' if review is not None else 'Codificação manual pendente'}}

def pct(n,d): return f'{100*n/d:.1f}%' if d else 'não estimável'

def render(s):
    d=s['difficulty']; age=s['age']; ci=d['wilson95']
    lines=['# Compreensão e facilidade do CHYPS-V BR','',
      f"Base: **{s['total_submissions']} submissões**; incluídas por TR1: **{s['eligible']}**; excluídas: **{sum(s['exclusions'].values())}**.",
      '', 'Mesma tradução Deepseek-v3.2 para todos; preenchimento autônomo, sem alterações na coleta ou reaplicações, conforme informado pelo responsável.',
      '',f"Período das submissões elegíveis (datas registradas): {' a '.join(s['collection_period'] or [])}.",
      '', '## Facilidade percebida (F1)', '', '| Alternativa | n | % dos elegíveis |','|---|---:|---:|']
    lines += [f'| {c} | {n} | {pct(n,s["eligible"])} |' for c,n in s['f1'].items()]
    lines += ['',f"Dificuldade (Muito difícil + Difícil): **{d['n']}/{d['denominator']} ({pct(d['n'],d['denominator'])})** entre as quatro respostas ordinais válidas."]
    if ci: lines += [f'IC 95% de Wilson: **{100*ci[0]:.1f}% a {100*ci[1]:.1f}%**.']
    lines += ['', f"Entre respostas ordinais válidas, {d['denominator']-d['n']}/{d['denominator']} ({pct(d['denominator']-d['n'],d['denominator'])}) indicaram facilidade. A baixa escolaridade reúne poucos casos, com maior dificuldade descritiva; priorizar entrevistas cognitivas nesse público antes de concluir acessibilidade ampla.", '', 'Recusa explícita e ausência não recebem pontuação ordinal. O intervalo expressa precisão sob um modelo binomial; a seleção da amostra não garante representatividade populacional.',
      '', '![Facilidade percebida](figures/f1.png)', '', '## Idade', '',f"Idades válidas: **{age['n']}**; situações de leitura/validade: `{json.dumps(age['status'],ensure_ascii=False)}`."]
    if age['summary']:
        a=age['summary']; lines += [f"Mediana: **{a['median']:g} anos**; Q1–Q3: **{a['q25']:g}–{a['q75']:g} anos**; limites observados: {a['minimum']:g}–{a['maximum']:g} anos."]
    lines += ['', 'Idade em anos completos na data da submissão; datas fora dos formatos explícitos ou idades fora de 0–120 anos são sinalizadas. Histograma em intervalos fixos de dez anos, incluindo apenas idades válidas.',
      '', '![Distribuição etária](figures/ages.png)', '', '## Escolaridade e facilidade', '', '| Escolaridade | n | Difícil ou muito difícil / F1 válido |', '|---|---:|---:|']
    for e,n in s['education'].items():
        v=s['f1_by_education'].get(e,{}); den=sum(v.get(c,0) for c in F1); k=sum(v.get(c,0) for c in F1[:2])
        lines.append(f'| {e} | {n} | {k}/{den} ({pct(k,den)}) |')
    lines += ['', '![F1 por escolaridade](figures/education.png)', '', '## Idade e facilidade', '', '| Idade | F1 válido | Difícil ou muito difícil |', '|---|---:|---:|']
    for e,v in s['f1_by_age_band'].items():
        den=sum(v[c] for c in F1); k=sum(v[c] for c in F1[:2]); lines.append(f'| {e} | {den} | {k} ({pct(k,den)}) |')
    lines += ['', 'As comparações por grupos são descritivas. Células pequenas exigem cautela; diferenças não demonstram efeito causal da idade ou da escolaridade.',
      '', '## Observações (F2)', '', '| Situação | n |', '|---|---:|---:|']
    lines += [f'| {k} | {n} |' for k,n in s['f2']['status'].items()]
    den=s['f2']['status'].get('comentario_com_conteudo',0)
    lines += ['',s['f2']['method'], '',f"{s['f2']['comments_tagged']} comentários receberam ao menos um dos temas abaixo; denominador de comentários com conteúdo: {den}. Relatos exclusivamente pessoais ou clínicos não foram interpretados clinicamente. Comentários fora dos temas não significam avaliação positiva.",
      '', '| Tema | n de comentários | % dos comentários com conteúdo |', '|---|---:|---:|---:|']
    lines += [f'| {THEMES[k]} | {n} | {pct(n,den)} |' for k,n in s['f2']['themes'].items()]
    lines += ['', 'Codificação interpretativa assistida por IA, exploratória e multirrótulo, sem revisão humana independente ou estimativa de concordância entre avaliadores. Nenhum comentário individual é reproduzido.',
      '', '## Interpretação e limitações', '',
      'A conclusão refere-se às pessoas que acertaram TR1. Excluir quem não compreendeu essa instrução pode tornar a estimativa de facilidade mais favorável do que na base completa. TR1 serve somente para seleção e documentação.',
      '', 'F1 combina entender e responder o teste. F2 ajuda a localizar problemas, mas não separa de maneira experimental tradução, interface, memória e experiência com as situações. Facilidade autorrelatada não comprova adaptação transcultural, equivalência semântica ou validade psicométrica.',
      '', 'A distribuição completa de F1 é o resultado principal. Não foi definido limiar de aprovação, nem realizados testes de hipóteses pós-hoc. Q1–Q20, seus escores e os campos clínicos não entram nos cálculos.',
      '', '## Reprodutibilidade e publicação', '',
      'O script analyze_usability.py recebe o JSON e a revisão temática privados fora de qualquer checkout Git. Apenas agregados e figuras são gravados. summary.json registra parâmetros e hashes de integridade; a revisão privada é necessária para reproduzir a codificação temática. Sem ela, o script informa que a codificação está pendente.',
      '', 'Referência para o IC: Wilson (1927), Probable Inference, the Law of Succession, and Statistical Inference. DOI: 10.1080/01621459.1927.10502953.', '']
    return '\n'.join(lines)

def plots(s,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    p=out/'figures';p.mkdir()
    def save(fig,name):
        fig.tight_layout();fig.savefig(p/f'{name}.png',dpi=170);fig.savefig(p/f'{name}.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4)); cats=list(s['f1']); vals=list(s['f1'].values())
    ax.barh(cats[::-1],vals[::-1],color='#21669b');ax.set_xlabel('Submissões elegíveis (n)')
    for i,n in enumerate(vals[::-1]):ax.text(n+1,i,str(n),va='center')
    save(fig,'f1')
    fig,ax=plt.subplots(figsize=(8,4));h=s['age']['histogram_10_years']; ax.bar([r['from'] for r in h],[r['n'] for r in h],width=10,align='edge',edgecolor='white',color='#21669b')
    nonzero=[r['from'] for r in h if r['n']];ax.set_xlim(min(nonzero,default=0),max(nonzero,default=90)+10)
    ax.set_xlabel('Idade na submissão (anos; intervalos de 10 anos)');ax.set_ylabel('Submissões (n)');save(fig,'ages')
    fig,ax=plt.subplots(figsize=(10,5));left=[0.]*len(EDUCATION)
    for c,color in zip(F1,['#9c3e36','#da9069','#7fb5ac','#256e77']):
        vals=[100*s['f1_by_education'][e][c]/max(1,sum(s['f1_by_education'][e][v] for v in F1)) for e in EDUCATION]
        ax.barh(EDUCATION,vals,left=left,label=c,color=color);left=[a+b for a,b in zip(left,vals)]
    ax.set_xlim(0,100);ax.set_xlabel('% entre respostas ordinais válidas de F1');ax.legend(ncol=2,loc='upper center',bbox_to_anchor=(.5,1.2));save(fig,'education')

def private_file(path):
    path=path.resolve()
    result=subprocess.run(['git','-C',str(path.parent),'rev-parse','--show-toplevel'],capture_output=True,text=True)
    if result.returncode==0: raise ValueError('Private inputs must be outside every Git checkout.')
    return path

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',required=True,type=Path);ap.add_argument('--review',type=Path);ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args(); inp=private_file(args.input)
    review=None
    if args.review:
        review=json.loads(private_file(args.review).read_text())
        if review['input_sha256']!=hashlib.sha256(inp.read_bytes()).hexdigest():raise ValueError('Review/input checksum mismatch.')
    s=analyze(json.loads(inp.read_text()),review)
    s['runtime']={'python':__import__('platform').python_version(), 'numpy':__import__('numpy').__version__, 'matplotlib':__import__('matplotlib').__version__}
    s['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    s['input_sha256']=hashlib.sha256(inp.read_bytes()).hexdigest()
    s['review_sha256']=hashlib.sha256(args.review.read_bytes()).hexdigest() if args.review else None
    s['parameters']={'age_range':[0,120],'histogram_bin_width':10,'confidence':.95,'age_date':'submitted_at','normalization':'Unicode NFC, whitespace and case only','f1_grouping':F1[:2]}
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
    plots(s,args.output)
    md=render(s);(args.output/'report.md').write_text(md)
    # Escape every report line; no raw input, HTML or respondent text reaches output.
    body=[]; in_table=False
    def inline(t):
        return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html.escape(t))
    for line in md.splitlines():
        if line.startswith('|'):
            if re.fullmatch(r'[| :\-]+',line): continue
            if not in_table: body.append('<table>'); in_table=True
            body.append('<tr>'+''.join('<td>'+inline(c.strip())+'</td>' for c in line.strip('|').split('|'))+'</tr>')
            continue
        if in_table:body.append('</table>');in_table=False
        match=re.fullmatch(r'!\[(.*?)\]\((figures/[a-z0-9]+\.png)\)',line)
        if match:body.append(f'<img alt="{html.escape(match[1])}" src="{match[2]}">')
        elif line.startswith('#'):body.append(f'<h2>{html.escape(line.lstrip("# "))}</h2>')
        elif line:body.append(f'<p>{inline(line)}</p>')
    if in_table:body.append('</table>')
    (args.output/'report.html').write_text('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Compreensão do CHYPS-V BR</title><style>body{font:16px/1.65 system-ui;max-width:1050px;margin:40px auto;padding:20px;color:#173042;background:#f4f6f8}img{max-width:100%;background:white}table{border-collapse:collapse;width:100%;background:white}td{border:1px solid #ccd5dc;padding:8px}tr:first-child{font-weight:bold;background:#e6edf3}.line{white-space:pre-wrap;min-height:.6em}@media print{body{background:white;margin:0}.line{font-size:11px}img{max-height:370px;object-fit:contain}}</style>'+''.join(body)+'</html>')
    print(f"Aggregate report generated: {s['eligible']} eligible / {s['total_submissions']} submissions.")

if __name__=='__main__':main()
