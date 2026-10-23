"""Reproducible lexical, semantic, inferential and qualitative analyses."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, rankdata, spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer

from .corpus import SUBSCALES, load_corpus
from .inference import (
    bootstrap_indices,
    mean_interval,
    pairwise_inference,
    ranking_stability,
)
from .lexical import MODES, STOPWORDS, compare, tokens, word_differences

LEXICAL_METRICS = [
    "jaccard",
    "dice",
    "token_f1",
    "fuzzy_f1",
    "lcs_f1",
    "edit_similarity",
    "bigram_jaccard",
    "word_tfidf_cosine",
    "char_tfidf_cosine",
]
INFERENCE_METRICS = ["jaccard", "token_f1", "fuzzy_f1", "lcs_f1", "char_tfidf_cosine"]


def lexical_scores(corpus: pd.DataFrame) -> pd.DataFrame:
    records = []
    for (group, unit), frame in corpus.groupby(["group", "unit_id"], sort=True):
        frame = frame.sort_values("candidate_id").reset_index(drop=True)
        text = frame.translation.tolist()
        names = frame.candidate_id.tolist()
        pairs = list(combinations(range(len(frame)), 2))
        # IDF fitted within this aligned unit across all versions, including human.
        for mode in MODES:
            words = [tokens(t, mode) for t in text]
            joined = [" ".join(w) for w in words]
            word_vectors = TfidfVectorizer(
                tokenizer=str.split,
                token_pattern=None,
                lowercase=False,
                ngram_range=(1, 2),
            ).fit_transform(joined)
            char_vectors = TfidfVectorizer(
                analyzer="char_wb", ngram_range=(3, 5), lowercase=False
            ).fit_transform(joined)
            word_cosine = (word_vectors @ word_vectors.T).toarray()
            char_cosine = (char_vectors @ char_vectors.T).toarray()
            for a, b in pairs:
                metrics = compare(words[a], words[b])
                # Explicit spelling-threshold sensitivity; no synonym dictionary.
                if mode == "content" and group == "questions":
                    metrics["fuzzy_f1_075"] = compare(words[a], words[b], 0.75)[
                        "fuzzy_f1"
                    ]
                    metrics["fuzzy_f1_095"] = compare(words[a], words[b], 0.95)[
                        "fuzzy_f1"
                    ]
                records.append(
                    dict(
                        group=group,
                        unit_id=unit,
                        subscale=frame.subscale.iloc[0],
                        mode=mode,
                        candidate_a=names[a],
                        candidate_b=names[b],
                        **metrics,
                        word_tfidf_cosine=float(word_cosine[a, b]),
                        char_tfidf_cosine=float(char_cosine[a, b]),
                    )
                )
    return pd.DataFrame(records)


def reference_scores(pair_scores: pd.DataFrame, human_id: str) -> pd.DataFrame:
    scores = pair_scores.loc[
        (pair_scores.candidate_a == human_id) | (pair_scores.candidate_b == human_id)
    ].copy()
    scores["candidate_id"] = np.where(
        scores.candidate_a == human_id, scores.candidate_b, scores.candidate_a
    )
    return scores


def analyze_reference(
    scores: pd.DataFrame,
    resamples: int,
    seed: int,
    permutations: int,
    eligible: set[str],
    margin: float,
):
    summaries, comparisons, rankings, influence, subgroup, stratified = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for mode, frame in scores.loc[scores.group == "questions"].groupby("mode"):
        metrics = INFERENCE_METRICS if mode == "content" else ["token_f1", "fuzzy_f1"]
        if mode == "semantic":
            metrics = [
                m
                for m in ["bertscore", "bertscore_no_special", "comet", "composite_050"]
                if m in frame
            ]
        for metric in metrics:
            if metric not in frame or frame[metric].isna().all():
                continue
            matrix = (
                frame.pivot(index="unit_id", columns="candidate_id", values=metric)
                .sort_index()
                .sort_index(axis=1)
            )
            if matrix.shape[0] != 20 or matrix.isna().any().any():
                raise ValueError(f"Unbalanced candidate/item panel for {mode}/{metric}")
            indices = bootstrap_indices(len(matrix), resamples, seed)
            for candidate in matrix:
                summaries.append(
                    dict(
                        mode=mode,
                        metric=metric,
                        candidate_id=candidate,
                        **mean_interval(matrix[candidate], indices),
                    )
                )
            ranks = ranking_stability(matrix, indices)
            ranks["mode"], ranks["metric"], ranks["population"] = (
                mode,
                metric,
                "all_automatic",
            )
            rankings.extend(ranks.to_dict("records"))
            chosen = [c for c in matrix if c in eligible]
            if chosen:
                ranks = ranking_stability(matrix[chosen], indices)
                ranks["mode"], ranks["metric"], ranks["population"] = (
                    mode,
                    metric,
                    "ALT_le_8",
                )
                rankings.extend(ranks.to_dict("records"))
            pairwise = pairwise_inference(
                matrix, indices, seed + 1, permutations, margin
            )
            pairwise["mode"], pairwise["metric"] = mode, metric
            comparisons.extend(pairwise.to_dict("records"))
            full = matrix.mean()
            base_ranks = rankdata(-full)
            for unit in matrix.index:
                reduced = matrix.drop(unit).mean()
                for candidate in matrix:
                    influence.append(
                        dict(
                            mode=mode,
                            metric=metric,
                            removed_unit=unit,
                            candidate_id=candidate,
                            mean_change=float(reduced[candidate] - full[candidate]),
                            rank_change=float(
                                rankdata(-reduced)[matrix.columns.get_loc(candidate)]
                                - base_ranks[matrix.columns.get_loc(candidate)]
                            ),
                        )
                    )
            labels = [
                next(k for k, ids in SUBSCALES.items() if int(u[1:]) in ids)
                for u in matrix.index
            ]
            strat_indices = bootstrap_indices(len(matrix), resamples, seed, labels)
            for candidate in matrix:
                draws = matrix[candidate].to_numpy()[strat_indices].mean(axis=1)
                lo, hi = np.quantile(draws, [0.025, 0.975])
                stratified.append(
                    dict(
                        mode=mode,
                        metric=metric,
                        candidate_id=candidate,
                        mean=float(full[candidate]),
                        percentile_low=float(lo),
                        percentile_high=float(hi),
                        method="percentile_stratified_by_subscale_fixed_5_items_each",
                    )
                )
            for subscale in SUBSCALES:
                mask = np.array(labels) == subscale
                for candidate in matrix:
                    subgroup.append(
                        dict(
                            mode=mode,
                            metric=metric,
                            subscale=subscale,
                            candidate_id=candidate,
                            within_subscale_mean=float(
                                matrix.loc[mask, candidate].mean()
                            ),
                            without_subscale_mean=float(
                                matrix.loc[~mask, candidate].mean()
                            ),
                        )
                    )
    return {
        "reference_intervals": pd.DataFrame(summaries),
        "paired_comparisons": pd.DataFrame(comparisons),
        "rank_stability": pd.DataFrame(rankings),
        "leave_one_item_out": pd.DataFrame(influence),
        "subscale_sensitivity": pd.DataFrame(subgroup),
        "stratified_intervals": pd.DataFrame(stratified),
    }


def qualitative_differences(
    corpus: pd.DataFrame, pairs: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    content = pairs.loc[(pairs.group == "questions") & (pairs["mode"] == "content")]
    lookup = corpus.set_index(["unit_id", "candidate_id"]).translation.to_dict()
    rows, variants = [], []
    for r in content.itertuples():
        a, b = lookup[(r.unit_id, r.candidate_a)], lookup[(r.unit_id, r.candidate_b)]
        d = word_differences(a, b)
        rows.append(
            dict(
                unit_id=r.unit_id,
                candidate_a=r.candidate_a,
                candidate_b=r.candidate_b,
                token_f1=r.token_f1,
                fuzzy_f1=r.fuzzy_f1,
                text_a=a,
                text_b=b,
                shared_words=" | ".join(d["shared_words"]),
                only_a_words=" | ".join(d["only_a_words"]),
                only_b_words=" | ".join(d["only_b_words"]),
                modifier_difference=d["modifiers_a"] != d["modifiers_b"],
                edits=json.dumps(d["edits"], ensure_ascii=False),
            )
        )
    for unit, frame in corpus.loc[corpus.group == "questions"].groupby("unit_id"):
        documents = [set(tokens(s, "content")) for s in frame.translation]
        vocabulary = sorted(set.union(*documents))
        for word in vocabulary:
            users = [
                r.candidate_id
                for r in frame.itertuples()
                if word in tokens(r.translation, "content")
            ]
            variants.append(
                dict(
                    unit_id=unit,
                    word=word,
                    document_frequency=len(users),
                    total_versions=len(frame),
                    candidates=" | ".join(users),
                )
            )
    return pd.DataFrame(rows), pd.DataFrame(variants)


def composite_sensitivity(
    semantic: pd.DataFrame, eligible: set[str], resamples: int, seed: int
):
    if not {"bertscore", "comet"}.issubset(semantic.columns):
        return pd.DataFrame()
    frame = semantic.loc[semantic.group == "questions"]
    bert = (
        frame.pivot(index="unit_id", columns="candidate_id", values="bertscore")
        .sort_index()
        .sort_index(axis=1)
    )
    comet = frame.pivot(
        index="unit_id", columns="candidate_id", values="comet"
    ).reindex_like(bert)
    indices = bootstrap_indices(len(bert), resamples, seed)
    results = []
    for weight in np.linspace(0, 1, 21):
        combined = weight * bert + (1 - weight) * comet
        for population, cols in [
            ("all_automatic", list(combined)),
            ("ALT_le_8", [c for c in combined if c in eligible]),
        ]:
            if cols:
                ranks = ranking_stability(combined[cols], indices)
                ranks["bert_weight"], ranks["population"] = float(weight), population
                results.extend(ranks.to_dict("records"))
    return pd.DataFrame(results)


def run_analysis(
    root: Path,
    output: Path,
    resamples=10000,
    seed=2026,
    permutations=10000,
    semantic_mode="auto",
    margin=0.01,
) -> dict:
    if resamples < 1000 or permutations < 1000:
        raise ValueError(
            "Use at least 1000 resamples/permutations; published runs use 10000"
        )
    output.mkdir(parents=True, exist_ok=False)
    corpus, audit = load_corpus(root)
    human_id = corpus.loc[corpus.is_reference, "candidate_id"].iloc[0]
    corpus.to_csv(output / "aligned_segments.csv", index=False)
    print(
        f"Validated {audit['candidates']} versions × 20 items; scoring lexical pairs",
        flush=True,
    )
    pairs = lexical_scores(corpus)
    pairs.to_csv(output / "pairwise_item_scores.csv", index=False)
    reference = reference_scores(pairs, human_id)
    semantic = pd.DataFrame()
    semantic_pairs = pd.DataFrame()
    if semantic_mode != "off":
        print("Attempting human-reference BERTScore and COMET", flush=True)
        try:
            from .semantic import score_semantics

            semantic, statuses, semantic_pairs = score_semantics(
                corpus, root / ".cache/sensitivity"
            )
        except Exception as exc:
            statuses = {
                name: dict(status="blocked", error=f"{type(exc).__name__}: {exc}")
                for name in ["bertscore", "comet"]
            }
        if not semantic.empty:
            if {"bertscore", "comet"}.issubset(semantic.columns):
                semantic["composite_050"] = (semantic.bertscore + semantic.comet) / 2
            semantic.to_csv(output / "semantic_item_scores.csv", index=False)
            semantic["mode"] = "semantic"
            reference = pd.concat([reference, semantic], ignore_index=True)
    else:
        statuses = {
            name: dict(status="not_requested") for name in ["bertscore", "comet"]
        }
    reference.to_csv(output / "reference_item_scores.csv", index=False)
    # Use published readability only for eligibility, never as segment scores.
    published_path = root / "results/questions-only/original/analysis_results_alt.csv"
    published = pd.read_csv(published_path)
    published["candidate_id"] = published.model_id.str.removeprefix("CHYPS-V-br20-")
    expected = set(corpus.loc[corpus.group == "questions", "candidate_id"])
    if set(published.candidate_id) != expected:
        raise ValueError("Published eligibility IDs do not match the translation panel")
    eligible = set(
        published.loc[published.final_readability_score <= 8, "candidate_id"]
    ) - {human_id}
    print(
        "Computing paired BCa intervals, permutations and ranking sensitivity",
        flush=True,
    )
    tables = analyze_reference(
        reference, resamples, seed, permutations, eligible, margin
    )
    differences, vocabulary = qualitative_differences(corpus, pairs)
    tables.update(
        qualitative_differences=differences,
        vocabulary_variants=vocabulary,
        composite_sensitivity=composite_sensitivity(
            semantic, eligible, resamples, seed
        ),
    )
    if not semantic_pairs.empty:
        tables["semantic_pairwise_item_scores"] = semantic_pairs
        tables["semantic_pairwise_model_means"] = (
            semantic_pairs.groupby(["candidate_a", "candidate_b"])[
                ["bertscore", "bertscore_no_special"]
            ]
            .mean()
            .reset_index()
        )
        auto_pairs = semantic_pairs.loc[
            (semantic_pairs.candidate_a != human_id)
            & (semantic_pairs.candidate_b != human_id)
        ]
        item_means = (
            auto_pairs.groupby("unit_id")[["bertscore", "bertscore_no_special"]]
            .mean()
            .sort_index()
        )
        tables["semantic_corpus_similarity_intervals"] = pd.DataFrame(
            [
                dict(
                    metric=metric,
                    **mean_interval(
                        item_means[metric], bootstrap_indices(20, resamples, seed)
                    ),
                )
                for metric in item_means
            ]
        )
    if {"bertscore", "comet"}.issubset(semantic.columns):
        new_scores = (
            semantic.loc[semantic.group == "questions"]
            .groupby("candidate_id")[["bertscore", "comet"]]
            .mean()
        )
        previous = published.set_index("candidate_id")[
            ["bertscore", "comet"]
        ].add_prefix("published_")
        protocol_comparison = new_scores.add_prefix("human_item_").join(previous)
        protocol_comparison["published_composite"] = (
            protocol_comparison.published_bertscore
            + protocol_comparison.published_comet
        ) / 2
        protocol_comparison["human_item_composite"] = (
            protocol_comparison.human_item_bertscore
            + protocol_comparison.human_item_comet
        ) / 2
        protocol_comparison["published_rank"] = (
            protocol_comparison.published_composite.rank(ascending=False)
        )
        protocol_comparison["human_item_rank"] = (
            protocol_comparison.human_item_composite.rank(ascending=False)
        )
        tables["protocol_rank_comparison"] = protocol_comparison.reset_index()
    tolerance_rows = []
    for (mode, metric), family in tables["paired_comparisons"].groupby(
        ["mode", "metric"]
    ):
        for tolerance in [0.005, 0.01, 0.02, 0.05]:
            inside = (family.ci90_low > -tolerance) & (family.ci90_high < tolerance)
            tolerance_rows.append(
                dict(
                    mode=mode,
                    metric=metric,
                    exploratory_margin=tolerance,
                    pairs_inside_marginal_ci90=int(inside.sum()),
                    total_pairs=len(family),
                )
            )
    tables["tolerance_sensitivity"] = pd.DataFrame(tolerance_rows)
    # Approximate matching thresholds and stopword/stemming choices remain distinct.
    tables["normalization_sensitivity"] = (
        reference.loc[reference.group == "questions"]
        .groupby(["mode", "candidate_id"])[
            [
                c
                for c in LEXICAL_METRICS + ["fuzzy_f1_075", "fuzzy_f1_095"]
                if c in reference
            ]
        ]
        .mean()
        .reset_index()
    )
    agg = (
        pairs.loc[pairs.group == "questions"]
        .groupby(["mode", "candidate_a", "candidate_b"])[LEXICAL_METRICS]
        .mean()
        .reset_index()
    )
    tables["pairwise_model_means"] = agg
    # Each unit contributes one mean over all distinct system pairs: pairs are not
    # treated as independent observations in the interval calculation.
    automatic = pairs.loc[
        (pairs.group == "questions")
        & (pairs["mode"] == "content")
        & (pairs.candidate_a != human_id)
        & (pairs.candidate_b != human_id)
    ]
    unit_means = automatic.groupby("unit_id")[INFERENCE_METRICS].mean().sort_index()
    indices = bootstrap_indices(len(unit_means), resamples, seed)
    tables["corpus_similarity_intervals"] = pd.DataFrame(
        [
            dict(metric=m, **mean_interval(unit_means[m], indices))
            for m in INFERENCE_METRICS
        ]
    )
    correlation = (
        reference.loc[
            (reference.group == "questions") & (reference["mode"] == "content")
        ]
        .groupby("candidate_id")[INFERENCE_METRICS]
        .mean()
    )
    if not semantic.empty:
        semcols = [c for c in ["bertscore", "comet"] if c in semantic]
        correlation = correlation.join(
            semantic.loc[semantic.group == "questions"]
            .groupby("candidate_id")[semcols]
            .mean()
        )
    tables["metric_rank_correlations"] = pd.DataFrame(
        [
            dict(
                metric_a=a,
                metric_b=b,
                spearman=float(spearmanr(correlation[a], correlation[b]).statistic),
                kendall=float(kendalltau(correlation[a], correlation[b]).statistic),
            )
            for a, b in combinations(correlation.columns, 2)
        ]
    )
    for name, table in tables.items():
        table.to_csv(output / f"{name}.csv", index=False)
    versions = {}
    for package in [
        "numpy",
        "pandas",
        "scipy",
        "scikit-learn",
        "rapidfuzz",
        "snowballstemmer",
        "torch",
        "transformers",
        "unbabel-comet",
    ]:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not_installed"
    metadata = dict(
        protocol="human-reference-item-v1",
        seed=seed,
        resamples=resamples,
        permutations=permutations,
        confidence=0.95,
        status="complete"
        if all(s["status"] == "completed" for s in statuses.values())
        else "lexical_only"
        if semantic_mode == "off"
        else "partial",
        semantic=statuses,
        corpus=audit,
        versions=versions,
        human_candidate_id=human_id,
        eligible_automatic_candidates=sorted(eligible),
        exploratory_margin=margin,
        stopwords=sorted(STOPWORDS),
        inference_family="all automatic pairs separately per mode/metric; Holm p-values",
        estimand="unweighted mean across 20 fixed questionnaire items under item resampling",
        limitations=[
            "Intervals describe item-composition stability, not general-text population coverage.",
            "Failure to reject differences is not equivalence; 0.01 is an exploratory tolerance.",
            "Instruction comparisons are descriptive only (one composite block).",
            "BCa assumes exchangeable items; stratified intervals are percentile, explicitly labeled.",
            "Word similarity, stemming and spelling matching do not establish semantic validity.",
            "The human reference is preserved verbatim, including apparent errors.",
        ],
    )
    hf_root = root / ".cache/huggingface/hub"
    metadata["cached_model_revisions"] = {
        model.name.removeprefix("models--").replace("--", "/"): sorted(
            p.name for p in (model / "snapshots").iterdir()
        )
        for model in sorted(hf_root.glob("models--*"))
        if (model / "snapshots").is_dir()
    }
    (output / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2)
    )
    from .reporting import write_reports

    write_reports(output, corpus, pairs, tables, metadata)
    outputs = {
        str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in output.rglob("*")
        if p.is_file()
    }
    (output / "checksums.json").write_text(json.dumps(outputs, indent=2))
    return metadata
