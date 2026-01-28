import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from data.data_loader import load_data

st.title("🚢 Route & Cruise Performance")
st.caption("Identify high-performing routes and underperforming cruises.")

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
st.subheader("🗺️ Revenue by Route")

route_revenue = (
    filtered
    .groupby("route_name", as_index=False)
    .agg(
        Revenue=("total_booking_value", "sum"),
        Bookings=("booking_id", "count")
    )
)

fig_route = px.bar(
    route_revenue,
    x="route_name",
    y="Revenue",
    color="route_name",
    text="Revenue",
    title="Revenue Contribution by Route"
)

fig_route.update_traces(textposition="outside")

st.plotly_chart(fig_route, use_container_width=True)
st.divider()

# ==================== SECTION 2: CRUISE OCCUPANCY ====================
st.subheader("🛳️ Cruise Occupancy")

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

fig_occupancy = px.bar(
    cruise_perf.sort_values("Occupancy %"),
    x="Occupancy %",
    y="cruise_name",
    orientation="h",
    color="Occupancy %",
    title="Occupancy Percentage by Cruise"
)

st.plotly_chart(fig_occupancy, use_container_width=True)
st.divider()

# ==================== SECTION 3: CRUISE PERFORMANCE (REPLACED) ====================
st.subheader("📊 Cruise Performance Overview")

fig_perf = px.bar(
    cruise_perf.sort_values("Revenue"),
    x="Revenue",
    y="cruise_name",
    orientation="h",
    color="Occupancy %",
    color_continuous_scale="Teal",
    title="Revenue by Cruise (Color = Occupancy %)",
    text="Revenue"
)

fig_perf.update_traces(textposition="outside")

fig_perf.update_layout(
    xaxis_title="Total Revenue",
    yaxis_title="Cruise"
)

st.plotly_chart(fig_perf, use_container_width=True)
st.divider()

# ==================== SECTION 4: UNDERPERFORMING CRUISES ====================
st.subheader("⚠️ Underperforming Cruises")

underperforming = cruise_perf[
    (cruise_perf["Occupancy %"] < 50) &
    (cruise_perf["Revenue"] < cruise_perf["Revenue"].median())
].sort_values("Occupancy %")

if underperforming.empty:
    st.success("No severely underperforming cruises in this period 🎉")
else:
    st.dataframe(
        underperforming[
            ["cruise_name", "Occupancy %", "Revenue", "Seats_Booked"]
        ].style.format({
            "Occupancy %": "{:.1f}",
            "Revenue": "₹ {:,.0f}"
        })
    )

# ==================== INSIGHT PANEL ====================
st.info(
    """
💡 **How to use this page**

- Compare revenue performance across cruises  
- Use color intensity to spot low-occupancy risks  
- Focus promotions on high-occupancy but low-revenue cruises  
- Review underperformers for pricing or route changes  
"""
)


