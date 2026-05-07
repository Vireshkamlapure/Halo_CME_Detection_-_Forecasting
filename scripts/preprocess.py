import pandas as pd
import numpy as np
import os
from glob import glob

def calculate_vector_magnitudes(df):
    """Calculates B_total magnitude from MAG vector data."""
    if 'B_x' in df.columns and 'B_y' in df.columns and 'B_z' in df.columns:
        df['B_total'] = np.sqrt(df['B_x']**2 + df['B_y']**2 + df['B_z']**2)
    return df

def calculate_ion_ratios(df):
    """Calculates Proton-to-Alpha ratios from ASPEX."""
    if 'proton_count' in df.columns and 'alpha_count' in df.columns:
        df['proton_alpha_ratio'] = df['proton_count'] / (df['alpha_count'] + 1e-6)
    return df

def resample_payload(df, payload_name, interval='10s'):
    """
    Standardizes a payload to a fixed interval using Min-Max-Std pooling.
    This preserves shock signatures (max) and turbulence (std) while average (mean) maintains trend.
    """
    df = df.set_index('timestamp')
    
    # Aggregation mapping: Mean, Max, Std for all numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    agg_map = {col: ['mean', 'max', 'std'] for col in numeric_cols}
    
    resampled = df.resample(interval).agg(agg_map)
    
    # Flatten multi-index columns: "MAG_B_z_mean", "MAG_B_z_max", etc.
    resampled.columns = [f"{payload_name}_{col[0]}_{col[1]}" for col in resampled.columns]
    return resampled.reset_index()

