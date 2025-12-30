import os
import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from modules.f1_utils import get_session_data

# --- GLOBAL CONFIGURATION ---
# Set the directory for storing F1 data to avoid redundant downloads
cache_dir = 'f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

# Enable FastF1 caching and setup Matplotlib styling for F1 data
fastf1.Cache.enable_cache(cache_dir)
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, color_scheme='fastf1', misc_mpl_mods=False)

# Configure Streamlit page for a professional wide-screen view
st.set_page_config(page_title="F1 Telemetry Lab", layout="wide")

# --- CIRCUIT CORNER DATA (Example: Spain/Barcelona) ---
# Approximate distance in meters for labeling corner markers on charts
CIRCUIT_CORNERS = {
    "Spain": {
        "T1": 650, "T3": 1200, "T4": 1550, "T5": 1850, "T7": 2500, 
        "T9": 2950, "T10": 3300, "T12": 3900, "T14": 4550
    }
}

# --- DATA LOADING (Streamlit Caching) ---
@st.cache_data
def load_analysis_data(y, g, s):
    """Fetches and loads session data from the FastF1 API."""
    session = get_session_data(y, g, s)
    session.load()
    return session

# --- HELPER FUNCTIONS ---
def get_laps_to_analyze(session, d1, d2, session_type, lap_num):
    """Logic to decide between fastest laps (Qualifying) or specific laps (Race)."""
    if session_type == "Q" or lap_num is None:
        l1 = session.laps.pick_driver(d1).pick_fastest()
        l2 = session.laps.pick_driver(d2).pick_fastest()
        label = "Fastest Laps"
    else:
        l1 = session.laps.pick_driver(d1).pick_lap(lap_num)
        l2 = session.laps.pick_driver(d2).pick_lap(lap_num)
        label = f"Lap {lap_num}"
    return l1, l2, label

# --- DYNAMIC PLOTTING FUNCTIONS ---

def plot_master_dashboard(session, d1, d2, session_type, lap_num, gp_name, zoom_range=None):
    """Generates a 5-panel dashboard: Gap, Speed, Throttle, Brake, and Gear."""
    l1, l2, lap_label = get_laps_to_analyze(session, d1, d2, session_type, lap_num)
    color1 = fastf1.plotting.get_driver_color(d1, session=session)
    color2 = fastf1.plotting.get_driver_color(d2, session=session)

    # Extract telemetry and add distance coordinate
    t1 = l1.get_telemetry().add_distance()
    t2 = l2.get_telemetry().add_distance()

    # Time Delta Calculation (Interpolation to sync different sampling rates)
    dist_common = np.linspace(0, max(t1['Distance'].max(), t2['Distance'].max()), 2000)
    t1_i = np.interp(dist_common, t1['Distance'], t1['Time'].dt.total_seconds())
    t2_i = np.interp(dist_common, t2['Distance'], t2['Time'].dt.total_seconds())
    delta = t1_i - t2_i

    # Initialize subplots with specific height ratios
    fig, ax = plt.subplots(5, 1, figsize=(14, 12), sharex=True, 
                           gridspec_kw={'height_ratios': [1.5, 2, 1, 1, 1]})
    plt.style.use('dark_background')

    # Panel 0: Time Gap
    ax[0].plot(dist_common, delta, color='white')
    ax[0].fill_between(dist_common, delta, 0, where=(delta < 0), color=color1, alpha=0.3)
    ax[0].fill_between(dist_common, delta, 0, where=(delta > 0), color=color2, alpha=0.3)
    ax[0].set_ylabel("Gap (s)", color='gray')
    
    # Panel 1: Speed + Corner Labels
    ax[1].plot(t1['Distance'], t1['Speed'], color=color1, label=d1)
    ax[1].plot(t2['Distance'], t2['Speed'], color=color2, label=d2)
    ax[1].set_ylabel("Speed (km/h)", color='gray')
    ax[1].legend(loc='upper right', frameon=False)

    # Dynamic Corner Marker placement
    if gp_name in CIRCUIT_CORNERS:
        for corner, dist in CIRCUIT_CORNERS[gp_name].items():
            if zoom_range is None or (zoom_range[0] <= dist <= zoom_range[1]):
                ax[1].text(dist, ax[1].get_ylim()[1]*0.95, corner, color='gray', fontsize=10, ha='center', weight='bold')

    # Panels 2-4: Inputs (Throttle, Brake, Gear)
    ax[2].plot(t1['Distance'], t1['Throttle'], color=color1)
    ax[2].plot(t2['Distance'], t2['Throttle'], color=color2)
    ax[2].set_ylabel("Throttle %", color='gray')
    ax[3].plot(t1['Distance'], t1['Brake'], color=color1)
    ax[3].plot(t2['Distance'], t2['Brake'], color=color2)
    ax[3].set_ylabel("Brake", color='gray')
    ax[4].plot(t1['Distance'], t1['nGear'], color=color1, drawstyle='steps-post')
    ax[4].plot(t2['Distance'], t2['nGear'], color=color2, drawstyle='steps-post')
    ax[4].set_ylabel("Gear", color='gray')
    ax[4].set_xlabel("Distance (m)")

    # Apply X-axis limits for technical zoom
    if zoom_range:
        ax[4].set_xlim(zoom_range)
    
    for a in ax: a.grid(alpha=0.1)
    plt.tight_layout()
    return fig

