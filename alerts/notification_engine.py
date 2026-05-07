class NotificationEngine:
    """
    Alerts mapper engine for the Aditya-L1 Dashboard.
    Maps localized payload triggers to the NOAA Space Weather Scales (R-S-G).
    """
    
    def __init__(self):
        self.active_alerts = []

    def evaluate_xray_flux(self, peak_flux_wm2):
        """
        Maps X-Ray flux (SoLEXS/HEL1OS) to the NOAA Radio Blackout (R) Scale.
        """
        alert = None
        if peak_flux_wm2 >= 2e-3: alert = ("R5", "Extreme Radio Blackout")
        elif peak_flux_wm2 >= 1e-3: alert = ("R4", "Severe Radio Blackout")
        elif peak_flux_wm2 >= 1e-4: alert = ("R3", "Strong Radio Blackout")
        elif peak_flux_wm2 >= 5e-5: alert = ("R2", "Moderate Radio Blackout")
        elif peak_flux_wm2 >= 1e-5: alert = ("R1", "Minor Radio Blackout")
        
        if alert:
            self._trigger(alert[0], alert[1], source="SoLEXS/HEL1OS X-Ray Trigger")
        return alert

    def evaluate_geomagnetic_prognosis(self, bz_nt, is_icme_shock=False):
        """
        Maps MAG & ASPEX data to NOAA Geomagnetic Storms (G) Scale.
        Aditya-L1 provides 1-4 hour advance warning of these conditions at Earth.
        """
        alert = None
        
        # Simplified logic for demonstrating the trigger mapping
        if is_icme_shock:
            if bz_nt < -50: alert = ("G5", "Extreme Geomagnetic Storm Predicted")
            elif bz_nt < -30: alert = ("G4", "Severe Geomagnetic Storm Predicted")
            elif bz_nt < -20: alert = ("G3", "Strong Geomagnetic Storm Predicted")
            elif bz_nt < -10: alert = ("G2", "Moderate Geomagnetic Storm Predicted")
        
        if alert:
            self._trigger(alert[0], alert[1], source="MAG/ASPEX ICME Shock")
        return alert

    def _trigger(self, scale, description, source):
        """
        Pushes alert to the Dashboard.
        """
        timestamp = "LIVE"
        msg = f"[{scale} ALERT] {description} (Source: {source})"
        self.active_alerts.append(msg)
        print(f"🚨 {msg}")
