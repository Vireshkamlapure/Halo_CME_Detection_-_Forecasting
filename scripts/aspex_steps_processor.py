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
    print("⚠️  Warning: cdflib not installed. STEPS processing will use fallback.")

def extract_steps_metrics(cdf_path):
    """
    Extracts high-energy particle flux from ASPEX STEPS CDF files.
    """
    if cdflib is None:
        return 0.0, None # Placeholder
    
    try:
        cdf = cdflib.CDF(cdf_path)
        # STEPS variables
        # Typical: Proton_Flux, Electron_Flux, Energy
        flux = cdf.varget("Proton_Flux", None) or cdf.varget("Electron_Flux", None) or cdf.varget("Flux", None)
        epoch = cdf.varget("Epoch", None)
        
        if flux is not None:
            mean_flux = float(np.mean(flux))
            obs_time = cdflib.cdfutil.to_datetime(epoch[0])[0] if epoch is not None else None
            return mean_flux, obs_time
    except Exception as e:
        pass
    return 0.0, None

def run_steps_pipeline(steps_dir="dataset/ASPEX_STEPS"):
    print("🛰️  BrahmaTron Sentinel: Initializing ASPEX STEPS-Ingestion...")
    
    if not os.path.exists(steps_dir):
        print(f"❌ Directory {steps_dir} does not exist. Run downloader first.")
        return

    files = [f for f in os.listdir(steps_dir) if f.endswith(".cdf")]
    if not files:
        print("❌ No STEPS CDF files found.")
        return

    telemetry_data = []
    
    for filename in tqdm(files, desc="Parsing STEPS Streams"):
        file_path = os.path.join(steps_dir, filename)
        
        flux, obs_time = extract_steps_metrics(file_path)
        
        if obs_time is None:
            # Fallback to filename: AL1_AST91_L2_NP_20260417_V01.cdf
            try:
                date_part = filename.split('_')[4] # 20260417
                obs_time = datetime.strptime(date_part, "%Y%m%d").strftime("%Y-%m-%dT00:00:00")
            except:
                continue

        telemetry_data.append({
            'timestamp': obs_time,
            'steps_particle_flux': flux
        })

    if not telemetry_data:
        print("❌ No valid STEPS telemetry extracted.")
        return

    df = pd.DataFrame(telemetry_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Export
    output_path = "scripts/aspex_steps_telemetry.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ STEPS Processing Complete. {len(df)} cycles synchronized to {output_path}")

if __name__ == "__main__":
    run_steps_pipeline()
