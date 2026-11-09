# Translation similarity and sensitivity analysis

This workflow evaluates how strongly the translations agree, which differences
deserve review, and how sensitive rankings are to the composition of the
questionnaire and the scoring choices. It does not assume equivalence or a winner.

The original published CSVs and their evaluation protocol are preserved. New
outputs live in a separate, newly created directory under `results/sensitivity/`.

## Protocol

- Source: original English questionnaire.
- Reference: existing human Portuguese translation, preserved verbatim.
- Candidates: the other 24 translations. The reference never competes with itself.
- Primary unit: each of the 20 numbered questions, aligned across all versions.
- Complement: the complete introductory instructions, as one descriptive block.
  Repeated instructions and response labels are not treated as independent samples.
- Primary estimand: unweighted mean of item-level scores. This differs from
  scoring the entire concatenated document, as in the published pipeline.
- Eligibility: retain the published ALT ≤8 filter for a separate ranking of
  eligible automatic translations. No readability values are resampled.

The reference contains apparent typos (`poque`, `ach oas`) and wording that warrants
expert review (`cortinas` in a driving context). These are recorded in the corpus
audit, not silently edited. A human reference is a measurement choice, not proof
of perfect translation or independent clinical validation.

## Installation

Run from `cardiff-translation/` with Python 3.12. A small lexical/inference
environment can be reproduced without model downloads:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-sensitivity.txt
```

For the full project, `uv sync --frozen` uses `pyproject.toml` and `uv.lock`.
The default Linux PyTorch distribution includes GPU dependencies. On a CPU-only
machine, the following smaller environment was used for this analysis:

```bash
uv pip install --python .venv/bin/python torch==2.10.0 \
  --index-url https://download.pytorch.org/whl/cpu
uv pip install --python .venv/bin/python \
  transformers==4.57.6 unbabel-comet==2.2.7 setuptools==69.5.1
```

Transformers was updated from the repository's 4.40 requirement because the
currently published NeoBERTugues checkpoint uses ModernBERT and a newer tokenizer
format, which 4.40 cannot load. The new protocol records the exact checkpoint
revision, dependency versions, tokenizer backend, and attention implementation.
It does not claim byte-for-byte reproduction of an unpinned historical checkpoint.

Hugging Face downloads require `huggingface.co` and the HTTPS artifact CDN to
which it redirects (observed: `us.aws.cdn.hf.co`). Use the environment network
settings to allow required destinations. Do not disable TLS or checksum checks.
Public model access does not normally require a token.

## Run

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 \
  .venv/bin/python scripts/analyze_sensitivity.py \
  --output results/sensitivity/my-run \
  --resamples 10000 --permutations 10000 --seed 2026
```

The output directory must not already exist. This protects previous runs.
Model caches and the Matplotlib font cache use ignored `.cache/` paths.

The default attempts both semantic models and completes independent analyses
even if a download fails. Exit status **2** means a partial analysis; check
`metadata.json`. Exit status zero with `--semantic off` means an explicitly
requested lexical analysis, not successful semantic scoring:

```bash
.venv/bin/python scripts/analyze_sensitivity.py \
  --semantic off --output results/sensitivity/lexical-run
```

## Measures

| Measure | What it captures | Important limitation |
| --- | --- | --- |
| Common/unique words | Intersection and differences of vocabularies | Word presence ignores order and frequency |
| Jaccard and Dice | Set overlap | Different sets can still express the same meaning |
| Token F1 | Multiset overlap, including repeated words | Insensitive to word order |
| Approximate token F1 | Maximum-weight one-to-one spelling matches | Not synonym matching; thresholds 0.75, 0.85, 0.95 |
| LCS F1 / ROUGE-L-style overlap | Longest common subsequence, allowing interleaved words | Maintains relative order; not semantic paraphrase recognition |
| Token edit similarity | Insertions, deletions and substitutions | Word order affects the result |
| Bigram Jaccard | Local phrase order | Sensitive to small wording changes |
| Word TF-IDF cosine | Weighted unigram/bigram overlap | IDF is descriptive, fitted across versions within each item |
| Character TF-IDF cosine | Partial spelling and morphology | Orthographic similarity is not semantic equivalence |
| NeoBERTugues cosine-matching F1 | Contextual token representations, last-layer matching | Custom BERTScore variant; special-token exclusion reported separately |
| COMET-22 | Source/candidate/human-reference translation quality | Model calibration is not questionnaire validation |

Lexical comparisons use three explicitly separated normalization modes: surface
words, removal of a conservative function-word list, and Portuguese Snowball
stems after function-word removal. Negation and intensity modifiers are retained;
approximate matching requires exact identity for protected modifiers. The exact
stop list and installed stemmer version are included in the metadata.

## Statistical and sensitivity analyses

1. **Paired BCa 95% intervals:** each candidate's mean and every pairwise difference.
   The same sampled item IDs are used across candidates and metrics. The mean BCa
   calculation is checked against SciPy. Constant/degenerate cases are explicitly
   labeled, not silently replaced with another interval.
