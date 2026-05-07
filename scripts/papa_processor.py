import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from datetime import datetime

# Optional dependency: cdflib is common for CDF files
try:
    import cdflib
except ImportError:
    cdflib = None
    print("⚠️  Warning: cdflib not installed. PAPA processing will use fallback.")

def extract_papa_metrics(cdf_path):
    """
    Extracts plasma flux and energy metrics from PAPA CDF files.
    """
    if cdflib is None:
        return 0.0, None # Placeholder
    
    try:
        cdf = cdflib.CDF(cdf_path)
        # PAPA SWP/SWR variables
        flux = cdf.varget("Electron_Flux", None) or cdf.varget("Ion_Flux", None) or cdf.varget("Flux", None)
        epoch = cdf.varget("Epoch", None)
        
        if flux is not None:
            mean_flux = float(np.mean(flux))
            obs_time = cdflib.cdfutil.to_datetime(epoch[0])[0] if epoch is not None else None
            return mean_flux, obs_time
    except Exception as e:
        pass
    return 0.0, None

def run_papa_pipeline(papa_dir="dataset/PAPA"):
    print("🛰️  BrahmaTron Sentinel: Initializing PAPA Plasma-Ingestion...")
    
    if not os.path.exists(papa_dir):
        print(f"❌ Directory {papa_dir} does not exist. Run downloader first.")
        return

    files = [f for f in os.listdir(papa_dir) if f.endswith(".cdf")]
    if not files:
        print("❌ No PAPA CDF files found.")
        return

    telemetry_data = []
    
    for filename in tqdm(files, desc="Parsing PAPA Streams"):
        file_path = os.path.join(papa_dir, filename)
        
        flux, obs_time = extract_papa_metrics(file_path)
        
        if obs_time is None:
            # Fallback to filename: PPA_SWR_ion_E32_..._20241231115955_L2_V1_0.cdf
            try:
                parts = filename.split('_')
                if len(parts) > 11:
                    date_part = parts[11] # 20241231115955
                    obs_time = datetime.strptime(date_part, "%Y%m%d%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")
            except:
                continue

        if obs_time:
            telemetry_data.append({
                'timestamp': obs_time,
                'papa_plasma_flux': flux
            })

    if not telemetry_data:
        print("⚠️  Warning: No valid PAPA telemetry extracted.")
        df = pd.DataFrame(columns=['timestamp', 'papa_plasma_flux'])
    else:
        df = pd.DataFrame(telemetry_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
    
    # Export
    output_path = "scripts/papa_telemetry.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ PAPA Processing Complete. {len(df)} cycles synchronized to {output_path}")

if __name__ == "__main__":
    run_papa_pipeline()
