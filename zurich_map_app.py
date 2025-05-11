import streamlit as st
import folium
from folium.features import GeoJsonTooltip
import geopandas as gpd
from streamlit_folium import folium_static

# Page setup
st.set_page_config(page_title="Zurich Neighborhoods", layout="wide")
st.title("Zurich Neighborhood Map")

# Function to load GeoJSON data
@st.cache_data
def load_geojson(file_path):
    """Load GeoJSON file with neighborhood boundaries"""
    try:
        gdf = gpd.read_file(file_path)
        return gdf
    except Exception as e:
        st.error(f"Error loading GeoJSON: {e}")
        return None

# File uploader for GeoJSON
uploaded_file = st.sidebar.file_uploader("Upload Zurich GeoJSON file", type=['geojson', 'json'])

# Path input for existing file
geojson_path = st.sidebar.text_input(
    "Or enter the path to your GeoJSON file:",
    value=""  # Replace with default path to your file if you have one
)

# Decide which source to use
if uploaded_file is not None:
    # If file was uploaded, save it temporarily and use that
    with open("temp_geojson.json", "wb") as f:
        f.write(uploaded_file.getbuffer())
    gdf = load_geojson("temp_geojson.json")
elif geojson_path:
    # If path is provided, use that
    gdf = load_geojson(geojson_path)
else:
    st.info("Please upload a GeoJSON file with Zurich neighborhood boundaries or provide a file path.")
    st.stop()

if gdf is not None:
    # Check the columns in the GeoJSON to find the name property
    property_cols = [col for col in gdf.columns if col not in ['geometry']]
    
    # Try to identify name column (common name variations)
    name_options = ['name', 'Name', 'NAME', 'district', 'District', 'neighborhood', 
                   'Neighborhood', 'quartier', 'Quartier', 'bezeichnung', 'Bezeichnung']
    
    # Find the first matching column or default to first property
    name_column = next((col for col in name_options if col in property_cols), property_cols[0])
    
    # Let user select the name column if needed
    name_column = st.sidebar.selectbox(
        "Column containing neighborhood names:",
        options=property_cols,
        index=property_cols.index(name_column) if name_column in property_cols else 0
    )
    
    # Create the Folium map centered on Zurich
    m = folium.Map(
        location=[47.3769, 8.5417],
        zoom_start=12,
        tiles="CartoDB positron"
    )
    
    # Create a simple tooltip with just the neighborhood name
    tooltip = GeoJsonTooltip(
        fields=[name_column],
        aliases=["Neighborhood"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: white;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
            font-size: 14px;
            font-weight: bold;
            padding: 5px;
        """,
    )
    
    # Add the GeoJSON as a layer with hover interactivity
    folium.GeoJson(
        gdf,
        name="Neighborhoods",
        style_function=lambda x: {
            "fillColor": "#95B2B8",  # Light blue fill
            "color": "#333333",      # Dark grey boundary
            "weight": 2,             # Border thickness
            "fillOpacity": 0.4,      # Semi-transparent fill
        },
        highlight_function=lambda x: {
            "fillColor": "#FFD700",  # Gold highlight color
            "color": "#000000",      # Black boundary when highlighted
            "weight": 3,             # Thicker border when highlighted
            "fillOpacity": 0.6,      # More opaque when highlighted
        },
        tooltip=tooltip,
    ).add_to(m)
    
    # Display the map
    st.write("Hover over a neighborhood to see its name")
    folium_static(m, width=900, height=700)
    
    # Optional: Show a simple list of all neighborhoods
    with st.expander("Show list of all neighborhoods"):
        st.write(sorted(gdf[name_column].unique().tolist()))
else:
    st.error("No GeoJSON data loaded. Please check your file and try again.")
