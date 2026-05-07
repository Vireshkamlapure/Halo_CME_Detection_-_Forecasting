import pandas as pd
import json
import os

def export_to_dashboard(csv_file="processed_mission_data.csv", output_dir="Project_2_3D_L1_Sim/dashboard/public"):
    """
    Converts processed mission data to a compressed JSON format for the React dashboard.
    Ensures Three.js can parse frames efficiently during Time-Machine playback.
    """
    print(f"🌉 Initializing Data Bridge: {csv_file} -> JSON")
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} not found. Run scripts/preprocess.py first.")
        return

    df = pd.read_csv(csv_file)
    
    # 1. Row Decimation / Selection for Dashboard
    # To keep the frontend smooth, we export everything but round floating points
    df = df.round(4)
    
    # 2. Structure for Easy Indexing by Frame
    # [{timestamp: ..., MAG_B_z_max: ...}, ...]
    data_list = df.to_dict(orient='records')
    
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "telemetry_data.json")
    
    with open(json_path, 'w') as f:
        json.dump(data_list, f)
        
    print(f"✅ Data exported to {json_path}")
    print(f"   -> Records: {len(data_list)}")
    print(f"   -> Features per record: {len(df.columns)}")

def sync_importance_manifest(manifest_file="scripts/importance_manifest.json", output_dir="Project_2_3D_L1_Sim/dashboard/public"):
    """
    Moves the importance manifest to the dashboard's public directory for sensor highlighting.
    """
    if not os.path.exists(manifest_file):
        print("⚠️ Warning: Importance manifest not found. Run scripts/tft_prognosis.py to generate it.")
        return
        
    import shutil
    shutil.copy(manifest_file, os.path.join(output_dir, "importance_manifest.json"))
    print(f"✅ Importance manifest synced to dashboard.")

if __name__ == "__main__":
    export_to_dashboard()
    sync_importance_manifest()
