from src.preprocessing import read_band, resample_band, load_bands, resample_ms_to_pan
from src.gram_schmidt import pansharpen_gs
import numpy as np

def main():
    # Test load_bands function
    print("\nTesting load_bands function:")
    ms_list, ms_meta_list, pan, pan_meta = load_bands("data")
    
    if ms_list is None:
        print("Failed to load bands.")
        return
        
    print(f"\nSuccessfully loaded {len(ms_list)} multispectral bands")
    print(f"Panchromatic band shape: {pan.shape}")
    
    # Print shapes of all multispectral bands
    for i, (band, meta) in enumerate(zip(ms_list, ms_meta_list)):
        print(f"Multispectral band {i+1} shape: {band.shape}")
    
    # Testing resampling using resample_ms_to_pan function
    print("\nTesting resampling using resample_ms_to_pan function:")
    resampled_ms_array = resample_ms_to_pan(ms_list, ms_meta_list, pan.shape, pan_meta)
    
    # Print shapes of resampled bands
    for i in range(resampled_ms_array.shape[0]):
        print(f"Resampled multispectral band {i+1} shape: {resampled_ms_array[i].shape}")
    
    # Test Gram-Schmidt pansharpening
    print("\nTesting Gram-Schmidt pansharpening:")
    sharpened_ms = pansharpen_gs(resampled_ms_array, pan)
    print(f"Sharpened multispectral image shape: {sharpened_ms.shape}")
    
    # stats
    for i in range(sharpened_ms.shape[0]):
        print(f"Sharpened band {i+1} - Mean: {np.mean(sharpened_ms[i]):.2f}, Std: {np.std(sharpened_ms[i]):.2f}")
   
if __name__ == "__main__":
    main()
