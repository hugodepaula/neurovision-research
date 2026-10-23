"""Verify model weights against official LFS SHA-256 metadata for a recorded run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(ROOT / ".cache/huggingface"))
ARTIFACTS = {"bertscore": "model.safetensors", "comet": "checkpoints/model.ckpt"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    from huggingface_hub import model_info

    metadata = json.loads((args.run / "metadata.json").read_text())
    results = []
    for metric, filename in ARTIFACTS.items():
        status = metadata["semantic"][metric]
        if status["status"] != "completed":
            raise ValueError(f"Cannot verify an incomplete metric: {metric}")
        model_id, revision = status["model"], status["revision"]
        info = model_info(model_id, revision=revision, files_metadata=True)
        entry = next(s for s in info.siblings if s.rfilename == filename)
        expected = entry.lfs.sha256
        folder = (
            Path(os.environ["HF_HOME"])
            / "hub"
            / ("models--" + model_id.replace("/", "--"))
        )
        path = folder / "snapshots" / revision / filename
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
                digest.update(block)
        actual = digest.hexdigest()
        if actual != expected:
            raise ValueError(
                f"Official SHA-256 mismatch: {metric}; affected results must not be used"
            )
        results.append(
            dict(
                metric=metric,
                model=model_id,
                revision=revision,
                file=filename,
                sha256=actual,
                bytes=path.stat().st_size,
            )
        )
        print(f"Official model checksum verified: {metric}", flush=True)
    (args.run / "model_integrity.json").write_text(json.dumps(results, indent=2))
    checksums = {
        str(p.relative_to(args.run)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(args.run.rglob("*"))
        if p.is_file() and p.name != "checksums.json"
    }
    (args.run / "checksums.json").write_text(json.dumps(checksums, indent=2))


if __name__ == "__main__":
    main()
