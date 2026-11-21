import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


def env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def load_yaml(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = ROOT_DIR / file_path
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    with file_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Configuration must contain a YAML mapping: {file_path}")
    return data


def load_models(path: str | Path = "configs/models.yaml") -> list[dict[str, str]]:
    data = load_yaml(path)
    models = data.get("models")
    if not isinstance(models, list):
        raise ValueError("models.yaml must contain a models list")
    return [dict(model) for model in models]


def load_label_sets(path: str | Path = "configs/labels.yaml") -> list[dict[str, Any]]:
    data = load_yaml(path)
    label_sets = data.get("label_sets")
    if not isinstance(label_sets, list):
        raise ValueError("labels.yaml must contain a label_sets list")
    return [dict(label_set) for label_set in label_sets]


def validate_labels(labels: list[str]) -> list[str]:
    cleaned = [label.strip() for label in labels if isinstance(label, str) and label.strip()]
    if len(cleaned) < 2:
        raise ValueError("At least two non-empty candidate labels are required")
    normalized = [label.casefold() for label in cleaned]
    if len(normalized) != len(set(normalized)):
        raise ValueError("Candidate labels must be unique")
    return cleaned


def validate_text(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must not be empty")
    return text.strip()


def save_label_sets(
    label_sets: list[dict[str, Any]],
    path: str | Path = "configs/labels.yaml",
) -> None:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = ROOT_DIR / file_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump({"label_sets": label_sets}, handle, sort_keys=False)
