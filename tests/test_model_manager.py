from pathlib import Path

import pytest

from app.services.model_manager import ModelManager
from app.utils.config import load_models


def test_model_configuration_loads_two_models():
    models = load_models()
    assert len(models) >= 2
    assert any(model["id"] == "MoritzLaurer/deberta-v3-base-zeroshot-v2.0" for model in models)


def test_missing_model_is_reported(tmp_path):
    manager = ModelManager(model_dir=tmp_path / "models", hf_home=tmp_path / "cache")
    status = manager.model_status("owner/example")
    assert status["status"] == "missing"


def test_model_download_avoids_complete_model(tmp_path):
    manager = ModelManager(model_dir=tmp_path / "models", hf_home=tmp_path / "cache")
    path = manager._safe_model_path("owner/example")
    path.mkdir(parents=True)
    (path / "config.json").write_text("{}", encoding="utf-8")
    (path / "model.safetensors").write_bytes(b"weights")
    calls = []

    def unexpected_download(**kwargs):
        calls.append(kwargs)
        return str(path)

    manager.download_fn = unexpected_download
    status = manager.download_model("owner/example")
    assert status["status"] == "ready"
    assert calls == []


def test_failed_download_is_cleaned_up(tmp_path):
    manager = ModelManager(model_dir=tmp_path / "models", hf_home=tmp_path / "cache")

    def failed_download(**kwargs):
        staging = Path(kwargs["local_dir"])
        (staging / "partial.txt").write_text("partial", encoding="utf-8")
        raise RuntimeError("download failed")

    manager.download_fn = failed_download
    with pytest.raises(RuntimeError, match="Failed to download model"):
        manager.download_model("owner/example")
    assert not list((tmp_path / "models").glob("**/*.downloading"))


def test_model_deletion_and_cache_cleanup(tmp_path):
    manager = ModelManager(model_dir=tmp_path / "models", hf_home=tmp_path / "cache")
    path = manager._safe_model_path("owner/example")
    path.mkdir(parents=True)
    (path / "config.json").write_text("{}", encoding="utf-8")
    manager.hf_home.mkdir(parents=True)
    (manager.hf_home / "cached.bin").write_bytes(b"x")

    manager.delete_model("owner/example")
    manager.clear_cache()
    assert not path.exists()
    assert not (manager.hf_home / "cached.bin").exists()
