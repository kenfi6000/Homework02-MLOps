import time
from pathlib import Path
from typing import Any, Callable

from transformers import pipeline

from app.utils.config import env, validate_labels, validate_text


class ZeroShotClassifier:
    def __init__(
        self,
        model_dir: str | Path | None = None,
        pipeline_factory: Callable[..., Any] = pipeline,
    ) -> None:
        configured_dir = model_dir or env("MODEL_DIR", "./models")
        self.model_dir = Path(configured_dir)
        if not self.model_dir.is_absolute():
            self.model_dir = Path(__file__).resolve().parents[2] / self.model_dir
        self.pipeline_factory = pipeline_factory
        self._pipelines: dict[str, Any] = {}

    @staticmethod
    def _model_path(model_dir: Path, model_id: str) -> Path:
        owner, name = model_id.split("/", 1)
        return model_dir / owner / name

    def get_pipeline(self, model_id: str) -> Any:
        if model_id not in self._pipelines:
            path = self._model_path(self.model_dir, model_id)
            if not path.is_dir():
                raise FileNotFoundError(f"Model '{model_id}' is not downloaded")
            self._pipelines[model_id] = self.pipeline_factory(
                "zero-shot-classification",
                model=str(path),
                local_files_only=True,
            )
        return self._pipelines[model_id]

    def classify(self, text: str, candidate_labels: list[str], model_id: str) -> dict[str, Any]:
        cleaned_text = validate_text(text)
        cleaned_labels = validate_labels(candidate_labels)
        classifier = self.get_pipeline(model_id)
        start = time.perf_counter()
        raw = classifier(cleaned_text, candidate_labels=cleaned_labels)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        ranked = [
            {"label": str(label), "score": float(score)}
            for label, score in zip(raw["labels"], raw["scores"], strict=True)
        ]
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return {
            "predicted_class": ranked[0]["label"],
            "confidence": ranked[0]["score"],
            "ranked_predictions": ranked,
            "candidate_labels": cleaned_labels,
            "latency_ms": elapsed_ms,
        }
