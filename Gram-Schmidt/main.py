from src.band_operations import read_band, resample_band, load_bands, resample_ms_to_pan, downsample_image
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
    
    # original MS shape 
    original_ms_shape = ms_list[0].shape
    
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
    
    # Downsample the sharpened image 
    print("\nDownsampling the sharpened image to original MS resolution:")
    downsampled_sharpened = np.zeros((sharpened_ms.shape[0], original_ms_shape[0], original_ms_shape[1]))
    for i in range(sharpened_ms.shape[0]):
        downsampled_sharpened[i] = downsample_image(sharpened_ms[i], original_ms_shape)
    print(f"Original sharpened shape: {sharpened_ms.shape}")
    print(f"Downsampled sharpened shape: {downsampled_sharpened.shape}")
    
    # stats
    for i in range(sharpened_ms.shape[0]):
        print(f"Sharpened band {i+1} - Mean: {np.mean(sharpened_ms[i]):.2f}, Std: {np.std(sharpened_ms[i]):.2f}")
   
if __name__ == "__main__":
    main()
