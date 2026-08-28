import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# ============================================================
# PAGE CONFIGURATION
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
# CALCULATE DERIVED METRICS
# ============================================================

df["Safety Stock Coverage (%)"] = (
    df["Safety Stock"] / df["Forecast Demand"]
) * 100


# ============================================================
# FORECAST MODEL PERFORMANCE
# ============================================================

MAE = 8.18
RMSE = 10.65
R2 = 0.8256

TEST_OBSERVATIONS = 420


# ============================================================
# PORTFOLIO METRICS
# ============================================================

total_baseline = df["Baseline Cost"].sum()
total_optimized = df["Optimized Cost"].sum()

total_savings = total_baseline - total_optimized

overall_reduction = (
    total_savings / total_baseline
) * 100


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
# FORECAST MODEL PERFORMANCE
# ============================================================

st.subheader("🤖 Forecast Model Performance")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "MAE",
        f"{MAE:.2f}",
        help=(
            "Mean Absolute Error — average absolute difference "
            "between actual and predicted demand."
        )
    )

with col2:
    st.metric(
        "RMSE",
        f"{RMSE:.2f}",
        help=(
            "Root Mean Squared Error — gives greater weight "
            "to larger forecasting errors."
        )
    )

with col3:
    st.metric(
        "R²",
        f"{R2:.2%}",
        help=(
            "Coefficient of determination — proportion of "
            "demand variation explained by the model."
        )
    )

st.caption(
    f"Performance evaluated on the held-out test set "
    f"({TEST_OBSERVATIONS} observations)."
)

st.divider()


# ============================================================
# PORTFOLIO OVERVIEW
# ============================================================

st.subheader("📊 Portfolio Overview")

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
# SKU-LEVEL DECISION
# ============================================================

st.subheader("🎯 SKU-Level Decision")

sku = st.selectbox(
    "Select SKU",
    df["SKU"].unique()
)

selected = df.loc[
    df["SKU"] == sku
].iloc[0]


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
# 🔮 SCENARIO / WHAT-IF ANALYSIS
# ============================================================

st.subheader("🔮 Scenario / What-If Analysis")

st.markdown(
    """
    Explore how changes in demand and forecast uncertainty affect
    inventory requirements.
    """
)

# ------------------------------------------------------------
# Scenario Controls
# ------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    demand_change = st.slider(
        "Demand Change (%)",
        min_value=-20,
        max_value=30,
        value=0,
        step=5,
        help="Simulate a decrease or increase in forecast demand."
    )

with col2:
    uncertainty_change = st.slider(
        "Forecast Uncertainty Change (%)",
        min_value=-20,
        max_value=50,
        value=0,
        step=5,
        help="Simulate a decrease or increase in forecast uncertainty."
    )
# ================================
# INVENTORY POLICY PARAMETERS
# ================================

lead_time = 5
service_level = 0.95

# Z-value corresponding to 95% service level
Z = 1.645

# ------------------------------------------------------------
# Scenario Calculations
# ------------------------------------------------------------

base_demand = selected["Forecast Demand"]
base_std = selected["Forecast Error Std"]

# Scenario demand
scenario_demand = base_demand * (1 + demand_change / 100)

# Scenario uncertainty
scenario_std = base_std * (1 + uncertainty_change / 100)

# Scenario safety stock
scenario_safety_stock = (
    Z * scenario_std * np.sqrt(lead_time)
)

# Scenario reorder point
scenario_reorder_point = (
    scenario_demand * lead_time
    + scenario_safety_stock
)

demand_change_actual = (
    (scenario_demand - selected["Forecast Demand"])
    / selected["Forecast Demand"]
) * 100

uncertainty_change_actual = (
    (scenario_std - selected["Forecast Error Std"])
    / selected["Forecast Error Std"]
) * 100

safety_stock_change = (
    (scenario_safety_stock - selected["Safety Stock"])
    / selected["Safety Stock"]
) * 100

reorder_point_change = (
    (scenario_reorder_point - selected["Reorder Point"])
    / selected["Reorder Point"]
) * 100

# ------------------------------------------------------------
# Scenario Results
# ------------------------------------------------------------