def plot_speed_delta_map(session, d1, d2, session_type, lap_num):
    """Generates a track heatmap visualizing the speed differential between drivers."""
    l1, l2, _ = get_laps_to_analyze(session, d1, d2, session_type, lap_num)
    t1 = l1.get_telemetry().add_distance()
    t2 = l2.get_telemetry().add_distance()
    
    dist_common = np.linspace(0, max(t1['Distance'].max(), t2['Distance'].max()), 2000)
    v1 = np.interp(dist_common, t1['Distance'], t1['Speed'])
    v2 = np.interp(dist_common, t2['Distance'], t2['Speed'])
    x = np.interp(dist_common, t1['Distance'], t1['X'])
    y = np.interp(dist_common, t1['Distance'], t1['Y'])
    
    speed_delta = v1 - v2
    
    fig, ax = plt.subplots(figsize=(10, 10))
    plt.style.use('dark_background')
    
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    # Divergent colormap (Red for D1 faster, Blue for D2 faster)
    norm = plt.Normalize(-5, 5) 
    lc = LineCollection(segments, cmap='RdBu_r', norm=norm, linewidth=6)
    lc.set_array(speed_delta)
    
    ax.add_collection(lc)
    ax.set_aspect('equal')
    ax.autoscale_view()
    ax.axis('off')
    
    cbar = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap='RdBu_r'), ax=ax, shrink=0.5)
    cbar.set_label('Difference (km/h)')
    
    return fig

def plot_tyre_strategy(session, d1, d2):
    """Analyzes race pace trends and tire degradation over lap numbers."""
    laps_d1 = session.laps.pick_driver(d1).pick_quicklaps()
    laps_d2 = session.laps.pick_driver(d2).pick_quicklaps()
    color1 = fastf1.plotting.get_driver_color(d1, session=session)
    color2 = fastf1.plotting.get_driver_color(d2, session=session)

    fig, ax = plt.subplots(figsize=(12, 6))
    plt.style.use('dark_background')
    ax.plot(laps_d1['LapNumber'], laps_d1['LapTime'].dt.total_seconds(), color=color1, marker='o', label=f"{d1} Pace")
    ax.plot(laps_d2['LapNumber'], laps_d2['LapTime'].dt.total_seconds(), color=color2, marker='o', label=f"{d2} Pace")
    ax.set_title("Race Pace Consistency")
    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time (s)")
    ax.legend()
    ax.grid(alpha=0.2)
    return fig

# --- APP LAYOUT ---
st.title("🏎️ F1 Interactive Telemetry Lab")

# Sidebar for session and driver configuration
st.sidebar.header("1. Session & Drivers")
year = st.sidebar.selectbox("Year", [2024, 2023], index=0)
gp = st.sidebar.text_input("Grand Prix", "Spain")
session_type = st.sidebar.selectbox("Session", ["Q", "R", "FP3"])

lap_to_plot = None
if session_type == "R":
    lap_to_plot = st.sidebar.number_input("Select Lap", min_value=1, max_value=80, value=1)

d1 = st.sidebar.text_input("Driver 1", "VER")
d2 = st.sidebar.text_input("Driver 2", "NOR")

st.sidebar.header("2. Zoom Settings")
dist_min, dist_max = st.sidebar.slider("Distance Range (m)", 0, 7000, (1500, 3500), step=100)

# --- AUTOMATIC EXECUTION (Reactive Logic) ---
try:
    with st.spinner("Processing data..."):
        session = load_analysis_data(year, gp, session_type)
        
        tab1, tab2, tab3 = st.tabs(["📊 Telemetry", "📍 Track Map", "📈 Race Strategy"])
        
        with tab1:
            st.subheader("Master Telemetry Analysis")
            # Render full lap overview
            st.pyplot(plot_master_dashboard(session, d1, d2, session_type, lap_to_plot, gp))
            st.markdown("---")
            # Render focused technical zoom based on sidebar slider
            st.subheader("Technical Zoom Analysis")
            st.pyplot(plot_master_dashboard(session, d1, d2, session_type, lap_to_plot, gp, zoom_range=(dist_min, dist_max)))
            
        with tab2:
            st.subheader("Speed Delta Track Map")
            # Dynamic track heatmap generation
            st.pyplot(plot_speed_delta_map(session, d1, d2, session_type, lap_to_plot))
            
        with tab3:
            if session_type == "R":
                st.subheader("Race Pace & Tyre Degradation")
                # Dynamic race pace trend chart
                st.pyplot(plot_tyre_strategy(session, d1, d2))
            else:
                st.warning("Strategy analysis is designed for Race ('R') sessions.")

except Exception as e:
    st.sidebar.info("Waiting for valid input...")
    # st.error(f"Error details: {e}") # Uncomment for debugging