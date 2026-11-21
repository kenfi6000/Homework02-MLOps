
import streamlit as st

from app.services.model_manager import ModelManager
from app.utils.config import load_label_sets, save_label_sets, validate_labels

st.set_page_config(page_title="Admin", page_icon="A", layout="wide")
st.title("Administrator")
st.warning(
    "No authentication is implemented. Use this page only locally "
    "or in a trusted environment."
)

manager = ModelManager()

st.subheader("Model management")
st.caption(f"Local model directory: `{manager.model_dir}`")
st.caption(f"Hugging Face cache: `{manager.hf_home}`")

models = manager.load_configured_models()
for model in models:
    model_id = model["id"]
    status = manager.model_status(model_id)
    columns = st.columns([3, 1, 1, 1])
    columns[0].markdown(f"**{model['name']}**  \n`{model_id}`")
    columns[1].write(status["status"])
    if status["revision"]:
        columns[1].caption(status["revision"])
    if columns[2].button(
        "Download",
        key=f"download-{model_id}",
        disabled=status["status"] == "ready",
    ):
        with st.spinner("Downloading model..."):
            try:
                manager.download_model(model_id, model.get("revision"))
                st.success(f"Model '{model_id}' is ready.")
            except RuntimeError as exc:
                st.error(str(exc))
    if columns[3].button("Delete", key=f"delete-{model_id}", disabled=status["status"] != "ready"):
        try:
            manager.delete_model(model_id)
            st.success(f"Deleted '{model_id}'.")
        except (RuntimeError, ValueError) as exc:
            st.error(str(exc))

action_columns = st.columns(2)
if action_columns[0].button("Refresh model status"):
    st.rerun()
if action_columns[1].button("Clear Hugging Face cache"):
    try:
        manager.clear_cache()
        st.success("Hugging Face cache cleared.")
    except (OSError, RuntimeError) as exc:
        st.error(f"Could not clear cache: {exc}")

st.subheader("Candidate label sets")
try:
    label_sets = load_label_sets()
except (FileNotFoundError, ValueError) as exc:
    st.error(str(exc))
    label_sets = []

names = [item["name"] for item in label_sets]
new_name = st.text_input("Label set name", value="Common Topics")
new_labels_text = st.text_area(
    "Candidate labels (one per line)",
    value="\n".join(
        names and label_sets[0].get("labels", []) or
        ["sports", "politics", "technology", "finance"]
    ),
)

if st.button("Save label set"):
    labels = [line.strip() for line in new_labels_text.splitlines()]
    try:
        cleaned = validate_labels(labels)
        if not new_name.strip():
            raise ValueError("Label set name must not be empty")
        saved = {"name": new_name.strip(), "labels": cleaned}
        matching = next(
            (
                i
                for i, item in enumerate(label_sets)
                if item["name"].casefold() == saved["name"].casefold()
            ),
            None,
        )
        if matching is None:
            label_sets.append(saved)
        else:
            label_sets[matching] = saved
        save_label_sets(label_sets)
        st.success(f"Saved label set '{saved['name']}'.")
    except ValueError as exc:
        st.error(str(exc))
