import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from data.data_loader import load_data

st.title("💰 Pricing, Discounts & Revenue Leakage")
st.caption("Understand pricing power, discount impact, and revenue efficiency.")

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

# ==================== SECTION 1: REVENUE PER SEAT ====================
st.subheader("📊 Revenue Efficiency by Cruise")

fig_rps = px.bar(
    pricing_perf.sort_values("Revenue per Seat"),
    x="Revenue per Seat",
    y="cruise_name",
    orientation="h",
    color="Revenue per Seat",
    color_continuous_scale="Blues",
    title="Revenue per Seat (Pricing Power)"
)

st.plotly_chart(fig_rps, use_container_width=True)
st.divider()

# ==================== SECTION 2: GROSS REVENUE ====================
st.subheader("💵 Gross Revenue by Cruise")

fig_gross = px.bar(
    pricing_perf.sort_values("Revenue"),
    x="Revenue",
    y="cruise_name",
    orientation="h",
    color="Revenue",
    color_continuous_scale="Teal",
    title="Gross Revenue by Cruise"
)

st.plotly_chart(fig_gross, use_container_width=True)
st.divider()

# ==================== SECTION 3: DISCOUNT ANALYSIS (ADAPTIVE) ====================
DISCOUNT_COLUMNS = ["discount_amount", "discount_percent", "discount_value"]
discount_col = next((c for c in DISCOUNT_COLUMNS if c in filtered.columns), None)

if discount_col:
    st.subheader("🏷️ Discount Impact Analysis")

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
        title="Total Discounts Given by Cruise"
    )

    st.plotly_chart(fig_discount, use_container_width=True)
    st.divider()

    st.subheader("⚠️ Over-Discounted Cruises")

    over_discounted = discount_df[
        discount_df["Discount_Total"] > discount_df["Discount_Total"].median()
    ]

    st.dataframe(over_discounted)

else:
    st.info(
        """
ℹ️ **Discount data not available**

- Discount-based insights are hidden  
- Showing pricing efficiency and revenue performance only  
"""
    )

st.divider()

# ==================== SECTION 4: REVENUE LEAKAGE ====================
st.subheader("🚨 Revenue Leakage (Low Yield Cruises)")

leakage = pricing_perf[
    pricing_perf["Revenue per Seat"] < pricing_perf["Revenue per Seat"].median()
].sort_values("Revenue per Seat")

if leakage.empty:
    st.success("No major revenue leakage detected 🎉")
else:
    st.dataframe(
        leakage[
            ["cruise_name", "Revenue", "Seats_Booked", "Revenue per Seat"]
        ].style.format({
            "Revenue": "₹ {:,.0f}",
            "Revenue per Seat": "₹ {:,.0f}"
        })
    )

# ==================== INSIGHT PANEL ====================
st.info(
    """
💡 **How to use this page**

- Identify cruises with strong pricing power  
- Reduce discount dependency where revenue per seat is healthy  
- Investigate low revenue-per-seat cruises for leakage  
- Optimize pricing before increasing marketing spend  
"""
)
