"""
F1 Telemetry Lab - Utility Module
Author: Sergio Gonzalez
Description: Helper functions for session loading, telemetry interpolation, 
             and sector timing analysis using FastF1.
"""

import fastf1
import numpy as np
import os

def get_session_data(year, gp, session_type):
    """
    Sets up the local cache and loads the session data from FastF1.

    Args:
        year (int): Year of the Grand Prix (e.g., 2024).
        gp (str): Name or location of the GP (e.g., 'Spain').
        session_type (str): Type of session ('Q' for Qualy, 'R' for Race).

    Returns:
        fastf1.core.Session: The fully loaded session object.
    """
    cache_dir = 'f1_cache'
    if not os.path.exists(cache_dir): 
        os.makedirs(cache_dir)
    
    fastf1.Cache.enable_cache(cache_dir)
    
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    return session

def delta_calculator(lap1, lap2):
    """
    Calculates the time delta between two laps based on track distance.
    Uses linear interpolation to align telemetry samples.

    Args:
        lap1 (Lap): FastF1 Lap object for driver 1.
        lap2 (Lap): FastF1 Lap object for driver 2.

    Returns:
        tuple: (common_distance_grid, time_delta_array)
    """
    # 1. Add distance data to telemetry
    tel1 = lap1.get_telemetry().add_distance()
    tel2 = lap2.get_telemetry().add_distance()

    # 2. Convert timestamps to total seconds from lap start
    t1 = (tel1['Time'] - tel1['Time'].iloc[0]).dt.total_seconds()
    t2 = (tel2['Time'] - tel2['Time'].iloc[0]).dt.total_seconds()

    # 3. Create a unified distance grid (2000 points) to compare samples
    # This solves the problem of sensors not pinging at the same time
    dist_max = tel1['Distance'].max()
    common_dist = np.linspace(0, dist_max, 2000)

    # 4. Interpolate time values based on the common distance grid
    time_interp1 = np.interp(common_dist, tel1['Distance'], t1)
    time_interp2 = np.interp(common_dist, tel2['Distance'], t2)

    # 5. Calculate the gap (Delta)
    delta = time_interp1 - time_interp2
    return common_dist, delta

def print_sector_times(lap1, lap2, driver1, driver2):
    """
    Compares and prints the S1, S2, and S3 times in the terminal.

    Args:
        lap1 (Lap): Lap object for driver 1.
        lap2 (Lap): Lap object for driver 2.
        driver1 (str): Code of driver 1 (e.g., 'NOR').
        driver2 (str): Code of driver 2 (e.g., 'RUS').
    """
    sectors = ['Sector1Time', 'Sector2Time', 'Sector3Time']
    print(f"\n--- SECTOR ANALYSIS: {driver1} vs {driver2} ---")
    
    for sector in sectors:
        # Convert Timedelta to float seconds
        s1 = getattr(lap1, sector).total_seconds()
        s2 = getattr(lap2, sector).total_seconds()
        diff = s1 - s2
        
        faster = driver1 if diff < 0 else driver2
        print(f"{sector[:7]}: {driver1} {s1:.3f}s | {driver2} {s2:.3f}s | Delta: {abs(diff):.3f}s ({faster} wins)")