2. **Percentile comparison:** reported alongside BCa to expose method dependence.
3. **Paired randomization:** two-sided sign randomization with a plus-one
   correction; 10,000 draws, preserving item pairing. It assumes within-item
   exchangeability of candidate labels. Holm adjusts the 276 candidate pairs
   separately within each metric and normalization configuration. It does not
   correct across all exploratory analyses.
4. **Exploratory tolerance:** whether a marginal 90% BCa interval of a difference
   lies inside ±0.01. The tolerance is configurable and not clinically validated.
   This is not an adjusted or confirmatory claim of practical equivalence.
5. **Item influence:** leave-one-question-out means and rank changes.
6. **Subscales:** means within each domain, leave-one-domain-out means, and a
   stratified percentile bootstrap preserving five items per domain. Four domains
   do not provide enough clusters for strong cluster-bootstrap claims.
7. **Ranking stability:** average bootstrap ranks, rank quantiles, fractional
   first-place shares for ties, all candidates and ALT-eligible candidates.
8. **Metric agreement:** Spearman and Kendall rank correlations, descriptive only.
9. **Composite weights:** when both semantic metrics are available, vary BERTScore
   weight from 0 to 1 by 0.05, with COMET weight `1-w`; resample the two together.
10. **Orthographic choices:** stopword/stemming modes and fuzzy thresholds remain
    separate, making normalization effects visible.
11. **Qualitative review:** exact shared/exclusive words, sequence edits, modifier
    differences, word frequencies by item and candidate, and examples selected
    reproducibly from the most lexically divergent pairs.
12. **Corpus similarity:** average all distinct automatic-system pairs within each
    question, then bootstrap the 20 question means. The thousands of correlated
    pairs are never treated as independent observations.

BERTScore is also computed directly for every pair of Portuguese translations
of the same item, separating semantic similarity between candidates from COMET
quality differences against the fixed human reference. The equal-weight semantic
composite receives its own paired intervals and comparisons. Exploratory
tolerances of 0.005, 0.01, 0.02 and 0.05 are tabulated separately.

The corpus is a fixed instrument, not a random sample of general text. Intervals
describe item-composition stability under the resampling model. They do not
capture uncertainty from fresh translation generations, reference selection or
clinical adaptation, nor guarantee frequentist coverage outside this instrument.
High lexical overlap can coexist with an important negation or intensity change.
Nonsignificance is not equivalence; statistical significance is not clinical
importance. The exploratory dendrogram does not establish significant clusters.

## Outputs

`report.html` is a self-contained interactive visualization with no external
JavaScript or CDN: select versions and an item, inspect shared/exclusive words,
and click a heatmap cell to compare that pair. The detailed Markdown and CSV links
refer to companion files in the same output directory.

`report.md` records findings and limitations. `figures/` contains exportable PNG
and SVG plots. CSV files contain aligned text, item scores, model-pair means,
intervals, randomization results, rank stability, item/subscale influence,
normalization choices, composite weights, vocabulary frequencies and word edits.

`metadata.json` records input hashes, model revisions, versions, parameters and
completion status per metric. `checksums.json` verifies output artifacts.
Missing semantic scores remain missing; lexical proxies are never relabeled as
BERTScore or COMET. Original files under the published result directories are
not overwritten.

## Validation

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest discover -s tests -v
```

Tests exercise real-corpus alignment, rejected misalignments, negation retention,
one-to-one word matching, order sensitivity, SciPy agreement, pairing, degenerate
samples, Holm correction, stratum sizes and tied ranks. Full-run validation also
checks report rendering and output checksums; semantic downloads and predictions
are reported separately from dependency-free tests.

To verify the downloaded model weights against their official Hugging Face LFS
SHA-256 values at the exact revisions recorded in a complete run:

```bash
.venv/bin/python scripts/verify_sensitivity_artifacts.py results/sensitivity/my-run
```

This writes `model_integrity.json` and refreshes the output checksum manifest.

## References

- Efron (1987), Better Bootstrap Confidence Intervals. doi:10.1080/01621459.1987.10478410.
- Koehn (2004), Statistical Significance Tests for Machine Translation Evaluation.
  https://aclanthology.org/W04-3250/
- Dror et al. (2018), The Hitchhiker's Guide to Testing Statistical Significance in NLP.
  https://aclanthology.org/P18-1128/
- Zhang et al. (2020), BERTScore. https://arxiv.org/abs/1904.09675
- Rei et al. (2020), COMET. https://aclanthology.org/2020.emnlp-main.213/
- Glushkova et al. (2021), Uncertainty-Aware Machine Translation Evaluation.
  https://aclanthology.org/2021.findings-emnlp.330/

## Explanatory documentation and questionnaire usability

See the [Portuguese explanation](SENSITIVITY_ANALYSIS_EXPLAINED_PT.md) for the
methodological rationale and [questionnaire mapping](questionnaire/MAPPING.md)
for the application/export contract. [Usability results](../results/usability/initial-cohort/report.md)
use participant-level aggregated outcomes under a separate protocol. No response
exports or individual records may be published.
