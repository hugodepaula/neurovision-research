# Verificação da implementação

- Branch de trabalho: feat/semantic-similarity-sensitivity-analysis.
- 25 testes aprovados: 12 existentes de sensibilidade e 13 de usabilidade/publicação.
- Navegador Chromium: cinco tabelas, três figuras carregadas, 37 cartões do
  dicionário, busca de F1 isolando um cartão e ausência de erros JavaScript.
- PDFs do relatório e do apêndice gerados a partir dos HTMLs verificados.
- Totais conferidos: 531 entradas, 425 elegíveis, 106 excluídas; F1, escolaridade,
  situações de F2 e histograma somam 425. F1 ordinal válido soma 419, com 25 casos
  de dificuldade. SHA-256 do script confere com summary.json.
- Auditoria dos arquivos novos/modificados e texto extraído dos PDFs: nenhuma
  correspondência com os nomes/e-mails protegidos ou comentários longos da base;
  nenhuma estrutura de export de respostas ou revisão por indivíduo.
- Revisão dos esquemas: dictionary.json contém definições de perguntas;
  summary.json contém apenas agregados, parâmetros, versões e hashes.
- Nenhuma resposta Q1–Q20 ou pontuação clínica é usada pelo script de usabilidade.
- Nenhum modelo semântico foi reexecutado; os resultados anteriores foram preservados.

Os testes foram executados com o Python do ambiente e as dependências já disponíveis,
acrescentando rapidfuzz 3.14.6 e snowballstemmer 3.1.1 em diretório de trabalho externo
ao repositório para a suíte existente. Os comandos de reprodução ficam no protocolo.
As versões efetivas de Python, NumPy e Matplotlib usadas no relatório estão em summary.json.

A codificação de F2 foi interpretativa pelo assistente de IA e continua exploratória,
sem validação humana independente. As contagens por tema não são diagnósticos nem
estimativas confirmatórias de prevalência de problemas linguísticos.
