import streamlit as st
import pandas as pd

st.title("🏁 Competitive Landscape & Strategic Positioning")
st.caption(
    "Positioning iCruiseEgypt against customer-facing cruise OTAs such as ChooseCruise."
)

# ==================== SECTION 1: CONTEXT ====================
st.markdown(
    """
### 📌 Competitive Context

**ChooseCruise** is a customer-facing cruise booking platform (OTA) focused on:
- Price comparison  
- Cruise discovery  
- Booking convenience  

**iCruiseEgypt**, in contrast, is designed as an **operator and partner intelligence platform**.

This page clarifies how both platforms differ in **purpose, users, and analytical depth**.
"""
)

st.divider()

# ==================== SECTION 2: COMPARISON TABLE ====================
st.subheader("🔍 iCruiseEgypt vs ChooseCruise")

comparison_df = pd.DataFrame({
    "Dimension": [
        "Primary Focus",
        "Target Users",
        "Core Objective",
        "Analytics Depth",
        "Partner / OTA Evaluation",
        "Pricing Intelligence",
        "Customer Loyalty Insights",
        "Operational Decision Support",
        "Revenue Leakage Detection"
    ],
    "iCruiseEgypt Analytics": [
        "Operator & partner analytics",
        "Cruise operators, partners, management",
        "Improve operational performance & profitability",
        "Advanced (diagnostic & efficiency-driven)",
        "Yes (cancellations, revenue quality, dependency)",
        "Revenue per seat, discounts, leakage",
        "Yes (repeat customers, high-value segments)",
        "Strong",
        "Yes"
    ],
    "ChooseCruise (OTA)": [
        "Customer booking & discovery",
        "End customers",
        "Enable cruise discovery and booking",
        "Basic (prices, availability)",
        "No",
        "Listed prices only",
        "Limited",
        "Minimal",
        "No"
    ]
})

st.dataframe(comparison_df, use_container_width=True)

st.divider()

# ==================== SECTION 3: ANALYTICAL DIFFERENTIATION ====================
st.subheader("🧠 Analytical Differentiation")

st.markdown(
    """
Unlike customer-facing OTAs, **iCruiseEgypt focuses on internal performance diagnostics**, such as:

- Identifying **underperforming routes and cruises**
- Measuring **capacity utilization vs revenue efficiency**
- Detecting **high-risk partners based on cancellations**
- Highlighting **revenue leakage caused by discounting**
- Understanding **customer lifetime value**, not just bookings

These insights are **not visible** in consumer OTAs like ChooseCruise.
"""
)

st.divider()

# ==================== SECTION 4: STRATEGIC VALUE ====================
st.subheader("🎯 Strategic Value for Cruise Operators")

st.markdown(
    """
This dashboard enables cruise operators to:

- Decide **which partners to promote or renegotiate**
- Optimize **pricing and discount strategies**
- Reduce **last-minute cancellations**
- Improve **route-level profitability**
- Shift focus from volume-driven sales to **value-driven growth**

The platform complements OTAs rather than competing with them.
"""
)

st.divider()

# ==================== ALIGNMENT STATEMENT ====================
st.info(
    """
✅ **Alignment with Project Objective**

This dashboard demonstrates a clear understanding of the competitive landscape by
distinguishing between customer-facing OTAs (such as ChooseCruise) and operator-focused
analytics platforms.

The insights presented are designed to support **high-value, operational decision-making**
rather than standard booking reports.
"""
)
