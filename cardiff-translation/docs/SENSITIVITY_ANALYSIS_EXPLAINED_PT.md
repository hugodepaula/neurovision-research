# Como interpretar a análise de sensibilidade das traduções

Este texto transforma as explicações metodológicas do histórico de discussão em
documentação do projeto. Foi confrontado com SENSITIVITY_ANALYSIS.md, o pipeline,
report.md e metadata.json de results/sensitivity/human-reference. Uma discussão
contém propostas e decisões intermediárias; apenas decisões e artefatos confirmados
são descritos como implementação. Esta tarefa não reexecuta modelos semânticos.

## Por que foi necessária uma análise nova

O fluxo anterior produzia um score por tradução concatenada. Reamostrar esse único
valor produz intervalo de largura zero: falta variação entre unidades. A coluna
item do loop antigo identificava a tradução, não cada pergunta. Dividir frases
arbitrariamente também inflaria o número de observações e poderia desalinhá-las.

O novo protocolo usa os mesmos 20 itens em todas as 24 traduções automáticas.
Uma pergunta com várias sentenças continua sendo uma unidade. O alinhamento é
conferido por número e conteúdo. As instruções são um bloco complementar descritivo;
alternativas e instruções repetidas não contam como observações independentes.

## Original, candidata e referência

O inglês é a origem do significado; a candidata é uma tradução automática em
português; a referência é a tradução humana portuguesa existente. COMET recebe os
três papéis: src inglês, mt candidata e ref humana portuguesa. BERTScore compara
candidata e referência em português. A humana fica fora do ranking, para não ser
comparada consigo mesma. Esse protocolo é human-reference-item-v1.

O fluxo histórico que usava inglês também no papel de referência foi preservado
para rastreabilidade. Os novos números não são uma melhora diretamente comparável
nos scores históricos: referência, unidade de agregação e checkpoint diferem.
A média dos scores por pergunta não precisa igualar o score do documento completo.

Uma referência humana não é verdade absoluta. Erros aparentes como poque, ach oas
e a escolha de cortinas em contexto de condução foram registrados e preservados.
O pipeline não corrige a referência nem comprova sua validação independente.
COMETKiwi e UA-COMET foram discutidos como possibilidades, não são métodos
implementados neste fluxo. Incerteza preditiva de métrica e reamostragem do corpus
são fontes distintas de incerteza.

## O que cada medida permite dizer

Jaccard, F1 de tokens e casamento aproximado medem palavras compartilhadas; o
casamento aproximado tolera grafia, sem reconhecer sinônimos. A atribuição é um a
um; a negação e modificadores de intensidade são protegidos. LCS considera ordem
relativa, com palavras intercaladas. Bigramas, edição e TF-IDF oferecem outras
perspectivas. Normalização superficial, remoção conservadora de palavras funcionais
e radicalização são configurações separadas.

O BERTScore implementado é uma variante de casamento de cossenos com a última
camada do NeoBERTugues. A exclusão de tokens especiais é analisada separadamente.
COMET avalia qualidade com origem e referência, não distância simétrica entre duas
candidatas. BERTScore também foi calculado diretamente entre pares de candidatas.
Nem sobreposição lexical nem score contextual significam percentual de correção.
Uma pequena mudança em não, e ou ou pode importar mesmo com score alto.

## Como funciona a inferência

Cada média dá peso igual aos 20 itens. Em 10.000 réplicas com semente 2026,
os mesmos IDs de perguntas são sorteados com reposição para todos os modelos e
métricas, preservando pares e covariância. Mais réplicas reduzem o erro numérico,
sem criar mais informação no instrumento.

BCa 95% ajusta viés e assimetria com aceleração por jackknife. O percentil aparece
como comparação. Amostras constantes ou degeneradas recebem estado explícito;
BCa não é automaticamente confiável por n ser pequeno. Intervalos das métricas
não são recortados artificialmente a 0–1.

