import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from datetime import datetime

# Optional dependency: netCDF4 is preferred for .nc files
try:
    from netCDF4 import Dataset as nc_dataset
except ImportError:
    nc_dataset = None
    print("⚠️  Warning: netCDF4 not installed. MAG processing will use fallback.")

def extract_mag_metrics(nc_path):
    """
    Extracts magnetic field intensity and variance from NetCDF file.
    """
    if nc_dataset is None:
        return 0.0, 0.0, 0.0 # Placeholder
    
    try:
        with nc_dataset(nc_path, 'r') as ds:
            # Common NetCDF variable names for MAG
            # We look for B_TOTAL, B_X, B_Y, B_Z or similar
            b_total = ds.variables.get('B_TOTAL', ds.variables.get('bt', None))
            timestamp = ds.variables.get('TIME', ds.variables.get('time', None))
            
            if b_total is not None:
                data = b_total[:]
                return float(np.mean(data)), float(np.std(data)), timestamp[0] if timestamp is not None else None
    except Exception as e:
        # print(f"Error reading {nc_path}: {e}")
        return 0.0, 0.0, None
    return 0.0, 0.0, None

def run_mag_pipeline(mag_dir="dataset/MAG"):
    print("🛰️  BrahmaTron Sentinel: Initializing MAG Triaxial-Flux Ingestion...")
    
    if not os.path.exists(mag_dir):
        print(f"❌ Directory {mag_dir} does not exist. Run downloader first.")
        return

    files = [f for f in os.listdir(mag_dir) if f.endswith(".nc")]
    if not files:
        print("❌ No MAG NetCDF files found.")
        return

    telemetry_data = []
    
    for filename in tqdm(files, desc="Parsing MAG Streams"):
        file_path = os.path.join(mag_dir, filename)
        
        # Try extracting from NetCDF
        mean_b, std_b, obs_time = extract_mag_metrics(file_path)
        
        if obs_time is None:
            # Fallback to filename: L2_AL1_MAG_20260409_V00.nc
            try:
                date_part = filename.split('_')[3] # 20260409
                obs_time = datetime.strptime(date_part, "%Y%m%d").strftime("%Y-%m-%dT00:00:00")
            except:
                continue

        telemetry_data.append({
            'timestamp': obs_time,
            'mag_b_total_mean': mean_b,
            'mag_b_total_std': std_b
        })

    if not telemetry_data:
        print("❌ No valid MAG telemetry extracted.")
        return

    df = pd.DataFrame(telemetry_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Export for multi-modal merge
    output_path = "scripts/mag_telemetry.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ MAG Processing Complete. {len(df)} days synchronized to {output_path}")

if __name__ == "__main__":
    run_mag_pipeline()
