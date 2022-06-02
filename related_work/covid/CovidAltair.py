# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.0
#   kernelspec:
#     display_name: Python [conda env:ds]
#     language: python
#     name: conda-env-ds-py
# ---

# + slideshow={"slide_type": "skip"}
#import pyforest

# + slideshow={"slide_type": "skip"}
#pyforest.active_imports()

# + slideshow={"slide_type": "skip"}
import altair as alt
alt.data_transformers.disable_max_rows()
# -

# ## Get Data

from pathlib import Path

# +
#https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0

file = Path("data/RKI_COVID19.csv")
import pandas as pd
date_parser = lambda x : pd.to_datetime(x.replace("Uhr", ""), errors="coerce")

date_cols = ["Meldedatum","Datenstand","Refdatum"]
categories = ["Bundesland", "Landkreis","Altergruppe", "Geschlecht","IdLandkreis"]
cat_dict = dict(zip(categories, ["category"]*len(categories)))


if not file.exists():
    pd.read_csv("https://opendata.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0.csv").to_csv(file)   
rki_data = pd.read_csv(file, dtype=cat_dict)

for col in date_cols:
    rki_data[col] = pd.to_datetime(rki_data[col].str.replace("Uhr",""))
    
ddr = ["Mecklenburg","Brandenburg","Sachsen-Anhalt","Sachsen","Thüringen"]
rki_data["ddr"] = rki_data.Bundesland.isin(ddr)
# -

print(rki_data.Meldedatum.max())

data_landkreise = pd.read_csv("data/RKI_Corona_Landkreise.csv")
data_bundesländer = pd.read_csv("data/RKI_Corona_Bundesländer.csv")

rki_data = rki_data.join(data_landkreise.set_index("county")[["GEN","cases7_bl_per_100k","cases7_bl","death7_bl","cases7_lk","death7_lk","cases7_per_100k"]], on="Landkreis")

rki_data["fälle_100_kreis"] = rki_data.join(data_landkreise.set_index("county").EWZ, on="Landkreis").pipe(lambda df: df.AnzahlFall / (df.EWZ / 100000))
rki_data["fälle_100_land"] = rki_data.join(data_bundesländer.set_index("LAN_ew_GEN").LAN_ew_EWZ, on="Bundesland").pipe(lambda df: df.AnzahlFall / (df.LAN_ew_EWZ / 100000))

# + [markdown] slideshow={"slide_type": "slide"}
# # Grammar of Graphics
#
# * [Buch](https://www.springer.com/de/book/9780387245447) von Wilkinson, Leland aus 2005
#
# ![](https://miro.medium.com/max/1800/1*mcLnnVdHNg-ikDbHJfHDNA.png)

# + [markdown] slideshow={"slide_type": "subslide"}
# * Data => [Chart](https://altair-viz.github.io/user_guide/data.html) + [Transformations](https://altair-viz.github.io/user_guide/transform/index.html)
# * Aesthetics => [encodings](https://altair-viz.github.io/user_guide/encoding.html)
# * Scale => [Scales](https://altair-viz.github.io/user_guide/scale_resolve.html)
# * Geometric objects => [Marks](https://altair-viz.github.io/user_guide/marks.html)
# * Statistics => [BuildIn vega-lite Aggregations](https://vega.github.io/vega-lite/docs/aggregate.html#ops)
# * Facets => Compound Charts (https://altair-viz.github.io/user_guide/compound_charts.html)
# * Coordinate system => ? [Map](https://altair-viz.github.io/gallery/index.html#maps)
# -

# # Basic Examples

# ## Pandas API

rki_data.groupby("Meldedatum").AnzahlFall.sum().rolling(7).mean().plot.line()

pd.__version__

fig = rki_data.groupby("Meldedatum").AnzahlFall.sum().rolling(7).mean().plot.line(backend="altair")
fig

pd.Series(rki_data.Landkreis.unique()).apply(lambda s: s.split(" ")[0]).value_counts().plot.barh(backend="altair")

rki_data.groupby(["Bundesland", "Geschlecht"]).AnzahlFall.sum().unstack().plot.barh(stacked=True, backend="altair")

# ## Altair syntax
#
# * Chart: Which Data Source
# * Marks. How to represent (Chart Type)
# * Encodings:
#     * [Channels](https://altair-viz.github.io/user_guide/encoding.html#encoding-channels): X-Axis, Y-Axis, Color, Size
#     * [Encode Data Type](https://altair-viz.github.io/user_guide/encoding.html#encoding-data-types): Quantiative, Ordinal, Nominal

