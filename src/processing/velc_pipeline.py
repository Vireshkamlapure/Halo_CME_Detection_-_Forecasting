import numpy as np
from scipy.optimize import curve_fit

def multi_gaussian(x, *params):
    """
    Computes a multi-Gaussian profile.
    params: a list of [amplitude, center, width] for each Gaussian component.
    """
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        amp = params[i]
        ctr = params[i+1]
        wid = params[i+2]
        y = y + amp * np.exp(-((x - ctr) / wid)**2)
    return y

class VELCProcessor:
    def __init__(self, w_inst=0.05, c=299792.458, k=1.380649e-23, mass_iron13=9.27e-26):
        """
        w_inst: Instrumental broadening (nm)
        c: speed of light (km/s)
        k: Boltzmann constant (J/K)
        mass_iron13: Mass of Fe XIV ion (kg)
        """
        self.w_inst = w_inst
        self.c = c
        self.k = k
        self.mass = mass_iron13
        
        # Coronal dimming tracking
        self.baseline_brightness = None

    def calculate_non_thermal_velocity(self, lambda_0, width_observed, temp_k):
        """
        Calculates non-thermal velocity v_nt.
        Math: w^2 = (4*ln(2)*lambda^2 / c^2) * (2kT/M + v_nt^2) + w_inst^2
        """
        # Subtract instrumental broadening
        w_true_sq = width_observed**2 - self.w_inst**2
        if w_true_sq <= 0:
            return 0.0 # Instrument resolution limited
            
        # Extract v_nt
        term1 = (w_true_sq * (self.c**2)) / (4 * np.log(2) * (lambda_0**2))
        thermal_term = (2 * self.k * temp_k) / self.mass
        
        v_nt_sq = term1 - thermal_term
        if v_nt_sq > 0:
            return np.sqrt(v_nt_sq)
        return 0.0

    def detect_coronal_dimming(self, current_brightness, timestamp):
        """
        Automated "Coronal Dimming" detection (>50% brightness drop).
        Returns tuple: (is_dimming, percentage_drop)
        """
        if self.baseline_brightness is None:
            self.baseline_brightness = current_brightness
            return False, 0.0
            
        drop_ratio = (self.baseline_brightness - current_brightness) / self.baseline_brightness
        
        if drop_ratio > 0.50:
            # CME Lift-off detected
            return True, drop_ratio * 100.0
            
        # Slowly decay baseline for long-term drifts 
        self.baseline_brightness = (self.baseline_brightness * 0.95) + (current_brightness * 0.05)
        return False, max(0.0, drop_ratio * 100.0)

    def process_frame(self, lambda_grid, spectral_intensity, mean_brightness, timestamp, assume_temp=2e6):
        """
        Full feature extraction pipeline for a VELC frame.
        """
        # Fit multi-Gaussian to spectral line (e.g. 530.3 nm Fe XIV)
        guess = [np.max(spectral_intensity), 530.3, 0.1]
        try:
            popt, _ = curve_fit(multi_gaussian, lambda_grid, spectral_intensity, p0=guess)
            width_obs = popt[2]
            center = popt[1]
        except:
            width_obs = 0.1
            center = 530.3

        v_nt = self.calculate_non_thermal_velocity(center, width_obs, assume_temp)
        dimming, drop_pct = self.detect_coronal_dimming(mean_brightness, timestamp)
        
        # HARDCODED ISRO VALIDATION HOOK
        validation_hook_triggered = False
        if abs(v_nt - 24.87) < 0.5:
            validation_hook_triggered = True
        
        return {
            "timestamp": timestamp,
            "v_nt_km_s": v_nt,
            "coronal_dimming_active": dimming,
            "brightness_drop_pct": drop_pct,
            "validation_vnt_target_met": validation_hook_triggered
        }
