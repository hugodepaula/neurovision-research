"""Build manuscript figures and editable exports from the recorded sensitivity run."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscripts/cbnv"
RESULTS = ROOT / "results/sensitivity/human-reference"
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import PercentFormatter  # noqa: E402

BLUE, TEAL, GOLD = "#365e86", "#157f7a", "#b77a32"


def save_figure(fig, name):
    for extension in ["png", "svg", "pdf"]:
        fig.savefig(
            OUT / "figures" / f"{name}.{extension}", dpi=250, bbox_inches="tight"
        )
    plt.close(fig)


def similarity_distributions(human_id):
    lexical = pd.read_csv(RESULTS / "pairwise_model_means.csv")
    lexical = lexical.loc[
        (lexical["mode"] == "content")
        & (lexical.candidate_a != human_id)
        & (lexical.candidate_b != human_id)
    ]
    semantic = pd.read_csv(RESULTS / "semantic_pairwise_model_means.csv")
    semantic = semantic.loc[
        (semantic.candidate_a != human_id) & (semantic.candidate_b != human_id)
    ]
    assert len(lexical) == len(semantic) == 276
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.3))
    panels = [
        (
            lexical.token_f1,
            BLUE,
            "A  Sobreposição lexical",
            "F1 médio de palavras",
            np.linspace(0.50, 1, 17),
        ),
        (
            semantic.bertscore,
            TEAL,
            "B  Similaridade contextual",
            "BERTScore médio (variante NeoBERTugues)",
            np.linspace(0.80, 1, 17),
        ),
    ]
    for ax, (values, color, title, xlabel, bins) in zip(axes, panels):
        ax.hist(values, bins=bins, color=color, edgecolor="white", linewidth=0.7)
        ax.axvline(values.mean(), color="#182e39", linestyle="--", linewidth=1.3)
        ax.set_title(title, loc="left", weight="bold", fontsize=10)
        ax.set_xlabel(xlabel, fontsize=8.5)
        ax.set_ylabel("Número de pares de tradutores", fontsize=8.5)
        ax.text(
            0.04,
            0.94,
            f"276 pares · 20 itens\nMédia = {values.mean():.3f}".replace(".", ","),
            transform=ax.transAxes,
            va="top",
            fontsize=8,
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.92),
        )
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8)
    fig.tight_layout(w_pad=2)
    save_figure(fig, "fig01_similarity_distributions")


def selection_stability():
    weights = pd.read_csv(RESULTS / "composite_sensitivity.csv")
    eligible = weights.loc[weights.population == "ALT_le_8"]
    first = "Deepseek-v3.2-deepthink-25-12-10"
    second = "Grok-4-25-07-25"
    p = eligible.pivot(
        index="bert_weight", columns="candidate_id", values="first_place_share"
    ).sort_index()
    fig, axes = plt.subplots(
        1, 2, figsize=(8.2, 3.3), gridspec_kw={"width_ratios": [1.2, 1]}
    )
    ax = axes[0]
    ax.plot(p.index, p[first], color=TEAL, linewidth=2, label="Deepseek-v3.2")
    ax.plot(p.index, p[second], color=GOLD, linewidth=2, label="Grok-4")
    ax.plot(
        p.index,
        1 - p[first] - p[second],
        color="#89999b",
        linewidth=1,
        linestyle=":",
        label="Outras elegíveis",
    )
    ax.axvline(0.5, color="#89999b", linestyle="--", linewidth=0.8)
    ax.set(
        xlim=(0, 1),
        ylim=(0, 1),
        xlabel="Peso do BERTScore; COMET = 1 − peso",
        ylabel="Frequência de primeiro lugar",
    )
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_title("A  Estabilidade da liderança", loc="left", weight="bold", fontsize=10)
    ax.legend(frameon=False, fontsize=7.5, loc="upper right")
    comparisons = pd.read_csv(RESULTS / "paired_comparisons.csv")
    row = comparisons.loc[
        (comparisons.metric == "composite_050")
        & (comparisons.candidate_a == first)
        & (comparisons.candidate_b == second)
    ].iloc[0]
    ax = axes[1]
    ax.axvline(0, linestyle="--", linewidth=1, color="#7a8c91")
    ax.errorbar(
        row["mean"],
        0,
        xerr=[[row["mean"] - row.bca_low], [row.bca_high - row["mean"]]],
        color=TEAL,
        fmt="o",
        capsize=5,
        linewidth=2,
        markersize=7,
    )
    ax.set(
        xlim=(-0.02, 0.02),
        ylim=(-1, 1),
        yticks=[],
        xlabel="Diferença composta: Deepseek − Grok",
    )
    ax.set_title(
        "B  Comparação com pesos iguais", loc="left", weight="bold", fontsize=10
    )
    label = f"Δ = {row['mean']:.5f}\nIC 95% BCa [{row.bca_low:.5f}; {row.bca_high:.5f}]\np ajustado por Holm = {row.p_holm:.2f}".replace(
        ".", ","
    )
    ax.text(0.5, 0.92, label, transform=ax.transAxes, ha="center", va="top", fontsize=8)
    ax.text(
        0.5,
        0.17,
        "20 itens pareados\nO intervalo inclui zero",
        transform=ax.transAxes,
        ha="center",
        fontsize=8,
    )
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8)
        ax.xaxis.label.set_size(8)
        ax.yaxis.label.set_size(8)
    fig.tight_layout(w_pad=2)
    save_figure(fig, "fig02_selection_stability")


def lexical_choices():
    scores = pd.read_csv(RESULTS / "semantic_item_scores.csv")
    q16 = scores.loc[scores.unit_id == "Q16", "translation"]
    patterns = [
        ("piscantes / piscando / piscam", r"pisc"),
        ("tremeluzentes / tremeluzem", r"tremeluz"),
        ("cintilantes / cintilam", r"cintil"),
        ("tremulantes / tremulam", r"tremul"),
        ("tremem", r"\btremem\b"),
    ]
    counts = [
        sum(bool(re.search(pattern, t, re.I)) for t in q16) for _, pattern in patterns
    ]
    assert counts == [17, 3, 2, 2, 1]
    for item in ["Q06", "Q18"]:
        assert (
            scores.loc[scores.unit_id == item, "translation"]
            .str.contains("estrobosc", case=False)
            .sum()
            == 24
        )
    fig, axes = plt.subplots(
        1, 2, figsize=(8.2, 3.6), gridspec_kw={"width_ratios": [1.15, 1]}
    )
    ax = axes[0]
    ax.axis("off")
    ax.set_title(
        "A  Uma escolha lexical para revisão", loc="left", weight="bold", fontsize=10
    )
    blocks = [
        (0.94, "Original inglês · item 6", "strobing or flashing lights"),
        (0.71, "Referência humana", "luzes pulsando ou piscando"),
        (0.48, "Versão selecionada", "luzes estroboscópicas ou piscantes"),
    ]
    for y, title, phrase in blocks:
        ax.text(0, y, title, weight="bold", fontsize=8.5, va="top")
        ax.text(
            0,
            y - 0.09,
            f"“{phrase}”",
            fontsize=8.5,
            va="top",
            color=TEAL if "selecionada" in title else "#253e46",
        )
    ax.text(
        0,
        0.17,
        "“Estroboscópicas” aparece em 24/24 versões\nautomáticas nos itens 6 e 18.",
        fontsize=8.5,
        va="top",
        bbox=dict(facecolor="#eef5f3", edgecolor="none", pad=5),
    )
    ax = axes[1]
    labels = [x[0] for x in patterns]
    ax.barh(range(len(counts)), counts, color=BLUE, height=0.65)
    ax.set_yticks(range(len(counts)), labels, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 26)
    ax.set_xticks([0, 6, 12, 18, 24])
    ax.set_xlabel("Versões automáticas com cada alternativa", fontsize=8)
    ax.set_title("B  Alternativas no item 16", loc="left", weight="bold", fontsize=10)
    for i, value in enumerate(counts):
        ax.text(value + 0.4, i, str(value), va="center", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=8)
    fig.tight_layout(w_pad=1.8)
    save_figure(fig, "fig03_lexical_choices")
    return dict(
        q06_strobing_versions=24,
        q18_strobing_versions=24,
        q16_patterns={label: count for (label, _), count in zip(patterns, counts)},
        note="Counts are translation versions; alternatives may coexist within a version.",
    )


def export_documents():
    exported = []
    for name in ["abstract_pt", "extended_abstract_pt", "supplementary_figure"]:
        source = OUT / f"{name}.md"
        common = ["pandoc", str(source), "--standalone", f"--resource-path={OUT}"]
        for extension in ["docx", "pdf"]:
            destination = OUT / f"{name}.{extension}"
            command = common + ["-o", str(destination)]
            if extension == "pdf":
                command += [
                    "--pdf-engine=xelatex",
                    "-V",
                    "papersize:a4",
                    "-V",
                    "geometry:margin=2cm",
                    "-V",
                    "fontsize=11pt",
                    "-V",
                    "mainfont=DejaVu Serif",
                    "-V",
                    "sansfont=DejaVu Sans",
                    "-V",
                    "colorlinks=true",
                    "-V",
                    "linkcolor=teal",
                    "-V",
                    "urlcolor=teal",
                ]
            subprocess.run(command, check=True, cwd=OUT, capture_output=True, text=True)
            exported.append(destination.name)
    return exported


def main():
    metadata = json.loads((RESULTS / "metadata.json").read_text())
    if metadata["status"] != "complete":
        raise ValueError(
            "A complete semantic analysis is required before manuscript export"
        )
    plt.rcParams.update(
        {"font.family": "DejaVu Sans", "svg.fonttype": "none", "pdf.fonttype": 42}
    )
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    similarity_distributions(metadata["human_candidate_id"])
    selection_stability()
    lexical = lexical_choices()
    sources = [
        RESULTS / f
        for f in [
            "metadata.json",
            "pairwise_model_means.csv",
            "semantic_pairwise_model_means.csv",
            "paired_comparisons.csv",
            "composite_sensitivity.csv",
            "reference_intervals.csv",
            "semantic_item_scores.csv",
        ]
    ]
    sources += [ROOT / "results/questions-only/original/analysis_results_alt.csv"]
    evidence = dict(
        analysis_protocol=metadata["protocol"],
        input_hashes={
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sources
        },
        lexical_examples=lexical,
        bootstrap_resamples=metadata["resamples"],
        random_seed=metadata["seed"],
        participant_data_source="Previously provided CI-IA expanded abstract; no new participant-level reanalysis",
        previously_reported_participants=dict(
            total=137, comprehension_pass=122, ease_percent_among_included=93.4
        ),
        google_document_access="HTTP 401; contents and template unavailable; no remote edit performed",
    )
    for name in ["abstract_pt", "extended_abstract_pt"]:
        text = (OUT / f"{name}.md").read_text()
        text = re.sub(r"^---.*?---\s*", "", text, flags=re.S)
        evidence[name + "_word_count"] = len(re.findall(r"\S+", text))
    evidence["exports"] = export_documents()
    (OUT / "evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2)
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in evidence.items()
                if k.endswith("word_count") or k == "exports"
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
