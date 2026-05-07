class SUITProcessor:
    """
    Solar Ultraviolet Imaging Telescope processing payload.
    """
    def __init__(self):
        self.contrast_threshold = 10.0 # 10:1 Contrast Ratio
        
    def evaluate_contrast_ratio(self, plage_intensity, background_intensity):
        """
        Math: Contrast ratio evaluation for solar irradiance.
        """
        if background_intensity <= 0: return 0.0
        return plage_intensity / background_intensity
        
    def is_significant_eruption(self, contrast_ratio):
        """
        Checks if the contrast ratio meets the 10:1 requirement.
        """
        return contrast_ratio >= self.contrast_threshold

    def map_stratified_eruption(self, is_nb02_bright, is_nb05_bright):
        """
        Diagnosis: Depth-stratified imaging.
        Correlate brightenings in NB02/NB05 (Photosphere) with chromospheric eruptions.
        """
        if is_nb02_bright and is_nb05_bright:
            return "Deep Photospheric to Chromospheric Eruption Detected"
        elif is_nb02_bright:
            return "Lower Photospheric Eruption"
        elif is_nb05_bright:
            return "Upper Photospheric Eruption"
        return "Stable"
