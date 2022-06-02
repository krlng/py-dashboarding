import streamlit as st
import pandas as pd
from datetime import datetime as dt
import datetime

import plotly.express as px

st.title('New Cases per Continent')

@st.cache
def load_data():
    raw_data = pd.read_csv("https://covid.ourworldindata.org/data/owid-covid-data.csv")
    countries = raw_data.dropna(subset=["continent"])
    countries = countries.assign(date = pd.to_datetime(countries.date).dt.date)
    return countries.groupby(["date","continent"])["new_cases"].sum().reset_index()

def display_continent(aggregation, start_date):
    plot_df = df.loc[df.date > start_date]
    plot_df = plot_df.groupby("continent").rolling(aggregation, on="date").new_cases.mean().reset_index()
    chart =  px.line(plot_df, x="date", y="new_cases", color="continent", title="New Cases per continent")
    st.plotly_chart(chart)

df = load_data()
aggregation_period = st.number_input(min_value=1, max_value=30, value=7, step=1, label="Aggregation")
start_date = st.date_input("Start date", (dt.today()-datetime.timedelta(days=365)).date())
display_continent(aggregation_period, start_date)
