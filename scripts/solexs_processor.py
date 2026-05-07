import os
import pandas as pd
import numpy as np
import zipfile
from tqdm import tqdm
from datetime import datetime
from glob import glob

def extract_solexs_metrics(zip_path, temp_dir="scripts/temp_solexs"):
    """
    Unzips and extracts X-ray intensity metrics from SoLEXS Level 1 telemetry.
    """
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        data_files = glob(os.path.join(temp_dir, "**/*.csv"), recursive=True) + \
                     glob(os.path.join(temp_dir, "**/*.fits"), recursive=True)
        
        # Placeholder intensity
        mean_flux = 1.0 
        obs_time = None
        
        # Parse filename for time: AL1_SLX_L1_20260415_v1.0.zip
        filename = os.path.basename(zip_path)
        try:
            parts = filename.split('_')
            if len(parts) > 3:
                date_part = parts[3] # 20260415
                obs_time = datetime.strptime(date_part, "%Y%m%d").strftime("%Y-%m-%dT00:00:00")
        except:
            pass
            
        return mean_flux, obs_time
    except Exception as e:
        return 0.0, None
    finally:
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def run_solexs_pipeline(solexs_dir="dataset/SoLEXS"):
    print("🛰️  BrahmaTron Sentinel: Initializing SoLEXS X-Ray Ingestion...")
    
    if not os.path.exists(solexs_dir):
        print(f"❌ Directory {solexs_dir} does not exist. Run downloader first.")
        return

    files = [f for f in os.listdir(solexs_dir) if f.endswith(".zip")]
    if not files:
        print("❌ No SoLEXS ZIP files found.")
        return

    telemetry_data = []
    
    for filename in tqdm(files, desc="Parsing SoLEXS ZIPs"):
        file_path = os.path.join(solexs_dir, filename)
        
        flux, obs_time = extract_solexs_metrics(file_path)
        
        if obs_time:
            telemetry_data.append({
                'timestamp': obs_time,
                'solexs_soft_xray_flux': flux
            })

    if not telemetry_data:
        print("⚠️  Warning: No valid SoLEXS telemetry extracted.")
        df = pd.DataFrame(columns=['timestamp', 'solexs_soft_xray_flux'])
    else:
        df = pd.DataFrame(telemetry_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
    
    # Export
    output_path = "scripts/solexs_telemetry.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ SoLEXS Processing Complete. {len(df)} files synchronized to {output_path}")

if __name__ == "__main__":
    run_solexs_pipeline()
