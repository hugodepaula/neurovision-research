"""Validate item alignment and preserve source text and reference provenance."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path

import pandas as pd

HUMAN = "CHYPS-V-br20-Human-25-09-30.txt"
SUBSCALES = {
    "brightness": [3, 7, 9, 14, 19],
    "pattern": [1, 5, 12, 15, 20],
    "strobing": [2, 6, 10, 16, 18],
    "intense_environments": [4, 8, 11, 13, 17],
}
ITEM_PATTERN = re.compile(r"(?m)^\s*(\d{1,2})[.)]\s+")


def read_text(path: Path) -> str:
    return unicodedata.normalize(
        "NFC", path.read_text(encoding="utf-8-sig").replace("\ufeff", "")
    )


def parse_items(text: str) -> dict[int, str]:
    markers = list(ITEM_PATTERN.finditer(text))
    numbers = [int(m.group(1)) for m in markers]
    if numbers != list(range(1, 21)):
        raise ValueError(f"Expected ordered, unique item IDs 1..20; received {numbers}")
    items = {}
    for i, marker in enumerate(markers):
        end = markers[i + 1].start() if i + 1 < len(markers) else len(text)
        value = text[marker.end() : end].strip()
        if not value:
            raise ValueError(f"Empty item {numbers[i]}")
        items[numbers[i]] = value
    return items


def introduction(text: str) -> str:
    marker = ITEM_PATTERN.search(text)
    if marker is None:
        raise ValueError("Full questionnaire has no first numbered item")
    return text[: marker.start()].strip()


def candidate_id(filename: str) -> str:
    prefix, suffix = "CHYPS-V-br20-", ".txt"
    if not filename.startswith(prefix) or not filename.endswith(suffix):
        raise ValueError(f"Unexpected translation filename: {filename}")
    return filename[len(prefix) : -len(suffix)]


def load_corpus(root: Path) -> tuple[pd.DataFrame, dict]:
    question_dir = root / "translations/questions-only"
    files = sorted(question_dir.glob("*.txt"))
    if not files or not (question_dir / HUMAN).is_file():
        raise ValueError("Translations and an independent human reference are required")
    source_path = root / "docs/CHYPS-V-questions-only.txt"
    source = parse_items(read_text(source_path))
    reference = parse_items(read_text(question_dir / HUMAN))
    subscale = {item: name for name, items in SUBSCALES.items() for item in items}
    hashes = {}
    rows = []
    candidates = []
    for path in [source_path, *files]:
        hashes[str(path.relative_to(root))] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    for path in files:
        content = parse_items(read_text(path))
        cid = candidate_id(path.name)
        candidates.append(cid)
        for item, text in content.items():
            rows.append(
                dict(
                    candidate_id=cid,
                    filename=path.name,
                    group="questions",
                    unit_id=f"Q{item:02d}",
                    item_id=item,
                    subscale=subscale[item],
                    source=source[item],
                    reference=reference[item],
                    translation=text,
                    is_reference=path.name == HUMAN,
                )
            )
    # Instructions are one descriptive block per version. Splitting independently
    # would invent alignment and count repeated response labels as observations.
    full_dir = root / "translations/plain-text"
    source_full = root / "docs/CHYPS-V-plain-text.txt"
    ref_full = full_dir / HUMAN
    instruction_audit = []
    if source_full.is_file() and ref_full.is_file():
        source_intro, ref_intro = (
            introduction(read_text(source_full)),
            introduction(read_text(ref_full)),
        )
        for path in [source_full, *sorted(full_dir.glob("*.txt"))]:
            hashes[str(path.relative_to(root))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
        for path in sorted(full_dir.glob("*.txt")):
            cid = candidate_id(path.name)
            # A date discrepancy in legacy plain-text filenames must not silently
            # join a different translation. Unambiguous model-name joins are audited.
            model = re.sub(r"-\d{2}-\d{2}-\d{2}$", "", cid)
            matches = [
                c for c in candidates if re.sub(r"-\d{2}-\d{2}-\d{2}$", "", c) == model
            ]
            if len(matches) != 1:
                raise ValueError(f"Ambiguous instruction candidate: {path.name}")
            aligned_id = matches[0]
            text = introduction(read_text(path))
            paragraphs = [
                re.sub(r"\s+", " ", p).strip().casefold()
                for p in re.split(r"\n\s*\n", text)
                if p.strip()
            ]
            instruction_audit.append(
                dict(
                    filename=path.name,
                    candidate_id=aligned_id,
                    date_alias=aligned_id != cid,
                    exact_duplicate_paragraphs=len(paragraphs) - len(set(paragraphs)),
                )
            )
            rows.append(
                dict(
                    candidate_id=aligned_id,
                    filename=path.name,
                    group="instructions",
                    unit_id="INTRO",
                    item_id=0,
                    subscale="instructions",
                    source=source_intro,
                    reference=ref_intro,
                    translation=text,
                    is_reference=path.name == HUMAN,
                )
            )
    audit = dict(
        source_hashes=hashes,
        candidates=len(files),
        automatic_candidates=len(files) - 1,
        question_items=20,
        reference_file=HUMAN,
        instruction_alignment=instruction_audit,
        reference_review=[
            "Human Q3 contains 'poque'; Q9 contains 'ach oas'. Preserved verbatim.",
            "Human Q7 uses 'cortinas' for 'window shade' in driving context; review suggested.",
            "Human reference has not been independently revalidated by this analysis.",
        ],
        instructions_policy="One complete introductory block; descriptive comparisons only, no segment CI.",
    )
    return pd.DataFrame(rows), audit
