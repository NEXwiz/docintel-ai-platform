"""
Streamlit dashboard for Docintel RAGAS evaluation metrics.
Run: streamlit run evals/dashboard.py
"""
import json
import os

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.json")

st.set_page_config(page_title="Docintel Eval Dashboard", layout="wide")
st.title("Docintel RAG Evaluation Dashboard")


def load_results():
    if not os.path.exists(RESULTS_PATH):
        return None
    with open(RESULTS_PATH, "r") as f:
        return json.load(f)


results = load_results()

if results is None:
    st.warning("No results.json found. Run `python evals/run_eval.py` first.")
    st.stop()

threshold = results.get("threshold", 0.7)
passed = results.get("passed", False)

# Overall status
if passed:
    st.success(f"Overall: PASSED (threshold: {threshold})")
else:
    st.error(f"Overall: FAILED (threshold: {threshold})")

# Extract metric scores
metrics = {k: v for k, v in results.items() if k not in ("passed", "threshold")}

# Gauge charts row
cols = st.columns(len(metrics))
for col, (name, score) in zip(cols, metrics.items()):
    with col:
        color = "green" if score >= threshold else "red"
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": name.replace("_", " ").title()},
            gauge={
                "axis": {"range": [0, 1]},
                "bar": {"color": color},
                "threshold": {
                    "line": {"color": "black", "width": 2},
                    "value": threshold,
                },
            },
        ))
        fig.update_layout(height=250, margin=dict(t=40, b=0, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

# Table view
st.subheader("Score Details")
df = pd.DataFrame([
    {"Metric": k.replace("_", " ").title(), "Score": v, "Status": "PASS" if v >= threshold else "FAIL"}
    for k, v in metrics.items()
])
st.dataframe(df, use_container_width=True, hide_index=True)

# Raw JSON
with st.expander("Raw Results JSON"):
    st.json(results)
