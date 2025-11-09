"""Preprocessing utilities to build and persist catalogue embeddings."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass
class EmbeddingArtifacts:
    catalogue_path: Path
    embeddings_path: Path
    metadata_path: Path
    model_name: str


def _compose_record_text(row: pd.Series) -> str:
    parts: List[str] = [row["name"], row["description"]]
    parts.append(f"Domain: {row['domain']}")
    parts.append(f"Levels: {row['job_levels']}")
    return ". ".join(part for part in parts if part)


def build_catalogue_embeddings(
    catalogue_csv: str | Path = "data/shl_catalogue.csv",
    output_dir: str | Path = "artifacts",
    model_name: str = DEFAULT_MODEL_NAME,
) -> EmbeddingArtifacts:
    catalogue_path = Path(catalogue_csv)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    catalogue_df = pd.read_csv(catalogue_path)
    sentences = catalogue_df.apply(_compose_record_text, axis=1).tolist()

    model = SentenceTransformer(model_name)
    embeddings = model.encode(sentences, normalize_embeddings=True, show_progress_bar=True)

    embeddings_array = np.asarray(embeddings, dtype=np.float32)
    embeddings_path = output_dir / "catalogue_embeddings.npy"
    np.save(embeddings_path, embeddings_array)

    metadata_path = output_dir / "catalogue_metadata.parquet"
    catalogue_df.to_parquet(metadata_path, index=False)

    config_path = output_dir / "embedding_config.json"
    config_path.write_text(
        json.dumps({"model_name": model_name, "catalogue_csv": str(catalogue_path)}, indent=2),
        encoding="utf-8",
    )

    return EmbeddingArtifacts(
        catalogue_path=catalogue_path,
        embeddings_path=embeddings_path,
        metadata_path=metadata_path,
        model_name=model_name,
    )


if __name__ == "__main__":
    artifacts = build_catalogue_embeddings()
    print(f"Embeddings saved to {artifacts.embeddings_path}")