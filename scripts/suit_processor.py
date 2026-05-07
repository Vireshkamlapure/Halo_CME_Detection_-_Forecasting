import os
import pandas as pd
import numpy as np
from astropy.io import fits
from tqdm import tqdm
from datetime import datetime

def extract_suit_metrics(hdu):
    """
    Extracts mean intensity and standard deviation from SUIT imaging HDU.
    Used as a proxy for UV solar flux in the 10s-sync pipeline.
    """
    data = hdu.data
    if data is None:
        return 0.0, 0.0
    
    # Simple statistics from the CCD frame
    mean_intensity = np.mean(data)
    std_intensity = np.std(data)
    
    return float(mean_intensity), float(std_intensity)

def run_suit_pipeline(suit_dir="dataset/SUIT"):
    print("🛰️  BrahmaTron Sentinel: Initializing SUIT UV-Imaging Ingestion...")
    
    if not os.path.exists(suit_dir):
        print(f"❌ Directory {suit_dir} does not exist. Run downloader first.")
        return

    files = [f for f in os.listdir(suit_dir) if f.endswith(".fits")]
    if not files:
        print("❌ No SUIT FITS files found.")
        return

    telemetry_data = []
    
    for filename in tqdm(files, desc="Parsing SUIT Frames"):
        file_path = os.path.join(suit_dir, filename)
        obs_time_str = None
        mean_flux, flux_std = 0.0, 0.0
        
        try:
            with fits.open(file_path) as hdul:
                header = hdul[0].header
                obs_time_str = header.get('DATE-OBS', header.get('DATE-BEG', None))
                
                # Extract metrics
                hdu_to_process = hdul[0]
                if hdu_to_process.data is None and len(hdul) > 1:
                    hdu_to_process = hdul[1]
                mean_flux, flux_std = extract_suit_metrics(hdu_to_process)
        except:
            pass 

        if not obs_time_str:
            # Fallback to filename: SUT_T26_0567_002052_Lev1.0_2026-04-10T18.10.24.523_...
            try:
                parts = filename.split('_')
                # The date part is the 6th element (index 5)
                if len(parts) > 5:
                    raw_ts = parts[5] # 2026-04-10T18.10.24.523
                    if 'T' in raw_ts:
                        date_p, time_p = raw_ts.split('T')
                        time_p = time_p.replace('.', ':', 2) # Fix 18.10.24 -> 18:10:24
                        obs_time_str = f"{date_p}T{time_p}"
            except:
                continue

        if obs_time_str:
            telemetry_data.append({
                'timestamp': obs_time_str,
                'suit_mean_intensity': mean_flux,
                'suit_intensity_std': flux_std
            })

    # Robust dataframe initialization
    if not telemetry_data:
        print("⚠️  Warning: No valid SUIT telemetry extracted.")
        df = pd.DataFrame(columns=['timestamp', 'suit_mean_intensity', 'suit_intensity_std'])
    else:
        df = pd.DataFrame(telemetry_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
    
    # Export for multi-modal merge
    output_path = "scripts/suit_telemetry.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ SUIT Processing Complete. {len(df)} frames synchronized to {output_path}")

if __name__ == "__main__":
    run_suit_pipeline()