Para comparar A e B, calcula-se primeiro d_i = score_A_i − score_B_i e a média
dessas diferenças. Reamostrar os pares informa se a vantagem é estável. Sobrepor
intervalos individuais não resolve a comparação. Randomizações pareadas bilaterais
usam 10.000 sorteios e correção plus-one, sob permutabilidade dentro de cada item.
Holm é aplicado aos 276 pares por métrica/configuração; não cobre conjuntamente
todas as análises exploratórias. ICs marginais não são intervalos simultâneos.

Tolerâncias de 0,005, 0,01, 0,02 e 0,05 são exploratórias. Não rejeitar diferença
não prova equivalência; não há margem clinicamente validada. Intervalo estreito
não corrige configuração inadequada de uma métrica.

## Quais escolhas foram perturbadas

Exclusão de um item por vez, exclusão de subescala, médias por domínio, bootstrap
estratificado preservando cinco itens por domínio, normalização e limiares de
casamento aproximado. Os intervalos estratificados são percentis. Apenas quatro
domínios não sustentam afirmações fortes de bootstrap por clusters.

A composição varia o peso BERTScore de 0 a 1 em passos de 0,05, com COMET recebendo
1 − peso. Peso igual não garante influência igual, pois escalas e distribuições
diferem. O filtro histórico ALT ≤ 8 é fixo e há rankings de todas as candidatas
e das elegíveis. Frequência de primeiro lugar no bootstrap mede estabilidade
condicional aos itens e métricas; não é probabilidade de superioridade geral.

Os 276 pares de modelos em 20 itens geram 5.520 pares de itens dependentes.
A semelhança do corpus é primeiro resumida por pergunta; só então se reamostram
20 médias. Os milhares de pares nunca são tratados como amostras independentes.
Dendrogramas e correlações de rankings são descritivos.

## O que os resultados existentes mostram

O relatório registrado informa F1 lexical médio 0,7844 e casamento aproximado
0,7995. O F1 lexical de palavras não é a pergunta F1 de usabilidade. BERTScore
direto entre candidatas tem média 0,9302, IC BCa 95% [0,9202; 0,9408].
Com pesos iguais e ALT ≤ 8, Deepseek-v3.2 e Grok-4 têm médias próximas; diferença
0,00085, IC [-0,00843; 0,01567], p ajustado 1,0000. O ranking muda com os pesos.
Há convergência geral com diferenças localizadas; esses resultados não provam
que todas as traduções sejam equivalentes ou que exista um vencedor robusto.

Os intervalos descrevem estabilidade sob reamostragem de um instrumento fixo,
sem generalização automática a textos em geral ou a novas gerações dos tradutores.
Qualidade semântica computacional e facilidade percebida pelos participantes
complementam-se, mas não substituem adaptação transcultural e validação clínica.

## Rastreabilidade e leitura recomendada

O guia [técnico](SENSITIVITY_ANALYSIS.md) documenta comandos, dependências e arquivos.
O [relatório existente](../results/sensitivity/human-reference/report.md) e seu HTML
reúnem resultados. metadata.json fixa revisões dos modelos, configurações, hashes e
estados de execução; checksums.json e model_integrity.json registram integridade.
A atualização de Transformers foi necessária para o checkpoint ModernBERT atual,
sem promessa de reprodução byte a byte do checkpoint histórico não fixado.

Esta implementação de usabilidade acrescenta um [protocolo](questionnaire/USABILITY_PROTOCOL.md),
um [mapeamento](questionnaire/MAPPING.md) e um relatório próprio. Seus denominadores
são submissões elegíveis, enquanto os da sensibilidade são itens do instrumento.

Referências: Efron (1987), DOI 10.1080/01621459.1987.10478410; Koehn (2004),
https://aclanthology.org/W04-3250/; Dror et al. (2018),
https://aclanthology.org/P18-1128/; Zhang et al. (2020),
https://arxiv.org/abs/1904.09675; Rei et al. (2020),
https://aclanthology.org/2020.emnlp-main.213/.
