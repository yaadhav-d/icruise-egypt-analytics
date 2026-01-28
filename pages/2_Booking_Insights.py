import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from data.data_loader import load_data

st.title("📈 Booking & Demand Insights")
st.caption("How customers book, where they come from, and how early they plan.")

# -------------------- LOAD DATA --------------------
data = load_data()
bookings = data["bookings"]
customers = data["customers"]

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

# -------------------- APPLY FILTERS --------------------
filtered = bookings[bookings["booking_date"] >= start_date].copy()

filtered = filtered.merge(
    customers,
    on="customer_id",
    how="left"
)

# ==================== SECTION 1: BOOKING TREND ====================
st.subheader("📅 Booking Volume Trend")

trend = (
    filtered
    .assign(day=filtered["booking_date"].dt.date)
    .groupby("day", as_index=False)
    .agg(Bookings=("booking_id", "count"))
)

trend.rename(columns={"day": "booking_date"}, inplace=True)

fig_trend = px.area(
    data_frame=trend,
    x="booking_date",
    y="Bookings",
    title="Daily Booking Volume",
)

fig_trend.update_layout(
    xaxis_title="Date",
    yaxis_title="Bookings",
    hovermode="x unified"
)


st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ==================== SECTION 2: CHANNEL & DEVICE ====================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🧭 Booking Channel Mix")

    channel_df = (
        filtered
        .groupby("booking_channel", as_index=False)
        .agg(Bookings=("booking_id", "count"))
    )

    fig_channel = px.bar(
        channel_df,
        x="Bookings",
        y="booking_channel",
        orientation="h",
        color="booking_channel",
        title="Bookings by Channel",
        text="Bookings"
    )

    fig_channel.update_traces(textposition="outside")

    st.plotly_chart(fig_channel, use_container_width=True)

with col2:
    st.subheader("📱 Device Usage")

    device_df = (
        filtered
        .groupby("device_type", as_index=False)
        .agg(Bookings=("booking_id", "count"))
    )

    fig_device = px.pie(
        device_df,
        names="device_type",
        values="Bookings",
        hole=0.45,
        title="Device Split"
    )

    st.plotly_chart(fig_device, use_container_width=True)

st.divider()

# ==================== SECTION 3: BOOKING LEAD TIME ====================
st.subheader("⏳ Booking Lead Time Behavior")

filtered["lead_time_days"] = (
    filtered["cruise_date"] - filtered["booking_date"]
).dt.days

filtered["booking_behavior"] = filtered["lead_time_days"].apply(
    lambda x: "Early Booking (15+ days)" if x >= 15 else "Last-Minute Booking (<15 days)"
)

lead_df = (
    filtered
    .groupby("booking_behavior", as_index=False)
    .agg(Bookings=("booking_id", "count"))
)

fig_lead = px.bar(
    lead_df,
    x="booking_behavior",
    y="Bookings",
    color="booking_behavior",
    title="Early vs Last-Minute Bookings",
    text="Bookings"
)

fig_lead.update_traces(textposition="outside")

st.plotly_chart(fig_lead, use_container_width=True)

st.divider()

# ==================== SECTION 4: CUSTOMER ORIGIN ====================
st.subheader("🌍 Customer Origin")

origin_df = (
    filtered
    .groupby("customer_type", as_index=False)
    .agg(Bookings=("booking_id", "count"))
)

fig_origin = px.bar(
    origin_df,
    x="customer_type",
    y="Bookings",
    color="customer_type",
    title="Domestic vs International Demand",
    text="Bookings"
)

fig_origin.update_traces(textposition="outside")

st.plotly_chart(fig_origin, use_container_width=True)

# ==================== INSIGHT PANEL ====================
st.info(
    """
💡 **How to use this page**

- Identify which booking channels deserve more marketing spend  
- Improve mobile experience if mobile share is high  
- Adjust pricing strategy if last-minute bookings dominate  
- Track growth in international demand for expansion planning  
"""
)

