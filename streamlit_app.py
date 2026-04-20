import streamlit as st
import pickle
import numpy as np
import folium
from streamlit_folium import st_folium
import random

# Load trained model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

st.title(" Waterborne Disease Prediction")

# ---------------- INPUTS ----------------
st.subheader("Enter Water Quality Parameters")

# Blank inputs
pH = st.text_input("pH")
turbidity = st.text_input("Turbidity (NTU)")
temperature = st.text_input("Temperature (°C)")
conductivity = st.text_input("Conductivity (µS/cm)")
tds = st.text_input("TDS (mg/L)")
hardness = st.text_input("Hardness (mg/L)")

# Safe float conversion
def safe_float(x):
    try:
        return float(x)
    except:
        return None

pH = safe_float(pH)
turbidity = safe_float(turbidity)
temperature = safe_float(temperature)
conductivity = safe_float(conductivity)
tds = safe_float(tds)
hardness = safe_float(hardness)

# Weather
weather = st.selectbox("Weather Condition", ["Sunny", "Rainy", "Cloudy", "Humid"])

# Locations
locations = {
    "Delhi": (28.7041, 77.1025),
    "Mumbai": (19.0760, 72.8777),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Bangalore": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Kanpur": (26.4499, 80.3319),
    "Nagpur": (21.1458, 79.0882),
    "Indore": (22.7196, 75.8577),
    "Thane": (19.2183, 72.9781),
    "Bhopal": (23.2599, 77.4126)
}
location_name = st.selectbox("Location", list(locations.keys()))
lat, lon = locations[location_name]

# Encode weather
weather_dict = {"Sunny": 0, "Rainy": 1, "Cloudy": 2, "Humid": 3}
weather_encoded = weather_dict[weather]

# Disease mapping
disease_map = {
    0: {"name": "Cholera", "solution": "Boil water before drinking, maintain hygiene, use ORS, wash hands frequently, avoid street food.", "medicine": "ORS, Zinc supplements, Doxycycline (as prescribed).", "color": "red"},
    1: {"name": "Dysentery", "solution": "Use clean water, avoid contaminated food, maintain hand hygiene, keep surroundings clean, wash fruits/vegetables.", "medicine": "Metronidazole, Ciprofloxacin (as prescribed), Hydration with ORS.", "color": "blue"},
    2: {"name": "Typhoid", "solution": "Vaccinate, drink purified water, wash hands frequently, avoid raw food, maintain personal hygiene.", "medicine": "Ciprofloxacin, Azithromycin, Paracetamol for fever (as prescribed).", "color": "green"},
    3: {"name": "Hepatitis A", "solution": "Vaccinate, drink safe water, wash hands before eating, avoid raw or undercooked food.", "medicine": "Rest, hydration, avoid alcohol, medications for symptoms as prescribed.", "color": "orange"},
    4: {"name": "Giardiasis", "solution": "Use clean water, wash fruits and vegetables properly, maintain hygiene, avoid swimming in contaminated water.", "medicine": "Metronidazole, Tinidazole (as prescribed), maintain hydration.", "color": "purple"}
}

# Initialize session state
if "prediction" not in st.session_state:
    st.session_state.prediction = None
if "map" not in st.session_state:
    st.session_state.map = None

# ---------------- PREDICTION ----------------
if st.button("Predict"):
    if None in [pH, turbidity, temperature, conductivity, tds, hardness]:
        st.error(" Please fill in all input values before predicting.")
    else:
        features = np.array([[pH, turbidity, temperature, conductivity, tds, hardness]])
        try:
            prediction = model.predict(features)[0]
            st.session_state.prediction = disease_map.get(
                prediction,
                {"name": "Unknown", "solution": "No solution.", "medicine": "N/A", "color": "gray"}
            )

            # Create map centered at user location
            m = folium.Map(location=[lat, lon], zoom_start=6)

            # User location marker
            folium.CircleMarker(
                location=[lat, lon],
                radius=15,
                color="black",
                weight=2,
                fill=True,
                fill_color=st.session_state.prediction.get('color', 'gray'),
                fill_opacity=0.7,
                popup=f"{location_name}: {st.session_state.prediction.get('name', 'Unknown')}",
                tooltip=st.session_state.prediction.get('name', 'Unknown')
            ).add_to(m)

            # Other demo markers
            for loc_name, (lat_o, lon_o) in locations.items():
                if loc_name == location_name:
                    continue
                d_idx = random.choice(list(disease_map.keys()))
                color = disease_map[d_idx]["color"]
                folium.CircleMarker(
                    location=[lat_o, lon_o],
                    radius=10,
                    color="black",
                    weight=2,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    popup=f"{loc_name}: {disease_map[d_idx]['name']}",
                    tooltip=disease_map[d_idx]['name']
                ).add_to(m)

            # Legend
            legend_items = "".join(
                [f'<div style="margin:2px"><span style="background:{d["color"]};'
                 f'width:12px;height:12px;border-radius:50%;display:inline-block;"></span> {d["name"]}</div>'
                 for d in disease_map.values()]
            )
            legend_html = f"""
            <div style="
                 position: fixed; 
                 bottom: 50px; left: 50px; width: 200px; height: auto; 
                 background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                 padding: 10px; color:black; font-weight:bold;">
            <b>Disease Legend</b><br>
            {legend_items}
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))

            st.session_state.map = m

        except Exception as e:
            st.error(f"Error making prediction: {e}")

# ---------------- RESULTS ----------------
if st.session_state.prediction:
    st.subheader(f"  Location: {location_name}")
    st.markdown(f"###  Predicted Disease: **{st.session_state.prediction.get('name', 'Unknown')}**")
    st.markdown(f"###  Precautions / Suggested Measures:\n{st.session_state.prediction.get('solution', 'No solution.')}")
    st.markdown(f"###  Recommended Medicines / Treatment:\n{st.session_state.prediction.get('medicine', 'N/A')}")

if st.session_state.map:
    st_folium(st.session_state.map, width=700, height=500)
