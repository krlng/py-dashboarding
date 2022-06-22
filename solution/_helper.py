import altair as alt
import plotly.express as px

def construct_groups(countries, single_important_countries = ["China", "United States"]):
    # Create a list of interesting metrics that keep truth by aggregation
    summable_metrics = ['co2', 'trade_co2', 'cement_co2','coal_co2', 'flaring_co2', 'gas_co2', 'oil_co2', 'other_industry_co2','consumption_co2', 'total_ghg', 'total_ghg_excluding_lucf', 'methane','nitrous_oxide', 'population', 'gdp', 'primary_energy_consumption']
    aggregations = dict(zip(summable_metrics, ["sum"] * len(summable_metrics)))

    # Split the list of countries into groups
    filter_term = countries.country.isin(single_important_countries)
    groups = countries.loc[~filter_term].fillna(0).groupby(["continent", "year"]).agg(aggregations).reset_index()

    groups_important_countries = countries.loc[filter_term, ["country"] + list(groups.columns)].rename(columns={"country": "name"})

    groups["name"] = groups.continent
    groups = groups.append(groups_important_countries)
    groups = groups.assign(co2_per_capita = groups.co2 / groups.population * 10e5).sort_values("year")
    return groups


def plot_area(df, select_y, **kwargs):
    return px.area(df, y=select_y, x="year", color="name")

def plot_line(df, select_y, **kwargs):
    return alt.Chart(df, width=1009, height=250).mark_line().encode(
        x="year", 
        y=select_y,
        color="name"
    )#.interactive()

def plot_connected_lines(df, select_y, **kwargs):
    chart = alt.Chart(df.query("year>1900"),
        height=600,
        width=1000,
    ).mark_circle().encode(
        x="co2",
        y=select_y,
        color="name:N",
        order="year",
        tooltip=["name", "year"]
    )
    return chart + chart.mark_trail().encode()