# +
source = rki_data.groupby("Meldedatum").AnzahlFall.sum().reset_index()

alt.Chart(source).mark_line().encode(
    x="Meldedatum:T", 
    y="AnzahlFall:Q"
).properties(width=1000).interactive()
# -

# ## Custom Order oder Colors

# +
fälle_je_tag_bundesland = rki_data.query("Meldedatum > '2020-08-15'").groupby(["Altersgruppe","Meldedatum"])["fälle_100_land"].sum().fillna(0).reset_index()
rolling_fall_bundesland = fälle_je_tag_bundesland.groupby(["Altersgruppe"]).rolling(7, on="Meldedatum")["fälle_100_land"].mean().fillna(0).reset_index()

ages = ['unbekannt','A00-A04', 'A05-A14', 'A15-A34','A35-A59', 'A60-A79', 'A80+'][::-1]

timeline_age = alt.Chart(rolling_fall_bundesland).mark_area().encode(
    x="Meldedatum:T", 
    y="fälle_100_land:Q", 
    tooltip="Altersgruppe",
    color=alt.Color('Altersgruppe', scale=alt.Scale(scheme='spectral'), sort=ages)
)
timeline_age

# +
fälle_je_tag_bundesland = rki_data.query("Meldedatum > '2020-08-15'").groupby(["Geschlecht","Meldedatum"])["AnzahlFall"].sum().fillna(0).reset_index()
rolling_fall_bundesland = fälle_je_tag_bundesland.groupby(["Geschlecht"]).rolling(7, on="Meldedatum")["AnzahlFall"].mean().fillna(0).reset_index()

timeline_sex= alt.Chart(rolling_fall_bundesland).mark_line().encode(
    x="Meldedatum:T", y="AnzahlFall:Q", color="Geschlecht"
)
timeline_sex
# -

# # Aggregations

group = ["Altersgruppe","Geschlecht","Bundesland"]
fälle_je_tag_bundesland = rki_data.query("Meldedatum > '2020-05-15'").groupby(group + ["Meldedatum"])["AnzahlFall"].sum().fillna(0).reset_index()
rolling_fall_bundesland = fälle_je_tag_bundesland.groupby(group).rolling(7, on="Meldedatum")["AnzahlFall"].mean().fillna(0).reset_index()


rolling_fall_bundesland

agg_timeline = alt.Chart(rolling_fall_bundesland).mark_area().encode(
    x="Meldedatum:T", 
    y="sum(AnzahlFall):Q", 
    tooltip="Altersgruppe:N",
    color=alt.Color('Altersgruppe:N', sort=ages)
)
agg_timeline

agg_timeline.encode(
    column='Geschlecht',
    row='Bundesland'
)

# # Combining Charts

# +
# Pandas Syntax
mean = rki_data.groupby("Meldedatum").AnzahlFall.sum().plot.line(backend="altair")
rolling = rki_data.groupby("Meldedatum").AnzahlFall.sum().rolling(7).mean().plot.line(backend="altair")

comb = (mean + rolling).properties(width=1000)
#for l in comb.layer:
#    l.selection = alt.Undefined
comb

# +
summed = rki_data.groupby("Meldedatum").AnzahlFall.sum()

actual = alt.Chart(summed.reset_index()).mark_line()
rolling = alt.Chart(summed.rolling(7).mean().reset_index()).mark_line().encode(
    color=alt.value("orange")
)

comb = (actual + rolling).encode(
    x="Meldedatum:T", 
    y="AnzahlFall:Q"
).properties(width=1000)
comb
# -

timeline_age | timeline_age.encode(y=alt.Y("fälle_100_land:Q", stack="normalize"))

timeline_sex | timeline_sex.mark_area()

# +
multi_select = alt.selection_multi(encodings=['color'])

(timeline_age.add_selection(multi_select) | timeline_age.transform_filter(multi_select).add_selection(multi_select)).resolve_scale(y='shared')
# -

# # Interaction & Scales

data = data_landkreise[["GEN", "BL", "BEZ","EWZ", "cases7_lk","death7_lk","cases7_per_100k","cases7_bl_per_100k"]]
alt.Chart(data).mark_circle().encode(
    x=alt.X("EWZ", scale=alt.Scale(type="log", zero=False)),
    y="cases7_per_100k",
    color="BL",
    tooltip=['GEN', 'BL', 'cases7_lk', 'cases7_per_100k']
).interactive()

# +
brush = alt.selection(type='interval', encodings=['x'])

upper = comb.encode(
    alt.X('Meldedatum:T', scale=alt.Scale(domain=brush))
)

lower = comb.properties(
    height=60
).add_selection(brush)

