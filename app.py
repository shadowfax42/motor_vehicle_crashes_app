import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# DATA source: https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95

DATA_URL = ("data/Motor_Vehicle_Collisions.csv")


st.title("Motor Vehicle Collisions in New York City")
st.markdown("This is a Streamlit dashboard used to visualize/analyze"
            "Motor Vehicle Collisions 💥🚗 in New York City 🗽")

@st.cache(persist=True)
def load_data(numrows):
    data = pd.read_csv(DATA_URL, nrows=numrows)
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.columns = data.columns.str.replace(' ', '_')
    data['crash_date_time'] = data['crash_date'].astype(str) + ' ' + data['crash_time'].astype(str)
    data.rename(columns={'crash_date_time': 'date/time', 'number_of_persons_injured': 'injured_persons', 'number_of_pedestrians_injured':'injured_pedestrians',
                     'number_of_motorist_injured':'injured_motorists'}, inplace=True)
    data['date/time'] = pd.to_datetime(data['date/time'])
    # data.drop(columns=['crash_date', 'crash_time'], inplace=True)

    # pop date/time column from the dataframe
    # first_col = data.pop('date/time')
    # insert the column at the first position
    # data.insert(0, 'date/time', first_col)
    return data


# load 100000 rows from the data
data = load_data(100000)

original_data = data
st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19) # 19 injuries is the max in the dataset
st.map(data.query("injured_persons >= @injured_people")[['latitude', 'longitude']].dropna(how="any"))

st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0,23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1)))

midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 15,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time', 'latitude', 'longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 200,
        extruded = True,
        pickable = True,
        elevation_scale = 4,
        elevation_range = [0, 1000],
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))

filtered = data[
    (data['date/time'].dt.hour >= hour) & (data["date/time"].dt.hour < (hour + 1))
    ]
hist = np.histogram(filtered["date/time"].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})
fig = px.bar(chart_data, x="minute", y="crashes", hover_data=['minute', "crashes"], height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected class of people")
select = st.selectbox("Affected type of people", ["Pedestrians", "Cyclists", "Motorists"])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how="any")[:5])
elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how="any")[:5])
else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how="any")[:5])


if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)



