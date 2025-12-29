import fastf1
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import os
from modules.f1_utils import get_session_data

# --- Configuration ---
year, gp, session_type = 2024, 'Spain', 'Q'
driver = 'NOR'

session = get_session_data(year, gp, session_type)
session.load()
lap = session.laps.pick_driver(driver).pick_fastest()
tel = lap.get_telemetry()

# --- Plotting ONLY the Track ---
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 10))

points = np.array([tel['X'], tel['Y']]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

# Plasma colormap is standard for absolute speed
lc = LineCollection(segments, cmap='plasma', linewidth=6)
lc.set_array(tel['Speed'])

ax.add_collection(lc)
ax.set_aspect('equal')
ax.autoscale_view()
ax.axis('off')

ax.set_title(f"ABSOLUTE SPEED: {driver}", size=15, weight='bold', pad=20)

cbar = plt.colorbar(lc, ax=ax, shrink=0.5)
cbar.set_label('Speed (km/h)', size=10)


# --- 8. Export & Display ---
# Save the figure with high resolution (300 DPI) BEFORE showing it
file_name = f"{year}_{gp}_{session_type}_{driver}_heatmap.png"
plt.savefig(f"plots/{file_name}", dpi=300, bbox_inches='tight', facecolor='black')
plt.show()