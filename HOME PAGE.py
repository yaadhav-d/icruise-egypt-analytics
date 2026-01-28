import streamlit as st

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="iCruiseEgypt Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown(
    """
    <style>
    /* Background */
    .stApp {
        background-image: linear-gradient(
            rgba(0, 0, 0, 0.35),
            rgba(0, 0, 0, 0.35)
        ),
        url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Hero section */
    .hero {
        padding: 5rem 3rem;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(8px);
        color: white;
        text-align: center;
    }

    .hero h1 {
        font-size: 3rem;
        font-weight: 700;
    }

    .hero p {
        font-size: 1.2rem;
        opacity: 0.9;
    }

    /* Card layout */
    .card {
        background: rgba(255, 255, 255, 0.12);
        padding: 1.8rem;
        border-radius: 14px;
        color: white;
        backdrop-filter: blur(6px);
        height: 100%;
    }

    .card h3 {
        margin-bottom: 0.6rem;
    }

    /* Section spacing */
    .section {
        margin-top: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================== HERO SECTION ====================
st.markdown(
    """
    <div class="hero">
        <h1>🚢 iCruiseEgypt Analytics</h1>
        <p>
            A unified intelligence platform for cruise operators, partners, and decision-makers.
        </p>
        <p>
            Turn bookings, routes, pricing, and partners into clear business actions.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ==================== VALUE CARDS (ROW 1) ====================
st.markdown('<div class="section"></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="card">
            <h3>📊 Executive Visibility</h3>
            <p>
                Get a real-time view of revenue, occupancy, cancellations,
                and overall business health — all in one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="card">
            <h3>🧭 Operational Insights</h3>
            <p>
                Understand which routes, cruises, and schedules are performing
                well and which need immediate attention.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="card">
            <h3>💰 Revenue Control</h3>
            <p>
                Monitor pricing efficiency, discounts, cancellations,
                and revenue leakage before they hurt profitability.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==================== SECOND ROW (2 CARDS) ====================
st.markdown('<div class="section"></div>', unsafe_allow_html=True)

col4, col5 = st.columns(2)

with col4:
    st.markdown(
        """
        <div class="card">
            <h3>🤝 Partner & OTA Scorecards</h3>
            <p>
                Identify high-performing partners and risky OTAs
                based on revenue, booking share, and cancellations.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col5:
    st.markdown(
        """
        <div class="card">
            <h3>👥 Customer Intelligence</h3>
            <p>
                Track new vs repeat customers, loyalty patterns,
                and high-value customers driving your revenue.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==================== HOW TO USE ====================
st.markdown('<div class="section"></div>', unsafe_allow_html=True)

st.info(
    """
💡 **How to use this dashboard**

- Use the **sidebar** to navigate between analytics sections  
- Start with **Executive Overview** for a quick business snapshot  
- Drill down into **Routes, Pricing, Partners, and Customers**  
- Use insights to optimize pricing, routes, and partnerships  

This dashboard is designed by Yaadhav.
"""
)
