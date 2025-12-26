"""
F1 Qualifying Telemetry Analysis
Author: Sergio
Description: This script compares the fastest laps of two drivers during a 
             qualifying session. It generates a 5-panel chart showing time gap, 
             speed, throttle, brake, and gear usage, synchronized by distance.
"""

from modules.f1_utils import get_session_data, delta_calculator, print_sector_times
import numpy as np
from fastf1 import plotting
import matplotlib.pyplot as plt

# --- 1. Session Configuration ---
year = 2024
gp = 'Spain'
session_type = 'Q'

# Load session data using our custom utility
session = get_session_data(year, gp, session_type)

# --- 2. Plotting Setup ---
# Setup FastF1 styling for professional-looking charts
plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')
fig, ax = plt.subplots(5, 1, figsize=(15, 12), sharex=True)

# --- 3. Data Processing ---
drivers = ['NOR', 'RUS']

# Select the fastest lap for each driver
lap1 = session.laps.pick_drivers(drivers[0]).pick_fastest()
lap2 = session.laps.pick_drivers(drivers[1]).pick_fastest()

# Print mathematical comparison of sectors in the terminal
print_sector_times(lap1, lap2, drivers[0], drivers[1])

# Calculate distance-based time gap (Delta) using interpolation
ref_dist, delta_values = delta_calculator(lap1, lap2)

# --- 4. Plotting Panel 1: The Gap (Delta) ---
ax[0].plot(ref_dist, delta_values, color='white', label=f'Gap {drivers[0]} vs {drivers[1]}')
ax[0].axhline(0, color='white', linestyle='--', alpha=0.5)

# Axis formatting for the Gap: we invert the Y-axis so that when the line goes up, 
# the first driver is gaining time.
max_gap = np.max(np.abs(delta_values))
ax[0].set_ylim(-max_gap * 1.1, max_gap * 1.1)
ax[0].invert_yaxis()

# --- 5. Plotting Panels 2-5: Telemetry Channels ---
for driver in drivers:
    # Get the fastest lap and official team style (colors/line types)
    laps = session.laps.pick_drivers(driver).pick_fastest()
    style = plotting.get_driver_style(identifier=driver, style=['color', 'linestyle'], session=session)

    # Get telemetry data and add distance column for the X-axis
    telemetry = laps.get_telemetry().add_distance()

    # Plot Speed, Throttle, Brake, and Gears
    ax[1].plot(telemetry['Distance'], telemetry['Speed'], **style, label=driver)
    ax[2].plot(telemetry['Distance'], telemetry['Throttle'], **style, label=driver)
    ax[3].plot(telemetry['Distance'], telemetry['Brake'], **style, label=driver)
    ax[4].plot(telemetry['Distance'], telemetry['nGear'], **style, label=driver)

# --- 6. Circuit Landmarks (Corners) ---
# Fetch official FIA track info to draw vertical lines at corner vertices
circuit_info = session.get_circuit_info()
corners = circuit_info.corners

for _, corner in corners.iterrows():
    dist = corner['Distance']
    name = f"T{int(corner['Number'])}"

    # Draw a subtle vertical line across all 5 panels
    for i in range(5):
        ax[i].axvline(dist, color='white', linestyle=':', alpha=0.3)
    
    # Add the corner name (e.g., T1, T2) at the top of the Gap chart
    ax[0].text(dist, ax[0].get_ylim()[1], f"  {name}", 
               rotation=90, va='bottom', ha='center', 
               fontsize=9, color='grey', alpha=0.9)

# --- 7. Final Decorations & Legend ---
labels = ['Gap (s)', 'Speed (km/h)', 'Throttle %', 'Brake %', 'Gears']

for i in range(5):
    ax[i].set_ylabel(labels[i])

# Legend placement: Bottom right for speed, top right for others to avoid overlapping data
ax[1].legend(loc='lower right', fontsize=10, frameon=True)
for i in range(1, 5):
    ax[i].legend(loc='upper right', fontsize=8)

plt.tight_layout()

# --- 8. Export & Display ---
# Save the figure with high resolution (300 DPI) BEFORE showing it
file_name = f"{year}_{gp}_{session_type}_{drivers[0]}_vs_{drivers[1]}_telemetry.png"
plt.savefig(f"plots/{file_name}", dpi=300, bbox_inches='tight', facecolor='black')

plt.show()