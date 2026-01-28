import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from data.data_loader import load_data

st.title("💰 Pricing, Discounts & Revenue Leakage")
st.caption("Evaluate pricing efficiency, discount dependency, and revenue quality.")

# ==================== LOAD DATA ====================
data = load_data()
bookings = data["bookings"]
cruises = data["cruises"]

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
filtered = filtered.merge(cruises, on="cruise_id", how="left")

# ==================== BASE PRICING METRICS ====================
pricing_perf = (
    filtered
    .groupby(["cruise_id", "cruise_name", "total_seats"], as_index=False)
    .agg(
        Revenue=("total_booking_value", "sum"),
        Seats_Booked=("seats_booked", "sum"),
        Bookings=("booking_id", "count")
    )
)

pricing_perf["Revenue per Seat"] = (
    pricing_perf["Revenue"] / pricing_perf["Seats_Booked"]
)

median_rps = pricing_perf["Revenue per Seat"].median()

# ==================== SECTION 1: PRICING EFFICIENCY ====================
st.subheader("📊 Pricing Efficiency (Revenue per Seat)")

fig_rps = px.bar(
    pricing_perf.sort_values("Revenue per Seat"),
    x="Revenue per Seat",
    y="cruise_name",
    orientation="h",
    color="Revenue per Seat",
    color_continuous_scale="Blues",
    title="Revenue per Seat — Indicator of Pricing Power"
)

st.plotly_chart(fig_rps, use_container_width=True)

st.caption(
    "ℹ️ Cruises below the median revenue per seat indicate weak pricing efficiency or excessive discounting."
)

st.divider()

# ==================== SECTION 2: GROSS REVENUE ====================
st.subheader("💵 Gross Revenue Contribution")

fig_gross = px.bar(
    pricing_perf.sort_values("Revenue"),
    x="Revenue",
    y="cruise_name",
    orientation="h",
    color="Revenue",
    color_continuous_scale="Teal",
    title="Total Revenue by Cruise"
)

st.plotly_chart(fig_gross, use_container_width=True)
st.divider()

# ==================== SECTION 3: DISCOUNT ANALYSIS ====================
DISCOUNT_COLUMNS = ["discount_amount", "discount_percent", "discount_value"]
discount_col = next((c for c in DISCOUNT_COLUMNS if c in filtered.columns), None)

if discount_col:
    st.subheader("🏷️ Discount Dependency Risk")

    discount_df = (
        filtered
        .groupby("cruise_name", as_index=False)
        .agg(
            Discount_Total=(discount_col, "sum"),
            Revenue=("total_booking_value", "sum"),
            Bookings=("booking_id", "count")
        )
    )

    fig_discount = px.bar(
        discount_df.sort_values("Discount_Total"),
        x="Discount_Total",
        y="cruise_name",
        orientation="h",
        color="Discount_Total",
        color_continuous_scale="Reds",
        title="Total Discounts Applied by Cruise"
    )

    st.plotly_chart(fig_discount, use_container_width=True)

    st.caption(
        "⚠️ High discount dependency may increase bookings but reduce net revenue quality."
    )

    st.divider()

else:
    st.info(
        """
ℹ️ **Discount data not available**

Discount-based risk analysis is hidden.
Pricing efficiency and revenue quality insights are still shown.
"""
    )

# ==================== SECTION 4: LOW PRICING EFFICIENCY (ACTION REQUIRED) ====================
st.subheader("🚨 Low Pricing Efficiency — Action Required")

low_efficiency = pricing_perf[
    pricing_perf["Revenue per Seat"] < median_rps
].sort_values("Revenue per Seat")

if low_efficiency.empty:
    st.success("No pricing efficiency risks detected 🎉")
else:
    st.dataframe(
        low_efficiency[
            ["cruise_name", "Revenue", "Seats_Booked", "Revenue per Seat"]
        ].style.format({
            "Revenue": "₹ {:,.0f}",
            "Revenue per Seat": "₹ {:,.0f}"
        })
    )

# ==================== STRATEGIC INSIGHT ====================
st.info(
    """
💡 **Why this matters**

- Revenue per seat reflects true pricing efficiency, not just volume  
- Excessive discounting can hide weak demand or poor pricing strategy  
- Improving pricing efficiency often delivers higher returns than increasing marketing spend  

This view supports **pricing optimization, discount control, and revenue quality improvement**.
"""
)
