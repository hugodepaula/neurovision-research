"""Human-reference semantic scoring with explicit model/version provenance."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import re
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


def public_error(exc: Exception) -> str:
    """Keep diagnostics without persisting expiring signed download queries."""
    message = str(exc)
    message = re.sub(
        r"https?://[^\s'\"<>]+", lambda m: m.group(0).split("?", 1)[0], message
    )
    if "Max retries exceeded with url:" in message:
        hosts = re.findall(r"host='([^']+)'", message)
        return f"{type(exc).__name__}: download failed for {', '.join(sorted(set(hosts)))}; inspect network access."
    return f"{type(exc).__name__}: {message[:1200]}"


def score_semantics(
    corpus: pd.DataFrame, cache_dir: Path
) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """Attempt each metric independently; never substitute lexical scores.

    The NeoBERTugues variant preserves legacy last-layer cosine matching for
    comparability, and separately excludes special tokens as a sensitivity.
    The human translation is a reference, not a competing system.
    """
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    import torch
    from huggingface_hub import model_info
    from huggingface_hub.utils import logging as hub_logging

    hub_logging.set_verbosity_error()

    torch.set_num_threads(2)
    torch.manual_seed(2026)
    data = corpus.loc[~corpus.is_reference].copy().reset_index(drop=True)
    statuses = {}
    pairwise = pd.DataFrame()
    cache_dir.mkdir(parents=True, exist_ok=True)
    key_columns = [
        "candidate_id",
        "unit_id",
        "group",
        "source",
        "reference",
        "translation",
    ]
    recipe = {
        "protocol": "human-reference-semantic-v1",
        "attention": "eager",
        "layer": "last",
        "versions": {
            p: importlib.metadata.version(p)
            for p in ["torch", "transformers", "unbabel-comet"]
        },
    }
    digest = hashlib.sha256(
        (
            data[key_columns].to_json(force_ascii=False)
            + json.dumps(recipe, sort_keys=True)
        ).encode()
    ).hexdigest()
    try:
        from transformers import AutoModel, AutoTokenizer

        model_id = "lorenzocc/NeoBERTugues"
        revision = model_info(model_id).sha
        cache = cache_dir / f"bert-pairs-v1-{digest}-{revision}.json"
        if cache.exists():
            result = json.loads(cache.read_text())
            data["bertscore"] = result["scores"]
            data["bertscore_no_special"] = result["no_special_scores"]
            pairwise = pd.DataFrame(result["pairwise_scores"])
        else:
            tokenizer = AutoTokenizer.from_pretrained(
                model_id, revision=revision, use_fast=True
            )
            model = AutoModel.from_pretrained(
                model_id,
                revision=revision,
                attn_implementation="eager",
                reference_compile=False,
            ).eval()
            embeddings = {}

            def embed(text):
                if text not in embeddings:
                    encoded = tokenizer(
                        text,
                        return_tensors="pt",
                        truncation=False,
                        return_token_type_ids=False,
                        return_special_tokens_mask=True,
                    )
                    special = encoded.pop("special_tokens_mask")[0].bool()
                    if encoded["input_ids"].shape[1] > 8192:
                        raise ValueError(
                            "Segment exceeds NeoBERTugues context; truncation is forbidden"
                        )
                    with torch.inference_mode():
                        hidden = model(**encoded).last_hidden_state[0]
                    mask = encoded["attention_mask"][0].bool()
                    embeddings[text] = (
                        torch.nn.functional.normalize(hidden, dim=-1),
                        mask,
                        special,
                    )
                return embeddings[text]

            def score(a, b, exclude_special=False):
                ea, ma, sa = embed(a)
                eb, mb, sb = embed(b)
                if exclude_special:
                    ma, mb = ma & ~sa, mb & ~sb
                cosine = ea[ma] @ eb[mb].T
                precision, recall = (
                    cosine.max(dim=1).values.mean(),
                    cosine.max(dim=0).values.mean(),
                )
                return (
                    float(2 * precision * recall / (precision + recall))
                    if precision + recall > 0
                    else 0.0
                )

            data["bertscore"] = [
                score(r.translation, r.reference) for r in data.itertuples()
            ]
            data["bertscore_no_special"] = [
                score(r.translation, r.reference, True) for r in data.itertuples()
            ]
            pair_rows = []
            for unit, group in corpus.loc[corpus.group == "questions"].groupby(
                "unit_id"
            ):
                versions = list(group.sort_values("candidate_id").itertuples())
                for a, b in combinations(versions, 2):
                    pair_rows.append(
                        dict(
                            unit_id=unit,
                            candidate_a=a.candidate_id,
                            candidate_b=b.candidate_id,
                            bertscore=score(a.translation, b.translation),
                            bertscore_no_special=score(
                                a.translation, b.translation, True
                            ),
                        )
                    )
            pairwise = pd.DataFrame(pair_rows)
            cache.write_text(
                json.dumps(
                    dict(
                        scores=data.bertscore.tolist(),
                        no_special_scores=data.bertscore_no_special.tolist(),
                        pairwise_scores=pair_rows,
                    )
                )
            )
        statuses["bertscore"] = dict(
            status="completed",
            model=model_id,
            revision=revision,
            reference_language="pt-BR",
            layer="last",
            idf=False,
            rescale=False,
            tokenizer="model-provided fast tokenizer",
            attention="eager",
            implementation="NeoBERTugues cosine-matching variant; legacy formula",
        )
    except Exception as exc:
        statuses["bertscore"] = dict(status="blocked", error=public_error(exc))
    try:
        from comet import load_from_checkpoint
        from huggingface_hub import snapshot_download

        model_id = "Unbabel/wmt22-comet-da"
        revision = model_info(model_id).sha
        cache = cache_dir / f"comet-{digest}-{revision}.json"
        if cache.exists():
            data["comet"] = json.loads(cache.read_text())["scores"]
        else:
            folder = snapshot_download(model_id, revision=revision)
            checkpoints = list(Path(folder).glob("checkpoints/*.ckpt"))
            if len(checkpoints) != 1:
                raise ValueError("Expected exactly one pinned COMET checkpoint")
            model = load_from_checkpoint(str(checkpoints[0])).eval()
            samples = [
                dict(src=r.source, mt=r.translation, ref=r.reference)
                for r in data.itertuples()
            ]
            predictions = model.predict(samples, batch_size=4, gpus=0, num_workers=0)
            data["comet"] = list(map(float, predictions.scores))
            cache.write_text(json.dumps(dict(scores=data.comet.tolist())))
        statuses["comet"] = dict(
            status="completed",
            model=model_id,
            revision=revision,
            src_language="en",
            ref_language="pt-BR",
            batch_size=4,
        )
    except Exception as exc:
        statuses["comet"] = dict(status="blocked", error=public_error(exc))
    metrics = [c for c in ["bertscore", "bertscore_no_special", "comet"] if c in data]
    for metric in metrics:
        if not np.isfinite(data[metric]).all():
            raise ValueError(f"Non-finite scores for {metric}")
    return data, statuses, pairwise
