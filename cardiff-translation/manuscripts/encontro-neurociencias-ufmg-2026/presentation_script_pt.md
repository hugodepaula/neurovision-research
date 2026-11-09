# Roteiro de fala — aproximadamente sete minutos

Estimativa de duração, sem ensaio cronometrado. Apresentador: Hugo Bastos de Paula.
O pôster é a superfície de apoio durante toda a fala.

## 0:00–0:45 — Problema e objetivo

“Este trabalho trata da etapa linguística de adaptação do CHYPS-V, um questionário
com 20 itens sobre hipersensibilidade visual. Precisamos preservar o significado
das perguntas e permitir que as pessoas entendam como responder. Nossa pergunta
foi como combinar métricas de tradução com a facilidade percebida pelo público.
O trabalho amplia o recorte anterior com a avaliação da coleta atual.”

## 0:45–2:00 — Dois componentes, duas unidades de análise

“Na parte computacional, partimos de 24 traduções automáticas e uma humana.
Usamos a humana como referência e mantivemos os mesmos 20 itens alinhados.
Avaliamos palavras compartilhadas, uma variante baseada em BERTScore e COMET-22.
Reamostramos as perguntas em pares, 10 mil vezes, para estimar os intervalos.

Na aplicação, todos receberam a mesma versão, Deepseek-v3.2, em preenchimento
autônomo. Das 531 submissões, selecionamos as 425 que identificaram o sentido
físico de desconforto nas instruções. Entre elas, seis pessoas preferiram não
responder à pergunta de facilidade, restando 419 respostas ordinais válidas.
A idade e a escolaridade descrevem esse público selecionado.”

## 2:00–3:15 — Figura 1: tradução e estabilidade

“A sobreposição lexical média entre as traduções foi 0,784, e a similaridade
contextual média foi 0,930. São índices das métricas, não percentuais de correção.
A Figura 1 mostra que a liderança entre Deepseek e Grok depende do peso atribuído
a cada métrica. Com pesos iguais, o intervalo da diferença pareada inclui zero.
Isso limita uma afirmação de superioridade, mas não demonstra equivalência.
O filtro ALT foi um critério operacional de legibilidade, não garantia de que
qualquer pessoa entenderia todos os termos.”

## 3:15–4:45 — Figura 2: facilidade percebida

“O resultado novo principal está aqui: 394 das 419 respostas válidas indicaram
fácil ou muito fácil, ou 94%. Vinte e cinco indicaram difícil ou muito difícil:
6%, com intervalo de Wilson de aproximadamente 4,1% a 8,7%.

As barras também mostram as seis recusas. Seus percentuais têm base em 425,
enquanto o indicador de 94% usa as 419 respostas válidas. Essa distinção evita
tratar recusa como facilidade ou como nível intermediário.

Essa pergunta reúne entender e responder o teste. Portanto, o resultado não
isola a qualidade da tradução dos efeitos da interface, das instruções ou da
necessidade de lembrar experiências.”

## 4:45–6:00 — Figura 3 e observações

“A mediana da idade foi 24 anos; metade das pessoas tinha entre 19 e 33 anos.
A dificuldade apareceu com maior frequência nos grupos de ensino fundamental,
mas eles têm apenas nove e oito respostas válidas. Esse padrão é descritivo e
não sustenta uma conclusão causal ou generalização para esses níveis escolares.

As observações abertas sugerem atenção a contexto e memória das situações,
alternativas de resposta e instruções. Essa leitura foi exploratória, feita com
assistência de IA, e não teve revisão humana independente. Não interpretamos
relatos clínicos nem publicamos comentários individuais. Esses temas ajudam a
formular perguntas para uma próxima etapa de entrevistas cognitivas.”

## 6:00–7:00 — Conclusão e implicação

“Temos convergência entre traduções, mas a escolha computacional depende das
configurações. Temos também facilidade percebida elevada, condicionada a quem
compreendeu a instrução inicial. Excluir quem errou essa pergunta pode produzir
uma estimativa mais favorável do que a experiência de todos os respondentes.

Esses resultados ajudam a direcionar a revisão linguística e a investigação
com o público, especialmente pessoas com menor escolaridade. Ainda não estamos
afirmando equivalência entre traduções ou validade psicométrica da versão brasileira.”

## Versão abreviada de cinco minutos

Reduzir a explicação das métricas para 45 segundos e o perfil/observações para
45 segundos. Preservar o fluxo 531/425/419, os 94%, a distinção de denominadores
e a limitação da seleção por TR1. Evitar ler o pôster integralmente.

## Perguntas prováveis

**94% prova que a tradução está validada?** Não. É facilidade percebida, selecionada
por compreensão da instrução. Não comprova compreensão de cada termo, adaptação
transcultural concluída nem estrutura psicométrica.

**Por que excluir quem errou TR1?** Foi o critério definido pelo responsável para
esta análise. Delimita a população analisada; não é um procedimento que elimina
todo viés ou melhora automaticamente a qualidade da amostra.

**Por que não usar a antiga aplicação de 137 participantes junto à atual?** Elas
podem se sobrepor. O novo trabalho usa o retrato atual e não soma amostras nem
apresenta uma mudança temporal como se fosse seguimento independente.

**Por que o líder varia?** BERTScore e COMET têm comportamentos diferentes; mudar
o peso altera sua contribuição. A incerteza por composição dos itens também é
relevante. O primeiro lugar não é uma probabilidade de superioridade geral.

**O que fazer com a maior dificuldade no ensino fundamental?** Planejar investigação
de compreensão com esse público. Os tamanhos atuais são pequenos; não sustentar
uma diferença populacional a partir desses percentuais isolados.
