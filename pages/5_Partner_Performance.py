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

# ==================== DEFINE RISK LOGIC ====================
cancel_median = partner_perf["Cancellation Rate %"].median()
revenue_median = partner_perf["Revenue"].median()

partner_perf["Risk Category"] = partner_perf.apply(
    lambda x: "High Risk"
    if (x["Cancellation Rate %"] > cancel_median and x["Revenue"] < revenue_median)
    else "Stable",
    axis=1
)

# ==================== SECTION 1: REVENUE BY PARTNER ====================
st.subheader("💰 Revenue Contribution by Partner / OTA")

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
st.subheader("🚫 Cancellation Risk by Partner")

fig_cancel = px.bar(
    partner_perf.sort_values("Cancellation Rate %"),
    x="Cancellation Rate %",
    y=partner_col,
    orientation="h",
    color="Cancellation Rate %",
    color_continuous_scale="Reds",
    title="Partners with Frequent Cancellations"
)

st.plotly_chart(fig_cancel, use_container_width=True)
st.divider()

# ==================== SECTION 4: HIGH-RISK PARTNERS ====================
st.subheader("⚠️ High-Risk Partners (Action Required)")

high_risk = partner_perf[partner_perf["Risk Category"] == "High Risk"] \
    .sort_values("Cancellation Rate %", ascending=False)

if high_risk.empty:
    st.success("No high-risk partners detected for this period 🎉")
else:
    st.dataframe(
        high_risk[
            [partner_col, "Revenue", "Bookings", "Cancellation Rate %", "Risk Category"]
        ].style.format({
            "Revenue": "₹ {:,.0f}",
            "Cancellation Rate %": "{:.1f}%"
        })
    )

# ==================== STRATEGIC INSIGHT ====================
st.info(
    """
💡 **Why this matters**

- High cancellation partners may inflate booking volume but reduce net revenue  
- Heavy dependency on a single OTA increases operational risk  
- These risks are typically **not visible in customer-facing booking platforms**  

This view supports **partner renegotiation, promotion control, and channel strategy decisions**.
"""
)
