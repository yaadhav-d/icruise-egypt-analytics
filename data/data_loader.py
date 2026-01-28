import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data
def load_data():
    BASE_DIR = Path(__file__).resolve().parent
    file_path = BASE_DIR / "iCruiseEgypt_Sample_Data.xlsx"

    cruises = pd.read_excel(file_path, sheet_name="Cruises_Master")
    routes = pd.read_excel(file_path, sheet_name="Routes_Master")
    partners = pd.read_excel(file_path, sheet_name="Partners_Master")
    customers = pd.read_excel(file_path, sheet_name="Customers")
    bookings = pd.read_excel(file_path, sheet_name="Bookings")
    cancellations = pd.read_excel(file_path, sheet_name="Cancellations")

    # Date conversions
    bookings["booking_date"] = pd.to_datetime(bookings["booking_date"])
    bookings["cruise_date"] = pd.to_datetime(bookings["cruise_date"])
    customers["first_booking_date"] = pd.to_datetime(customers["first_booking_date"])
    cancellations["cancellation_date"] = pd.to_datetime(cancellations["cancellation_date"])

    return {
        "cruises": cruises,
        "routes": routes,
        "partners": partners,
        "customers": customers,
        "bookings": bookings,
        "cancellations": cancellations,
    }
