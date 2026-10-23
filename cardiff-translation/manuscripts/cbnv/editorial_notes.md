# Notas de revisão — uso interno

## Recorte e contribuição

A nova redação se concentra na qualidade linguística, na estabilidade da seleção
das traduções e na compreensão preliminar das instruções. Retira resultados e
conclusões de AFC, modelos bifatoriais, ajuste, escore total, alfa de Cronbach,
estrutura de subescalas brasileiras e integração/predição com ERG. As opiniões
técnicas da conversa foram tratadas como contexto editorial; não foram convertidas
em afirmações gerais sobre requisitos psicométricos.

A contribuição adicional em relação ao resumo anterior é a reanálise por item com
referência humana, IC pareados, sobreposição lexical, comparações diretas entre
traduções e sensibilidade dos rankings. Não foi redigida uma alegação de novidade
absoluta ou de validação psicométrica concluída.

## Limites documentais

- O link do Google Docs foi consultado por exportação e retornou HTTP 401,
  exigindo autenticação. Seu conteúdo, autoria e template não foram acessados;
  nenhuma alteração foi feita no documento remoto. Estes são novos arquivos
  para revisão e posterior incorporação.
- O resumo curto tem o número de palavras registrado em `evidence.json`.
  Não foram disponibilizados limites de palavras/páginas/figuras do edital
  CBNV. A formatação é uma proposta de revisão, não certificação de conformidade
  com o edital. A versão expandida inclui duas figuras principais; a terceira
  é suplementar e está disponível separadamente.
- Não foram preenchidos nomes/autoria a partir do PDF anterior. A conversa
  contém manifestação sobre não participação no resumo anterior; a nova autoria
  precisa refletir contribuições e concordância atuais, sem inclusão automática.
- A conversa privada não foi copiada para o manuscrito, citada como evidência
  científica nem incluída como anexo de divulgação.
- Os dados individuais dos respondentes não estão disponíveis no componente
  Cardiff. Os números 137, 122, 89,1% e 93,4% são agregados do resumo anterior;
  não representam uma análise nova da coleta atual. Os números N=180 ou >350
  mencionados na conversa não foram misturados a essa etapa histórica.
- A revisão por um psicólogo e dois pesquisadores é a revisão relatada no PDF
  anterior. Não se inventaram procedimento cego, notas individuais, CVC/IVC,
  concordância, protocolo de entrevistas cognitivas ou medidas de compreensão
  específicas de cada item.
- A retrotradução foi mencionada na conversa, mas não foi localizada documentação
  de sua execução ou seus resultados no material consultado. Não foi descrita como
  procedimento realizado. A referência [5] é o arquivo fornecido; dados editoriais
  de anais/DOI não foram inventados.
- O relato informal de dificuldade com “estroboscópico” motivou atenção lexical;
  não foi transformado em frequência de incompreensão na população. A Figura 3
  conta versões de tradução, não pessoas.

## Cuidados com a interpretação

- ALT ≤8 é o critério operacional registrado; não foi convertido em garantia de
  escolaridade, compreensão ou adequação clínica. O valor ALT 8 é o armazenado;
  não foi recalculado a partir dos índices individuais no manuscrito.
- A variante baseada em BERTScore usa NeoBERTugues, última camada, casamento de
  tokens, sem ponderação IDF e sem reescalonamento. A sensibilidade sem tokens
  especiais está no relatório analítico. Não se apresentam os scores como
  percentuais de fidelidade ou correção.
- Os resultados históricos usavam o original inglês como referência e texto
  concatenado; os novos usam referência humana portuguesa e média de itens.
  A versão atual do checkpoint também foi fixada. Valores absolutos dos dois
  protocolos não devem ser interpretados como melhora direta. O PDF anterior
  cita amplitude BERTScore ~0,028; o CSV contém ~0,0227. Essa discrepância não foi
  propagada ao novo resumo.
- A referência humana tem grafias e escolhas lexicais passíveis de revisão,
  registradas no relatório. Não foi alterada silenciosamente nem declarada
  padrão perfeito.
- Os IC de similaridade geral usam 20 médias por pergunta, sem pseudorreplicação
  dos 276 pares. A amostra é um instrumento fixo; os IC medem estabilidade sob
  esse modelo de reamostragem.
- Um IC de diferença contendo zero e p não significativo não provam equivalência.
  Houve diferenças detectáveis em alguns pares. A liderança dos elegíveis é
  sensível ao peso das métricas e não constitui classificação clínica.
- O bootstrap não mede variabilidade de novas gerações dos modelos nem substitui
  análise de compreensão do público-alvo.

## Figuras

1. Histogramas das médias de similaridade de pares, com eixos próprios e descrição
   da dependência entre pares. Respondem à pergunta sobre a proximidade geral das
   traduções.
2. Frequências de primeiro lugar nas reamostragens e IC da diferença dos líderes.
   Mostram a incerteza da escolha e sua sensibilidade aos pesos.
3. Exemplos e frequências lexicais por item, especialmente “estroboscópicas”.
   Mostram que convergência computacional e acessibilidade lexical precisam ser
   avaliadas separadamente. É figura suplementar.

Uma nuvem de palavras geral enfatizaria termos do tema — olhos, cabeça, luz,
desconforto — sem mostrar adequadamente as diferenças entre versões. Por isso
foram escolhidas frequências de alternativas lexicais alinhadas por item.

## Arquivos e reprodução

Fontes numéricas: `results/questions-only/original/analysis_results_alt.csv` e
`results/sensitivity/human-reference/`. Para reconstruir as figuras e exportar os
manuscritos, a partir de `cardiff-translation/`:

```bash
MPLCONFIGDIR="$PWD/.cache/matplotlib" OPENBLAS_NUM_THREADS=1 \
  .venv/bin/python scripts/build_cbnv_materials.py
```

Requer Matplotlib, Pandas e NumPy do ambiente já preparado; para DOCX/PDF, Pandoc
e XeLaTeX. A execução não modifica resultados de análise nem o documento remoto.
