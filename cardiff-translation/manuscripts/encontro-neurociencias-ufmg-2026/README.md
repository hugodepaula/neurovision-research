# IV Encontro de Pesquisa em Neurociências — UFMG, 2026

Material para submissão de resumo e apresentação em pôster, derivado do manuscrito
do CBNV e ampliado com os agregados atuais de facilidade e perfil do público.
O título científico do CBNV foi preservado literalmente. Autoria aprovada:
Hugo Bastos de Paula (primeiro autor/apresentador) e Jerome Baron. Afiliação:
Universidade Federal de Minas Gerais, Belo Horizonte, MG, Brasil.

## Arquivos para uso

| Arquivo | Uso |
|---|---|
| [abstract_identified_pt.docx](abstract_identified_pt.docx) / [PDF](abstract_identified_pt.pdf) | Resumo identificado no modelo oficial |
| [abstract_anonymous_pt.docx](abstract_anonymous_pt.docx) / [PDF](abstract_anonymous_pt.pdf) | Resumo sem identificação, com conteúdo científico idêntico |
| [poster_pt.pptx](poster_pt.pptx) / [PDF](poster_pt.pdf) | Pôster editável e impressão em 90 × 120 cm, vertical |
| [poster_outline.md](poster_outline.md) | Argumento, composição, evidências e fontes do pôster |
| [presentation_script_pt.md](presentation_script_pt.md) | Roteiro estimado de sete minutos e perguntas prováveis |
| [figure_captions.md](figure_captions.md) | Legendas completas das três figuras |
| [figures/](figures/) | Figuras em PNG, SVG e PDF; SVG/PDF preservam vetores |
| content.json | Texto canônico do resumo, comum às duas versões |
| evidence.json / checksums.json | Rastreabilidade dos agregados, modelos e artefatos |

## Conformidade e fontes

O corpo tem 236 palavras, contando subtítulos por separação em espaços; o limite
é 300, excluindo título, identificação e palavras-chave. Ambos os PDFs de resumo
têm uma página. Mantiveram-se a tipografia, a estrutura e o fundo institucional do
modelo oficial. Foram compactados apenas os parágrafos vazios para acomodar o
novo título e as palavras-chave sem reduzir a fonte do corpo (Arial 12, 1,5 linha).
A versão anônima remove nomes, afiliação, e-mails e metadados pessoais; a marca do
próprio evento, comum ao modelo, permanece. O número ético é conservado por exigência
do edital, com confirmação do responsável de cobertura da coleta atual.

- Normas: PDF INSTRUÇÕES_GERAIS.pdf fornecido pelo responsável, seções 8 e 10.
- [Modelo de resumo](https://docs.google.com/document/d/1veWwrwgkEpm-QPuXuEyJxG4hGA85njQK/edit), Office DOCX original.
- [Modelo de pôster](https://docs.google.com/presentation/d/1wDlXkZWWjSocFHC5Nq8KxfzHYfFwFQc9/edit), Office PPTX original.
- [Manuscrito do CBNV](../cbnv/extended_abstract_pt.md).
- [Relatório de usabilidade](../../results/usability/initial-cohort/report.md).
- [Relatório de sensibilidade](../../results/sensitivity/human-reference/report.md).

Os modelos foram trabalhados em cópias locais. Os arquivos remotos originais não
foram editados. No pôster, preservaram-se logotipos, divisórias e dimensões; os
quadros de texto foram adaptados e reposicionados. A figura e o QR de exemplo
foram removidos; nenhum QR foi inventado. Texto do pôster permanece editável e
as figuras possuem fontes vetoriais separadas. A exportação foi feita com
LibreOffice e inspecionada em PDF, sem teste declarado no Microsoft PowerPoint.

## Atualização científica em relação ao CBNV

Os antigos indicadores 122/137 e 93,4% são substituídos pelo retrato atual:
531 submissões, 425 incluídas por TR1, 419 respostas ordinais válidas de F1,
394 avaliações de facilidade e 25 de dificuldade; seis recusas. Não foram
somadas amostras potencialmente sobrepostas nem testada uma evolução temporal.
As métricas de traduções não foram recalculadas nem combinadas com a facilidade
em um índice único. Resultados de ERG, análise fatorial e consistência interna
não integram este recorte.

A mediana de idade é 24 anos (Q1–Q3: 19–33). A maior dificuldade nos grupos de
ensino fundamental é uma descrição de grupos pequenos (9 e 8 respostas válidas),
não uma associação confirmatória ou evidência de causalidade. F2 é apresentado
somente por temas agregados; sua codificação exploratória por IA não teve revisão
humana independente. Nomes e e-mails dos autores são metadados de autoria aprovados,
não dados dos respondentes.

## Reprodução

A partir de cardiff-translation, com NumPy, Pandas, Matplotlib, python-docx,
python-pptx, LibreOffice e Poppler disponíveis:

```sh
python scripts/build_encontro_neuro_materials.py \
  --abstract-template '/caminho/modelo-resumo-oficial.docx' \
  --poster-template '/caminho/modelo-poster-oficial.pptx'
```

Obter os modelos pelos links oficiais. Seus hashes de entrada estão em evidence.json.
O script utiliza somente agregados versionados, mantém o CBNV e seus resultados
intactos e reconstrói os arquivos desta pasta. Não recebe nem necessita do JSON de
respostas. Para editar o resumo, alterar content.json e reconstruir ambas as versões.
A inspeção visual precisa ser repetida após mudanças de conteúdo ou diagramação.

## Operação de submissão

Categoria proposta: estudo original. Área sugerida: Neurociência Clínica.
Segundo o PDF fornecido, o prazo dos resumos é 08/11/2026; o prazo de inscrição
geral, 13/11/2026. Evento presencial em 17–19/11/2026. Este pacote não comprova
prorrogação nem envio de formulário. A inscrição e a submissão não foram realizadas.
Antes do envio, conferir a autoria e anexar as duas versões corretas; para imprimir,
usar tamanho real (90 × 120 cm), sem ajustar para A4. O modelo do pôster é opcional
no edital; seu uso aqui foi aprovado como base visual.

**Dados individuais nunca são publicados.** Este pacote contém apenas texto
científico, autoria autorizada e resultados agregados, sem comentários individuais,
respostas Q1–Q20, identificadores, datas de nascimento ou export de respondentes.
