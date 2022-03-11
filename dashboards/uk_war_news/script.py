import pandas as pd

import altair as alt
import param
import panel as pn
alt.data_transformers.disable_max_rows()

pn.extension("vega", sizing_mode='stretch_width')

def get_data():
    uk_data = pd.read_csv("https://raw.githubusercontent.com/zhukovyuri/VIINA/master/Data/events_20220308110108.csv")
    uk_data["dt"] = pd.to_datetime(uk_data.date.astype(str) + "T"+ uk_data.time.astype(str), format="%Y%m%dT%H:%M")
    uk_data["date"] = pd.to_datetime(uk_data.date, format="%Y%m%d")
    uk_data["day_hour"] = pd.to_datetime(uk_data.date.astype(str) + "T"+ uk_data.time.astype(str).str.slice(stop=2), format="%Y%m%dT%H")

    news_origin = {"24tvua": "Ukrainian",
    "forbesua": "Ukrainian",
    "interfaxua": "Ukrainian",
    "kp": "Russian",
    "liga": "Ukrainian",
    "militarnyy": "Ukrainian",
    "mz": "Russian",
    "nv": "Ukrainian",
    "ng": "Russian",
    "ntv": "Russian",
    "pravdaua": "Ukrainian",
    "ria": "Russian",
    "unian": "Ukrainian"}

    uk_data["country_origin"] = uk_data.source.replace(news_origin)
    uk_data["content_military"] = uk_data.t_mil_pred.round() == 1
    uk_data["offensive_party"] = "none"
    uk_data.loc[(uk_data.a_rus_pred.round() == 1) & (uk_data.a_ukr_pred.round() == 0), "offensive_party"] = "russia"
    uk_data.loc[(uk_data.a_rus_pred.round() == 0) & (uk_data.a_ukr_pred.round() == 1), "offensive_party"] = "ukraine"
    uk_data.loc[(uk_data.a_rus_pred.round() == 1) & (uk_data.a_ukr_pred.round() == 1), "offensive_party"] = "both"
    return uk_data

uk_data = get_data()

offensive_party = alt.Chart(uk_data).mark_bar().encode(
    y="content_military",
    x="count(offensive_party)",
    color="offensive_party",
    row='country_origin:N'
)

country_origin = alt.Chart(uk_data).mark_bar().encode(
    y="country_origin",
    x="count(country_origin)"
)

hour_heatmap = alt.Chart(uk_data).mark_rect().encode(
    x='mounthdate(day_hour):O',
    y='hours(dt):O',
    color='count(event_id):Q'
)

topo_url = "https://raw.githubusercontent.com/org-scn-design-studio-community/sdkcommunitymaps/master/geojson/Europe/Ukraine-regions.json"
countries_topo = alt.topo_feature(topo_url, 'UKR_adm1')    
geomap = alt.Chart(countries_topo, width=900, height=380).mark_geoshape(stroke="white", color="lightgrey").encode().project("equirectangular")

timeline = alt.Chart(uk_data, width=900, height=250).mark_bar().encode(
    y=alt.Y(field='event_id', aggregate='count', type='quantitative'),
    x=alt.X('day_hour:T', ),
    color="country_origin"
)
timeline

selection = alt.selection("test", type="interval")

color = alt.condition(selection,
                      alt.Color('country_origin:N'),
                      alt.value('lightgray'))

lat_long_points = alt.Chart(uk_data).mark_point().encode(
    longitude='longitude:Q',
    latitude='latitude:Q',
    size=alt.value(20),
    tooltip=['source', 'dt', "url", "country_origin","text"],
    color=color
)
    
dashboard = (
    (geomap + lat_long_points.transform_filter(selection))
     & timeline.add_selection(selection).transform_filter(selection)
    & (offensive_party | country_origin).transform_filter(selection)
)

scatter = alt.Chart(uk_data).mark_point().encode(
    size=alt.value(1),
    x=alt.X('longitude:Q', scale=alt.Scale(range=(0, 350), zero=False)),
    y=alt.Y('latitude:Q', scale=alt.Scale(range=(165, 5), zero=False)),
)


timeline_filter = alt.Chart(uk_data, width=350, height=60).mark_line().encode(
    y=alt.Y(field='event_id', aggregate='count', type='quantitative'),
    x=alt.X('day_hour:T', )
)

filters = timeline_filter.add_selection(selection) & (
    geomap.properties(width=350, height=160) + scatter.add_selection(selection)
)
description = """# News on Ukraine war

On the left side, you can select a period of time or an area to filter the dashboard on the right side. Therefore click and drag to mark your area of intrest.

The dashboard was created from data of this repo: [https://github.com/zhukovyuri/VIINA](https://github.com/zhukovyuri/VIINA)
"""
ab = pn.Column(description, filters | dashboard, height=2000)
ab.servable()    