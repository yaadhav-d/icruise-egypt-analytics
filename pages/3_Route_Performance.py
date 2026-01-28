import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from data.data_loader import load_data

st.title("🚢 Route & Cruise Performance")
st.caption(
    "Evaluate route demand and cruise efficiency using real iCruiseEgypt itineraries "
    "and cruise durations."
)

# ==================== LOAD DATA ====================
data = load_data()
bookings = data["bookings"]
cruises = data["cruises"]
routes = data["routes"]

# ==================== NORMALIZE IDS (CRITICAL FIX) ====================
if "cruise_id" in bookings.columns and "cruise_id" in cruises.columns:
    bookings["cruise_id"] = bookings["cruise_id"].astype(str)
    cruises["cruise_id"] = cruises["cruise_id"].astype(str).str.replace("C", "", regex=False)

if "route_id" in bookings.columns and "route_id" in routes.columns:
    bookings["route_id"] = bookings["route_id"].astype(str)
    routes["route_id"] = routes["route_id"].astype(str).str.replace("R", "", regex=False)

# ==================== FILTERS ====================
st.sidebar.header("Filters")

date_option = st.sidebar.selectbox(
    "Choose a date range",
    ["Past 7 Days", "Past 30 Days", "Past 3 Months", "Past 6 Months", "All Time"]
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
filtered = filtered.merge(routes, on="route_id", how="left")

# ==================== ROUTE LABEL ====================
if "origin" in filtered.columns and "destination" in filtered.columns:
    filtered["Route"] = filtered["origin"] + " → " + filtered["destination"]
else:
    filtered["Route"] = filtered["route_name"]

# ==================== SECTION 1: ROUTE REVENUE ====================
st.subheader("🗺️ Revenue by Route (Origin → Destination)")

route_revenue = (
    filtered
    .groupby("Route", as_index=False)
    .agg(
        Revenue=("total_booking_value", "sum"),
        Bookings=("booking_id", "count")
    )
)

fig_route = px.bar(
    route_revenue.sort_values("Revenue"),
    x="Revenue",
    y="Route",
    orientation="h",
    color="Revenue",
    color_continuous_scale="Blues",
    title="Revenue Contribution by Real Cruise Routes"
)

st.plotly_chart(fig_route, use_container_width=True)
st.divider()

# ==================== SECTION 2: CRUISE OCCUPANCY ====================
st.subheader("🛳️ Cruise Capacity Utilization")

# ---- SAFE GROUP BY (ADAPTIVE TO DATASET) ----
base_dims = ["cruise_name", "total_seats"]
optional_dims = []

for col in ["cruise_type", "duration_nights"]:
    if col in filtered.columns:
        optional_dims.append(col)

group_cols = base_dims + optional_dims

cruise_perf = (
    filtered
    .groupby(group_cols, as_index=False)
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
    title="Cruise Occupancy (Capacity Utilization)"
)

st.plotly_chart(fig_occupancy, use_container_width=True)
st.divider()

# ==================== SECTION 3: UNDERPERFORMING CRUISES ====================
st.subheader("⚠️ Underperforming Cruises — Action Required")

underperforming = cruise_perf[
    (cruise_perf["Occupancy %"] < median_occupancy) &
    (cruise_perf["Revenue"] < median_revenue)
]

if underperforming.empty:
    st.success("No underperforming cruises detected 🎉")
else:
    st.dataframe(
        underperforming.style.format({
            "Occupancy %": "{:.1f}%",
            "Revenue": "₹ {:,.0f}"
        })
    )

# ==================== STRATEGIC INSIGHT ====================
st.info(
    """
💡 **Why this matters**

- Aligns analytics with real iCruiseEgypt routes and cruises  
- Prevents capacity waste on low-performing itineraries  
- Supports route planning, pricing, and scheduling decisions  
"""
)
