import json
import time
import os
from datetime import datetime, timedelta

class SpaceWeatherAdvisor:
    """
    Intelligence layer for Project 2: 3D L1 Sim.
    Processes telemetry from VELC, MAG, and SWIS to provide actionable advisories.
    Now includes Mission Playback support for historical validation.
    """
    def __init__(self, base_data_dir="raw_data"):
        self.base_data_dir = base_data_dir
        self.severity_levels = {
            "G1": "Minor", "G2": "Moderate", "G3": "Strong", "G4": "Severe", "G5": "Extreme"
        }
        self.historical_events = {
            "HALLOWEEN_2003": {"flux_peak": 4500, "duration_hours": 72},
            "MAY_2024": {"flux_peak": 3200, "duration_hours": 48}
        }

    def get_historical_telemetry(self, event_name, offset_hours):
        """
        Simulates retrieval from the preserved directory structure.
        """
        if event_name not in self.historical_events:
            return None
        
        # Directory preservation logic check
        # In a real scenario, we'd read FITS/CSV from os.path.join(self.base_data_dir, "ARCHIVE", event_name)
        peak = self.historical_events[event_name]["flux_peak"]
        # Simple Gaussian-like curve for simulation
        flux = peak * (0.5 + 0.5 * (1 - (offset_hours / 24)**2)) 
        return max(flux, 100)

    def analyze_event(self, swis_flux, velc_halo_confirmed, is_playback=False):
        """
        Diagnosis and Prognosis engine with Playback awareness.
        """
        diagnosis = ""
        prognosis = ""
        alerts = []
        
        # Threshold Logic
        if swis_flux > 1000:
            level = "G3" if swis_flux < 3000 else "G5"
            diagnosis = f"{'PLAYBACK: ' if is_playback else ''}High-energy proton flux ({int(swis_flux)} pFU) detected."
            arrival_estimate = datetime.now() + timedelta(hours=18)
            prognosis = f"CME impact predicted at {arrival_estimate.strftime('%H:%M UTC')}. Level: {self.severity_levels[level]}."
            
            alerts.append("CRITICAL: Rotate Aditya-L1 Panels to minimize ion-sputtering.")
            if swis_flux > 2500:
                alerts.append("DANGER: Electronic Upset likely. Enable redundant command buffers.")
            else:
                alerts.append("WARNING: Suspend VELC high-gain telemetry to protect downlink.")
        else:
            diagnosis = "Solar activity within baseline parameters."
            prognosis = "No significant Earth-bound events predicted."
            
        return {
            "timestamp": datetime.now().isoformat(),
            "diagnosis": diagnosis,
            "prognosis": prognosis,
            "alerts": alerts,
            "status": "DANGER" if swis_flux > 2500 else ("WARNING" if alerts else "NORMAL"),
            "is_playback": is_playback
        }

if __name__ == "__main__":
    advisor = SpaceWeatherAdvisor()
    # Mocking a Historical Playback step
    historical_flux = advisor.get_historical_telemetry("HALLOWEEN_2003", offset_hours=5)
    report = advisor.analyze_event(swis_flux=historical_flux, velc_halo_confirmed=True, is_playback=True)
    print(json.dumps(report, indent=4))
