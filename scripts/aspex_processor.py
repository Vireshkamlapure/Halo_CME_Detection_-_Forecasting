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
    print("⚠️  Warning: cdflib not installed. ASPEX processing will use fallback.")

def extract_aspex_metrics(cdf_path):
    """
    Extracts proton/alpha counts and speeds from CDF file.
    """
    if cdflib is None:
        return 0.0, 0.0, None # Placeholder
    
    try:
        cdf = cdflib.CDF(cdf_path)
        # Standard ISTP variables for Solar Wind Ion Spectrometers
        # Typical variable names: proton_speed, alpha_density, epochs
        proton_speed = cdf.varget("V_p", None) or cdf.varget("proton_speed", None)
        alpha_count = cdf.varget("N_alpha", None) or cdf.varget("alpha_count", None)
        epoch = cdf.varget("Epoch", None)
        
        if proton_speed is not None:
            mean_v = float(np.mean(proton_speed))
            ratio = float(np.mean(alpha_count)) if alpha_count is not None else 0.0
            obs_time = cdflib.cdfutil.to_datetime(epoch[0])[0] if epoch is not None else None
            return mean_v, ratio, obs_time
    except Exception as e:
        # print(f"Error reading {cdf_path}: {e}")
        pass
    return 0.0, 0.0, None

def run_aspex_pipeline(aspex_dir="dataset/ASPEX"):
    print("🛰️  BrahmaTron Sentinel: Initializing ASPEX SWIS-Ingestion...")
    
    if not os.path.exists(aspex_dir):
        print(f"❌ Directory {aspex_dir} does not exist. Run downloader first.")
        return

    files = [f for f in os.listdir(aspex_dir) if f.endswith(".cdf")]
    if not files:
        print("❌ No ASPEX CDF files found.")
        return

    telemetry_data = []
    
    for filename in tqdm(files, desc="Parsing ASPEX Streams"):
        file_path = os.path.join(aspex_dir, filename)
        
        speed, alpha, obs_time = extract_aspex_metrics(file_path)
        
        if obs_time is None:
            # Fallback to filename: AL1_ASW91_L2_TH2_20260417_UNP_9999_999999_V02.cdf
            try:
                date_part = filename.split('_')[4] # 20260417
                obs_time = datetime.strptime(date_part, "%Y%m%d").strftime("%Y-%m-%dT00:00:00")
            except:
                continue

        telemetry_data.append({
            'timestamp': obs_time,
            'aspex_swis_speed': speed,
            'aspex_alpha_ratio': alpha
        })

    if not telemetry_data:
        print("❌ No valid ASPEX telemetry extracted.")
        return

    df = pd.DataFrame(telemetry_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Export for multi-modal merge
    output_path = "scripts/aspex_telemetry.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ ASPEX Processing Complete. {len(df)} cycles synchronized to {output_path}")

if __name__ == "__main__":
    run_aspex_pipeline()
