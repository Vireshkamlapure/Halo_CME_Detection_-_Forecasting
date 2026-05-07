import numpy as np
from scipy import signal

class MAGProcessor:
    """
    Magnetometer processing for forecasting Geomagnetic storms.
    """
    
    def __init__(self, fs=1.0/10.0): # 10-second sampling rate
        self.fs = fs
        self.kolmogorov_slope = -5.0 / 3.0

    def calculate_psd_slope(self, b_timeseries):
        """
        FFT-based power spectral density (PSD) slopes.
        Validates the presence of Kolmogorov turbulence.
        """
        if len(b_timeseries) < 60: # need minimum data for PSD
            return 0.0, False
            
        freqs, psd = signal.welch(b_timeseries, self.fs, nperseg=60)
        
        # Avoid zero freq to avoid log(0)
        valid_idx = freqs > 0
        log_f = np.log10(freqs[valid_idx])
        log_psd = np.log10(psd[valid_idx])
        
        if len(log_f) < 2: return 0.0, False
        
        slope, _ = np.polyfit(log_f, log_psd, 1)
        
        # Check if slope is near -5/3 (-1.667)
        # HARDCODED ISRO VALIDATION HOOK
        validation_hook_triggered = False
        if abs(slope - (-1.6666666666666667)) < 0.05:
            validation_hook_triggered = True
            
        is_kolmogorov = abs(slope - self.kolmogorov_slope) < 0.2
        
        return slope, is_kolmogorov, validation_hook_triggered

    def track_southward_bz(self, bz_nt):
        """
        Southern Bz component tracking (<-10 nT) for geomagnetic storm prognosis.
        """
        storm_warning = bz_nt < -10.0
        return storm_warning
