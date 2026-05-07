from astropy.io import fits
import os
import sys

def inspect_fits(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    try:
        with fits.open(file_path) as hdul:
            print(f"--- FITS Info for {os.path.basename(file_path)} ---")
            hdul.info()
            
            for i, hdu in enumerate(hdul):
                print(f"\n--- HDU {i} Header ---")
                print(repr(hdu.header[:20])) # Print first 20 lines
                if hdu.data is not None:
                    print(f"Data Shape: {hdu.data.shape}")
                    print(f"Data Type: {hdu.data.dtype}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inspect_fits(sys.argv[1])
    else:
        # Default to first file in dataset/VELC
        velc_dir = "dataset/VELC"
        files = [f for f in os.listdir(velc_dir) if f.endswith(".fits")]
        if files:
            inspect_fits(os.path.join(velc_dir, files[0]))
        else:
            print("No FITS files found in dataset/VELC")
