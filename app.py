
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --------------------------------
# 1. Page Configuration
# --------------------------------

st.set_page_config(
    page_title="Hotel Booking Dashboard",
    page_icon="🏨",
    layout="wide"
)

# --------------------------------
# 2. Load Dataset
# --------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("hotel_bookings_cleaned.csv")
    return df

data = load_data()

# Calculate total guests
data['Total_guests'] = (
    data['adults'].fillna(0) +
    data['children'].fillna(0) +
    data['babies'].fillna(0)
)

# --------------------------------
# 3. Dashboard Header
# --------------------------------

st.title("🏨 Hotel Booking Analytics")
st.markdown(
    "Explore hotel booking trends, customer behaviour, "
    "revenue and cancellation patterns."
)

st.divider()

# --------------------------------
# 4. Sidebar Filters
# --------------------------------

st.sidebar.title("Dashboard Filters")

hotel_options = ["All"] + sorted(
    data['hotel'].dropna().unique().tolist()
)

selected_hotel = st.sidebar.selectbox(
    "Select Hotel",
    hotel_options
)

market_options = sorted(
    data['market_segment'].dropna().unique().tolist()
)

selected_market = st.sidebar.multiselect(
    "Market Segment",
    market_options,
    default=market_options
)

year_options = sorted(
    data['arrival_date_year'].dropna().unique().tolist()
)

selected_year = st.sidebar.multiselect(
    "Arrival Year",
    year_options,
    default=year_options
)

# --------------------------------
# 5. Apply Filters
# --------------------------------

filtered_data = data.copy()

if selected_hotel != "All":
    filtered_data = filtered_data[
        filtered_data['hotel'] == selected_hotel
    ]

filtered_data = filtered_data[
    filtered_data['market_segment'].isin(selected_market)
]

filtered_data = filtered_data[
    filtered_data['arrival_date_year'].isin(selected_year)
]

# --------------------------------
# 6. KPI Calculations
# --------------------------------

total_bookings = len(filtered_data)

cancelled_bookings = filtered_data['is_canceled'].sum()

cancellation_rate = (
    cancelled_bookings / total_bookings * 100
    if total_bookings > 0 else 0
)

average_adr = filtered_data['adr'].mean()

total_guests = filtered_data['Total_guests'].sum()

# --------------------------------
# 7. KPI Cards
# --------------------------------

st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Bookings", f"{total_bookings:,}")

col2.metric(
    "Cancellation Rate",
    f"{cancellation_rate:.2f}%"
)

col3.metric(
    "Average ADR",
    f"€{average_adr:,.2f}" if pd.notna(average_adr) else "N/A"
)

col4.metric("Total Guests", f"{total_guests:,.0f}")

st.divider()

# --------------------------------
# 8. Market Segment Analysis
# --------------------------------

st.subheader("Booking Distribution by Market Segment")

market_counts = filtered_data['market_segment'].value_counts()

if not market_counts.empty:
    fig_market = px.pie(
        names=market_counts.index,
        values=market_counts.values,
        hole=0.4,
        title="Market Segment Distribution"
    )

    st.plotly_chart(
        fig_market,
        use_container_width=True
    )

# --------------------------------
# 9. Monthly Booking Trends
# --------------------------------

st.subheader("Monthly Booking Trends")

month_dict = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}

monthly_data = filtered_data.copy()

monthly_data['month_number'] = (
    monthly_data['arrival_date_month'].map(month_dict)
)

monthly_data['arrival_period'] = pd.to_datetime(
    dict(
        year=monthly_data['arrival_date_year'],
        month=monthly_data['month_number'],
        day=1
    ),
    errors='coerce'
)

monthly_bookings = (
    monthly_data.groupby('arrival_period')
    .size()
    .reset_index(name='Bookings')
    .sort_values('arrival_period')
)

fig_month = px.line(
    monthly_bookings,
    x='arrival_period',
    y='Bookings',
    markers=True,
    title='Monthly Booking Trends'
)

st.plotly_chart(
    fig_month,
    use_container_width=True
)

# --------------------------------
# 10. Cancellation Analysis
# --------------------------------

st.subheader("Booking Cancellation Analysis")

cancellation_data = (
    filtered_data['is_canceled']
    .map({0: 'Not Cancelled', 1: 'Cancelled'})
    .value_counts()
    .reset_index()
)

cancellation_data.columns = ['Booking Status', 'Count']

fig_cancel = px.bar(
    cancellation_data,
    x='Booking Status',
    y='Count',
    color='Booking Status',
    title='Cancelled vs Non-Cancelled Bookings'
)

st.plotly_chart(
    fig_cancel,
    use_container_width=True
)

# --------------------------------
# 11. Country Analysis
# --------------------------------

st.subheader("Top 10 Guest Countries")

country_data = (
    filtered_data['country']
    .dropna()
    .value_counts()
    .head(10)
    .reset_index()
)

country_data.columns = ['Country', 'Bookings']

fig_country = px.bar(
    country_data,
    x='Country',
    y='Bookings',
    title='Top 10 Countries by Bookings'
)

st.plotly_chart(
    fig_country,
    use_container_width=True
)

# --------------------------------
# 12. Footer
# --------------------------------

st.divider()

st.caption(
    "Hotel Booking Analytics Dashboard | "
    "Developed using Python, Pandas, Plotly and Streamlit"
)