def run_pipeline(input_dir="raw_data", output_file="processed_mission_data.csv"):
    print("🛠️ Initializing Multi-Payload Feature Engineering Pipeline (10s Sync)...")
    
    # Payload identification
    payload_paths = glob(os.path.join(input_dir, "*/telemetry_*.csv"))
    if not payload_paths:
        print("❌ Error: No raw telemetry found. Run scripts/generate_mission_data.py first.")
        return

    # Master DataFrame initialization (empty grid)
    master_df = None
    
    for path in payload_paths:
        payload_name = os.path.basename(os.path.dirname(path))
        print(f"   -> Processing & Resampling Payload: {payload_name}")
        df = pd.read_csv(path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Payload-specific engineering (Pre-resample)
        if payload_name == 'MAG':
            df = calculate_vector_magnitudes(df)
        elif payload_name == 'ASPEX':
            df = calculate_ion_ratios(df)
            
        # Resample to 10s with Pooling
        df_resampled = resample_payload(df, payload_name, '10s')
        
        if master_df is None:
            master_df = df_resampled
        else:
            master_df = pd.merge(master_df, df_resampled, on='timestamp', how='outer')

    # Integrate real MAG Telemetry if available (Override/Supplement)
    real_mag_path = "scripts/mag_telemetry.csv"
    if os.path.exists(real_mag_path):
        print(f"   -> Merging Real MAG NetCDF Data: {real_mag_path}")
        real_mag_df = pd.read_csv(real_mag_path)
        real_mag_df['timestamp'] = pd.to_datetime(real_mag_df['timestamp'])
        
        # Resample to 10s
        real_mag_resampled = resample_payload(real_mag_df, 'REAL_MAG', '10s')
        
        if master_df is None:
            master_df = real_mag_resampled
        else:
            master_df = pd.merge(master_df, real_mag_resampled, on='timestamp', how='outer')

    # Integrate real ASPEX Telemetry if available
    real_aspex_path = "scripts/aspex_telemetry.csv"
    if os.path.exists(real_aspex_path):
        print(f"   -> Merging Real ASPEX SWIS Data: {real_aspex_path}")
        real_aspex_df = pd.read_csv(real_aspex_path)
        real_aspex_df['timestamp'] = pd.to_datetime(real_aspex_df['timestamp'])
        
        # Resample to 10s
        real_aspex_resampled = resample_payload(real_aspex_df, 'REAL_ASPEX', '10s')
        
        if master_df is None:
            master_df = real_aspex_resampled
        else:
            master_df = pd.merge(master_df, real_aspex_resampled, on='timestamp', how='outer')

    # Integrate real PAPA Telemetry if available
    real_papa_path = "scripts/papa_telemetry.csv"
    if os.path.exists(real_papa_path):
        print(f"   -> Merging Real PAPA Plasma Data: {real_papa_path}")
        real_papa_df = pd.read_csv(real_papa_path)
        real_papa_df['timestamp'] = pd.to_datetime(real_papa_df['timestamp'])
        
        # Resample to 10s
        real_papa_resampled = resample_payload(real_papa_df, 'REAL_PAPA', '10s')
        
        if master_df is None:
            master_df = real_papa_resampled
        else:
            master_df = pd.merge(master_df, real_papa_resampled, on='timestamp', how='outer')

    # Integrate real ASPEX STEPS Telemetry if available
    real_steps_path = "scripts/aspex_steps_telemetry.csv"
    if os.path.exists(real_steps_path):
        print(f"   -> Merging Real ASPEX STEPS Data: {real_steps_path}")
        real_steps_df = pd.read_csv(real_steps_path)
        real_steps_df['timestamp'] = pd.to_datetime(real_steps_df['timestamp'])
        
        # Resample to 10s
        real_steps_resampled = resample_payload(real_steps_df, 'REAL_STEPS', '10s')
        
        if master_df is None:
            master_df = real_steps_resampled
        else:
            master_df = pd.merge(master_df, real_steps_resampled, on='timestamp', how='outer')

    # Integrate real HEL1OS Telemetry if available
    real_hel1os_path = "scripts/hel1os_telemetry.csv"
    if os.path.exists(real_hel1os_path):
        print(f"   -> Merging Real HEL1OS X-Ray Data: {real_hel1os_path}")
        real_hel1os_df = pd.read_csv(real_hel1os_path)
        real_hel1os_df['timestamp'] = pd.to_datetime(real_hel1os_df['timestamp'])
        
        # Resample to 10s
        real_hel1os_resampled = resample_payload(real_hel1os_df, 'REAL_HEL1OS', '10s')
        
        if master_df is None:
            master_df = real_hel1os_resampled
        else:
            master_df = pd.merge(master_df, real_hel1os_resampled, on='timestamp', how='outer')

    # Integrate real SoLEXS Telemetry if available
    real_solexs_path = "scripts/solexs_telemetry.csv"
    if os.path.exists(real_solexs_path):
        print(f"   -> Merging Real SoLEXS X-Ray Data: {real_solexs_path}")
        real_solexs_df = pd.read_csv(real_solexs_path)
        real_solexs_df['timestamp'] = pd.to_datetime(real_solexs_df['timestamp'])
        
        # Resample to 10s
        real_solexs_resampled = resample_payload(real_solexs_df, 'REAL_SOLEXS', '10s')
        
        if master_df is None:
            master_df = real_solexs_resampled
        else:
            master_df = pd.merge(master_df, real_solexs_resampled, on='timestamp', how='outer')

    # Integrate real SPICE Metatdata if available
    real_spice_path = "scripts/spice_telemetry.csv"
    if os.path.exists(real_spice_path):
        print(f"   -> Merging Real SPICE Orbital Data: {real_spice_path}")
        real_spice_df = pd.read_csv(real_spice_path)
        real_spice_df['timestamp'] = pd.to_datetime(real_spice_df['timestamp'])
        
        # Resample to 10s
        real_spice_resampled = resample_payload(real_spice_df, 'REAL_SPICE', '10s')
        
        if master_df is None:
            master_df = real_spice_resampled
        else:
            master_df = pd.merge(master_df, real_spice_resampled, on='timestamp', how='outer')

    # Integrate VELC Scientific Telemetry if available
    velc_path = "scripts/velc_telemetry.csv"
    if os.path.exists(velc_path):
        print(f"   -> Merging VELC Spectroscopic Data: {velc_path}")
        velc_df = pd.read_csv(velc_path)
        velc_df['timestamp'] = pd.to_datetime(velc_df['timestamp'])
        
        # Resample to 10s (VELC is typically 1m, so we interpolate)
        velc_resampled = resample_payload(velc_df, 'VELC', '10s')
        
        if master_df is None:
            master_df = velc_resampled
        else:
            master_df = pd.merge(master_df, velc_resampled, on='timestamp', how='outer')

    # Integrate SUIT Imaging Telemetry if available
    suit_path = "scripts/suit_telemetry.csv"
    if os.path.exists(suit_path):
        print(f"   -> Merging SUIT UV-Imaging Data: {suit_path}")
        suit_df = pd.read_csv(suit_path)
        suit_df['timestamp'] = pd.to_datetime(suit_df['timestamp'])
        
        # Resample to 10s (SUIT is variable cadence)
        suit_resampled = resample_payload(suit_df, 'SUIT', '10s')
        
        if master_df is None:
            master_df = suit_resampled
        else:
            master_df = pd.merge(master_df, suit_resampled, on='timestamp', how='outer')

    # Add Target (Hours-to-Event)
    target_path = os.path.join(input_dir, "mission_targets.csv")
    if os.path.exists(target_path):
        print(f"   -> Merging Mission Targets: {target_path}")
        target_df = pd.read_csv(target_path)
        target_df['timestamp'] = pd.to_datetime(target_df['timestamp'])
        # Target only needs 'mean' (or take any, it's low cadence anyway)
        target_resampled = target_df.set_index('timestamp').resample('10s').mean().reset_index()
        master_df = pd.merge(master_df, target_resampled, on='timestamp', how='left')

    # GAIN-inspired Imputation (Linear interpolation for mission continuity)
    print("   -> Performing Safety Sync: Forward-filling gaps for 99.9% pipeline uptime...")
    master_df = master_df.sort_values('timestamp').interpolate(method='linear').fillna(0)

    # Save processed dataset
    master_df.to_csv(output_file, index=False)
    print(f"✅ Preprocessing Pipeline Complete. Data saved to {output_file}")
    print(f"   -> Grid Sync: 10 seconds (Multi-Modal)")
    print(f"   -> Features generated: {len(master_df.columns) - 1}")

if __name__ == "__main__":
    run_pipeline()
