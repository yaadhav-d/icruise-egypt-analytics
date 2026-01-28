import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from data.data_loader import load_data

st.title("🤝 Partner & OTA Performance")
st.caption(
    "Evaluate partner contribution, risk, and dependency. "
    "(OTA = Online Travel Agency — platforms that sell cruise bookings online on behalf of operators)"
)

# ==================== LOAD DATA ====================
data = load_data()
bookings = data["bookings"]

# ==================== DETECT PARTNER COLUMN ====================
PARTNER_COLUMNS = ["partner_name", "ota_name", "booking_partner", "booking_channel"]
partner_col = next((c for c in PARTNER_COLUMNS if c in bookings.columns), None)

if not partner_col:
    st.error("No partner or channel column found in booking data.")
    st.stop()

# ==================== FILTERS ====================
st.sidebar.header("Filters")

date_option = st.sidebar.selectbox(
    "Choose a date range",
    [
        "Past 7 Days",
        "Past 30 Days",
        "Past 3 Months",
        "Past 6 Months",
        "All Time"
    ]
)

latest_date = bookings["booking_date"].max()

if date_option == "Past 7 Days":
    start_date = latest_date - timedelta(days=7)
elif date_option == "Past 30 Days":
    start_date = latest_date - timedelta(days=30)
elif date_option == "Past 3 Months":
    start_date = latest_date - timedelta(days=90)
elif date_option == "Past 6 Months":
    start_date = latest_date - timedelta(days=180)
else:
    start_date = bookings["booking_date"].min()

# ==================== APPLY FILTER ====================
filtered = bookings[bookings["booking_date"] >= start_date].copy()

# ==================== PARTNER METRICS ====================
partner_perf = (
    filtered
    .groupby(partner_col, as_index=False)
    .agg(
        Revenue=("total_booking_value", "sum"),
        Bookings=("booking_id", "count"),
        Cancellations=("booking_status", lambda x: (x == "Cancelled").sum())
    )
)

partner_perf["Cancellation Rate %"] = (
    partner_perf["Cancellations"] / partner_perf["Bookings"] * 100
)

# ==================== SECTION 1: REVENUE BY PARTNER ====================
st.subheader("💰 Revenue by Partner / OTA")

fig_revenue = px.bar(
    partner_perf.sort_values("Revenue"),
    x="Revenue",
    y=partner_col,
    orientation="h",
    color="Revenue",
    color_continuous_scale="Blues",
    title="Revenue Contribution by Partner"
)

st.plotly_chart(fig_revenue, use_container_width=True)
st.divider()

# ==================== SECTION 2: BOOKING SHARE ====================
st.subheader("🍩 Booking Share (Dependency View)")

fig_share = px.pie(
    partner_perf,
    names=partner_col,
    values="Bookings",
    hole=0.45,
    title="Booking Share by Partner"
)

st.plotly_chart(fig_share, use_container_width=True)
st.divider()

# ==================== SECTION 3: PARTNER CANCELLATION RISK ====================
st.subheader("🚫 Partners with Frequent Cancellations")

fig_cancel = px.bar(
    partner_perf.sort_values("Cancellation Rate %"),
    x="Cancellation Rate %",
    y=partner_col,
    orientation="h",
    color="Cancellation Rate %",
    color_continuous_scale="Reds",
    title="Cancellation Rate by Partner"
)

st.plotly_chart(fig_cancel, use_container_width=True)
st.divider()

# ==================== SECTION 4: UNDERPERFORMING PARTNERS ====================
st.subheader("⚠️ Underperforming Partners")

underperforming = partner_perf[
    (partner_perf["Cancellation Rate %"] > partner_perf["Cancellation Rate %"].median()) &
    (partner_perf["Revenue"] < partner_perf["Revenue"].median())
].sort_values("Cancellation Rate %", ascending=False)

if underperforming.empty:
    st.success("No major partner performance risks detected 🎉")
else:
    st.dataframe(
        underperforming.style.format({
            "Revenue": "₹ {:,.0f}",
            "Cancellation Rate %": "{:.1f}%"
        })
    )

# ==================== INSIGHT PANEL ====================
st.info(
    """
💡 **How to use this page**

- Review partners with high cancellation rates  
- Reduce dependency if one OTA dominates bookings  
- Renegotiate terms with high-risk partners  
- Promote direct or low-cancellation channels  
"""
)
