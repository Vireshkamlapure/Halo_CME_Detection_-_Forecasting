import json
import os
import time

def generate_live_api(data_file="Project_2_3D_L1_Sim/dashboard/public/telemetry_data.json"):
    """
    Simulates a Mission API by enriching the local data bridge with active 
    Sentinel and Oracle flags.
    """
    print("🛰️  BrahmaTron Mission API: Syncing with Command Center...")
    
    if not os.path.exists(data_file):
        print("❌ Error: Telemetry JSON not found. Run scripts/data_bridge.py first.")
        return

    with open(data_file, 'r') as f:
        data = json.load(f)

    # Enrich with Mission State (Oracle Flags)
    threshold_hours = 24
    
    for frame in data:
        # Predict Red Alert status
        hte = frame.get('hours_to_event', 100)
        frame['is_red_alert'] = hte < threshold_hours
        
        # Calculate Expected Shock Arrival (Oracle)
        if hte < threshold_hours:
            frame['predicted_shock_eta'] = hte
        else:
            frame['predicted_shock_eta'] = None

    # Save as API payload
    api_path = "Project_2_3D_L1_Sim/dashboard/public/mission_api_payload.json"
    with open(api_path, 'w') as f:
        json.dump(data, f)
        
    print(f"✅ Mission API Payload Generated: {api_path}")
    print(f"   -> sentinel_state: ACTIVE")
    print(f"   -> oracle_forecast: {len(data)} frames")

if __name__ == "__main__":
    generate_live_api()
