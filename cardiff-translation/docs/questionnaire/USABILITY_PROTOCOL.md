# Protocolo de compreensão e facilidade — usability-tr1-v1

## Pergunta e escopo

Descrever a facilidade percebida de entender e responder a versão brasileira do
CHYPS-V e localizar dificuldades de linguagem, instruções, contexto e interface.
A aplicação foi autônoma, com a mesma versão para todos, sem mudanças na coleta
ou reaplicações, conforme informado pelo responsável. O universo exportado possui
531 submissões; a menção inicial a 530 era arredondamento informal.

A tradução aplicada é a Deepseek-v3.2-deepthink de 2025-12-10, indicada pelo
responsável. O dicionário referencia o arquivo e seu SHA-256. Análise de métricas
entre traduções e avaliação pelos participantes são linhas de evidência distintas:
seus números não são combinados em um índice de qualidade.

## Inclusão e desfechos

- Exigir uma única resposta TR1, com uma única alternativa física correta.
- Comparar texto normalizando somente NFC, caixa e espaços. Gabarito e score
  antigos não determinam inclusão. Registrar motivos de exclusão agregados.
- Exigir IDs de submissão únicos; duplicação técnica interrompe a execução.
  A inexistência de reaplicações é informação do responsável, não dedução dos IDs.
- F1 principal: distribuição das quatro categorias ordinais; recusa e ausência
  separadas. Proporção de dificuldade = (Muito difícil + Difícil) / quatro categorias.
- IC de 95% de Wilson para essa proporção. Sem limiar arbitrário de aprovação.
- Idade: anos completos em submitted_at, derivados de QS2. Formatos aceitos:
  DD/MM/AAAA, AAAA-MM-DD e ISO sem frações com horário, com ou sem Z.
  Valores impossíveis, futuros ou acima de 120 anos são sinalizados, sem imputação.
  Menores de idade não são removidos por critério introduzido após observar os dados.
- Histograma: intervalos fixos de dez anos; mediana e quartis lineares do NumPy.
- Escolaridade: categorias originais em ordem; recusa não equivale a escolaridade.
- Cruzamentos de F1 por escolaridade e faixas etárias 0–17, 18–29, 30–44,
  45–59 e 60–120, descritivos. As faixas não foram escolhidas para otimizar diferenças.
- Q1–Q20, total_score, chyps_score e respostas clínicas não entram nos cálculos.

Excluir quem erra TR1 condiciona o resultado à compreensão dessa instrução,
podendo selecionar uma amostra com maior facilidade. Não extrapolar aos excluídos,
a toda pessoa que iniciou o sistema nem à população brasileira. O export de
submissões não permite estimar abandono ou duração de preenchimento.

## F2: leitura temática

A leitura interpretativa pelo assistente de IA de todos os comentários elegíveis usa categorias conservadoras,
com múltiplos temas por comentário. Relatos de sintomas e diagnósticos não são
interpretados clinicamente. Ausência de crítica não demonstra satisfação.

| Código | Incluir quando o comentário mencionar explicitamente |
|---|---|
| instrucoes_exemplo | Entendimento ou avaliação das instruções e do exemplo inicial |
| alternativas_resposta | Categorias da escala, extremos, categoria intermediária ou resposta indisponível |
| clareza_linguagem | Ambiguidade, abstração ou diferença entre conectivos |
| contexto_memoria | Dificuldade/qualificação para lembrar, aplicar ou contextualizar as situações |
| exemplos_visuais | Pedido de imagens ou padrões para exemplificação |
| extensao_cansaco | Extensão, leitura cansativa ou desconforto durante preenchimento |
| navegacao | Forma de avançar entre telas |
| facilidade_explicita | Afirmação expressa de facilidade, clareza ou preenchimento tranquilo |
| sociodemografico_inclusao | Cobertura, nomenclatura ou inclusão de categorias sociodemográficas |
| recrutamento | Informações no convite |

A aprovação expressa da orientação inicial pode ser codificada também em
facilidade_explicita. Elogios genéricos à pesquisa não equivalem a clareza.
A codificação foi feita em uma única leitura pelo assistente de IA, sem validação humana independente ou concordância interavaliadores.
As categorias se consolidaram na leitura desta base e são exploratórias.
O total de temas pode superar o número de comentários.

O script distingue marcador N/A, ausência explícita de observações, texto vazio,
texto sem conteúdo interpretável e comentário com conteúdo; a lista explícita de
marcadores está no código. Nenhum marcador é convertido em satisfação.
Contagens são por comentário, com denominadores informados. O arquivo de revisão
manual relaciona IDs a rótulos apenas em armazenamento privado fora do Git; inclui
hash do JSON para impedir sua aplicação acidental a outra base.

## Execução

A partir de cardiff-translation, em ambiente com NumPy e Matplotlib:

```sh
python scripts/analyze_usability.py \
  --input /caminho/privado/fora-do-git/questionnaire_3_report.json \
  --review /caminho/privado/fora-do-git/review.json \
  --output results/usability/nova-execucao
python -m unittest discover -s tests -v
```

A pasta de saída precisa ser nova; relatórios anteriores não são sobrescritos.
O script recusa entradas privadas localizadas dentro de qualquer checkout Git.
Sem --review, gera a parte quantitativa e informa codificação temática pendente.
Para reproduzir temas, obter a revisão pelo canal privado autorizado, nunca pelo
repositório. Versões e hashes de código/entradas constam nos metadados da execução.

## Publicação

Nunca adicionar JSON de respostas, revisão por ID, comentários, linhas individuais,
nomes, e-mails, datas de nascimento individuais ou capturas preenchidas ao Git.
Arquivos anonimizados com uma linha por participante também estão proibidos.
Publicar somente documentação, código, metadados não pessoais, agregados e figuras.
.gitignore é uma barreira auxiliar; verificar a seleção do commit e os artefatos.
A análise temática não publica trechos, mesmo anonimizados. O apêndice visual é
reconstruído textualmente a partir das capturas: nenhuma seleção ou campo preenchido
é conservado. As capturas originais ficam fora do repositório.

## Próximos estudos sugeridos

Revisão das instruções e das categorias de resposta por especialistas; entrevistas
cognitivas para entender conectivos, situações abstratas e lembrança das experiências;
inclusão deliberada de pessoas com menor escolaridade. Mudanças no texto ou nas
alternativas exigem protocolo próprio e revisão de comparabilidade com o original.
A análise atual não altera o instrumento nem estabelece validade psicométrica.

## Verificação de publicação

```sh
python scripts/verify_usability_publication.py \
  --input /caminho/privado/fora-do-git/questionnaire_3_report.json \
  docs/questionnaire results/usability/initial-cohort
```

A verificação busca nomes/e-mails e comentários longos do export nos artefatos
textuais, além de assinaturas de export e revisão por indivíduo. É uma defesa
complementar: revisar também esquemas, gráficos, texto extraído dos PDFs e diff.
Nunca imprimir os valores encontrados em logs públicos.
