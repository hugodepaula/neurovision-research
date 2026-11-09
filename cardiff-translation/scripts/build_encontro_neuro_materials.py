"""Build local submission files from official Office templates and public aggregates."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from copy import deepcopy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from docx.shared import Pt as DPt, RGBColor as DColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pptx import Presentation
from pptx.util import Cm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscripts/encontro-neurociencias-ufmg-2026'
RES=ROOT/'results/sensitivity/human-reference'
USABILITY=ROOT/'results/usability/initial-cohort/summary.json'
TEAL='#006b70';NAVY='#004653';GOLD='#bd773d'
AUTHORS='Hugo Bastos de Paula; Jerome Baron'
AFFIL='Universidade Federal de Minas Gerais, Belo Horizonte, MG, Brasil.'
CONTACTS='hugodepaula@gmail.com · jerome.baron.ufmg@gmail.com'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def number(n):return str(n).replace('.',',')
def save(fig,name):
    fig.tight_layout(pad=1.2)
    for ext in ['png','svg','pdf']:
        p=OUT/'figures'/f'{name}.{ext}';fig.savefig(p,dpi=250,bbox_inches='tight')
        if ext=='svg':p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
    plt.close(fig)

def figures(s):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    first='Deepseek-v3.2-deepthink-25-12-10';second='Grok-4-25-07-25'
    w=pd.read_csv(RES/'composite_sensitivity.csv');w=w[w.population=='ALT_le_8']
    p=w.pivot(index='bert_weight',columns='candidate_id',values='first_place_share')
    fig,axs=plt.subplots(2,1,figsize=(8.2,5.6),gridspec_kw={'height_ratios':[1.25,1]})
    for candidate,color,label in [(first,TEAL,'Deepseek-v3.2'),(second,GOLD,'Grok-4')]:axs[0].plot(p.index,p[candidate]*100,color=color,label=label,lw=2.6)
    axs[0].set(xlim=(0,1),ylim=(0,100),ylabel='Primeiro lugar (%)',xlabel='Peso do BERTScore; COMET = 1 − peso')
    axs[0].legend(frameon=False,fontsize=11,loc='upper right');axs[0].set_title('A  A liderança depende dos pesos',loc='left',fontweight='bold')
    d=pd.read_csv(RES/'paired_comparisons.csv');r=d[(d.metric=='composite_050')&(d.candidate_a==first)&(d.candidate_b==second)].iloc[0]
    axs[1].axvline(0,color='#77858b',ls='--');axs[1].errorbar(r['mean'],0,xerr=[[r['mean']-r.bca_low],[r.bca_high-r['mean']]],fmt='o',color=TEAL,capsize=6,lw=3)
    axs[1].set(ylim=(-.8,.8),xlim=(-.02,.02),yticks=[],xlabel='Diferença composta: Deepseek − Grok (pesos iguais)')
    axs[1].set_title('B  Diferença sem vantagem robusta',loc='left',fontweight='bold')
    axs[1].text(.5,.8,'Δ = 0,00085 · IC 95% BCa [−0,00843; 0,01567]',ha='center',transform=axs[1].transAxes,fontsize=11)
    axs[1].text(.5,.1,'20 itens · 10.000 reamostragens pareadas · ALT ≤8',ha='center',transform=axs[1].transAxes,fontsize=10)
    save(fig,'fig01_translation_stability')
    fig,(ax0,ax)=plt.subplots(2,1,figsize=(8.2,5),gridspec_kw={'height_ratios':[.8,3]})
    ax0.axis('off')
    for x,label in [(.12,'531\nsubmissões'),(.5,'425\nincluídas por TR1'),(.88,'419\nF1 ordinal válido')]:
        ax0.text(x,.55,label,ha='center',va='center',weight='bold',color=NAVY,transform=ax0.transAxes)
    ax0.annotate('',xy=(.35,.55),xytext=(.23,.55),arrowprops={'arrowstyle':'->','color':TEAL})
    ax0.annotate('',xy=(.73,.55),xytext=(.66,.55),arrowprops={'arrowstyle':'->','color':TEAL})
    ax0.text(.5,-.12,'106 excluídas por TR1 · 6 recusas de F1 entre as incluídas',ha='center',transform=ax0.transAxes,fontsize=10)
    cats=['Muito difícil','Difícil','Fácil','Muito fácil','Prefiro não responder'];vals=[s['f1'][c] for c in cats]
    ax.barh(cats[::-1],vals[::-1],color=['#9ba6ab',TEAL,'#79b3af',GOLD,'#994f40'])
    ax.set_xlim(0,max(vals)*1.3);ax.set_xlabel('Submissões elegíveis (n; base = 425)')
    for i,n in enumerate(vals[::-1]):ax.text(n+2,i,f'{n} ({number(round(100*n/425,1))}%)',va='center',fontsize=11)
    save(fig,'fig02_participant_ease')
    fig,axs=plt.subplots(2,1,figsize=(8.2,7),gridspec_kw={'height_ratios':[1,1.3]})
    hist=s['age']['histogram_10_years'];h=[r for r in hist if r['from']<80]
    axs[0].bar([r['from'] for r in h],[r['n'] for r in h],width=10,align='edge',edgecolor='white',color=TEAL)
    axs[0].set(xlim=(0,80),xlabel='Idade na submissão (anos)',ylabel='Submissões (n)')
    axs[0].set_title('A  Mediana: 24 anos · Q1–Q3: 19–33 · n = 425',loc='left',fontweight='bold')
    edu=list(s['f1_by_education']);short=['Fund. incompleto','Fund. completo','Médio incompleto','Médio completo','Superior incompleto','Superior completo','Pós-graduação']
    vals=[];labels=[]
    for e in edu:
        v=s['f1_by_education'][e];den=sum(v[c] for c in ['Muito difícil','Difícil','Fácil','Muito fácil']);k=v['Muito difícil']+v['Difícil'];vals.append(100*k/den);labels.append(f'{k}/{den}')
    axs[1].barh(short[::-1],vals[::-1],color=TEAL);axs[1].set_xlim(0,58)
    for i,(v,label) in enumerate(zip(vals[::-1],labels[::-1])):axs[1].text(v+1,i,f'{label} ({number(round(v,1))}%)',va='center',fontsize=10)
    axs[1].set_xlabel('Difícil/muito difícil entre F1 válido (%)')
    axs[1].set_title('B  Escolaridade: comparação descritiva',loc='left',fontweight='bold')
    save(fig,'fig03_audience_profile')

def doc_run(p,text,bold=False,size=12,underline=False):
    r=p.add_run(text);r.bold=bold;r.underline=underline;r.font.name='Arial';r.font.size=DPt(size);r.font.color.rgb=DColor.from_string('FFFFFF');return r

def abstracts(template,c):
    for anonymous in [False,True]:
        d=Document(template);p=list(d.paragraphs)
        p[0].clear();doc_run(p[0],c['title'],True)
        p[2].clear()
        if not anonymous:
            doc_run(p[2],'Hugo Bastos de Paula',underline=True);doc_run(p[2],'; Jerome Baron')
        p[3].clear();p[5].clear();p[6].clear();p[7].clear()
        if not anonymous:
            doc_run(p[5],AFFIL,size=10);doc_run(p[6],CONTACTS,size=10)
        p[10].clear()
        for i,(label,body) in enumerate(c['sections']):
            doc_run(p[10],(' ' if i else '')+label,True);doc_run(p[10],' '+body)
        for empty in p:
            if not empty.text.strip():
                empty.paragraph_format.space_before=DPt(0);empty.paragraph_format.space_after=DPt(0)
                empty.paragraph_format.line_spacing=DPt(3)
        p[10].paragraph_format.line_spacing=1.5
        p[10].alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
        p[12].clear();doc_run(p[12],'Palavras-chave:',True);doc_run(p[12],' '+c['keywords'])
        # Preserve the official page background/header and typography. Remove template author metadata.
        for name in ['author','last_modified_by','comments','subject','keywords','category','identifier']:
            setattr(d.core_properties,name,'')
        d.core_properties.title=c['title']
        stem='abstract_anonymous_pt' if anonymous else 'abstract_identified_pt'
        d.save(OUT/f'{stem}.docx')
        head='' if anonymous else f'{AUTHORS}\n\n{AFFIL}\n\n{CONTACTS}\n\n'
        body=' '.join(f'**{a}** {b}' for a,b in c['sections'])
        (OUT/f'{stem}.md').write_text(f'# {c["title"]}\n\n{head}{body}\n\n**Palavras-chave:** {c["keywords"]}\n')

def text_box(shape,text,x,y,w,h,size=28,color=NAVY,bold=False,align=PP_ALIGN.LEFT):
    shape.left=Cm(x);shape.top=Cm(y);shape.width=Cm(w);shape.height=Cm(h)
    tf=shape.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=tf.margin_right=Cm(.1);tf.margin_top=Cm(.1);tf.margin_bottom=Cm(.1)
    for i,line in enumerate(text.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.alignment=align;p.space_after=Pt(7)
        for r in p.runs:r.font.name='Arial';r.font.size=Pt(size);r.font.bold=(bold or (i==0 and '\n' in text));r.font.color.rgb=RGBColor.from_string(color.lstrip('#'))
    return shape

def poster(template,c):
    prs=Presentation(template);slide=prs.slides[0];s=list(slide.shapes)
    # Map official exemplar: keep both logos and divider lines, replace narrative,
    # remove unrelated sample chart/QR, replace sample figure/source frames.
    for i in [13,15]:
        slide.part.drop_rel(s[i]._element.blipFill.blip.rEmbed)
        slide.shapes._spTree.remove(s[i]._element)
    text_box(s[0],c['title'],3,17.4,84,5,52,'#c72229',True,PP_ALIGN.CENTER)
    text_box(s[1],AUTHORS+'\n'+AFFIL+'\n'+CONTACTS,5,23,80,5,27,TEAL,False,PP_ALIGN.CENTER)
    text_box(s[7],'INTRODUÇÃO E OBJETIVO\nComo combinar avaliação computacional da tradução e facilidade de compreensão pelo público?\nO CHYPS-V reúne 20 itens sobre hipersensibilidade visual [1]. Avaliamos a qualidade linguística das versões e a facilidade percebida da versão brasileira.',3.8,31.5,39.1,10,30)
    text_box(s[2],'METODOLOGIA\n24 traduções automáticas e uma humana. Filtro operacional ALT ≤8.\n20 itens alinhados: sobreposição lexical, variante BERTScore/NeoBERTugues e COMET-22 [2,3]. IC BCa: 10.000 reamostragens pareadas.\nAplicação autônoma da versão Deepseek-v3.2. Inclusão: alternativa física correta em TR1. F1: quatro níveis de facilidade; recusa separada. Idade e escolaridade: descrição. IC da dificuldade: Wilson [4].',3.8,42.3,39.1,15,28)
    text_box(s[5],'1 · ESTABILIDADE DA SELEÇÃO',3.8,58,39.1,2,32,TEAL,True)
    slide.shapes.add_picture(str(OUT/'figures/fig01_translation_stability.png'),Cm(3.8),Cm(60.2),width=Cm(39.1))
    text_box(s[3],'CONCLUSÃO E IMPLICAÇÕES\nAs traduções convergem, mas a ordenação dos líderes depende dos pesos. A facilidade percebida foi alta entre os incluídos.\nSelecionar quem acertou TR1 limita a generalização. Os grupos de menor escolaridade são pequenos.\nF2 sugere atenção ao contexto/memória (7 comentários), alternativas (5) e instruções (3), entre 76 comentários com conteúdo; codificação exploratória por IA, multirrótulo e sem validação humana independente.\nA evidência orienta revisão linguística e entrevistas cognitivas; não estabelece validade psicométrica.',3.8,90.5,39.1,14.4,26)
    text_box(s[4],'REFERÊNCIAS\n[1] Price et al. Vision Res. 2025;233:108610.\n[2] Zhang et al. BERTScore. ICLR, 2020.\n[3] Rei et al. COMET. EMNLP, 2020:2685–2702.\n[4] Wilson. JASA. 1927;22:209–212.',3.8,105.8,39.1,5.8,20)
    text_box(s[14],'94,0% relataram facilidade\n394/419 respostas válidas · 6 recusas\nDificuldade: 6,0% (IC 95%: 4,1%–8,7%)',45,31.5,41,8,36,TEAL,True)
    slide.shapes.add_picture(str(OUT/'figures/fig02_participant_ease.png'),Cm(45),Cm(40.5),width=Cm(41))
    text_box(s[16],'2 · Fluxo e distribuição da facilidade. Percentuais das barras: base 425. O destaque de 94,0% usa as 419 respostas ordinais válidas.',45,66.3,41,3.8,23)
    text_box(s[8],'3 · PERFIL DO PÚBLICO',45,71.3,41,2,32,TEAL,True)
    slide.shapes.add_picture(str(OUT/'figures/fig03_audience_profile.png'),Cm(45),Cm(73.8),width=Cm(41))
    # Add only missing source/footer elements; all native title/body frames remain editable.
    box=slide.shapes.add_textbox(Cm(3.8),Cm(85),Cm(39.1),Cm(3))
    text_box(box,'Fonte: análise por item com referência humana. Frequências de primeiro lugar são condicionais ao corpus; não representam superioridade geral.',3.8,87.2,39.1,2.8,21)
    box=slide.shapes.add_textbox(Cm(3.8),Cm(114),Cm(82),Cm(4))
    text_box(box,'Fontes das figuras 2–3: agregados da coleta até 08/11/2026. Comparações por escolaridade são descritivas.\nCEP: Parecer 8.062.532 · CAAE 93614725.6.0000.5149\nPalavras-chave: hipersensibilidade visual; adaptação transcultural; tradução automática; compreensão; legibilidade.',3.8,114,82,4.8,21)
    for name in ['author','last_modified_by','comments','subject','keywords']:setattr(prs.core_properties,name,'')
    prs.core_properties.title=c['title']
    prs.save(OUT/'poster_pt.pptx')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--abstract-template',type=Path,required=True);ap.add_argument('--poster-template',type=Path,required=True);ap.add_argument('--no-export',action='store_true');a=ap.parse_args()
    OUT.mkdir(exist_ok=True,parents=True);(OUT/'figures').mkdir(exist_ok=True)
    c=json.loads((OUT/'content.json').read_text());s=json.loads(USABILITY.read_text())
    words=len(' '.join(' '.join(pair) for pair in c['sections']).split());assert words<=300
    assert s['eligible']==425 and s['difficulty']['denominator']==419 and s['difficulty']['n']==25
    figures(s);abstracts(a.abstract_template,c);poster(a.poster_template,c)
    if not a.no_export:
        for name in ['abstract_identified_pt.docx','abstract_anonymous_pt.docx','poster_pt.pptx']:
            subprocess.run(['soffice','-env:UserInstallation=file:///workspace/work/encontro-planning/build-lo','--headless','--convert-to','pdf','--outdir',str(OUT),str(OUT/name)],check=True)
            assert (OUT/Path(name).with_suffix('.pdf')).exists()
    evidence={'body_word_count_including_labels':words,'word_limit':300,'authors':AUTHORS,'affiliation':AFFIL,'ethics_confirmed_by_responsible':{'opinion':'8.062.532','caae':'93614725.6.0000.5149'},'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [USABILITY,RES/'paired_comparisons.csv',RES/'composite_sensitivity.csv',ROOT/'manuscripts/cbnv/abstract_pt.md',OUT/'content.json']},'templates':{'abstract':{'url':'https://docs.google.com/document/d/1veWwrwgkEpm-QPuXuEyJxG4hGA85njQK/edit','sha256':sha(a.abstract_template)},'poster':{'url':'https://docs.google.com/presentation/d/1wDlXkZWWjSocFHC5Nq8KxfzHYfFwFQc9/edit','sha256':sha(a.poster_template)}},'participant_data':'Public aggregates only; no access to raw response export in this build.'}
    (OUT/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    print('Built summary and poster. Body words:',words)
if __name__=='__main__':main()
