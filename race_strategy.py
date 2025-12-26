"""
F1 Race Strategy & Tyre Degradation Analysis
Author: Sergio Gonzalez
Description: This script analyzes and compares the lap-by-lap pace and tyre 
             degradation of two drivers during a specific race stint.
"""

from modules.f1_utils import get_session_data
import fastf1.plotting
import matplotlib.pyplot as plt
import os

# --- 1. Session Configuration ---
# Note: session_type must be 'R' (Race) for meaningful degradation analysis
year = 2024
gp = 'Spain'
session_type = 'R'
drivers = ['NOR', 'VER']
tyre = 'SOFT'

# Initialize session and styling
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')
session = get_session_data(year, gp, session_type)
laps = session.laps

# --- 2. Data Filtering Functions ---
def get_stint_data(all_laps, driver, compound, stint_number):
    """
    Filters laps for a specific driver, tyre compound, and stint number.
    Uses pick_quicklaps to remove outliers (pits, yellow flags).

    Args:
        all_laps (Laps): The full session laps object.
        driver (str): Driver code (e.g., 'NOR').
        compound (str): Tyre compound name (e.g., 'SOFT').
        stint_number (int): The number of the stint to analyze.

    Returns:
        Laps: Filtered lap data ready for plotting.
    """
    # Using pick_compound (singular) is the current standard in FastF1
    filtered = all_laps.pick_drivers(driver).pick_compounds(compound)
    
    # We filter by the 'Stint' column as there is no direct pick_stint method
    filtered = filtered[filtered['Stint'] == stint_number]
    
    return filtered.pick_quicklaps()

# --- 3. Data Extraction ---
# Analyzing the first stint (SOFT tyres) for both lead drivers
stint_nor = get_stint_data(laps, drivers[0], tyre, 1)
stint_ver = get_stint_data(laps, drivers[1], tyre, 1)

# --- 4. Plotting Construction ---
fig, ax = plt.subplots(figsize=(12, 6))

# Plotting Norris (Driver 1)
ax.plot(stint_nor['LapNumber'], stint_nor['LapTime'].dt.total_seconds(), 
        marker='o', color='orange', label=f'{drivers[0]} - Stint 1 (SOFT)')

# Plotting Verstappen (Driver 2)
ax.plot(stint_ver['LapNumber'], stint_ver['LapTime'].dt.total_seconds(), 
        marker='s', color='blue', label=f'{drivers[1]} - Stint 1 (SOFT)')

# --- 5. Chart Styling ---
ax.set_xlabel('Lap Number')
ax.set_ylabel('Lap Time (s)')
ax.set_title(f'Tyre Degradation Duel: {drivers[0]} vs {drivers[1]} ({gp} {year})')
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend()

# Calculate Y-axis limits dynamically based on the fastest and slowest laps
# This ensures the plot is zoomed in correctly on the relevant pace data
all_times = list(stint_nor['LapTime'].dt.total_seconds()) + list(stint_ver['LapTime'].dt.total_seconds())
if all_times:
    ax.set_ylim(min(all_times) - 0.5, max(all_times) + 0.5)

# --- 6. Export & Show ---
# Ensure the plots directory exists before saving
if not os.path.exists('plots'):
    os.makedirs('plots')

# Define the filename based on the analysis parameters
file_name = f"{year}_{gp}_{session_type}_{tyre}_deg_{drivers[0]}_{drivers[1]}.png"

# Save as high-resolution (300 DPI) with a black background for visibility in dark themes
plt.savefig(f"plots/{file_name}", dpi=300, bbox_inches='tight', facecolor='black')

plt.show()