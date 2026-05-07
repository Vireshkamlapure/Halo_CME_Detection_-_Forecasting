import numpy as np
import collections

class PlasmaProcessor:
    def __init__(self, mu_0=1.25663706e-6, k_b=1.380649e-23):
        """
        Constants:
        mu_0: Vacuum permeability (T.m/A)
        k_b: Boltzmann constant (J/K)
        """
        self.mu_0 = mu_0
        self.k_b = k_b
        
        # Ring buffer for 1300+ temporal feature generation via rolling stats
        self.history_len = 1350
        self.he_h_history = collections.deque(maxlen=self.history_len)

    def calculate_plasma_beta(self, n, T, B_mag_nT):
        """
        Calculates Plasma Beta (ASPEX).
        beta = (n * k * T) / (B^2 / 2*mu_0)
        n in m^-3, T in K, B in Tesla
        """
        B_tesla = B_mag_nT * 1e-9
        magnetic_pressure = (B_tesla**2) / (2 * self.mu_0)
        thermal_pressure = n * self.k_b * T
        
        if magnetic_pressure == 0: return float('inf')
        return thermal_pressure / magnetic_pressure

    def extract_papa_moments(self, distribution_func, velocities):
        """
        Calculates distribution moments for PAPA: 
        Number density (n), Bulk Velocity (V), Kinetic Temperature (Tk)
        """
        # 0th Moment: Density n
        n = np.trapz(distribution_func, velocities)
        
        if n == 0: return 0.0, 0.0, 0.0
        
        # 1st Moment: Bulk Velocity V
        V = np.trapz(velocities * distribution_func, velocities) / n
        
        # 2nd Moment: Kinetic Temperature Tk
        # Tk = (m / 3k) * integral((v - V)^2 * f(v) dv) / n
        # Approximated purely numerically here for protons
        m_p = 1.6726219e-27
        thermal_var = np.trapz(((velocities - V)**2) * distribution_func, velocities) / n
        T_k = (m_p * thermal_var) / (3 * self.k_b)
        
        return n, V, T_k

    def check_anisotropy(self, T_perp, T_parallel):
        """
        Diagnosis: Temperature anisotropy indices (T_perp != T_parallel)
        """
        if T_parallel == 0: return 1.0, False
        anisotropy = T_perp / T_parallel
        is_anisotropic = abs(1.0 - anisotropy) > 0.2 # 20% deviation threshold
        return anisotropy, is_anisotropic

    def evaluate_icme_shock(self, he_count, h_count):
        """
        Evaluates Helium-to-Proton (He++/H+) ratios for shock triggers.
        Returns: ratio, is_shock_onset (if deviation > 2 sigma from baseline)
        """
        if h_count == 0: return 0.0, False
        
        current_ratio = he_count / h_count
        self.he_h_history.append(current_ratio)
        
        if len(self.he_h_history) < 100:
            # Need sufficient baseline
            return current_ratio, False
            
        baseline_mean = np.mean(self.he_h_history)
        baseline_std = np.std(self.he_h_history)
        
        # > 2 sigma deviation
        is_shock = current_ratio > (baseline_mean + 2 * baseline_std)
        
        return current_ratio, is_shock
