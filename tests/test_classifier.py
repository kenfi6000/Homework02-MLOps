import pytest

from app.services.classifier import ZeroShotClassifier
from app.utils.config import validate_labels, validate_text


def test_empty_text_is_rejected():
    with pytest.raises(ValueError, match="must not be empty"):
        validate_text("  ")


def test_fewer_than_two_labels_is_rejected():
    with pytest.raises(ValueError, match="At least two"):
        validate_labels(["sports"])


def test_duplicate_labels_are_rejected_case_insensitively():
    with pytest.raises(ValueError, match="unique"):
        validate_labels(["Sports", " sports "])


def test_classifier_ranks_and_selects_highest(tmp_path):
    model_path = tmp_path / "owner" / "example"
    model_path.mkdir(parents=True)

    def mock_pipeline(*args, **kwargs):
        def classifier(text, candidate_labels):
            assert text == "A soccer team won"
            assert candidate_labels == ["sports", "politics"]
            return {
                "labels": ["politics", "sports"],
                "scores": [0.15, 0.85],
            }

        return classifier

    service = ZeroShotClassifier(model_dir=tmp_path, pipeline_factory=mock_pipeline)
    result = service.classify(
        "A soccer team won",
        ["sports", "politics"],
        "owner/example",
    )
    assert result["predicted_class"] == "sports"
    assert result["confidence"] == 0.85
    assert result["ranked_predictions"][0]["label"] == "sports"
