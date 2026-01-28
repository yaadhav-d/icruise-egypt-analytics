import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data
def load_data():
    BASE_DIR = Path(__file__).resolve().parent
    file_path = BASE_DIR / "iCruiseEgypt_Sample_Data.xlsx"

    def safe_read(sheet_name):
        try:
            return pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception:
            return None

    # Prefer updated masters if available
    cruises = safe_read("Cruises_Updated") or safe_read("Cruises_Master")
    routes = safe_read("Routes_Updated") or safe_read("Routes_Master")

    partners = safe_read("Partners_Master")
    customers = safe_read("Customers")
    bookings = safe_read("Bookings")
    cancellations = safe_read("Cancellations")
    stops = safe_read("Excursion_Stops")  # optional, future-ready

    # ---------- Date conversions ----------
    if bookings is not None:
        if "booking_date" in bookings.columns:
            bookings["booking_date"] = pd.to_datetime(bookings["booking_date"])
        if "cruise_date" in bookings.columns:
            bookings["cruise_date"] = pd.to_datetime(bookings["cruise_date"])

    if customers is not None and "first_booking_date" in customers.columns:
        customers["first_booking_date"] = pd.to_datetime(customers["first_booking_date"])

    if cancellations is not None and "cancellation_date" in cancellations.columns:
        cancellations["cancellation_date"] = pd.to_datetime(cancellations["cancellation_date"])

    return {
        "cruises": cruises,
        "routes": routes,
        "partners": partners,
        "customers": customers,
        "bookings": bookings,
        "cancellations": cancellations,
        "stops": stops,
    }
