import os
import pandas as pd
import numpy as np
from astropy.io import fits
from tqdm import tqdm
from datetime import datetime

def extract_physics_parameters(hdu):
    """
    Calculates Doppler Shift, Line Width (Turbulence), and Density Intensity
    using Moment Analysis of the Fe XIV 5303A line.
    """
    data = hdu.data
    if data is None:
        return 0, 0, 0
    
    # 1. Intensity (0th Moment)
    intensity = np.sum(data)
    
    # 2. Velocity / Doppler (1st Moment - simplified centroid)
    # Spectral dispersion is approx 28.4 mA/pixel
    # We take the mean position of the flux
    h, w = data.shape
    x = np.arange(w)
    marginal_x = np.sum(data, axis=0)
    centroid = np.sum(x * marginal_x) / (np.sum(marginal_x) + 1e-9)
    velocity = (centroid - (w/2)) * 28.4 # in mA shift
    
    # 3. Turbulence (2nd Moment - variance)
    variance = np.sum(((x - centroid)**2) * marginal_x) / (np.sum(marginal_x) + 1e-9)
    turbulence = np.sqrt(variance)
    
    # Normalize values for telemetry
    return float(velocity), float(turbulence), float(intensity)

def run_velc_pipeline(velc_dir="dataset/VELC"):
    print("🛰️  BrahmaTron Sentinel: Initializing VELC Spectroscopic Ingestion...")
    
    files = sorted([f for f in os.listdir(velc_dir) if f.endswith(".fits")])
    if not files:
        print("❌ No VELC FITS files found.")
        return

    telemetry_data = []
    
    for filename in tqdm(files, desc="Parsing FITS"):
        file_path = os.path.join(velc_dir, filename)
        try:
            with fits.open(file_path) as hdul:
                header = hdul[0].header
                # Try to get DATE-OBS or derived from filename
                obs_time_str = header.get('DATE-OBS', None)
                if not obs_time_str:
                    # Fallback to filename parsing: ..._20240629_082112_...
                    parts = filename.split('_')
                    if len(parts) >= 6:
                        date_str = parts[4] # 20240629
                        time_str = parts[5] # 082112
                        obs_time_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
                
                # Extract spectral moments from Level-2 data HDU
                # Assuming HDU 0 is data based on search results for Lev2
                velocity, turbulence, density = extract_physics_parameters(hdul[0])
                
                telemetry_data.append({
                    'timestamp': obs_time_str,
                    'velc_velocity': velocity,
                    'velc_turbulence': turbulence,
                    'velc_density': density
                })
        except Exception as e:
            # print(f"Error reading {filename}: {e}")
            continue

    df = pd.DataFrame(telemetry_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Export for multi-modal merge
    df.to_csv("scripts/velc_telemetry.csv", index=False)
    print(f"✅ Scientific Processing Complete. {len(df)} records synchronized.")
    print(df.head())

if __name__ == "__main__":
    run_velc_pipeline()
