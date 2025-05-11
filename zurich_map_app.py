import streamlit as st
import folium
from folium.features import GeoJsonTooltip
import geopandas as gpd
from streamlit_folium import folium_static
import branca.colormap as cm

# Page setup with German text and enhanced styling
st.set_page_config(
    page_title="Zürich Stadtquartiere",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        color: #0d4880;
        font-family: 'Helvetica Neue', sans-serif;
        margin-bottom: 1.5rem;
    }
    .stButton button {
        background-color: #0d4880;
        color: white;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background-color: #f5f7f9;
    }
    footer {visibility: hidden;}
    .st-emotion-cache-1wmy9hl {
        font-family: 'Helvetica Neue', sans-serif;
    }
    .zurich-info {
        background-color: #f1f7ff;
        border-left: 4px solid #0d4880;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction in German
st.title("Interaktive Karte der Zürcher Stadtquartiere")

with st.container():
    st.markdown('<div class="zurich-info">', unsafe_allow_html=True)
    st.markdown("""
    Diese interaktive Karte zeigt die verschiedenen Stadtquartiere von Zürich. 
    Bewegen Sie den Mauszeiger über ein Quartier, um seinen Namen anzuzeigen.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Function to load GeoJSON data
@st.cache_data
def load_geojson(file_path):
    """GeoJSON-Datei mit Quartiergrenzen laden"""
    try:
        gdf = gpd.read_file(file_path)
        return gdf
    except Exception as e:
        st.error(f"Fehler beim Laden der GeoJSON-Datei: {e}")
        return None

# File uploader with German text
with st.sidebar:
    st.markdown("### Kartendaten")
    uploaded_file = st.file_uploader("Zürich GeoJSON-Datei hochladen", type=['geojson', 'json'])
    geojson_path = st.text_input(
        "Oder geben Sie den Pfad zur GeoJSON-Datei ein:",
        value=""
    )

# Decide which source to use
if uploaded_file is not None:
    with open("temp_geojson.json", "wb") as f:
        f.write(uploaded_file.getbuffer())
    gdf = load_geojson("temp_geojson.json")
elif geojson_path:
    gdf = load_geojson(geojson_path)
else:
    st.info("Bitte laden Sie eine GeoJSON-Datei mit den Zürcher Quartiergrenzen hoch oder geben Sie einen Dateipfad an.")
    st.stop()

if gdf is not None:
    # Check columns to find name property
    property_cols = [col for col in gdf.columns if col not in ['geometry']]
    
    # Common name variations in German and English
    name_options = ['name', 'Name', 'NAME', 'quartier', 'Quartier', 'bezirk', 'Bezirk',
                   'bezeichnung', 'Bezeichnung', 'stadtquartier', 'Stadtquartier']
    
    # Find matching column or default to first
    name_column = next((col for col in name_options if col in property_cols), property_cols[0])
    
    # Let user select name column
    with st.sidebar:
        name_column = st.selectbox(
            "Spalte mit Quartiernamen:",
            options=property_cols,
            index=property_cols.index(name_column) if name_column in property_cols else 0
        )
        
        # Map styling options
        st.markdown("### Karteneinstellungen")
        map_style = st.selectbox(
            "Kartenstil:",
            options=["Cartodb Positron", "Cartodb Dark Matter", "Stamen Terrain", "Stamen Toner", "OpenStreetMap"],
            index=0
        )
        
        show_labels = st.checkbox("Quartiernamen auf der Karte anzeigen", value=False)
        
        color_scheme = st.selectbox(
            "Farbschema:",
            options=["Blau", "Grün", "Bunt", "Grau"],
            index=0
        )

    # Map style dictionary
    map_styles = {
        "Cartodb Positron": "CartoDB positron",
        "Cartodb Dark Matter": "CartoDB dark_matter",
        "Stamen Terrain": "Stamen Terrain",
        "Stamen Toner": "Stamen Toner",
        "OpenStreetMap": "OpenStreetMap"
    }
    
    # Color schemes
    color_schemes = {
        "Blau": {
            "base": "#b3cde3",
            "highlight": "#0d4880",
            "border": "#738595",
            "highlight_border": "#000000"
        },
        "Grün": {
            "base": "#b2df8a",
            "highlight": "#33a02c",
            "border": "#7d9c62",
            "highlight_border": "#1a5218"
        },
        "Bunt": {
            "base": "#fbb4ae",
            "highlight": "#ffdd94",
            "border": "#bc8c8a",
            "highlight_border": "#8b572a"
        },
        "Grau": {
            "base": "#d9d9d9",
            "highlight": "#969696",
            "border": "#737373",
            "highlight_border": "#252525"
        }
    }
    
    selected_colors = color_schemes[color_scheme]
    
    # Create the Folium map centered on Zurich
    m = folium.Map(
        location=[47.3769, 8.5417],
        zoom_start=12,
        tiles=map_styles[map_style]
    )
    
    # Improved tooltip styling
    tooltip = GeoJsonTooltip(
        fields=[name_column],
        aliases=["Quartier"],
        localize=True,
        sticky=True,
        labels=True,
        style="""
            background-color: white;
            border: 2px solid #0d4880;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            font-size: 14px;
            font-family: Helvetica, Arial, sans-serif;
            font-weight: bold;
            padding: 8px 12px;
        """,
    )
    
    # Add GeoJSON with improved styling
    gjson = folium.GeoJson(
        gdf,
        name="Stadtquartiere",
        style_function=lambda x: {
            "fillColor": selected_colors["base"],
            "color": selected_colors["border"],
            "weight": 2,
            "fillOpacity": 0.6,
        },
        highlight_function=lambda x: {
            "fillColor": selected_colors["highlight"],
            "color": selected_colors["highlight_border"],
            "weight": 3,
            "fillOpacity": 0.8,
            "dashArray": None
        },
        tooltip=tooltip,
    ).add_to(m)
    
    # Add neighborhood labels if requested
    if show_labels:
        # Function to get polygon centroid
        def get_centroid(geometry):
            centroid = geometry.centroid
            return [centroid.y, centroid.x]
        
        # Add text labels for each neighborhood
        for idx, row in gdf.iterrows():
            name = row[name_column]
            centroid = get_centroid(row.geometry)
            folium.Marker(
                location=centroid,
                icon=folium.DivIcon(
                    icon_size=(150, 36),
                    icon_anchor=(75, 18),
                    html=f'<div style="font-size: 10px; font-weight: bold; text-align: center; text-shadow: 1px 1px 2px white, -1px -1px 2px white, 1px -1px 2px white, -1px 1px 2px white; color: #333;">{name}</div>'
                )
            ).add_to(m)
    
    # Add scale bar
    folium.plugins.MeasureControl(position='bottomleft', primary_length_unit='meters').add_to(m)
    
    # Add fullscreen button
    folium.plugins.Fullscreen(position='topleft').add_to(m)
    
    # Display the map with custom container styling
    st.markdown('<div style="padding: 10px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); background-color: white;">', unsafe_allow_html=True)
    st.write("**Bewegen Sie den Mauszeiger über ein Quartier, um den Namen anzuzeigen**")
    folium_static(m, width=1000, height=700)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show list of all neighborhoods in a more attractive container
    with st.expander("Liste aller Stadtquartiere"):
        # Display neighborhoods in a grid
        neighborhoods = sorted(gdf[name_column].unique().tolist())
        
        # Create columns for neighborhood list
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        
        # Split neighborhoods into columns
        items_per_col = len(neighborhoods) // 3 + (1 if len(neighborhoods) % 3 > 0 else 0)
        
        for i, col in enumerate(cols):
            with col:
                start_idx = i * items_per_col
                end_idx = min((i + 1) * items_per_col, len(neighborhoods))
                
                for name in neighborhoods[start_idx:end_idx]:
                    st.markdown(f"• {name}")
    
    # Add information about Zurich districts
    with st.expander("Informationen zu Zürich"):
        st.markdown("""
        ### Über Zürich
        
        Zürich ist die größte Stadt der Schweiz und in verschiedene Stadtkreise und Quartiere unterteilt.
        Die Stadt ist bekannt für ihre hohe Lebensqualität, den Zürichsee, und als wichtiges Wirtschafts- und Finanzzentrum.
        
        ### Stadtkreise und Quartiere
        
        Zürich ist in 12 Stadtkreise (Kreis 1 bis 12) und insgesamt 34 Stadtquartiere aufgeteilt. Jedes Quartier 
        hat seinen eigenen Charakter und seine Geschichte.
        
        Die Altstadt (Kreis 1) bildet das historische Zentrum, während neuere Stadtteile wie Zürich-West (Teil von Kreis 5) 
        sich zu modernen Trendvierteln entwickelt haben.
        """)
        
else:
    st.error("Keine GeoJSON-Daten geladen. Bitte überprüfen Sie Ihre Datei und versuchen Sie es erneut.")

# Add footer with additional information
st.markdown("""
---
<div style="text-align: center; color: #888; font-size: 0.8em;">
Interaktive Karte der Zürcher Stadtquartiere | Datenquelle: Stadt Zürich
</div>
""", unsafe_allow_html=True)
