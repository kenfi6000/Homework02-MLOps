from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st

from app.services.classifier import ZeroShotClassifier
from app.services.minio_storage import MinioStorage
from app.services.model_manager import ModelManager
from app.utils.config import env, load_label_sets

st.set_page_config(page_title="Classify Text", page_icon="C", layout="wide")
st.title("Classify Text")

manager = ModelManager()
models = manager.load_configured_models()
ready_models = [model for model in models if manager.is_ready(model["id"])]

try:
    label_sets = load_label_sets()
except (FileNotFoundError, ValueError) as exc:
    st.error(str(exc))
    label_sets = []

if not ready_models:
    st.error("No downloaded model is available. Download a model on the Administrator page.")
if not label_sets:
    st.error("No saved label set is available.")

text = st.text_area("Text to classify", height=180)
model_names = {model["name"]: model["id"] for model in ready_models}
selected_model_name = st.selectbox("Model", list(model_names), disabled=not ready_models)
label_set_names = [item["name"] for item in label_sets]
selected_label_name = st.selectbox("Candidate label set", label_set_names, disabled=not label_sets)

if st.button("Classify", type="primary", disabled=not ready_models or not label_sets):
    try:
        model_id = model_names[selected_model_name]
        label_set = next(item for item in label_sets if item["name"] == selected_label_name)
        classifier = ZeroShotClassifier()
        output = classifier.classify(text, label_set["labels"], model_id)

        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        status = manager.model_status(model_id)
        request_id = str(uuid4())
        result = {
            "request_id": request_id,
            "timestamp": timestamp,
            "input_text": text.strip(),
            "predicted_class": output["predicted_class"],
            "confidence": output["confidence"],
            "candidate_labels": output["candidate_labels"],
            "ranked_predictions": output["ranked_predictions"],
            "model": model_id,
            "model_revision": status["revision"] or "main",
            "application_version": env("APP_VERSION", "0.1.0"),
            "latency_ms": output["latency_ms"],
        }

        try:
            storage = MinioStorage()
            object_name = storage.store_prediction(result)
            storage_status = f"Saved to MinIO: `{object_name}`"
        except (ValueError, RuntimeError) as exc:
            storage_status = f"Not saved: {exc}"
            st.error(storage_status)

        st.success(f"Predicted class: **{result['predicted_class']}**")
        st.metric("Confidence", f"{result['confidence']:.2%}")
        st.dataframe(output["ranked_predictions"], use_container_width=True)
        st.caption(f"Model: `{model_id}`")
        st.caption(f"Timestamp: {timestamp}")
        st.caption(f"Inference latency: {output['latency_ms']} ms")
        if "Saved to MinIO" in storage_status:
            st.success(storage_status)
    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        st.error(str(exc))
