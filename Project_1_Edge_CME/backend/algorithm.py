import pandas as pd
import numpy as np
from scipy import stats

class EdgeCMEDetector:
    """
    Multivariate Dynamic Thresholding Engine for SWIS-ASPEX datasets.
    Implements rolling Z-score analysis and CEF0.5 Score optimization.
    """
    def __init__(self, window_size=60, z_threshold=3.5, beta=0.5):
        self.window_size = window_size
        self.z_threshold = z_threshold
        self.beta = beta # F-beta score optimization factor

    def calculate_dynamic_thresholds(self, df):
        """
        Calculates adaptive thresholds based on a rolling window of past observations.
        """
        processed_df = df.copy()
        
        # Calculate Rolling Stats for Proton Flux
        rolling = processed_df['proton_flux'].rolling(window=self.window_size)
        processed_df['p_mean'] = rolling.mean()
        processed_df['p_std'] = rolling.std()
        
        # Dynamic Z-Score
        processed_df['z_score'] = (processed_df['proton_flux'] - processed_df['p_mean']) / processed_df['p_std']
        
        # Anomaly Detection (Thresholding)
        processed_df['is_anomaly'] = (processed_df['z_score'] > self.z_threshold).astype(int)
        
        return processed_df

    def cef05_metric(self, y_true, y_pred):
        """
        Calculates the CEF0.5 score (Custom Edge score with Precision priority).
        Weights precision higher to minimize false alarms on edge hardware.
        """
        tp = np.sum((y_true == 1) & (y_pred == 1))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        fn = np.sum((y_true == 1) & (y_pred == 0))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        # F-beta formula
        beta_sq = self.beta ** 2
        numerator = (1 + beta_sq) * precision * recall
        denominator = (beta_sq * precision) + recall
        
        if denominator == 0:
            return 0
        return numerator / denominator

# Example Usage & Scientific Sandbox
if __name__ == "__main__":
    # Mock data for demonstration
    data = {'proton_flux': np.random.normal(100, 10, 1000)}
    data['proton_flux'][500:510] *= 10 # Sudden spike
    df = pd.DataFrame(data)
    
    detector = EdgeCMEDetector()
    results = detector.calculate_dynamic_thresholds(df)
    
    anomaly_count = results['is_anomaly'].sum()
    print(f"Detected {anomaly_count} CME candidates.")