upper & lower
# -

# # Geo-Data

# ## Get Data

import json
from urllib.request import urlopen
map_url = "https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json"
json_data = json.loads(urlopen(map_url).read())
states = [c.get("properties").get("name") for c in json_data.get("objects").get("states").get("geometries")]
json_data.get("objects").get("states").get("geometries")[0].keys()


# Missing matched
conainted = pd.Series({
    e.get("properties").get("name"): e.get("properties").get("name") in data_landkreise.GEN.to_list()
    for e in json_data.get("objects").get("counties").get("geometries")
})
conainted.loc[conainted==False]

json_data.get("objects").get("counties").get("geometries")[0].get("properties")

# ## Simple Map

counties = alt.topo_feature(map_url, 'states')
alt.Chart(counties).mark_geoshape().encode(
    text='properties.name:N',
    tooltip='properties.name:N'
)

# +
highlight = alt.selection_single(on='mouseover', fields=['Bundesland'], empty='none')
bundesland_cnt = rki_data.groupby("Bundesland").size().to_frame("cnt").reset_index()

counties = alt.topo_feature(map_url, 'states')
county_map = alt.Chart(counties).mark_geoshape().encode(
    color=alt.condition(highlight, alt.value('red'), 'Bundesland:N'),
    text='name:N'
).transform_lookup(
    lookup='properties.name',
    from_=alt.LookupData(bundesland_cnt, 'Bundesland', ['Bundesland','cnt'])
)

county_map.add_selection(highlight)
# -

fälle_je_tag_bundesland = rki_data.query("Meldedatum > '2020-10-15'").groupby(["Bundesland","Meldedatum"])["fälle_100_land"].sum().fillna(0).reset_index()
rolling_fall_bundesland = fälle_je_tag_bundesland.groupby(["Bundesland"]).rolling(7, on="Meldedatum")["fälle_100_land"].mean().fillna(0).reset_index()
line = alt.Chart(rolling_fall_bundesland).mark_line().encode(
    x="Meldedatum:T", 
    y="fälle_100_land:Q", 
    color="Bundesland",
    tooltip=['Bundesland', 'fälle_100_land']
)
line

agg_timeline

# +
sel_neg = alt.selection_multi(fields=["Bundesland"], empty='none')
sel = alt.selection_multi(fields=["Bundesland"])

fig = county_map.encode(
    color=alt.condition(sel_neg, alt.value('red'), 'cnt:Q'),
).add_selection(sel).add_selection(sel_neg)

fig | (line.transform_filter(sel) & \
       agg_timeline.transform_filter(sel)
      ).resolve_scale(color='independent')
# -

# # Landkreise

# +
data = data_landkreise[["GEN", "BL", "BEZ", "cases7_lk","death7_lk","cases7_per_100k","cases7_bl_per_100k"]]

brush = alt.selection_interval(empty='none', zoom=False)
brush = alt.selection_interval(fields=['GEN:N'], empty='none', zoom=False)

color = alt.condition(sel_neg,
                      alt.Color('BL:N', legend=None),
                      alt.value('lightgray'))

scatter = alt.Chart(data).mark_circle().encode(
    x=alt.X("cases7_lk", scale=alt.Scale(type="log", zero=False)),
    y="cases7_per_100k",
    color=color,
    tooltip=['GEN', 'BL', 'cases7_lk', 'cases7_per_100k']
).add_selection(sel_neg)#.interactive()

# +
#category = "Bundesland"
category = "Landkreis"
if category == "Bundesland":
    map_data = alt.topo_feature(map_url, 'states')
if category == "Landkreis":
    map_data = alt.topo_feature(map_url, 'counties')

#cnt_data = rki_data.groupby(["GEN","Bundesland"]).size().to_frame("cnt")
#cnt_data = rki_data.loc[rki_data.Meldedatum == rki_data.Meldedatum.max()].groupby(["GEN"]).cases7_lk.mean().to_frame("cnt").reset_index()
#cnt_data = rki_data.groupby(["GEN","Meldedatum"]).AnzahlFall.sum().reset_index().pipe(lambda df: df.loc[df.groupby("GEN").Meldedatum.idxmax()])

cnt_data = data_landkreise[["GEN", "BL", "BEZ", "cases7_lk","death7_lk","cases7_per_100k","cases7_bl_per_100k"]]

sel_neg = alt.selection_multi(fields=["GEN"], init=[{'GEN': 'Köln'}, {'GEN': 'Frankfurt am Main'}], empty='none')
sel = alt.selection_multi(fields=["GEN"], init=[{'GEN': 'Köln'}, {'GEN': 'Frankfurt am Main'}])


