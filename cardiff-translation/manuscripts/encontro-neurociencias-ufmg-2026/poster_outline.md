# Roteiro científico do pôster

Título literal: **Qualidade linguística e compreensão preliminar na adaptação do CHYPS-V para o português brasileiro**.

Pergunta: como articular a qualidade linguística computacional de traduções e a
facilidade percebida pelo público da versão brasileira? O resultado central é
facilidade elevada entre os elegíveis, com limites de generalização e pontos
específicos para revisão.

| Ordem | Função e mensagem | Evidência / fonte | Composição | Tempo estimado |
|---|---|---|---|---|
| 1 | Identificar o estudo e motivar a adaptação | CHYPS-V, 20 itens; Price et al., 2025 | Título e metadados no cabeçalho; pergunta no alto à esquerda | 45 s |
| 2 | Explicar as duas unidades de análise | 20 itens para métricas; submissões para facilidade; protocolos versionados | Método à esquerda e fluxo de seleção à direita | 75 s |
| 3 | Mostrar estabilidade limitada da escolha | composite_sensitivity.csv; paired_comparisons.csv | Figura 1: liderança por pesos e diferença pareada com IC | 75 s |
| 4 | Apresentar o achado novo principal | summary.json: 531 → 425 → 419; 394/419 fácil/muito fácil | Destaque à direita e Figura 2 com barras de F1 | 90 s |
| 5 | Caracterizar o público e localizar possíveis dificuldades | summary.json: idade, escolaridade e temas de F2 | Figura 3 em dois painéis; F2 no bloco interpretativo | 75 s |
| 6 | Delimitar a conclusão e as implicações | Seleção por TR1, grupos pequenos, ausência de validação psicométrica | Conclusão à esquerda, referências abaixo; ética no rodapé | 60 s |

Total estimado: sete minutos, sem ensaio cronometrado. A contagem de 531 é de
submissões. A inexistência de reaplicações foi informada pelo responsável.
Não apresentar a seleção de 425 como taxa de abandono. As seis recusas de F1
continuam no perfil dos elegíveis e são excluídas apenas do denominador ordinal.

## O que cada figura sustenta

1. A proximidade dos líderes não permite superioridade inequívoca; frequência de
primeiro lugar depende de pesos, corpus e métricas. IC contendo zero não prova
que as traduções sejam equivalentes.
2. A facilidade autorrelatada foi alta entre os incluídos. Percentuais das barras
usam 425, enquanto o destaque de 94,0% usa 419; os denominadores aparecem no pôster.
3. A amostra é predominantemente jovem, com maior dificuldade descritiva em dois
pequenos grupos de ensino fundamental. Não se estimou efeito causal da escolaridade.

## Elementos do modelo oficial

Conservar ambos os logotipos e as três linhas de separação. Reutilizar os quadros
de título, autoria, introdução, método, resultado, conclusão, referência,
legenda e fonte. Remover a figura de desmatamento e o QR de exemplo. A referência
visual original é um único slide de 90 × 120 cm, vertical; nenhum slide extra é
necessário. O roteiro orienta a fala junto ao pôster, não uma palestra em slides.

## Priorização do conteúdo

No resumo curto: principais resultados computacionais, seleção atual, facilidade,
idade e limitação. No pôster: estabilidade por pesos, distribuição completa de F1,
perfil etário, escolaridade e breve indicação de temas de F2. Não incluir respostas
individuais, métricas de desempenho clínico, ERG ou propriedades psicométricas.
