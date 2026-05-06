import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from pathlib import Path

st.set_page_config(
    page_title="Manufacturing SPC Dashboard",
    page_icon="🏭",
    layout="wide",
)

@st.cache_resource
def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/postgres")

@st.cache_data
def load_alerts():
    engine = get_engine()
    sql = Path("sql/window_functions.sql").read_text()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)

alerts = load_alerts()

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("Filters")
all_operators = sorted(alerts["operator"].unique())
selected = st.sidebar.multiselect("Operator", all_operators, default=all_operators)

data = alerts[alerts["operator"].isin(selected)]

# ── Header ───────────────────────────────────────────────────────────────────
st.title("Manufacturing Process Control Dashboard")
st.markdown(
    "Statistical Process Control (SPC) analysis of height measurements. "
    "Control limits are computed with a rolling window of 5 measurements per operator."
)
st.divider()

# ── KPI row ──────────────────────────────────────────────────────────────────
total = len(data)
out_of_control = int(data["alert"].sum())
in_control = total - out_of_control

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Measurements", total)
col2.metric("In Control", in_control)
col3.metric("Out of Control", out_of_control)
col4.metric("Process Yield", f"{in_control / total * 100:.1f}%" if total else "—")

st.divider()

# ── Control charts ───────────────────────────────────────────────────────────
st.subheader("Control Charts")

for operator in sorted(selected):
    op = data[data["operator"] == operator].reset_index(drop=True)

    fig = go.Figure()

    # Shaded control band
    fig.add_trace(go.Scatter(
        x=list(op["row_number"]) + list(op["row_number"])[::-1],
        y=list(op["ucl"]) + list(op["lcl"])[::-1],
        fill="toself",
        fillcolor="rgba(0,180,0,0.06)",
        line=dict(color="rgba(0,0,0,0)"),
        hoverinfo="skip",
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        x=op["row_number"], y=op["ucl"],
        mode="lines", name="UCL / LCL",
        line=dict(color="red", dash="dash", width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=op["row_number"], y=op["lcl"],
        mode="lines", showlegend=False,
        line=dict(color="red", dash="dash", width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=op["row_number"], y=op["avg_height"],
        mode="lines", name="Avg Height",
        line=dict(color="green", dash="dash", width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=op["row_number"], y=op["height"],
        mode="lines+markers", name="Height",
        line=dict(color="steelblue", width=1.5),
        marker=dict(size=4, color="steelblue"),
    ))

    out = op[op["alert"] == True]
    if not out.empty:
        fig.add_trace(go.Scatter(
            x=out["row_number"], y=out["height"],
            mode="markers", name="Out of control",
            marker=dict(color="red", size=10, symbol="x-thin-open", line=dict(width=2.5)),
        ))

    fig.update_layout(
        title=f"Control Chart — {operator}",
        xaxis_title="Row Number",
        yaxis_title="Height",
        height=380,
        margin=dict(l=50, r=30, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Summary table ─────────────────────────────────────────────────────────────
st.subheader("Summary by Operator")

summary = (
    data.groupby("operator")
    .agg(total=("height", "count"), out_of_control=("alert", "sum"))
    .assign(in_control=lambda df: df["total"] - df["out_of_control"])
    .assign(pct_yield=lambda df: (df["in_control"] / df["total"] * 100).round(1))
    .reset_index()
    .rename(columns={
        "operator": "Operator",
        "total": "Total",
        "in_control": "In Control",
        "out_of_control": "Out of Control",
        "pct_yield": "Yield (%)",
    })
)
st.dataframe(summary, use_container_width=True, hide_index=True)

st.divider()

# ── Raw data ──────────────────────────────────────────────────────────────────
st.subheader("Raw Data")
show_alerts_only = st.toggle("Show out-of-control rows only", value=False)
display_data = data[data["alert"] == True] if show_alerts_only else data
st.dataframe(display_data, use_container_width=True, hide_index=True)
