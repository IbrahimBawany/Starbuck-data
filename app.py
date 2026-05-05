"""
Name: Ibrahim Bawany
CS230: Section 3
Data: Starbucks Data

Description: This program explores Starbucks stores throughout the world and can be
filtered by ownership type, number of stores per city, and country.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import pycountry

st.set_page_config(layout="wide")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("starbuck_directory.csv")
df.columns = df.columns.str.strip().str.replace(" ", "_")

# Fix coordinates
if "Latitude" in df.columns:
    df.rename(columns={"Latitude": "lat", "Longitude": "lon"}, inplace=True)

df = df.dropna(subset=["Country", "lat", "lon"])

# -----------------------------
# FULL COUNTRY NAMES
# -----------------------------
def get_country_name(code):
    code = str(code).strip().upper()
    try:
        return pycountry.countries.get(alpha_2=code).name
    except:
        try:
            return pycountry.countries.get(alpha_3=code).name
        except:
            return code

df["Country"] = df["Country"].apply(get_country_name)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

# Only countries with enough data
valid_countries = df["Country"].value_counts()
valid_countries = valid_countries[valid_countries > 10].index

# [ST1]
country = st.sidebar.selectbox("Select Country", sorted(valid_countries))

# Ownership filter (dynamic)
ownership_types = sorted(
    df[df["Country"] == country]["Ownership_Type"].dropna().unique()
)
ownership = st.sidebar.selectbox("Select Ownership Type", ownership_types)

# [ST2]
min_stores = st.sidebar.slider("Minimum Stores in City", 1, 50, 1)

# -----------------------------
# FUNCTIONS
# -----------------------------
# [FUNC2P]
def filter_and_prepare(data, country, ownership, min_stores=1):
    # [FILTER1]
    filtered = data[
        (data["Country"] == country) &
        (data["Ownership_Type"] == ownership)
    ]

    city_counts = filtered["City"].value_counts()

    # [FILTER2]
    valid_cities = city_counts[city_counts >= min_stores].index
    filtered = filtered[filtered["City"].isin(valid_cities)]

    return filtered, city_counts  # [FUNCRETURN2]

# [FUNCCALL2]
filtered_df, city_counts = filter_and_prepare(df, country, ownership, min_stores)
filtered_df, city_counts = filter_and_prepare(df, country, ownership, min_stores)

if filtered_df.empty:
    st.warning("No data for selected filters.")
    st.stop()

# [COLUMNS]
filtered_df["City_Count"] = filtered_df["City"].map(city_counts)

# [SORT]
filtered_df = filtered_df.sort_values(by="City_Count", ascending=False)

# -----------------------------
# LOOP + DICTIONARY
# -----------------------------
# [ITERLOOP]
total_stores = 0
for val in city_counts:
    total_stores += val

# [DICTMETHOD]
example_dict = {"A": 1, "B": 2}
keys = example_dict.keys()
values = example_dict.values()

# -----------------------------
# LOGO + TITLE
# -----------------------------
col1, col2 = st.columns([1, 6])

with col1:
    st.image("starbucks_logo.png", width=100)

with col2:
    st.title("STARBUCKS STORES DATA EXPLORER")  # [ST3]

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3 = st.tabs(["🗺 Map", "📊 Charts", "📋 Data"])

# -----------------------------
# MAP
# -----------------------------
with tab1:
    st.subheader("Store Locations")

    # [MAP]
    view_state = pdk.ViewState(
        latitude=filtered_df["lat"].mean(),
        longitude=filtered_df["lon"].mean(),
        zoom=8
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position='[lon, lat]',
        get_radius=200,
        get_color=[0, 120, 0],
        pickable=True
    )

    tooltip = {
        "html": """
            <b>Store #:</b> {Store_Number}<br/>
            <b>City:</b> {City}<br/>
            <b>Country:</b> {Country}<br/>
            <b>Ownership:</b> {Ownership_Type}
        """,
        "style": {"backgroundColor": "black", "color": "white"}
    }

    st.pydeck_chart(pdk.Deck(
        initial_view_state=view_state,
        layers=[layer],
        tooltip=tooltip
    ))

# -----------------------------
# CHARTS
# -----------------------------
with tab2:
    st.subheader("Top Cities")

    city_counts = filtered_df["City"].value_counts().head(10)

    # [CHART1]
    fig1, ax1 = plt.subplots()
    city_counts.plot(kind="bar", color="green", ax=ax1)
    ax1.set_title("Top Cities by Store Count")
    ax1.set_ylabel("Stores")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # [CHART2]
    fig2, ax2 = plt.subplots()
    city_counts.plot(kind="pie", autopct='%1.1f%%', ax=ax2)
    ax2.set_title("Store Distribution")
    ax2.set_ylabel("")
    st.pyplot(fig2)

# -----------------------------
# DATA TABLE
# -----------------------------
with tab3:
    st.subheader("Filtered Data")
    st.dataframe(filtered_df)

# -----------------------------
# INSIGHTS
# -----------------------------
st.subheader("Insights")

# [MAXMIN]
st.write("Total Stores:", total_stores)
st.write("Top City:", filtered_df["City"].value_counts().idxmax())
st.write("Lowest City:", filtered_df["City"].value_counts().idxmin())