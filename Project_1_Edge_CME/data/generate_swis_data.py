import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_swis_aspex_data(output_path, days=30):
    """
    Generates synthetic SWIS-ASPEX data for solar wind ion monitoring.
    Includes baseline noise and periodic CME (Coronal Mass Ejection) bursts.
    """
    np.random.seed(42)
    start_time = datetime(2026, 1, 1)
    
    # Frequency: 1 Sample per minute
    timestamps = [start_time + timedelta(minutes=i) for i in range(days * 24 * 60)]
    
    n_samples = len(timestamps)
    
    # Features: Proton Flux (n/cm^2/s), Alpha Flux, Iron/Oxygen Ratio, MAG Field Magnitude
    proton_flux = np.random.normal(loc=100, scale=10, size=n_samples)
    alpha_flux = np.random.normal(loc=5, scale=1, size=n_samples)
    fe_o_ratio = np.random.normal(loc=0.04, scale=0.01, size=n_samples)
    
    # Inject CME Events
    # Event 1: Moderate CME at day 10
    cme_start = 10 * 24 * 60
    cme_duration = 120 # 2 hours
    proton_flux[cme_start:cme_start+cme_duration] *= 5 + np.random.uniform(2, 5, size=cme_duration)
    alpha_flux[cme_start:cme_start+cme_duration] *= 3
    
    # Event 2: Major Flare at day 22
    flare_start = 22 * 24 * 60
    flare_duration = 60
    proton_flux[flare_start:flare_start+flare_duration] *= 20
    fe_o_ratio[flare_start:flare_start+flare_duration] += 0.1
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'proton_flux': proton_flux.clip(min=0),
        'alpha_flux': alpha_flux.clip(min=0),
        'fe_o_ratio': fe_o_ratio.clip(min=0)
    })
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {n_samples} samples at {output_path}")

if __name__ == "__main__":
    generate_swis_aspex_data("Project_1_Edge_CME/data/swis_aspex_raw.csv")
