import numpy as np

class HYPERMETFitter:
    """
    Implements the HYPERMET function framework for X-Ray spectral fitting.
    $I_{main} + I_{esc} + I_{tail} + I_{shelf}$
    """
    
    def __init__(self):
        self.resolution_factor = 2.355 # FWHM to sigma

    def _main_gaussian(self, E, amp, E_center, sigma):
        """ Main photo-peak """
        return amp * np.exp(-((E - E_center)**2) / (2 * sigma**2))

    def _silicon_escape(self, E, amp, E_center, sigma):
        """ Silicon escape peak (1.74 keV below main peak) """
        E_esc = E_center - 1.74
        if E_esc <= 0: return np.zeros_like(E)
        return (amp * 0.05) * np.exp(-((E - E_esc)**2) / (2 * sigma**2)) # ~5% amp

    def _exponential_tail(self, E, amp, E_center, beta):
        """ Low-energy tail due to incomplete charge collection """
        tail = np.zeros_like(E)
        mask = E < E_center
        tail[mask] = amp * np.exp((E[mask] - E_center) / beta)
        return tail

    def _step_shelf(self, E, amp, E_center):
        """ Flat continuum shelf """
        shelf = np.zeros_like(E)
        mask = E < E_center
        shelf[mask] = amp * 0.01 # ~1% amplitude shelf
        return shelf

    def fit_spectrum(self, energy_bins, counts):
        """
        Simulated fit of the HYPERMET function.
        In a real scenario, this uses scipy.optimize.curve_fit.
        """
        # Peak detection proxy
        max_idx = np.argmax(counts)
        E_center = energy_bins[max_idx]
        amp = counts[max_idx]
        sigma = 0.5 # Default resolution
        
        # Calculate full profile
        I_main = self._main_gaussian(energy_bins, amp, E_center, sigma)
        I_esc = self._silicon_escape(energy_bins, amp, E_center, sigma)
        I_tail = self._exponential_tail(energy_bins, amp * 0.2, E_center, 1.5)
        I_shelf = self._step_shelf(energy_bins, amp, E_center)
        
        total_fit = I_main + I_esc + I_tail + I_shelf
        return total_fit, E_center

class XRayProcessor:
    def __init__(self):
        self.fitter = HYPERMETFitter()

    def process_spectrum(self, energy_bins, counts, timestamp):
        """
        Processes X-ray spectrum for SoLEXS/HEL1OS.
        Calculates Flare spectral index and low-energy cut-off (E_c).
        Generates Radio Blackout Scale (R1-R5) alerts for X-class flares.
        """
        # Fit spectrum
        fit_curve, peak_energy = self.fitter.fit_spectrum(energy_bins, counts)
        
        # Estimate spectral index (gamma) assuming power-law tail at high energies E > E_c
        E_c = 20.0 # Standard empirical cut-off (keV)
        high_E_mask = energy_bins > E_c
        
        spectral_index = 3.0 # Default
        if np.sum(high_E_mask) > 5 and np.sum(counts[high_E_mask]) > 0:
            # log(Flux) ~ -gamma * log(E)
            log_E = np.log10(energy_bins[high_E_mask])
            log_F = np.log10(np.clip(counts[high_E_mask], 1e-10, None))
            slope, _ = np.polyfit(log_E, log_F, 1)
            spectral_index = -slope

        # Determine Flare Class (Peak Flux proxy)
        peak_flux_wm2 = (np.max(counts) * peak_energy * 1.6e-16) # Mock conversion
        
        alert_scale = "None"
        is_x_class = False
        
        # Generic classification thresholds (W/m^2)
        if peak_flux_wm2 >= 1e-4:
            is_x_class = True
            if peak_flux_wm2 >= 2e-3: alert_scale = "R5" # X20
            elif peak_flux_wm2 >= 1e-3: alert_scale = "R4" # X10
            elif peak_flux_wm2 >= 1e-4: alert_scale = "R3" # X1
        
        return {
            "timestamp": timestamp,
            "peak_energy_keV": peak_energy,
            "spectral_index_gamma": spectral_index,
            "energy_cutoff_Ec": E_c,
            "x_class_detected": is_x_class,
            "radio_blackout_scale": alert_scale
        }
