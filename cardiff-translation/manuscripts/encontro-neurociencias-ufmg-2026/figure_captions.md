# Legendas das figuras

**Figura 1 — Estabilidade da seleção de traduções automáticas elegíveis pelo
critério operacional ALT ≤8.** A: frequência de primeiro lugar de Deepseek-v3.2
e Grok-4 nas reamostragens, variando o peso do BERTScore; COMET recebe o peso
complementar. As outras candidatas elegíveis participam do ranking, mas suas
linhas não são mostradas. B: diferença composta Deepseek menos Grok, com pesos
iguais: 0,00085, IC 95% BCa [−0,00843; 0,01567]. O intervalo inclui zero.
São 20 itens pareados, com 10.000 reamostragens; as frequências dependem do corpus
e do protocolo e não representam probabilidade de superioridade geral.
Fonte: composite_sensitivity.csv e paired_comparisons.csv, protocolo
human-reference-item-v1. Figura adaptada do argumento do CBNV e refeita a partir
dos resultados registrados; não houve nova inferência ou geração de traduções.

**Figura 2 — Seleção e facilidade percebida na aplicação autônoma da versão
brasileira do CHYPS-V.** Das 531 submissões, 425 atenderam ao critério de TR1.
Seis das incluídas recusaram responder a F1, deixando 419 respostas ordinais
válidas. As barras mostram contagens e percentuais de cada alternativa entre
os 425 elegíveis. A facilidade agregada foi 394/419 (94,0%); a dificuldade foi
25/419 (6,0%), IC 95% de Wilson [4,1%; 8,7%]. Os denominadores diferentes são
explicitados. As exclusões não representam abandono. Fonte: summary.json do
protocolo usability-tr1-v1; apenas agregados.

**Figura 3 — Perfil etário e dificuldade por escolaridade entre os incluídos.**
A: histograma com intervalos fixos de dez anos, idade na data de submissão;
n=425, mediana 24, Q1–Q3 19–33, limites observados de 9 a 71 anos. B: percentual
de difícil/muito difícil entre respostas ordinais válidas de cada nível escolar;
rótulos indicam numerador/denominador. As seis recusas não integram esses
denominadores. Os pequenos grupos de ensino fundamental têm 9 e 8 respostas
válidas; a comparação é descritiva, sem teste confirmatório ou interpretação
causal. Fonte: summary.json do protocolo usability-tr1-v1; apenas agregados.
