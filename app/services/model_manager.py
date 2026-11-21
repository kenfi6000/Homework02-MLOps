import shutil
from pathlib import Path
from typing import Callable

from huggingface_hub import snapshot_download

from app.utils.config import env, load_models
from app.utils.logging_config import configure_logging

logger = configure_logging()


class ModelManager:
    def __init__(
        self,
        model_dir: str | Path | None = None,
        hf_home: str | Path | None = None,
        download_fn: Callable[..., str] = snapshot_download,
    ) -> None:
        configured_dir = model_dir or env("MODEL_DIR", "./models")
        self.model_dir = Path(configured_dir)
        if not self.model_dir.is_absolute():
            self.model_dir = Path(__file__).resolve().parents[2] / self.model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)

        configured_cache = hf_home or env("HF_HOME", "./.cache/huggingface")
        self.hf_home = Path(configured_cache)
        if not self.hf_home.is_absolute():
            self.hf_home = Path(__file__).resolve().parents[2] / self.hf_home
        self.download_fn = download_fn

    def _safe_model_path(self, model_id: str) -> Path:
        if not model_id or "/" not in model_id:
            raise ValueError("Model identifier must contain an owner and model name")
        owner, name = model_id.split("/", 1)
        if not owner or not name or any(ch in model_id for ch in (":", "\\", "..")):
            raise ValueError("Invalid model identifier")
        resolved_root = self.model_dir.resolve()
        path = (resolved_root / owner / name).resolve()
        if path != resolved_root and resolved_root not in path.parents:
            raise ValueError("Model path escapes the configured model directory")
        return path

    def load_configured_models(self) -> list[dict[str, str]]:
        return load_models()

    def model_status(self, model_id: str) -> dict[str, str]:
        path = self._safe_model_path(model_id)
        if self.is_ready(model_id):
            revision = self.read_revision(path)
            return {
                "model_id": model_id,
                "status": "ready",
                "path": str(path),
                "revision": revision,
            }
        return {"model_id": model_id, "status": "missing", "path": str(path), "revision": ""}

    def is_ready(self, model_id: str) -> bool:
        path = self._safe_model_path(model_id)
        if not path.is_dir():
            return False
        has_config = (path / "config.json").is_file()
        has_weights = any(path.glob("*.safetensors")) or any(path.glob("*.bin"))
        return has_config and has_weights

    @staticmethod
    def read_revision(path: Path) -> str:
        revision_file = path / "revision.txt"
        if revision_file.is_file():
            return revision_file.read_text(encoding="utf-8").strip()
        return ""

    def download_model(self, model_id: str, revision: str | None = None) -> dict[str, str]:
        path = self._safe_model_path(model_id)
        if self.is_ready(model_id):
            return self.model_status(model_id)

        path.parent.mkdir(parents=True, exist_ok=True)
        staging = path.with_name(f".{path.name}.downloading")
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)

        try:
            downloaded = Path(
                self.download_fn(
                    repo_id=model_id,
                    revision=revision,
                    cache_dir=str(self.hf_home),
                    local_dir=str(staging),
                    token=env("HF_TOKEN") or None,
                )
            )
            if not downloaded.exists():
                raise RuntimeError("Hugging Face download returned no local directory")
            if not (downloaded / "config.json").is_file():
                raise RuntimeError("Downloaded model is missing config.json")
            weight_files = list(downloaded.glob("*.safetensors")) + list(downloaded.glob("*.bin"))
            if not weight_files:
                raise RuntimeError("Downloaded model is missing model weights")

            (downloaded / "revision.txt").write_text(revision or "main", encoding="utf-8")
            if path.exists():
                shutil.rmtree(path)
            staging.replace(path)
            logger.info(
                "Model download completed",
                extra={"model_id": model_id, "revision": revision or "main"},
            )
            return self.model_status(model_id)
        except Exception as exc:
            shutil.rmtree(staging, ignore_errors=True)
            if path.exists() and not self.is_ready(model_id):
                shutil.rmtree(path, ignore_errors=True)
            logger.error("Model download failed", extra={"model_id": model_id, "error": str(exc)})
            raise RuntimeError(f"Failed to download model '{model_id}': {exc}") from exc

    def delete_model(self, model_id: str) -> None:
        path = self._safe_model_path(model_id)
        if path.exists():
            shutil.rmtree(path)
        logger.info("Model deleted", extra={"model_id": model_id})

    def clear_cache(self) -> None:
        if self.hf_home.exists():
            shutil.rmtree(self.hf_home)
        self.hf_home.mkdir(parents=True, exist_ok=True)
        logger.info("Hugging Face cache cleared", extra={"cache": str(self.hf_home)})
