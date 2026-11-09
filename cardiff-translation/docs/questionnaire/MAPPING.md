# Mapeamento do questionário e leitura do JSON

Este dicionário documenta o instrumento e a aplicação; não contém registros individuais. Fonte textual principal: [tradução Deepseek-v3.2](../../translations/markdown/CHYPS-V-br20-Deepseek-v3.2-deepthink-25-12-10.md). Fontes complementares: estrutura fornecida, capturas de tela e esclarecimentos do responsável pela coleta.

## Contrato do exportador

`success` indica o resultado da exportação; `data.questionnaire` contém metadados administrativos. `data.submissions` é uma lista de submissões. Cada submissão possui `submission_id`, `submitted_at`, `total_score`, `chyps_score` e `answers`. Os dois escores não são medidas de facilidade.

| Campo de answers | Significado e cuidado |
|---|---|
| answer_id | Identificador técnico da resposta; não é identificador de pessoa. |
| question_id | Chave da pergunta no banco; usar junto de caption e versão. |
| caption | Código lógico: QS, Q, F, TR1 ou T1; não localizar pela posição da lista. |
| question_title | Título opcional; quase todos estão nulos neste export. Não contém necessariamente o enunciado. |
| selected_option_ids | IDs técnicos das alternativas selecionadas; não equivalem à ordem ou pontuação ordinal. |
| selected_option_texts | Textos das alternativas selecionadas. Não é o catálogo de todas as alternativas. |
| text_response | Texto livre; pode conter datas, identificadores e observações. É privado. |
| score | Pontuação do sistema; não usar para definir correção de TR1 ou dificuldade de F1. |

O exportador em holhos-project/backend/app/api/v1/endpoints/reports.py omite o corpo da pergunta, tipo, obrigatoriedade, condicionais e opções não selecionadas, embora parte disso exista no modelo interno. Títulos nulos não indicam perguntas sem enunciado.

## Correspondência por código

| Código | ID neste export | Etapa | Tipo | Enunciado |
|---|---:|---:|---|---|
| T1 | 39 | 1 | single | TERMO DE CONSENTIMENTO LIVRE E ESCLARECIDO (TCLE) |
| QS1 | 29 | 2 | free_text | Nome |
| QS2 | 30 | 2 | free_text | Data de nascimento: __ / __ / ____ |
| QS3 | 41 | 2 | free_text | Email |
| QS4 | 31 | 2 | single | Sexo biológico ao nascer |
| QS5 | 44 | 2 | free_text | Gênero |
| QS6 | 32 | 2 | unconfirmed | Raça |
| QS7 | 45 | 2 | free_text | Etnia |
| QS8 | 33 | 2 | single | Grau de escolaridade |
| QS9 | 42 | 2 | free_text | Profissão |
| QS10 | 34 | 2 | multiple | Diagnóstico prévio de transtorno |
| QS11 | 35 | 2 | single | Faz uso de medicamento psiquiátrico? |
| QS12 | 43 | 2 | free_text | Quais medicamentos psiquiátricos você utiliza? |
| TR1 | 36 | 3 | single | Por favor, indique o que queremos dizer com 'desconfortável' nas perguntas que você está prestes a responder (leia o texto acima se não tiver certeza): |
| Q1 | 8 | 4 | single | Quando olho para padrões repetitivos ou listrados (ex.: piso padronizado, papel de parede, prédios, roupas listradas), meus olhos ou cabeça ficam tão desconfortáveis que preciso desviar o olhar. |
| Q2 | 9 | 4 | single | Eu tento evitar assistir filmes ou programas de TV que tenham muitos movimentos rápidos ou usem imagens instáveis (ex.: jogos esportivos, filmes de ação) porque os acho desconfortáveis de olhar. |
| Q3 | 10 | 4 | single | Eu desligo ou escureço luzes de teto brilhantes porque elas fazem meus olhos ou cabeça ficarem desconfortáveis. |
| Q4 | 11 | 4 | single | Eu tenho que desviar o olhar ao assistir esportes ou pessoas correndo e se movendo rapidamente porque é visualmente desconfortável. |
| Q5 | 12 | 4 | single | Padrões e imagens listradas e repetitivas parecem cintilar, piscar ou se mover quando eu olho para eles. |
| Q6 | 13 | 4 | single | Eu fecho os olhos ou desvio o olhar se houver luzes estroboscópicas ou piscantes em um programa de TV ou filme no cinema. |
| Q7 | 14 | 4 | single | Mesmo que o sol não esteja diretamente nos meus olhos, preciso baixar o quebra-sol ao dirigir em condições de luz forte porque a luz é desconfortável para meus olhos ou cabeça. |
| Q8 | 15 | 4 | single | Quando há muitas cores brilhantes ao meu redor, eu costumo ter dor de cabeça. |
| Q9 | 16 | 4 | single | Acho mudanças súbitas do escuro para o claro extremamente desconfortáveis para meus olhos e cabeça (ex.: acender luzes à noite, sair de um quarto escuro). |
| Q10 | 17 | 4 | single | Videogames com muito movimento fazem meus olhos ou cabeça ficarem desconfortáveis. |
| Q11 | 18 | 4 | single | Lugares desorganizados ou visualmente bagunçados (ex.: cômodos, lojas ou outros ambientes) fazem meus olhos ou cabeça ficarem desconfortáveis. |
| Q12 | 19 | 4 | single | Eu preciso desviar o olhar ou evitar padrões complexos no meu ambiente (ex.: papel de parede, carpetes, obras de arte). |
| Q13 | 20 | 4 | single | Assistir multidões de pessoas se movimentando é desconfortável para meus olhos e cabeça. |
| Q14 | 21 | 4 | single | Quando a luz do sol reflete em superfícies (ex.: água, neve, espelhos, carros, telas), meus olhos ou cabeça ficam tão desconfortáveis que preciso desviar o olhar. |
| Q15 | 22 | 4 | single | Acho cômodos ou prédios com detalhes listrados ou complexos (ex.: painéis de alto contraste, alvenaria, colunas) desconfortáveis de olhar. |
| Q16 | 23 | 4 | single | Olhar para telas piscantes é desconfortável para meus olhos e cabeça. |
| Q17 | 24 | 4 | single | Eu tento evitar ir a supermercados porque os acho visualmente desconfortáveis (ex.: muitos objetos, prateleiras, cores brilhantes e luzes). |
| Q18 | 25 | 4 | single | Eu tento evitar locais onde haverá luzes estroboscópicas ou piscantes (ex.: boates, teatros, shows) caso elas façam meus olhos ou cabeça ficarem desconfortáveis. |
| Q19 | 26 | 4 | single | Meus olhos ou cabeça ficam desconfortáveis se houver uma luz forte no escuro (ex.: telas de cinema, auditórios, lanternas, faróis de carro à noite). |
| Q20 | 27 | 4 | single | Roupas com listras, xadrez ou padrões complexos me dão vontade de desviar o olhar. |
| F1 | 28 | 5 | single | Qual foi a sua dificuldade ou facilidade em entender e responder este teste? |
| F2 | 40 | 5 | free_text | Observação |
| F3 | 46 | 5 | free_text | Como você ficou sabendo deste teste? |

