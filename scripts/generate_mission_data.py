import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_telemetry(mode="campaign", start_date="2024-05-10"):
    print(f"🚀 Initializing Aditya-L1 Mission Data Simulation [{mode.upper()} MODE]...")
    
    # Payload Configuration
    payloads = ['VELC', 'SUIT', 'SoLEXS', 'HEL1OS', 'ASPEX', 'PAPA', 'MAG']
    base_raw = "raw_data"
    os.makedirs(base_raw, exist_ok=True)
    for p in payloads:
        os.makedirs(os.path.join(base_raw, p), exist_ok=True)

    # Time Setup
    # Mode differences: 
    # 'campaign' = 72h window with high-res event
    # 'baseline' = 7 days quiet sun
    duration_hrs = 168 if mode == "baseline" else 72
    start_time = datetime.strptime(start_date, "%Y-%m-%d")
    
    # Base 5-min intervals for low-cadence instruments
    time_steps_5m = pd.date_range(start=start_time, periods=12 * duration_hrs, freq='5min')
    
    # High-cadence 8Hz for MAG (8 samples per second = 480 per minute)
    # To keep file sizes manageable for simulation, we'll simulate 1Hz here, 
    # but the logic will treat it as "high frequency" to be decimated.
    time_steps_mag = pd.date_range(start=start_time, periods=duration_hrs * 3600, freq='1s')
    
    # Event: CME Flare at T+24h
    cme_start_idx_5m = 12 * 24
    cme_start_idx_mag = 3600 * 24
    
    # 1. MAG (Magnetometer) - Simulated High Cadence
    print("   -> Generating High-Cadence MAG data (1Hz simulation for 8Hz logic)...")
    df_mag = pd.DataFrame({'timestamp': time_steps_mag})
    df_mag['B_x'] = np.random.normal(0, 0.2, len(df_mag))
    df_mag['B_y'] = np.random.normal(0, 0.2, len(df_mag))
    df_mag['B_z'] = np.random.normal(-5, 0.5, len(df_mag))
    
    if mode == "campaign":
        # Add a "Shock Front" - rapid spike then decay
        shock_indices = np.arange(cme_start_idx_mag, cme_start_idx_mag + 600) # 10 minute shock
        df_mag.loc[shock_indices, 'B_z'] += 25 * np.sin(np.pi * (shock_indices - cme_start_idx_mag) / 600)
        # Post-shock turbulence
        df_mag.loc[cme_start_idx_mag + 600:, 'B_z'] += 15 * np.exp(-0.0001 * (np.arange(len(df_mag) - (cme_start_idx_mag + 600))))
    
    df_mag.to_csv(os.path.join(base_raw, 'MAG', 'telemetry_mag.csv'), index=False)

    # 2. ASPEX (Plasma Analyzer) - 5-min
    df_aspex = pd.DataFrame({'timestamp': time_steps_5m})
    df_aspex['proton_count'] = 100 + np.random.poisson(20, len(df_aspex))
    if mode == "campaign":
        df_aspex.loc[cme_start_idx_5m:, 'proton_count'] += 5000 * np.exp(-0.02 * (np.arange(len(df_aspex)-cme_start_idx_5m)))
    df_aspex['alpha_count'] = df_aspex['proton_count'] * 0.04 + np.random.normal(0, 2, len(df_aspex))
    df_aspex.to_csv(os.path.join(base_raw, 'ASPEX', 'telemetry_aspex.csv'), index=False)

    # 3. VELC / SUIT / SoLEXS / HEL1OS / PAPA
    for p in ['VELC', 'SUIT', 'SoLEXS', 'HEL1OS', 'PAPA']:
        df_p = pd.DataFrame({'timestamp': time_steps_5m})
        df_p['value'] = 1.0 + np.random.normal(0, 0.1, len(df_p))
        if mode == "campaign":
            df_p.loc[cme_start_idx_5m:, 'value'] += 10.0 * np.exp(-0.05 * (np.arange(len(df_p)-cme_start_idx_5m)))
        df_p.to_csv(os.path.join(base_raw, p, f'telemetry_{p.lower()}.csv'), index=False)

    # Summary: Save Target
    df_target = pd.DataFrame({'timestamp': time_steps_5m})
    if mode == "campaign":
        cme_timestamp = time_steps_5m[cme_start_idx_5m]
        df_target['hours_to_event'] = (cme_timestamp - df_target['timestamp']).dt.total_seconds() / 3600
        df_target.loc[df_target['hours_to_event'] < 0, 'hours_to_event'] = 0
    else:
        df_target['hours_to_event'] = 168.0 # No event in progress
        
    # Standardize target to 10s sync later in preprocess
    df_target.to_csv(os.path.join(base_raw, 'mission_targets.csv'), index=False)

    print(f"✅ Simulation Complete ({mode}). Data saved to /{base_raw}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["baseline", "campaign"], default="campaign")
    parser.add_argument("--start", default="2024-05-10")
    args = parser.parse_args()
    generate_telemetry(args.mode, args.start)
