---
lang: pt-BR
title: "Qualidade linguística e compreensão preliminar na adaptação do CHYPS-V para o português brasileiro"
---

# Introdução e objetivo

A hipersensibilidade visual envolve desconforto diante de estímulos como brilho, padrões repetitivos, cintilação e ambientes visualmente intensos. O *Cardiff Hypersensitivity Scale–Visual* (CHYPS-V) reúne 20 itens destinados à avaliação dessas experiências [1]. Sua adaptação para o português brasileiro requer atenção à correspondência conceitual, às escolhas lexicais e à compreensão das instruções. A proximidade entre traduções automáticas torna relevante investigar se pequenas diferenças de pontuação sustentam a escolha de uma versão.

Este estudo examina a qualidade lexical e semântica das traduções e a estabilidade de sua seleção, articulando esses resultados às informações preliminares disponíveis sobre compreensão e facilidade de resposta. O recorte corresponde à etapa linguística da adaptação e não estabelece propriedades psicométricas da versão brasileira.

# Método

## Instrumento, traduções e revisão linguística

O corpus contém o original inglês e 25 versões em português brasileiro: 24 automáticas e uma humana. O CHYPS-V original organiza seus 20 itens em quatro domínios: brilho, padrões, estímulos estroboscópicos e ambientes visualmente intensos [1]. Essa organização foi utilizada para identificar os itens; sua reprodução na amostra brasileira não é objeto deste trabalho.

A elegibilidade seguiu o critério operacional ALT ≤8 aplicado às pontuações de legibilidade registradas no estudo anterior. A plataforma ALT reúne índices de facilidade de leitura e complexidade textual [2]. Foram preservadas a tradução humana e as versões candidatas, inclusive grafias e formulações passíveis de revisão. A versão anteriormente selecionada, Deepseek-v3.2-deepthink, passou por revisão de um psicólogo e dois pesquisadores especialistas, segundo o relato anterior [5]. Não foram atribuídos índices quantitativos de concordância a essa revisão.

## Análise dos dados textuais

Na nova análise, as 24 versões automáticas foram comparadas à referência humana em português, preservando o alinhamento dos 20 itens. Foram calculados F1 de sobreposição de palavras e de casamento aproximado de grafias, interseção/união de vocabulário, subsequência comum e medidas de caracteres. Examinaram-se os efeitos da remoção de palavras funcionais e da radicalização, preservando negação e intensidade. A inspeção qualitativa localizou palavras e trechos divergentes.

A similaridade contextual utilizou uma variante de F1 baseada em BERTScore, com NeoBERTugues e casamento de representações de tokens da última camada [3]. O COMET-22 recebeu o original inglês, a candidata portuguesa e a referência humana portuguesa [4]. As versões dos modelos foram fixadas e registradas. Também se calculou a similaridade contextual diretamente entre traduções automáticas do mesmo item. Os resultados novos são médias por item e não reproduzem o protocolo histórico de pontuação do documento concatenado.

Os IC de 95% foram estimados por bootstrap BCa, com 10.000 reamostragens dos mesmos itens para todos os candidatos. Na síntese entre traduções, calculou-se primeiro a similaridade média dos pares em cada pergunta, reamostrando-se então as 20 perguntas; os pares de modelos não foram tratados como observações independentes. Foram realizadas comparações pareadas com randomização e correção de Holm por métrica. A estabilidade foi examinada por exclusão de itens e subescalas, alteração de normalização e variação do peso do BERTScore de 0 a 1, em passos de 0,05, com peso complementar para COMET [6,7]. A pontuação composta com pesos iguais foi definida pela média das duas métricas.

## Compreensão das instruções e facilidade de resposta

Foram utilizados os resultados agregados da aplicação previamente relatada do CHYPS-BR: 137 respostas, das quais 122 passaram na verificação de compreensão da definição de desconforto físico nas instruções [5]. Essa verificação distingue o sentido pretendido de desconforto de interpretações emocionais. Também foi considerada a facilidade autorreferida de resposta. Não houve nova análise dos registros individuais desses participantes. A etapa com respondentes foi descrita como aprovada pelo CEP/UFMG, Parecer nº 8.062.532, CAAE 93614725.6.0000.5149 [5].

# Resultados

Doze das 25 versões (48%) atenderam ao critério de legibilidade registrado: 11 automáticas e a humana. A versão Deepseek-v3.2-deepthink apresentou ALT 8, Flesch 64,7 e Gulpease 74,3. Nos demais índices registrados, os valores foram Flesch–Kincaid 7,1, Gunning Fog 9,3, ARI 6,8 e Coleman–Liau 10,6. Esses índices descrevem aspectos da legibilidade e não constituem, isoladamente, demonstração de compreensão.

Nos 276 pares distintos de traduções automáticas, a média do F1 lexical por pergunta foi 0,784 (IC 95% BCa: 0,751–0,817); com casamento aproximado de grafias, foi 0,800 (0,769–0,828). A similaridade contextual média foi 0,930 (0,920–0,941). As distribuições das médias de cada par encontram-se na Figura 1. Esses valores indicam convergência no corpus, sem interpretação como percentual de correção da tradução.