## Regras de interpretação

- T1: consentimento. Nenhuma nova exclusão por consentimento foi inferida nesta análise; o fluxo de aplicação é documentado.
- TR1: incluir somente uma resposta única com o texto físico definido pelo protocolo. Comparar Unicode NFC, espaços normalizados e caixa; não remover acentos nem aceitar equivalência semântica aproximada. Ausência, múltiplas alternativas ou duplicação de TR1 excluem a submissão.
- F1: quatro categorias ordinais. Recusa e ausência são separadas. IDs e score nunca definem a ordem. Dificuldade reúne Muito difícil e Difícil; o denominador exclui recusas e ausências.
- QS2: data de nascimento em texto; calcular anos completos na data submitted_at. Não utilizar a data de execução. Aceitar somente formatos documentados pelo script; sinalizar valores inválidos.
- QS8: sete níveis educacionais e recusa explícita. Não converter automaticamente em anos de estudo.
- F2: opcional. Distinguir vazio, marcadores N/A, declaração explícita de ausência de observações, texto sem conteúdo interpretável e comentário com conteúdo. Nenhuma dessas ausências prova satisfação.
- QS12: seguimento sobre medicamentos; a condição provável é dependência de QS11, mas a regra exata não foi confirmada nas capturas. Não tratar ausência como resposta negativa.
- Q1–Q20: documentar enunciados e alternativas; não usar respostas ou escores nos cálculos de usabilidade.

Os IDs são próprios da base exportada e não devem ser calculados aritmeticamente. captions não substituem o controle de versão: migrações antigas contêm rótulos sociodemográficos diferentes dos observados no export.

## Histórico que afeta a interpretação

A migração a7f2e9c4d1b5 troca a referência de F1 de questionário para teste e organiza instruções/TR1; b3d8f6a2e9c7 corrige o gabarito de TR1. Essas migrações demonstram evolução do código, não comprovam quais versões estavam implantadas em cada data. O responsável informou que a versão e a aplicação permaneceram iguais durante esta coleta. A seleção atual usa texto da alternativa, independentemente do score histórico.

## Exemplo fictício

Uma resposta com caption F1 e selected_option_texts igual a ["Fácil"] incrementa a categoria Fácil uma vez. Uma resposta ["Prefiro não responder"] incrementa apenas recusa. Uma observação N/A não entra na codificação de temas. Nenhum exemplo é extraído de participante.

## Fontes, lacunas e apêndice

O arquivo [dictionary.json](dictionary.json) contém metadados e alternativas conhecidas em ordem de exibição. null em required significa não verificado, e não opcional. QS6 e QS12 carecem de confirmação visual; o enunciado abreviado nunca é completado por suposição. [Apêndice visual](visual-appendix.html) registra a cobertura das imagens e permite impressão em PDF; há também uma [cópia PDF](visual-appendix.pdf).
