"""Tests of alignment, pairing, metric behavior and statistical calculations."""

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import bootstrap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cardiff.analysis.sensitivity.corpus import load_corpus, parse_items  # noqa: E402
from cardiff.analysis.sensitivity.inference import (  # noqa: E402
    bootstrap_indices,
    holm,
    mean_interval,
    pairwise_inference,
    ranking_stability,
)
from cardiff.analysis.sensitivity.lexical import compare, tokens, word_differences  # noqa: E402


class AlignmentTests(unittest.TestCase):
    def test_actual_corpus_is_balanced_and_human_excluded_from_candidates(self):
        frame, audit = load_corpus(ROOT)
        questions = frame.loc[frame.group == "questions"]
        self.assertEqual(len(questions), 500)
        self.assertEqual(len(questions.loc[~questions.is_reference]), 480)
        self.assertEqual(
            questions.groupby("candidate_id").unit_id.nunique().tolist(), [20] * 25
        )
        self.assertTrue(questions.groupby("unit_id").reference.nunique().eq(1).all())
        self.assertEqual(audit["automatic_candidates"], 24)

    def test_invalid_missing_duplicate_and_reordered_items_rejected(self):
        for sequence in [
            list(range(1, 20)),
            [1, 1] + list(range(3, 21)),
            [2, 1] + list(range(3, 21)),
        ]:
            with self.assertRaises(ValueError):
                parse_items("\n".join(f"{i}. text" for i in sequence))


class MetricTests(unittest.TestCase):
    def test_identity_is_one_and_disjoint_is_zero(self):
        for key in [
            "jaccard",
            "dice",
            "token_f1",
            "fuzzy_f1",
            "lcs_f1",
            "edit_similarity",
            "bigram_jaccard",
        ]:
            self.assertAlmostEqual(
                compare(["olhos", "cabeça"], ["olhos", "cabeça"])[key], 1
            )
        self.assertEqual(compare(["abc"], ["xyz"])["token_f1"], 0)

    def test_interleaving_preserves_order_and_reordering_is_distinguished(self):
        a = ["luz", "olhos", "cabeça"]
        b = ["cabeça", "luz", "olhos"]
        metrics = compare(a, b)
        self.assertEqual(metrics["token_f1"], 1)
        self.assertLess(metrics["lcs_f1"], 1)
        self.assertGreater(
            compare(a, ["luz", "forte", "olhos", "e", "cabeça"])["lcs_f1"], 0.7
        )

    def test_approximate_matching_is_one_to_one(self):
        self.assertAlmostEqual(
            compare(["olhos", "olhos"], ["olhos"])["fuzzy_f1"], 2 / 3
        )
        self.assertGreater(
            compare(["desconfortável"], ["desconfortáveis"])["fuzzy_f1"], 0.8
        )

    def test_negation_and_intensity_survive_stopwords_and_stemming(self):
        for mode in ["surface", "content", "stemmed"]:
            self.assertIn("não", tokens("Eu não olho para luzes muito fortes", mode))
            self.assertIn("muito", tokens("Eu não olho para luzes muito fortes", mode))
        self.assertEqual(compare(["nunca"], ["nunca", "quase"])["fuzzy_f1"], 2 / 3)
        self.assertIn("não", word_differences("não olho", "olho")["only_a_words"])


class InferenceTests(unittest.TestCase):
    def test_bca_and_percentile_match_scipy(self):
        x = np.array([0.1, 0.2, 0.2, 0.3, 0.5, 0.6, 0.9, 0.95])
        indices = bootstrap_indices(len(x), 10000, 17)
        actual = mean_interval(x, indices)
        expected = bootstrap(
            (x,),
            np.mean,
            method="BCa",
            n_resamples=10000,
            rng=np.random.default_rng(17),
        )
        np.testing.assert_allclose(
            [actual["bca_low"], actual["bca_high"]], expected.confidence_interval
        )
        percentile = bootstrap(
            (x,),
            np.mean,
            method="percentile",
            n_resamples=10000,
            rng=np.random.default_rng(17),
        )
        np.testing.assert_allclose(
            [actual["percentile_low"], actual["percentile_high"]],
            percentile.confidence_interval,
        )

    def test_constant_sample_is_explicitly_non_estimable(self):
        result = mean_interval(np.ones(20), bootstrap_indices(20, 1000, 3))
        self.assertEqual(result["bca_status"], "constant_sample_not_estimable")
        self.assertTrue(np.isnan(result["bca_low"]))

    def test_pairing_uses_same_item_indices(self):
        rng = np.random.default_rng(42)
        a = rng.normal(0.8, 0.05, 20)
        b = a + rng.normal(0.01, 0.005, 20)
        indices = bootstrap_indices(20, 2000, 13)
        actual = mean_interval(a - b, indices)
        expected = bootstrap(
            (a, b),
            lambda x, y, axis: np.mean(x - y, axis=axis),
            paired=True,
            method="BCa",
            n_resamples=2000,
            rng=np.random.default_rng(13),
        )
        np.testing.assert_allclose(
            [actual["bca_low"], actual["bca_high"]], expected.confidence_interval
        )

    def test_holm_adjustment_and_stratum_sizes(self):
        np.testing.assert_allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
        labels = np.repeat(np.arange(4), 5)
        draws = bootstrap_indices(20, 1000, 8, labels)
        for label in range(4):
            self.assertTrue(np.all(np.sum(labels[draws] == label, axis=1) == 5))

    def test_ranking_splits_tied_first_place(self):
        matrix = pd.DataFrame({"A": [0.5] * 20, "B": [0.5] * 20})
        ranks = ranking_stability(matrix, bootstrap_indices(20, 1000, 4))
        np.testing.assert_allclose(ranks.first_place_share, [0.5, 0.5])

    def test_permutation_result_is_reproducible_and_identical_pair_is_not_significant(
        self,
    ):
        matrix = pd.DataFrame(
            {"A": np.linspace(0.4, 0.8, 20), "B": np.linspace(0.4, 0.8, 20)}
        )
        indices = bootstrap_indices(20, 1000, 3)
        first = pairwise_inference(matrix, indices, 3, permutations=1000)
        second = pairwise_inference(matrix, indices, 3, permutations=1000)
        pd.testing.assert_frame_equal(first, second)
        self.assertEqual(first.p_holm.iloc[0], 1)


if __name__ == "__main__":
    unittest.main()