fälle_je_tag = rki_data.query("Meldedatum > '2020-10-15'").groupby(["GEN","Meldedatum"])["fälle_100_kreis"].sum().fillna(0).reset_index()
rolling_fall = fälle_je_tag.groupby(["GEN"]).rolling(7, on="Meldedatum")["fälle_100_kreis"].mean().fillna(0).reset_index()

timeline = alt.Chart(rolling_fall).mark_line().encode(
    x="Meldedatum:T", 
    y="fälle_100_kreis:Q", 
    color="GEN",
    tooltip=["GEN"]
)

county_map = alt.Chart(map_data).mark_geoshape().encode(
    color=alt.condition(sel_neg, alt.value('red'), 'cases7_per_100k:Q'),
    tooltip='GEN:N',
).transform_lookup(
    lookup='properties.name',
    from_=alt.LookupData(cnt_data, "GEN", ["GEN",'cases7_per_100k'])
).add_selection(sel).add_selection(sel_neg)

county_map.properties(width=500, height=800) | timeline.transform_filter(sel) & scatter
# -

# # Conclusion 
#
# ## Strengths
#
# * Modular, Logical Concept
# * Interactions!
# * Support on Geo-Data
# * Handling of [many data](https://altair-viz.github.io/user_guide/faq.html#maxrowserror-how-can-i-plot-large-datasets)
# * [Flexibility](https://www.youtube.com/watch?v=SNaWwk_HzK0)
#         
# ## Weaknesses
#
# * Cumbersome definitions
# * Sometimes unclear behaivor
# * Still some bugs and missing support for elementary things ([See my issues](https://github.com/altair-viz/altair/issues?q=author%3Akrlng+))
#
# ## When do I use what?
#
# * Typical static Chart: Seaborn
# * Complex static Chart: Matplotlib
# * Typical interactive Chart: Plotly Express
# * Complex interactive Chart: Altair

# # Sonstiges

# +
brush = alt.selection_interval() 


legend_selection = alt.selection_multi(fields=['set'], bind='legend')

#
chart = alt.Chart(data.query("(training_points <65000) & (rel<2)")).mark_circle().encode(
    alt.X('training_points', scale=alt.Scale(zero=False)),
    alt.Y("rel"),
    color=alt.condition(brush | legend_selection, 'set:N', alt.value('lightgray'), sort=sorter)
).add_selection(brush).add_selection(legend_selection).properties(width=800)

bar =  alt.Chart(data, width=800).mark_bar().encode(y=alt.Y("set",sort=sorter)).transform_filter( brush ).properties(width=300)

err_bars = bar.encode(x=alt.X("average(rel)", scale=alt.Scale(zero=False)), color=alt.condition(legend_selection, "stdev(rel):Q", alt.value('lightgray'), sort=sorter))
est_bars = bar.encode(x=alt.X("average(params_n_estimators_)", scale=alt.Scale(domain=(100,1000))), color=alt.condition(legend_selection, "stdev(params_n_estimators_):Q", alt.value('lightgray'), sort=sorter))
fit_bars = bar.encode(x=alt.X("average(fit_time)", scale=alt.Scale(zero=False)), color=alt.condition(legend_selection, "stdev(fit_time):Q", alt.value('lightgray'), sort=sorter))
cnt_bars = bar.encode(x="count(fit_time)")
chart &  (((err_bars | est_bars) & (fit_bars | cnt_bars)).resolve_scale(color = 'independent') )

# +
source = data.set_index("set").rel.clip(0,2).reset_index()

best_set = source.groupby("set").rel.mean().idxmin()
selection = alt.selection_single(fields=["set"], init={'set': best_set})
ticks = alt.Chart(source, width=800, height=200).mark_tick().encode(
    y="set:N", 
    x="rel:Q",
    color=alt.condition(selection, alt.value('navy'), alt.value('lightgray'))
).add_selection(selection)

hist = alt.Chart(source).mark_bar().encode(
    alt.X('rel:Q', bin=alt.Bin(1, step=0.05)),
    alt.Y('count():Q'),
)

density = alt.Chart(source).transform_bin(
    "binned_rel", "rel", bin=alt.Bin(1, step=0.05)
).transform_density(
    'binned_rel',
    as_=['rel', 'density'],
    counts=True,
).mark_area().encode(
    alt.X('rel:Q'),
    alt.Y('density:Q'),
    opacity=alt.value(0.5)
)

ticks & (hist + density).resolve_scale(
    y='independent'
).transform_filter(
    selection
).properties(width=800, height=200)