st.markdown("### 📊 Scenario Results")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Scenario Demand",
        f"{scenario_demand:.2f}",
        delta=f"{scenario_demand - base_demand:+.2f}"
    )

with col2:
    st.metric(
        "Scenario Uncertainty",
        f"{scenario_std:.2f}",
        delta=f"{scenario_std - base_std:+.2f}"
    )

with col3:
    st.metric(
        "Scenario Safety Stock",
        f"{scenario_safety_stock:.2f}",
        delta=f"{scenario_safety_stock - selected['Safety Stock']:+.2f}"
    )

with col4:
    st.metric(
        "Scenario Reorder Point",
        f"{scenario_reorder_point:.2f}",
        delta=f"{scenario_reorder_point - selected['Reorder Point']:+.2f}"
    )

# ============================================================
# IMPACT VS BASELINE
# ============================================================

st.subheader("📌 Impact vs Baseline")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Safety Stock Change",
        f"{safety_stock_change:+.2f}%"
    )

with col2:
    st.metric(
        "Reorder Point Change",
        f"{reorder_point_change:+.2f}%"
    )
    
# ------------------------------------------------------------
# Scenario Interpretation
# ------------------------------------------------------------

if demand_change == 0 and uncertainty_change == 0:

    st.info(
        f"""
        **Baseline Scenario — {sku}**

        No changes applied. The dashboard is showing the original
        forecast demand, safety stock, and reorder point.
        """
    )

elif demand_change > 0 or uncertainty_change > 0:

    st.warning(
        f"""
        **Higher Inventory Requirement — {sku}**

        The scenario increases demand and/or forecast uncertainty.
        The recommended inventory buffer therefore increases.

        Reorder Point changes from
        **{selected['Reorder Point']:.2f}** to
        **{scenario_reorder_point:.2f} units**.
        """
    )

else:

    st.success(
        f"""
        **Lower Inventory Requirement — {sku}**

        The scenario assumes lower demand and/or lower forecast
        uncertainty, reducing the required inventory buffer.

        Reorder Point changes from
        **{selected['Reorder Point']:.2f}** to
        **{scenario_reorder_point:.2f} units**.
        """
    )

st.divider()

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
# RECOMMENDED INVENTORY ACTION
# ============================================================

st.subheader("🚦 Recommended Inventory Action")

baseline_q = selected["Forecast Demand"]
optimal_q = selected["Optimal Q"]
order_uplift = selected["Order Uplift (%)"]
safety_stock = selected["Safety Stock"]
reorder_point = selected["Reorder Point"]

st.info(
    f"""
    **{sku} Recommendation**

    Use an order quantity of **{optimal_q:.0f} units** rather than the
    baseline forecast-based quantity of **{baseline_q:.0f} units**.

    This represents an **{order_uplift:.2f}% order uplift** and provides
    **{safety_stock:.2f} units of safety stock**.

    Reorder when inventory position reaches approximately
    **{reorder_point:.2f} units**.
    """
)

st.divider()


# ============================================================
# SKU COMPARISON
# ============================================================

st.subheader("📈 SKU Comparison")

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Optimal Order Quantity
# ------------------------------------------------------------

with col1:

    st.markdown("**Optimal Order Quantity**")

    q_chart = df.set_index("SKU")[["Optimal Q"]]

    st.bar_chart(q_chart)


# ------------------------------------------------------------
# Reorder Point
# ------------------------------------------------------------

with col2:

    st.markdown("**Reorder Point**")

    rp_chart = df.set_index("SKU")[["Reorder Point"]]

    st.bar_chart(rp_chart)


# ============================================================
# SAFETY STOCK
# ============================================================

st.subheader("🛡️ Safety Stock by SKU")

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
# BASELINE VS OPTIMIZED COST
# ============================================================

st.subheader("💵 Baseline vs Optimized Cost")

cost_chart_data = df[
    ["SKU", "Baseline Cost", "Optimized Cost"]
].copy()

cost_chart_data = cost_chart_data.melt(
    id_vars="SKU",
    value_vars=[
        "Baseline Cost",
        "Optimized Cost"
    ],
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
    use_container_width=True
)


# ============================================================
# COMPLETE DECISION TABLE
# ============================================================

st.subheader("📋 Complete Decision Table")

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
    use_container_width=True,
    hide_index=True
)