![Distribuições descritivas das similaridades médias dos 276 pares de tradutores automáticos, nos 20 itens. A: F1 de palavras após remoção conservadora de palavras funcionais. B: similaridade contextual, variante BERTScore/NeoBERTugues. As linhas indicam as médias. Os IC foram calculados por reamostragem de perguntas, preservando a dependência entre pares; não são IC de 276 observações independentes. As escalas horizontais dos painéis são distintas.](figures/fig01_similarity_distributions.png){width=15.7cm}

Na comparação com a referência humana, Deepseek-v3.2-deepthink apresentou BERTScore 0,911 (IC 95%: 0,897–0,925), COMET 0,894 (0,879–0,907) e pontuação composta 0,903 (0,891–0,915). Entre as 11 candidatas automáticas elegíveis, obteve a maior média composta com pesos iguais, seguida por Grok-4 (0,902). A diferença pareada foi 0,00085 (IC 95%: −0,00843–0,01567; p ajustado por Holm =1,00), sem evidência de vantagem nessa comparação.

Com pesos iguais, Deepseek-v3.2 e Grok-4 ocuparam o primeiro lugar em 51,4% e 45,5% das reamostragens, respectivamente. Na grade de pesos testada, Grok-4 apresentou a maior média quando o peso do BERTScore foi ≥0,70 (Figura 2). Entre todas as 24 candidatas, detectaram-se diferenças em 25/276 comparações de BERTScore e 39/276 de COMET após a correção por métrica. A proximidade dos líderes, portanto, não implica equivalência de todas as traduções.

![Estabilidade da escolha entre candidatas elegíveis (ALT ≤8). A: frequência de primeiro lugar nas 10.000 reamostragens em função do peso do BERTScore; o peso do COMET é complementar. São frequências condicionadas aos itens e ao protocolo, não probabilidades de superioridade geral. B: diferença composta Deepseek-v3.2 menos Grok-4, com pesos iguais e IC 95% BCa. O intervalo inclui zero.](figures/fig02_selection_stability.png){width=15.7cm}

Na aplicação previamente relatada, 122/137 participantes (89,1%) passaram na verificação de compreensão das instruções; entre os incluídos, 93,4% consideraram o instrumento fácil ou muito fácil [5]. Esses indicadores não demonstram compreensão de cada termo. A inspeção lexical identificou “estroboscópicas” em todas as 24 traduções automáticas nos itens 6 e 18, enquanto a referência humana emprega “pulsando ou piscando”. No item 16, ocorreram alternativas como “piscantes”, “cintilantes” e “tremeluzentes” (Figura S1, material suplementar). Esses exemplos identificam pontos concretos para revisão com a população-alvo.

# Discussão e conclusão

A convergência lexical e contextual apoia a existência de formulações próximas, enquanto os intervalos e a sensibilidade dos rankings desaconselham atribuir superioridade inequívoca ao líder. A versão anteriormente escolhida permanece uma candidata linguística consistente com o critério de legibilidade, com índices semânticos próximos aos de outras elegíveis. A decisão de seleção pode incorporar critérios explícitos de clareza, adequação contextual e revisão especializada.

Métricas computacionais não substituem julgamentos de relevância e representatividade dos itens nem análise semântica com a população-alvo. A facilidade autorreferida e a compreensão das instruções são evidências preliminares, com alcance distinto da validade de construto. São limitações a referência humana única, com formulações passíveis de revisão, o corpus fixo de 20 itens e a ausência, nesta reanálise, de escores estruturados de concordância entre juízes ou de entrevistas cognitivas por item. Os IC descrevem estabilidade sob reamostragem deste corpus, sem assegurar generalização a outros textos.

O estudo oferece um procedimento reprodutível para documentar a qualidade da tradução e orientar a revisão do CHYPS-BR. As próximas etapas compreendem avaliação estruturada por juízes e investigação da compreensão de termos específicos pelo público-alvo, articuladas à revisão psicométrica especializada em trabalho próprio.

# Referências

1. Price A, Sumner P, Powell G. Understanding the subtypes of visual hypersensitivity: Four coherent factors and their measurement with the Cardiff Hypersensitivity Scale (CHYPS). *Vision Research*. 2025;233:108610. doi:10.1016/j.visres.2025.108610.
2. Moreno GCL, Leal SE, Duran MS, Aluísio SM. ALT: um software para análise de legibilidade de textos em Língua Portuguesa. 2022. arXiv:2203.12135.
3. Zhang T, Kishore V, Wu F, Weinberger KQ, Artzi Y. BERTScore: Evaluating text generation with BERT. *ICLR*. 2020. arXiv:1904.09675.
4. Rei R, Stewart C, Farinha CAF, Lavie A. COMET: A neural framework for MT evaluation. *EMNLP*. 2020:2685–2702. doi:10.18653/v1/2020.emnlp-main.213.
5. Barbosa ICS et al. Machine Translation para Adaptação Transcultural do CHYPS-BR e Integração com ERG. Resumo expandido disponibilizado do IV Simpósio do CI-IA Saúde da UFMG; 2026. Arquivo: *ciia_resumo_expandido_teseC_v3.pdf*.
6. Efron B. Better bootstrap confidence intervals. *J Am Stat Assoc*. 1987;82:171–185. doi:10.1080/01621459.1987.10478410.
7. Koehn P. Statistical significance tests for machine translation evaluation. *EMNLP*. 2004:388–395. https://aclanthology.org/W04-3250/.
