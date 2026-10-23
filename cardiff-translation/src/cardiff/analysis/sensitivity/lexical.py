"""Complementary word, sequence and character measures; none imply semantic equivalence."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher

import numpy as np
import snowballstemmer
from rapidfuzz.distance import LCSseq, Levenshtein
from scipy.optimize import linear_sum_assignment

# Explicit conservative function-word list; negation and intensity are retained.
# This is an analysis choice, not a claim of an exhaustive Portuguese stop list.
STOPWORDS = frozenset(
    "a o as os um uma uns umas de do da dos das em no na nos nas por pelo pela pelos pelas para com e ou que se eu me meu minha meus minhas ele ela eles elas isso isto esse essa esses essas este esta estes estas ao aos à às é são ser estar quando porque como onde qual quais".split()
)
MODIFIERS = frozenset(
    "não nunca jamais nem sem quase sempre frequentemente ocasionalmente pouco muito muitos muitas tão tanto tanta tãos tantos tantas".split()
)
STEMMER = snowballstemmer.stemmer("portuguese")
MODES = ("surface", "content", "stemmed")


def tokens(text: str, mode: str = "surface") -> list[str]:
    if mode not in MODES:
        raise ValueError(f"Unknown normalization: {mode}")
    words = re.findall(
        r"[^\W\d_]+(?:['’-][^\W\d_]+)*", unicodedata.normalize("NFC", text).casefold()
    )
    if mode != "surface":
        words = [w for w in words if w not in STOPWORDS]
    if mode == "stemmed":
        words = [w if w in MODIFIERS else STEMMER.stemWord(w) for w in words]
    return words


def compare(a: list[str], b: list[str], fuzzy_threshold: float = 0.85) -> dict:
    sa, sb = set(a), set(b)
    ca, cb = Counter(a), Counter(b)
    common = len(sa & sb)
    overlap = sum((ca & cb).values())
    total = len(a) + len(b)
    lcs = LCSseq.similarity(a, b)
    # One-to-one maximum-weight token matching, insensitive to word order.
    # Retain negation/intensity as exact matches only: 'com'/'sem' must not
    # become a soft match merely because their spelling is similar.
    similarities = np.zeros((len(a), len(b)))
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            score = float(Levenshtein.normalized_similarity(x, y))
            if (x in MODIFIERS or y in MODIFIERS) and x != y:
                score = 0.0
            similarities[i, j] = score if score >= fuzzy_threshold else 0.0
    fuzzy_weight = 0.0
    if similarities.size:
        i, j = linear_sum_assignment(similarities, maximize=True)
        fuzzy_weight = float(similarities[i, j].sum())
    bigrams_a, bigrams_b = set(zip(a, a[1:])), set(zip(b, b[1:]))
    return {
        "jaccard": common / len(sa | sb) if sa | sb else 1.0,
        "dice": 2 * common / (len(sa) + len(sb)) if sa or sb else 1.0,
        "token_f1": 2 * overlap / total if total else 1.0,
        "fuzzy_f1": 2 * fuzzy_weight / total if total else 1.0,
        "lcs_f1": 2 * lcs / total if total else 1.0,
        "edit_similarity": float(Levenshtein.normalized_similarity(a, b)),
        "bigram_jaccard": len(bigrams_a & bigrams_b) / len(bigrams_a | bigrams_b)
        if bigrams_a | bigrams_b
        else 1.0,
        "common_unique": common,
        "only_a_unique": len(sa - sb),
        "only_b_unique": len(sb - sa),
        "tokens_a": len(a),
        "tokens_b": len(b),
    }


def word_differences(a: str, b: str) -> dict:
    ta, tb = tokens(a, "content"), tokens(b, "content")
    matcher = SequenceMatcher(a=tokens(a), b=tokens(b), autojunk=False)
    edits = []
    for op, i, j, k, end_b in matcher.get_opcodes():
        if op != "equal":
            edits.append(
                {
                    "operation": op,
                    "a": " ".join(matcher.a[i:j]),
                    "b": " ".join(matcher.b[k:end_b]),
                }
            )
    return {
        "shared_words": sorted(set(ta) & set(tb)),
        "only_a_words": sorted(set(ta) - set(tb)),
        "only_b_words": sorted(set(tb) - set(ta)),
        "modifiers_a": sorted(set(tokens(a)) & MODIFIERS),
        "modifiers_b": sorted(set(tokens(b)) & MODIFIERS),
        "edits": edits,
    }
