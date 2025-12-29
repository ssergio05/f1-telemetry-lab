import fastf1
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import os
from modules.f1_utils import get_session_data

# --- Configuration ---
year, gp, session_type = 2024, 'Spain', 'Q'
drivers = ['VER', 'NOR']

session = get_session_data(year, gp, session_type)
session.load()

lap1 = session.laps.pick_driver(drivers[0]).pick_fastest()
lap2 = session.laps.pick_driver(drivers[1]).pick_fastest()

# --- Telemetry & Interpolation ---
tel1 = lap1.get_telemetry().add_distance()
tel2 = lap2.get_telemetry().add_distance()

dist_common = np.linspace(0, max(tel1['Distance'].max(), tel2['Distance'].max()), 2000)
v1 = np.interp(dist_common, tel1['Distance'], tel1['Speed'])
v2 = np.interp(dist_common, tel2['Distance'], tel2['Speed'])
x = np.interp(dist_common, tel1['Distance'], tel1['X'])
y = np.interp(dist_common, tel1['Distance'], tel1['Y'])

speed_delta = v1 - v2

# --- Plotting ONLY the Track ---
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 10))

points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

norm = plt.Normalize(-5, 5) 
lc = LineCollection(segments, cmap='RdBu_r', norm=norm, linewidth=6)
lc.set_array(speed_delta)

ax.add_collection(lc)
ax.set_aspect('equal')
ax.autoscale_view()
ax.axis('off')

# Professional Title
ax.set_title(f"SPEED DELTA: {drivers[0]} vs {drivers[1]}", size=15, weight='bold', pad=20)

# Add Colorbar
cbar = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap='RdBu_r'), ax=ax, shrink=0.5)
cbar.set_label('km/h Difference', size=10)

# --- 8. Export & Display ---
# Save the figure with high resolution (300 DPI) BEFORE showing it
file_name = f"{year}_{gp}_{session_type}_{drivers[0]}_vs_{drivers[1]}_delta_map.png"
plt.savefig(f"plots/{file_name}", dpi=300, bbox_inches='tight', facecolor='black')
plt.show()