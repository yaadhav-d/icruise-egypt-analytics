import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from data.data_loader import load_data

st.title("👥 Customer Behavior & Loyalty")
st.caption("Understand customer loyalty, repeat behavior, and revenue concentration.")

# ==================== LOAD DATA ====================
data = load_data()
bookings = data["bookings"]
customers = data["customers"]

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

# ==================== CUSTOMER METRICS ====================
customer_perf = (
    filtered
    .groupby("customer_id", as_index=False)
    .agg(
        Bookings=("booking_id", "count"),
        Revenue=("total_booking_value", "sum")
    )
)

# New vs Repeat
customer_perf["Customer Type"] = customer_perf["Bookings"].apply(
    lambda x: "Repeat Customer" if x > 1 else "New Customer"
)

# ==================== SECTION 1: NEW VS REPEAT (DONUT) ====================
st.subheader("🍩 New vs Repeat Customers")

type_df = (
    customer_perf["Customer Type"]
    .value_counts()
    .reset_index()
)

type_df.columns = ["Customer Type", "Customers"]

fig_type = px.pie(
    type_df,
    names="Customer Type",
    values="Customers",
    hole=0.45,
    color_discrete_map={
        "New Customer": "#1f77b4",
        "Repeat Customer": "#2ca02c"
    },
    title="Customer Loyalty Split"
)

st.plotly_chart(fig_type, use_container_width=True)
st.divider()

# ==================== SECTION 2: BOOKING FREQUENCY ====================
st.subheader("📊 Booking Frequency per Customer")

freq_df = (
    customer_perf
    .groupby("Bookings", as_index=False)
    .agg(Customers=("customer_id", "count"))
)

fig_freq = px.bar(
    freq_df,
    x="Bookings",
    y="Customers",
    color="Customers",
    color_continuous_scale="Blues",
    title="How Often Customers Book"
)

st.plotly_chart(fig_freq, use_container_width=True)
st.divider()

# ==================== SECTION 3: REVENUE CONCENTRATION ====================
st.subheader("🧱 Revenue Concentration (Top Customers)")

customer_perf_sorted = customer_perf.sort_values("Revenue", ascending=False)
top_20_percent = int(len(customer_perf_sorted) * 0.2)

top_customers = customer_perf_sorted.head(top_20_percent)
other_customers = customer_perf_sorted.tail(len(customer_perf_sorted) - top_20_percent)

revenue_split = pd.DataFrame({
    "Group": ["Top 20% Customers", "Other Customers"],
    "Revenue": [
        top_customers["Revenue"].sum(),
        other_customers["Revenue"].sum()
    ]
})

fig_rev_split = px.pie(
    revenue_split,
    names="Group",
    values="Revenue",
    hole=0.4,
    color_discrete_sequence=["#ff7f0e", "#aec7e8"],
    title="Revenue Contribution by Customer Group"
)

st.plotly_chart(fig_rev_split, use_container_width=True)
st.divider()

# ==================== SECTION 4: HIGH VALUE CUSTOMERS ====================
st.subheader("⭐ High-Value Customers")

high_value = customer_perf_sorted.head(10)

st.dataframe(
    high_value.style.format({
        "Revenue": "₹ {:,.0f}"
    })
)

# ==================== INSIGHT PANEL ====================
st.info(
    """
💡 **How to use this page**

- A high repeat share indicates strong customer loyalty  
- Too many one-time customers means retention needs improvement  
- Top 20% customers usually drive most revenue  
- Focus offers and loyalty programs on high-value repeat customers  
"""
)
