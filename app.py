import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy

# @st.dialog("Welcome!")
# def modal_dialog():
#     st.write("Hello")
 
@st.cache_data #decorator
def load_data(path):
    df = pd.read_csv(path)
    return df
@st.cache_data
def load_json(path):
    with open(path) as f:
        data = json.load(f)
    return data

## Load data
df_raw = load_data(path = "data/volcano_ds_pop.csv")

geojson = load_json(path = "data/countries.geojson")

# Data processing
dfv = deepcopy(df_raw)
dfv.drop("Unnamed: 0", axis=1, inplace=True)
df_contries = dfv.groupby(by=["Country"])["Volcano Name"].count().reset_index(name="num_volcanes")
gj_names = {f['properties']['ADMIN'] for f in geojson['features']}
df_names = set(df_contries['Country'])
# los que están en el DF pero NO en el geojson
missing = sorted(df_names - gj_names)

dfv["Country"] = dfv["Country"].replace({
    "United States" : "United States of America"
})
df_contries = dfv.groupby(by=["Country"])["Volcano Name"].count().reset_index(name="num_volcanes")

# Show fig - Map
fig = go.Figure(go.Choroplethmap(
    geojson=geojson,
    locations=df_contries["Country"],                 # llave en tu DF
    z=df_contries["num_volcanes"],                   # valor a colorear
    featureidkey="properties.ADMIN",          # llave en el GeoJSON
    colorscale="Viridis",
    colorbar_title="Volcanes",
    marker_line_width=0.2,
    showscale=True,
    hovertemplate="<b>%{location}</b><br>Volcanes: %{z}<extra></extra>"
))

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    title="Number of volcanoes per country",
    map_zoom=1, map_center = {"lat": -35.6751, "lon": -71.5430}, # latitud de Chile:)
    margin=dict(r=0,l=0,t=40,b=0), width=800
    )

# Top 5 anotado
top5 = df_contries.sort_values("num_volcanes", ascending=False).head(5)
# mi anotación lo deje como un javascript, 
anotation = "<br>".join(f"<span style='color:blue'>{fila.Country}: {fila.num_volcanes}" for fila in top5.itertuples())

fig.add_annotation(
    x=0.02, y=0.02, xref="paper", yref="paper",
    text=f"<b style='color:black'>Top 5 countries</b><br>{anotation}",  # usan javascript
    showarrow=False, bgcolor="white", borderpad=2
)

# Show fig_volcano - Scatter Map

fig_volcano = px.scatter_map(dfv, 
                             lat='Latitude', lon='Longitude', 
                             color='Type', 
                             hover_name='Volcano Name', 
                             hover_data=['Type','Country','Status','Region'], 
                             zoom=2 )
fig_volcano.update_geos(fitbounds="locations", visible=False)
fig_volcano.update_layout(
    title="Volcanes in the World",
    map_zoom=1, map_center = {"lat": -35.6751, "lon": -71.5430}, # latitud de Chile:)
    margin=dict(r=0,l=0,t=40,b=0), 
    width=800, showlegend=False 
    )
# mi anotación lo deje como un javascript, 
anotation = "<br>".join(f"<span style='color:blue'>{fila.Country}: {fila.num_volcanes}" for fila in top5.itertuples())

fig_volcano.add_annotation(
    x=0.02, y=0.02, xref="paper", yref="paper",
    text=f"<b style='color:black'>Top 5 countries</b><br>{anotation}",  # usan javascript
    showarrow=False, bgcolor="white", borderpad=2
)
fig_volcano.update_layout(title_font_size = 22)

# Streamlit App
st.title("Volcanoes in the World")
st.header("Volcanoes Exploration")

if st.checkbox("Show Dataframe"):
    st.subheader("This is my dataset:")
    st.dataframe(data=dfv)
    
left_col, right_col = st.columns([2,2]) # estas columnas son las ventanas no tiene que ver con el dataframe

countries = ["All"] + sorted(pd.unique(df_contries["Country"]))
country = left_col.selectbox("Choose a Country", countries)
if country == "All":
    reduced_df = df_contries
else:
    reduced_df = df_contries[df_contries["Country"] == country]
    left_col.write(f"Number of Volcanoes in {country}")
    left_col.write(reduced_df)
        
plot_types = ["Number_Volcanos_Country", "Location_Volcanos_World"]
plot_type = right_col.radio("Choose Plot type", plot_types)

if plot_type == "Number_Volcanos_Country":
    st.plotly_chart(fig)
else:
    st.plotly_chart(fig_volcano)