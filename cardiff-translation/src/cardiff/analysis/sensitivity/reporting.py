"""Portable research reports, exportable figures and an interactive word comparison."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


def markdown_table(frame: pd.DataFrame, columns=None, limit=30) -> str:
    frame = frame[columns] if columns else frame

    def cell(value):
        if isinstance(value, (float, np.floating)):
            return f"{value:.4f}" if np.isfinite(value) else "não estimável"
        return str(value).replace("|", "/").replace("\n", " ")

    rows = [
        "| " + " | ".join(frame.columns) + " |",
        "| " + " | ".join(["---"] * len(frame.columns)) + " |",
    ]
    rows.extend(
        "| " + " | ".join(cell(v) for v in row) + " |"
        for row in frame.head(limit).itertuples(index=False, name=None)
    )
    return "\n".join(rows)


def plots(output: Path, tables: dict, metadata: dict):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.cluster.hierarchy import dendrogram, linkage
    from scipy.spatial.distance import squareform

    folder = output / "figures"
    folder.mkdir(exist_ok=True)
    agg = tables["pairwise_model_means"]
    content = agg.loc[agg["mode"] == "content"]
    names = sorted(set(content.candidate_a) | set(content.candidate_b))
    matrix = pd.DataFrame(np.eye(len(names)), index=names, columns=names)
    for row in content.itertuples():
        matrix.loc[row.candidate_a, row.candidate_b] = matrix.loc[
            row.candidate_b, row.candidate_a
        ] = row.fuzzy_f1
    labels = [n[:35] for n in names]
    fig, ax = plt.subplots(figsize=(13, 11))
    im = ax.imshow(matrix, vmin=0, vmax=1, cmap="viridis")
    ax.set_xticks(range(len(names)), labels, rotation=90, fontsize=6)
    ax.set_yticks(range(len(names)), labels, fontsize=6)
    ax.set_title(
        "Similaridade lexical: casamento aproximado de palavras (F1)\nMédia dos 20 itens; sem palavras funcionais; referência humana incluída"
    )
    fig.colorbar(im, ax=ax, label="F1 de casamento de palavras")
    fig.tight_layout()
    fig.savefig(folder / "pairwise_similarity.png", dpi=180)
    fig.savefig(folder / "pairwise_similarity.svg")
    plt.close(fig)
    distances = np.clip(1 - matrix.to_numpy(), 0, 1)
    np.fill_diagonal(distances, 0)
    fig, ax = plt.subplots(figsize=(11, 8))
    dendrogram(
        linkage(squareform(distances, checks=True), method="average"),
        labels=names,
        orientation="left",
        ax=ax,
        leaf_font_size=7,
    )
    ax.set_title("Agrupamento descritivo por similaridade lexical")
    ax.set_xlabel("1 − F1 médio de casamento aproximado; ligação média")
    fig.tight_layout()
    fig.savefig(folder / "lexical_clustering.png", dpi=180)
    fig.savefig(folder / "lexical_clustering.svg")
    plt.close(fig)
    summaries = tables["reference_intervals"]
    forest = summaries.loc[
        (summaries["mode"] == "content") & (summaries.metric == "fuzzy_f1")
    ].sort_values("mean")
    fig, ax = plt.subplots(figsize=(11, 9))
    for i, row in enumerate(forest.itertuples()):
        if np.isfinite([row.bca_low, row.bca_high]).all():
            ax.plot([row.bca_low, row.bca_high], [i, i], color="#227187")
        ax.scatter(row.mean, i, color="#163947", s=20)
    ax.set_yticks(range(len(forest)), forest.candidate_id, fontsize=7)
    ax.set_xlabel(
        "F1 médio de casamento aproximado com a referência humana; IC 95% BCa"
    )
    ax.set_title("Similaridade lexical com referência humana")
    ax.set_xlim(0, 1)
    fig.tight_layout()
    fig.savefig(folder / "human_reference_intervals.png", dpi=180)
    fig.savefig(folder / "human_reference_intervals.svg")
    plt.close(fig)
    semantic_summary = summaries.loc[summaries["mode"] == "semantic"]
    if not semantic_summary.empty:
        metrics = [
            m for m in ["bertscore", "comet"] if m in set(semantic_summary.metric)
        ]
        fig, axes = plt.subplots(
            1, len(metrics), figsize=(8 * len(metrics), 9), squeeze=False
        )
        for ax, metric in zip(axes[0], metrics):
            frame = semantic_summary.loc[semantic_summary.metric == metric].sort_values(
                "mean"
            )
            for i, row in enumerate(frame.itertuples()):
                if np.isfinite([row.bca_low, row.bca_high]).all():
                    ax.plot([row.bca_low, row.bca_high], [i, i], color="#227187")
                ax.scatter(row.mean, i, color="#163947", s=20)
            ax.set_yticks(range(len(frame)), frame.candidate_id, fontsize=7)
            ax.set_xlabel(f"{metric}: média por item e IC 95% BCa")
            ax.set_title("Referência humana em português")
        fig.tight_layout()
        fig.savefig(folder / "semantic_intervals.png", dpi=180)
        fig.savefig(folder / "semantic_intervals.svg")
        plt.close(fig)
    if not tables["composite_sensitivity"].empty:
        fig, ax = plt.subplots(figsize=(11, 7))
        frame = tables["composite_sensitivity"]
        for name, group in frame.loc[frame.population == "ALT_le_8"].groupby(
            "candidate_id"
        ):
            ax.plot(group.bert_weight, group.mean_rank, label=name)
        ax.invert_yaxis()
        ax.set_xlabel("Peso do BERTScore (COMET = 1 − peso)")
        ax.set_ylabel("Posição bootstrap média")
        ax.set_title("Sensibilidade da classificação semântica aos pesos")
        ax.legend(fontsize=6, bbox_to_anchor=(1.01, 1))
        fig.tight_layout()
        fig.savefig(folder / "semantic_weight_sensitivity.png", dpi=180)
        fig.savefig(folder / "semantic_weight_sensitivity.svg")
        plt.close(fig)


def write_reports(
    output: Path,
    corpus: pd.DataFrame,
    pairs: pd.DataFrame,
    tables: dict,
    metadata: dict,
):
    plots(output, tables, metadata)
    human = metadata["human_candidate_id"]
    agg = tables["pairwise_model_means"]
    auto = agg.loc[
        (agg["mode"] == "content")
        & (agg.candidate_a != human)
        & (agg.candidate_b != human)
    ]
    closest = auto.sort_values("fuzzy_f1", ascending=False)
    farthest = auto.sort_values("fuzzy_f1")
    summaries = tables["reference_intervals"]
    main = summaries.loc[
        (summaries["mode"] == "content") & (summaries.metric == "fuzzy_f1")
    ].sort_values("mean", ascending=False)
    ci = tables["corpus_similarity_intervals"]
    comparison = tables["paired_comparisons"]
    tests = (
        comparison.groupby(["mode", "metric"])
        .agg(
            comparisons=("p_holm", "size"),
            significant_holm=("significant_holm", "sum"),
            within_exploratory_margin=("within_exploratory_margin", "sum"),
        )
        .reset_index()
    )
    lexical = pairs.loc[
        (pairs.group == "questions")
        & (pairs["mode"] == "content")
        & (pairs.candidate_a != human)
        & (pairs.candidate_b != human)
    ]
    exact = int((lexical.token_f1 >= 1 - 1e-12).sum())
    order_different = int(
        ((lexical.token_f1 >= 1 - 1e-12) & (lexical.lcs_f1 < 1 - 1e-12)).sum()
    )
    summary = dict(
        status=metadata["status"],
        automatic_candidates=metadata["corpus"]["automatic_candidates"],
        item_pairs=len(lexical),
        normalized_bag_identical_pairs=exact,
        same_words_different_order_pairs=order_different,
        pairwise_fuzzy_mean=float(auto.fuzzy_f1.mean()),
        pairwise_fuzzy_min=float(auto.fuzzy_f1.min()),
        pairwise_fuzzy_max=float(auto.fuzzy_f1.max()),
        pairwise_token_f1_mean=float(auto.token_f1.mean()),
        pairwise_token_f1_min=float(auto.token_f1.min()),
        pairwise_token_f1_max=float(auto.token_f1.max()),
        nearest_pair=closest.iloc[0][
            ["candidate_a", "candidate_b", "fuzzy_f1"]
        ].to_dict(),
        farthest_pair=farthest.iloc[0][
            ["candidate_a", "candidate_b", "fuzzy_f1"]
        ].to_dict(),
    )
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2)
    )
    qualitative = tables["qualitative_differences"]
    differences = qualitative.loc[
        (qualitative.candidate_a != human) & (qualitative.candidate_b != human)
    ].sort_values("fuzzy_f1")
    selected = differences.drop_duplicates("unit_id").head(8)
    parts = [
        "# Sensibilidade e semelhança das traduções do CHYPS-V",
        "",
        f"Estado desta execução: **{metadata['status']}**. Protocolo: `{metadata['protocol']}`.",
        "",
        "## O que foi medido",
        "",
        f"{metadata['corpus']['automatic_candidates']} candidatas automáticas; 20 itens alinhados; referência humana excluída dos rankings. "
        "Cada comparação entre duas candidatas preserva o mesmo item. O bloco de instruções é complementar e descritivo.",
        "",
        "Os scores lexicais quantificam palavras e estrutura compartilhadas. Não validam equivalência semântica ou clínica. "
        "A análise não assume que as traduções sejam equivalentes nem que exista um vencedor.",
        "",
        "## Síntese da semelhança entre traduções automáticas",
        "",
        f"Foram avaliados {len(auto)} pares de candidatas em {len(lexical)} pares de itens. "
        f"O F1 médio de palavras compartilhadas foi {summary['pairwise_token_f1_mean']:.4f}; "
        f"o casamento aproximado elevou a média para {summary['pairwise_fuzzy_mean']:.4f}. "
        f"Entre pares de candidatas, o F1 aproximado variou de {summary['pairwise_fuzzy_min']:.4f} a {summary['pairwise_fuzzy_max']:.4f}.",
        "",
        f"Em {exact} pares de itens, o multiconjunto de palavras de conteúdo foi idêntico após normalização; "
        f"{order_different} desses pares tinham ordem diferente. Esses números não se referem a igualdade literal dos arquivos.",
        "",
        "ICs abaixo reamostram as 20 perguntas, após calcular a semelhança média dos pares dentro de cada pergunta. "
        "Os milhares de pares não foram tratados como observações independentes.",
        "",
        markdown_table(ci),
        "",
        "### Pares mais semelhantes",
        "",
        markdown_table(
            closest,
            ["candidate_a", "candidate_b", "token_f1", "fuzzy_f1", "lcs_f1"],
            10,
        ),
        "",
        "### Pares menos semelhantes",
        "",
        markdown_table(
            farthest,
            ["candidate_a", "candidate_b", "token_f1", "fuzzy_f1", "lcs_f1"],
            10,
        ),
        "",
        "## Comparação lexical com a referência humana",
        "",
        markdown_table(
            main, ["candidate_id", "mean", "bca_low", "bca_high", "bca_status"]
        ),
        "",
        "## Diferenças estatísticas e tolerância exploratória",
        "",
        "Testes bilaterais de randomização pareada, com Holm aplicado a todos os pares de candidatas separadamente em cada métrica/configuração. "
        "A validade pressupõe permutabilidade de rótulos dentro dos itens. Os ICs BCa são marginais, não simultâneos. "
        "Resultados em diferentes métricas constituem análises exploratórias adicionais, sem correção conjunta entre métricas.",
        "",
        f"A coluna de tolerância indica se o IC 90% da diferença cabe em ±{metadata['exploratory_margin']}; "
        "é uma análise exploratória, sem margem validada de equivalência, sem ajuste de multiplicidade para equivalência. "
        "Não rejeitar igualdade não comprova equivalência.",
        "",
        markdown_table(tests),
        "",
        "## Sensibilidade e agrupamento",
        "",
        "Foram comparadas normalização superficial, remoção conservadora de palavras funcionais e radicalização portuguesa; "
        "a negação e os modificadores de intensidade são preservados. O casamento aproximado usa atribuição ótima um-a-um "
        "com similaridade de grafia ≥0,85, e sensibilidades de 0,75 e 0,95. Não interpreta sinônimos.",
        "",
        "A subsequência comum mais longa permite palavras intercaladas, preservando a ordem relativa. "
        "O F1 de palavras ignora ordem; bigramas, distância de edição e TF-IDF de caracteres complementam essa informação. "
        "O IDF é calculado separadamente por item, usando todas as versões, inclusive a humana.",
        "",
        "Os arquivos de saída incluem exclusão de um item por vez, exclusão de subescalas, bootstrap estratificado "
        "por subescala (percentil, cinco itens por estrato), estabilidade de posições com desempate fracionário e correlações entre métricas. "
        "O dendrograma é descritivo, com ligação média; não representa grupos estatisticamente comprovados.",
        "",
        "![Semelhança entre versões](figures/pairwise_similarity.png)",
        "",
        "![Agrupamento lexical](figures/lexical_clustering.png)",
        "",
        "![Intervalos com referência humana](figures/human_reference_intervals.png)",
        "",
        "## Avaliação semântica",
        "",
    ]
    for name, status in metadata["semantic"].items():
        parts.append(
            f"- **{name}**: {status['status']}. "
            + status.get(
                "error",
                f"Modelo: {status.get('model', '')}; revisão: {status.get('revision', '')}.",
            )
        )
    semantic_summary = summaries.loc[summaries["mode"] == "semantic"]
    if not semantic_summary.empty:
        for metric in semantic_summary.metric.unique():
            frame = semantic_summary.loc[semantic_summary.metric == metric].sort_values(
                "mean", ascending=False
            )
            parts += [
                "",
                f"### {metric}: média por pergunta e IC 95% BCa",
                "",
                markdown_table(
                    frame, ["candidate_id", "mean", "bca_low", "bca_high", "bca_status"]
                ),
            ]
        parts += ["", "![Intervalos semânticos](figures/semantic_intervals.png)", ""]
    if "semantic_corpus_similarity_intervals" in tables:
        parts += [
            "",
            "### Semelhança semântica direta entre as candidatas automáticas",
            "",
            "BERTScore também foi calculado entre os pares de traduções portuguesas do mesmo item. "
            "COMET permanece uma avaliação de qualidade com referência humana, não uma distância entre duas candidatas.",
            "",
            markdown_table(tables["semantic_corpus_similarity_intervals"]),
        ]
    if not tables["composite_sensitivity"].empty:
        frame = tables["composite_sensitivity"]
        mid = frame.loc[
            np.isclose(frame.bert_weight, 0.5) & (frame.population == "ALT_le_8")
        ].sort_values("mean", ascending=False)
        parts += [
            "",
            "### Pontuação composta: pesos iguais, candidatas elegíveis ALT ≤8",
            "",
            markdown_table(
                mid,
                [
                    "candidate_id",
                    "mean",
                    "mean_rank",
                    "rank_p025",
                    "rank_p975",
                    "first_place_share",
                ],
            ),
            "",
            "A participação no primeiro lugar é uma frequência de reamostragem condicionada a estes itens e métricas, "
            "não uma probabilidade de superioridade geral.",
            "",
            "![Sensibilidade aos pesos](figures/semantic_weight_sensitivity.png)",
            "",
        ]
    parts += [
        "",
        "Scores semânticos ausentes não foram substituídos por scores lexicais. "
        "Quando ambas as métricas estão disponíveis, os pesos BERTScore/COMET são variados de 0 a 1 em passos de 0,05, "
        "com reamostragem conjunta e ranking de todas as candidatas e das elegíveis ALT ≤8. "
        "A fórmula NeoBERTugues preserva a variante de casamento de cossenos do estudo; a exclusão de tokens especiais é uma sensibilidade separada.",
        "",
        "## Diferenças para revisão qualitativa",
        "",
        "Exemplos selecionados por baixa similaridade lexical, um por item. Substituições e sinalizadores de negação/intensidade "
        "sugerem trechos para revisão humana; não são classificações automáticas de erro de tradução.",
        "",
    ]
    for r in selected.itertuples():
        parts.extend(
            [
                f"### {r.unit_id}: {r.candidate_a} / {r.candidate_b}",
                "",
                f"- A: {r.text_a}",
                f"- B: {r.text_b}",
                f"- Palavras somente em A: {r.only_a_words}",
                f"- Palavras somente em B: {r.only_b_words}",
                "",
            ]
        )
    parts += [
        "## O que os resultados sustentam",
        "",
        "As medidas mostram convergência geral e diferenças localizadas. Um score lexical elevado pode "
        "coexistir com uma mudança de negação, intensidade ou de conectivo, como 'ou' versus 'e'. "
        "A avaliação por item e a revisão dos trechos preservam essas diferenças para interpretação especializada.",
        "",
    ]
    if "semantic_corpus_similarity_intervals" in tables:
        semantic_ci = (
            tables["semantic_corpus_similarity_intervals"]
            .set_index("metric")
            .loc["bertscore"]
        )
        parts += [
            f"A semelhança contextual direta entre as candidatas teve BERTScore médio {semantic_ci['mean']:.4f}, "
            f"IC 95% BCa [{semantic_ci.bca_low:.4f}; {semantic_ci.bca_high:.4f}]. "
            "Esse valor depende do encoder e da fórmula, sem interpretação como percentual de correção.",
            "",
        ]
    if not tables["composite_sensitivity"].empty:
        mid = tables["composite_sensitivity"]
        mid = mid.loc[
            (mid.population == "ALT_le_8") & np.isclose(mid.bert_weight, 0.5)
        ].sort_values("mean", ascending=False)
        winner, runner = mid.candidate_id.iloc[:2]
        comparison_row = comparison.loc[
            (comparison.metric == "composite_050")
            & (
                (
                    (comparison.candidate_a == winner)
                    & (comparison.candidate_b == runner)
                )
                | (
                    (comparison.candidate_a == runner)
                    & (comparison.candidate_b == winner)
                )
            )
        ]
        if not comparison_row.empty:
            r = comparison_row.iloc[0]
            sign = 1 if r.candidate_a == winner else -1
            low, high = (
                (r.bca_low, r.bca_high) if sign == 1 else (-r.bca_high, -r.bca_low)
            )
            parts += [
                f"Com pesos iguais e ALT ≤8, as maiores médias foram {winner} e {runner}. "
                f"A diferença pareada foi {sign * r['mean']:.5f}, IC 95% BCa [{low:.5f}; {high:.5f}], "
                f"p ajustado por Holm {r.p_holm:.4f}. "
                + (
                    "O intervalo inclui zero: esta comparação não estabelece uma vantagem robusta do primeiro colocado."
                    if low <= 0 <= high
                    else "O intervalo marginal exclui zero; a inferência conjunta deve considerar o p ajustado."
                ),
                "",
            ]
    parts += [
        "Não rejeitar diferenças em determinados pares não demonstra equivalência; outros pares apresentaram "
        "diferenças detectáveis. A decisão sobre relevância substantiva requer uma tolerância validada e revisão "
        "linguística e clínica. O protocolo novo usa referência humana, médias por item e um checkpoint fixado, "
        "portanto seus valores absolutos não devem ser interpretados como melhora numérica sobre os scores publicados.",
        "",
        "## Referência e limitações",
        "",
    ]
    parts += [f"- {x}" for x in metadata["corpus"]["reference_review"]]
    parts += [f"- {x}" for x in metadata["limitations"]]
    parts += [
        "",
        "## Reprodutibilidade",
        "",
        f"Semente {metadata['seed']}; {metadata['resamples']} réplicas bootstrap; {metadata['permutations']} randomizações. "
        "`metadata.json` registra hashes dos textos, versões de dependências, parâmetros e estado de cada métrica. "
        "`checksums.json` registra os artefatos. Os resultados publicados anteriores permanecem separados.",
        "",
        "Consulte `report.html` para explorar palavras comuns/diferentes e trocar os pares e itens. "
        "As figuras também estão disponíveis em SVG.",
        "",
        "Referências: Efron (1987), doi:10.1080/01621459.1987.10478410; "
        "Koehn (2004), https://aclanthology.org/W04-3250/; Dror et al. (2018), https://aclanthology.org/P18-1128/.",
    ]
    (output / "report.md").write_text("\n".join(parts), encoding="utf-8")
    payload = dict(
        summary=summary,
        metadata=metadata,
        segments=corpus.loc[
            corpus.group == "questions",
            ["candidate_id", "unit_id", "source", "translation"],
        ].to_dict("records"),
        pair_means=agg.to_dict("records"),
        pair_items=pairs.loc[
            (pairs.group == "questions") & (pairs["mode"] == "content"),
            [
                "unit_id",
                "candidate_a",
                "candidate_b",
                "jaccard",
                "fuzzy_f1",
                "token_f1",
                "lcs_f1",
                "char_tfidf_cosine",
            ],
        ].to_dict("records"),
    )
    if "semantic_pairwise_model_means" in tables:
        means = tables["semantic_pairwise_model_means"].copy()
        means["mode"] = "semantic"
        payload["pair_means"].extend(means.to_dict("records"))
        lookup = {
            (r.unit_id, r.candidate_a, r.candidate_b): r.bertscore
            for r in tables["semantic_pairwise_item_scores"].itertuples()
        }
        for row in payload["pair_items"]:
            row["bertscore"] = lookup[
                (row["unit_id"], row["candidate_a"], row["candidate_b"])
            ]
    template = Path(__file__).with_name("report_template.html").read_text()
    data = json.dumps(payload, ensure_ascii=False, allow_nan=False).replace(
        "<", "\\u003c"
    )
    (output / "report.html").write_text(
        template.replace("__REPORT_DATA__", data), encoding="utf-8"
    )
