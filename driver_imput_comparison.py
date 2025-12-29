import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import os
from modules.f1_utils import get_session_data

# Initialize FastF1 plotting styles and set the dark theme for professional visualization
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, color_scheme='fastf1', misc_mpl_mods=False)
plt.style.use('dark_background') 

# --- 1. Session Configuration ---
year = 2024
gp = 'Spain'
session_type = 'Q'  # Qualifying
drivers = ['VER', 'NOR']

# Load session data using the custom utility module
session = get_session_data(year, gp, session_type)
session.load()

# --- 2. Driver & Color Setup ---
# Fetch official team colors directly from the session for visual accuracy
color1 = fastf1.plotting.get_driver_color(drivers[0], session=session)
color2 = fastf1.plotting.get_driver_color(drivers[1], session=session)

# --- 3. Telemetry Extraction ---
# Get the fastest lap for both drivers
lap1 = session.laps.pick_driver(drivers[0]).pick_fastest()
lap2 = session.laps.pick_driver(drivers[1]).pick_fastest()

# Get telemetry data and add 'Distance' to synchronize plots by track position rather than time
tel1 = lap1.get_telemetry().add_distance()
tel2 = lap2.get_telemetry().add_distance()

# --- 4. Plotting Construction (4 Panels) ---
# Create a figure with 4 subplots: Speed, Throttle, Brake, and Gear selection
# Gridspec height ratios prioritize the Speed chart as the primary reference
fig, ax = plt.subplots(4, 1, figsize=(14, 12), sharex=True, 
                       gridspec_kw={'height_ratios': [2, 1, 1, 1]})

fig.suptitle(f"DRIVER INPUT ANALYSIS: {drivers[0]} vs {drivers[1]}\n{year} {gp} Grand Prix", 
             size=18, weight='bold', y=0.97)

# --- PANEL 1: SPEED (Velocity) ---
ax[0].plot(tel1['Distance'], tel1['Speed'], color=color1, label=drivers[0], linewidth=2)
ax[0].plot(tel2['Distance'], tel2['Speed'], color=color2, label=drivers[1], linewidth=2)
ax[0].set_ylabel("Speed (km/h)", color='gray')
ax[0].legend(loc='lower center', ncol=2, frameon=False)
ax[0].grid(color='gray', linestyle='--', alpha=0.2)

# --- PANEL 2: THROTTLE ---
ax[1].plot(tel1['Distance'], tel1['Throttle'], color=color1, linewidth=1.5)
ax[1].plot(tel2['Distance'], tel2['Throttle'], color=color2, linewidth=1.5)
ax[1].set_ylabel("Throttle %", color='gray')
ax[1].set_ylim(-5, 105)
ax[1].grid(color='gray', linestyle='--', alpha=0.2)

# --- PANEL 3: BRAKE ---
ax[2].plot(tel1['Distance'], tel1['Brake'], color=color1, linewidth=1.5)
ax[2].plot(tel2['Distance'], tel2['Brake'], color=color2, linewidth=1.5)
ax[2].set_ylabel("Brake", color='gray')
ax[2].set_ylim(-0.1, 1.1)
ax[2].grid(color='gray', linestyle='--', alpha=0.2)

# --- PANEL 4: GEARS ---
# Using 'steps-post' drawstyle to accurately reflect discrete gear changes
ax[3].plot(tel1['Distance'], tel1['nGear'], color=color1, linewidth=2, drawstyle='steps-post')
ax[3].plot(tel2['Distance'], tel2['nGear'], color=color2, linewidth=2, drawstyle='steps-post')
ax[3].set_ylabel("Gear", color='gray')
ax[3].set_xlabel("Distance (m)")
ax[3].set_ylim(0.5, 8.5)
ax[3].grid(color='gray', linestyle='--', alpha=0.2)

# --- 5. Focus Zoom ---
# Zooming into the technical middle sector (Turns 7-12) where delta usually fluctuates
ax[3].set_xlim(1500, 3500) 

plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# --- 6. Export Analysis ---
# Ensure the plots directory exists before saving
if not os.path.exists('plots'):
    os.makedirs('plots')

# Define the filename following the lab's standard naming convention
file_name = f"{year}_{gp}_{session_type}_inputs_zoom_{drivers[0]}_{drivers[1]}.png"

# Save as high-resolution (300 DPI) for the README gallery
plt.savefig(f"plots/{file_name}", dpi=300, bbox_inches='tight', facecolor='black')

print(f"Analysis saved as plots/{file_name}")
plt.show()