"""Utilities for assembling a lightweight SHL assessment catalogue.

The provided training spreadsheet only lists assessment URLs. This module
creates a structured catalogue file with inferred metadata so that the
retrieval pipeline has something to work with before full web crawling is
implemented (the public catalog now returns `404` for many historic URLs).
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

import pandas as pd


DOMAIN_KEYWORDS = {
    "sales": "Sales",
    "marketing": "Marketing",
    "finance": "Finance",
    "bank": "Finance",
    "data": "Data",
    "programming": "Technology",
    "developer": "Technology",
    "technology": "Technology",
    "it": "Technology",
    "engineer": "Technology",
    "analytics": "Data",
    "analysis": "Data",
    "admin": "Administration",
    "leadership": "Leadership",
    "manager": "Management",
    "hr": "Human Resources",
    "talent": "Human Resources",
    "customer": "Customer Service",
    "support": "Customer Service",
}


LEVEL_KEYWORDS = {
    "entry": "Entry",
    "graduate": "Entry",
    "junior": "Entry",
    "mid": "Mid",
    "middle": "Mid",
    "intermediate": "Mid",
    "lead": "Senior",
    "senior": "Senior",
    "manager": "Senior",
    "director": "Senior",
    "executive": "Executive",
    "chief": "Executive",
    "coo": "Executive",
    "cxo": "Executive",
}


DEFAULT_CATEGORY = "Individual Test Solution"


@dataclass
class AssessmentRecord:
    assessment_id: str
    name: str
    category: str
    job_levels: str
    domain: str
    description: str
    url: str


def _sanitize_slug(url: str) -> str:
    slug = url.rstrip("/").split("/")[-1]
    slug = slug.replace("?", "-")
    return re.sub(r"[^a-z0-9-]", "", slug.lower())


def _slug_to_name(slug: str) -> str:
    tokens = [token for token in slug.split("-") if token]
    if not tokens:
        return "Unknown Assessment"
    tokens = [token.upper() if token in {"shl", "ai"} else token.capitalize() for token in tokens]
    replacements = {"verify": "VERIFY", "aplus": "A+", "ii": "II", "iii": "III"}
    tokens = [replacements.get(token.lower(), token) for token in tokens]
    return " ".join(tokens)


def _infer_domain(tokens: Sequence[str]) -> str:
    for token in tokens:
        domain = DOMAIN_KEYWORDS.get(token)
        if domain:
            return domain
    return "General"


def _infer_levels(tokens: Sequence[str]) -> str:
    levels = {LEVEL_KEYWORDS[token] for token in tokens if token in LEVEL_KEYWORDS}
    if not levels:
        return "Entry|Mid|Senior"
    # Preserve a deterministic ordering for readability
    ordered = [lvl for lvl in ("Entry", "Mid", "Senior", "Executive") if lvl in levels]
    return "|".join(ordered)


def _generate_description(name: str, domain: str, levels: str) -> str:
    levels_str = levels.replace("|", "/")
    return (
        f"{name} evaluates role-fit competencies for {domain.lower()} positions "
        f"targeted at {levels_str.lower()} talent levels."
    )


def build_catalogue(train_dataset: Path, output_csv: Path) -> List[AssessmentRecord]:
    df = pd.read_excel(train_dataset, sheet_name="Train-Set")
    unique_urls = df["Assessment_url"].dropna().unique()

    records: List[AssessmentRecord] = []
    for url in unique_urls:
        slug = _sanitize_slug(url)
        tokens = tuple(token for token in slug.split("-") if token)
        name = _slug_to_name(slug)
        domain = _infer_domain(tokens)
        levels = _infer_levels(tokens)
        description = _generate_description(name, domain, levels)

        records.append(
            AssessmentRecord(
                assessment_id=slug,
                name=name,
                category=DEFAULT_CATEGORY,
                job_levels=levels,
                domain=domain,
                description=description,
                url=url,
            )
        )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "assessment_id",
                "name",
                "category",
                "job_levels",
                "domain",
                "description",
                "url",
            ),
        )
        writer.writeheader()
        for record in records:
            writer.writerow(record.__dict__)

    return records


def build_default_catalogue(dataset_path: str | Path = "Gen_AI Dataset.xlsx") -> Path:
    dataset_path = Path(dataset_path)
    output_csv = dataset_path.parent / "data" / "shl_catalogue.csv"
    build_catalogue(dataset_path, output_csv)
    return output_csv


if __name__ == "__main__":
    output_path = build_default_catalogue()
    print(f"Catalogue written to {output_path}")