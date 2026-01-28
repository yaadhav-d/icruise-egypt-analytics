import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from data.data_loader import load_data

st.title("🚢 Route & Cruise Performance")
st.caption(
    "Evaluate route demand, capacity utilization, and cruise-level efficiency "
    "to support scheduling, pricing, and promotion decisions."
)

# -------------------- LOAD DATA --------------------
data = load_data()
bookings = data["bookings"]
cruises = data["cruises"]
routes = data["routes"]

# -------------------- FILTERS --------------------
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

# -------------------- APPLY FILTER --------------------
filtered = bookings[bookings["booking_date"] >= start_date].copy()
filtered = filtered.merge(cruises, on="cruise_id", how="left")
filtered = filtered.merge(routes, on="route_id", how="left")

# ==================== SECTION 1: ROUTE REVENUE ====================
st.subheader("🗺️ Route Revenue Concentration")

route_revenue = (
    filtered
    .groupby("route_name", as_index=False)
    .agg(
        Revenue=("total_booking_value", "sum"),
        Bookings=("booking_id", "count")
    )
)

fig_route = px.bar(
    route_revenue.sort_values("Revenue"),
    x="Revenue",
    y="route_name",
    orientation="h",
    color="Revenue",
    color_continuous_scale="Blues",
    title="Revenue Contribution by Route"
)

st.plotly_chart(fig_route, use_container_width=True)

st.caption(
    "ℹ️ Routes with consistently low revenue contribution may require reduced frequency, "
    "pricing review, or targeted promotions."
)

st.divider()

# ==================== SECTION 2: CRUISE OCCUPANCY ====================
st.subheader("🛳️ Capacity Utilization by Cruise")

cruise_perf = (
    filtered
    .groupby(["cruise_id", "cruise_name", "total_seats"], as_index=False)
    .agg(
        Seats_Booked=("seats_booked", "sum"),
        Revenue=("total_booking_value", "sum"),
        Sailings=("booking_id", "count")
    )
)

cruise_perf["Occupancy %"] = (
    cruise_perf["Seats_Booked"] / cruise_perf["total_seats"] * 100
)

median_occupancy = cruise_perf["Occupancy %"].median()
median_revenue = cruise_perf["Revenue"].median()

fig_occupancy = px.bar(
    cruise_perf.sort_values("Occupancy %"),
    x="Occupancy %",
    y="cruise_name",
    orientation="h",
    color="Occupancy %",
    color_continuous_scale="Teal",
    title="Cruise Occupancy — Capacity Utilization Efficiency"
)

st.plotly_chart(fig_occupancy, use_container_width=True)
st.divider()

# ==================== SECTION 3: REVENUE vs UTILIZATION ====================
st.subheader("📊 Revenue vs Capacity Utilization (Decision View)")

fig_perf = px.bar(
    cruise_perf.sort_values("Revenue"),
    x="Revenue",
    y="cruise_name",
    orientation="h",
    color="Occupancy %",
    color_continuous_scale="Teal",
    title="Cruise Revenue with Capacity Utilization Context"
)

st.plotly_chart(fig_perf, use_container_width=True)
st.divider()

# ==================== SECTION 4: UNDERPERFORMING CRUISES ====================
st.subheader("⚠️ Underperforming Cruises — Action Required")

underperforming = cruise_perf[
    (cruise_perf["Occupancy %"] < median_occupancy) &
    (cruise_perf["Revenue"] < median_revenue)
].sort_values("Occupancy %")

if underperforming.empty:
    st.success("No underperforming cruises detected for this period 🎉")
else:
    st.dataframe(
        underperforming[
            ["cruise_name", "Occupancy %", "Revenue", "Seats_Booked"]
        ].style.format({
            "Occupancy %": "{:.1f}%",
            "Revenue": "₹ {:,.0f}"
        })
    )

# ==================== STRATEGIC INSIGHT ====================
st.info(
    """
💡 **Why this matters**

- Low occupancy indicates inefficient capacity usage  
- Low revenue despite active sailings suggests pricing or demand mismatch  
- These cruises may require schedule changes, pricing optimization, or route reassessment  

This view supports **capacity planning, route optimization, and promotion strategy decisions**.
"""
)
