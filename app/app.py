import streamlit as st
import pandas as pd
import plotly.express as px 
import pandas as pd
import plotly.express as px

# ============================================================
# INVENTORY OPTIMIZATION DECISION DASHBOARD
# ============================================================

st.set_page_config(
    page_title="Inventory Optimization Dashboard",
    page_icon="📦",
    layout="wide"
)

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv("inventory_decision_dashboard.csv")

# ============================================================
# TITLE
# ============================================================

st.title("📦 Inventory Optimization Decision Dashboard")

st.markdown(
    """
    **ML-based demand forecasting + uncertainty analysis + inventory optimization**
    
    Transforming demand forecasts into SKU-level inventory decisions.
    """
)

st.divider()

# ============================================================
# PORTFOLIO OVERVIEW
# ============================================================

st.subheader("📊 Portfolio Overview")

total_baseline = df["Baseline Cost"].sum()
total_optimized = df["Optimized Cost"].sum()
total_savings = total_baseline - total_optimized
overall_reduction = (total_savings / total_baseline) * 100

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Baseline Cost",
        f"{total_baseline:.2f}"
    )

with col2:
    st.metric(
        "Total Optimized Cost",
        f"{total_optimized:.2f}"
    )

with col3:
    st.metric(
        "Total Cost Savings",
        f"{total_savings:.2f}"
    )

with col4:
    st.metric(
        "Overall Cost Reduction",
        f"{overall_reduction:.2f}%"
    )

st.divider()

# ============================================================
# SKU SELECTION
# ============================================================

st.subheader("🎯 SKU-Level Decision")

sku = st.selectbox(
    "Select SKU",
    df["SKU"].unique()
)

selected = df[df["SKU"] == sku].iloc[0]

# ============================================================
# KEY INVENTORY DECISIONS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Forecast Demand",
        f"{selected['Forecast Demand']:.2f}"
    )

with col2:
    st.metric(
        "Optimal Order Quantity",
        f"{selected['Optimal Q']:.0f}"
    )

with col3:
    st.metric(
        "Safety Stock",
        f"{selected['Safety Stock']:.2f}"
    )

with col4:
    st.metric(
        "Reorder Point",
        f"{selected['Reorder Point']:.2f}"
    )

# ============================================================
# COST IMPACT
# ============================================================

st.subheader("💰 Cost Impact")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Baseline Cost",
        f"{selected['Baseline Cost']:.2f}"
    )

with col2:
    st.metric(
        "Optimized Cost",
        f"{selected['Optimized Cost']:.2f}"
    )

with col3:
    st.metric(
        "Cost Reduction",
        f"{selected['Cost Reduction (%)']:.2f}%"
    )

# ============================================================
# RECOMMENDED ACTION
# ============================================================

st.subheader("🚦 Recommended Inventory Action")

baseline_q = selected["Forecast Demand"]
optimal_q = selected["Optimal Q"]

order_uplift = selected["Order Uplift (%)"]

st.info(
    f"""
    **{sku} Recommendation**
    
    Use an order quantity of **{optimal_q:.0f} units** rather than the
    baseline forecast-based quantity of **{baseline_q:.0f} units**.
    
    This represents an **{order_uplift:.2f}% order uplift** and provides
    **{selected['Safety Stock']:.2f} units of safety stock**.
    
    Reorder when inventory position reaches approximately
    **{selected['Reorder Point']:.2f} units**.
    """
)

st.divider()

# ============================================================
# SKU COMPARISON
# ============================================================

st.subheader("📈 SKU Comparison")

col1, col2 = st.columns(2)

with col1:

    st.markdown("**Optimal Order Quantity**")

    q_chart = df.set_index("SKU")[["Optimal Q"]]

    st.bar_chart(q_chart)

with col2:

    st.markdown("**Reorder Point**")

    rp_chart = df.set_index("SKU")[["Reorder Point"]]

    st.bar_chart(rp_chart)

# ============================================================



st.subheader("🛡️ Safety Stock by SKU")

df["Safety Stock Coverage (%)"] = (
    df["Safety Stock"] /
    df["Forecast Demand"]
) * 100

risk_chart_data = df[
    ["SKU", "Safety Stock", "Safety Stock Coverage (%)"]
].copy()

fig_risk = px.bar(
    risk_chart_data,
    x="SKU",
    y="Safety Stock",
    text="Safety Stock",
    hover_data={
        "Safety Stock": ":.2f",
        "Safety Stock Coverage (%)": ":.2f"
    },
    labels={
        "SKU": "SKU",
        "Safety Stock": "Safety Stock (units)"
    }
)

fig_risk.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig_risk.update_layout(
    yaxis_title="Safety Stock (units)",
    xaxis_title="SKU",
    showlegend=False,
    height=450
)

st.plotly_chart(
    fig_risk,
    use_container_width=True
)

# ============================================================
# COMPLETE DECISION TABLE
# ============================================================

# ============================================================
# BASELINE VS OPTIMIZED COST
# ============================================================

st.subheader("💵 Baseline vs Optimized Cost")

cost_chart_data = df[
    ["SKU", "Baseline Cost", "Optimized Cost"]
].copy()

cost_chart_data = cost_chart_data.melt(
    id_vars="SKU",
    value_vars=["Baseline Cost", "Optimized Cost"],
    var_name="Cost Type",
    value_name="Cost"
)

fig_cost = px.bar(
    cost_chart_data,
    x="SKU",
    y="Cost",
    color="Cost Type",
    barmode="group",
    text="Cost"
)

fig_cost.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig_cost.update_layout(
    xaxis_title="SKU",
    yaxis_title="Expected Cost",
    legend_title="",
    height=450
)

st.plotly_chart(
    fig_cost,
    width="stretch"
)
display_columns = [
    "SKU",
    "Forecast Demand",
    "Forecast Error Std",
    "Optimal Q",
    "Safety Stock",
    "Reorder Point",
    "Baseline Cost",
    "Optimized Cost",
    "Cost Reduction (%)",
    "Safety Stock Coverage (%)",
    "Order Uplift (%)"
]

st.dataframe(
    df[display_columns],
    width="stretch",
    hide_index=True
)