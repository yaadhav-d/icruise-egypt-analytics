import streamlit as st
import pandas as pd
from datetime import timedelta
from data.data_loader import load_data

st.title("📊 Executive Overview")

# -------------------- LOAD DATA --------------------
data = load_data()
bookings = data["bookings"]
cruises = data["cruises"]
routes = data["routes"]

# -------------------- FILTERS --------------------
st.sidebar.header("Filters")

# Preset date ranges
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

selected_routes = st.sidebar.multiselect(
    "Route",
    options=routes["route_name"].unique()
)

selected_cruises = st.sidebar.multiselect(
    "Cruise",
    options=cruises["cruise_name"].unique()
)

# -------------------- APPLY FILTERS --------------------
filtered = bookings[bookings["booking_date"] >= start_date]

if selected_routes:
    route_ids = routes[routes["route_name"].isin(selected_routes)]["route_id"]
    filtered = filtered[filtered["route_id"].isin(route_ids)]

if selected_cruises:
    cruise_ids = cruises[cruises["cruise_name"].isin(selected_cruises)]["cruise_id"]
    filtered = filtered[filtered["cruise_id"].isin(cruise_ids)]

# -------------------- KPIs --------------------
total_revenue = filtered["total_booking_value"].sum()
total_bookings = len(filtered)

cancelled = filtered[filtered["booking_status"] == "Cancelled"]
cancellation_rate = (len(cancelled) / total_bookings * 100) if total_bookings else 0

seats_booked = filtered["seats_booked"].sum()
total_seats = cruises["total_seats"].sum()
occupancy = (seats_booked / total_seats * 100) if total_seats else 0

# -------------------- DISPLAY KPIs --------------------
col1, col2, col3, col4 = st.columns([2.2, 1.2, 1.3, 1.1])

col1.metric("Total Revenue", f"₹ {total_revenue:,.0f}")
col2.metric("Occupancy %", f"{occupancy:.1f}%")
col3.metric("Cancellation Rate", f"{cancellation_rate:.1f}%")
col4.metric("Total Bookings", total_bookings)

st.divider()

# -------------------- TREND --------------------
st.subheader("Revenue Trend")

trend = (
    filtered.groupby("booking_date")["total_booking_value"]
    .sum()
    .reset_index()
)

st.line_chart(trend, x="booking_date", y="total_booking_value")
