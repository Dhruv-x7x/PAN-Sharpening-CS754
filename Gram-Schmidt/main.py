from src.band_operations import read_band, resample_band, load_bands, resample_ms_to_pan, downsample_image
from src.gram_schmidt import pansharpen_gs
import numpy as np

def print_image_stats(image, name, is_3d=False):
    print(f"\n{name}:")
    if is_3d:
        for i in range(image.shape[0]):
            band = image[i]
            print(f"Band {i+1} - Min: {np.min(band):.2f}, Max: {np.max(band):.2f}, Mean: {np.mean(band):.2f}")
    else:
        print(f"Min: {np.min(image):.2f}, Max: {np.max(image):.2f}, Mean: {np.mean(image):.2f}")

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
    
    # Print initial statistics
    print("\nInitial values:")
    print_image_stats(pan, "Pan")
    for i, band in enumerate(ms_list):
        print_image_stats(band, f"MS Band {i+1}")
    
    # original MS shape 
    original_ms_shape = ms_list[0].shape
    
    # Testing resampling using resample_ms_to_pan function
    print("\nTesting resampling using resample_ms_to_pan function:")
    resampled_ms_array = resample_ms_to_pan(ms_list, ms_meta_list, pan.shape, pan_meta)
    
    # Print shapes of resampled bands
    for i in range(resampled_ms_array.shape[0]):
        print(f"Resampled multispectral band {i+1} shape: {resampled_ms_array[i].shape}")
    
    # Print statistics after resampling
    print_image_stats(resampled_ms_array, "After resampling", is_3d=True)
    
    # Test Gram-Schmidt pansharpening
    print("\nTesting Gram-Schmidt pansharpening:")
    sharpened_ms = pansharpen_gs(resampled_ms_array, pan)
    print(f"Sharpened multispectral image shape: {sharpened_ms.shape}")
    
    # Print statistics after pansharpening
    print_image_stats(sharpened_ms, "After pansharpening", is_3d=True)
    
    # Downsample the sharpened image 
    print("\nDownsampling the sharpened image to original MS resolution:")
    downsampled_sharpened = np.zeros((sharpened_ms.shape[0], original_ms_shape[0], original_ms_shape[1]))
    for i in range(sharpened_ms.shape[0]):
        downsampled_sharpened[i] = downsample_image(sharpened_ms[i], original_ms_shape)
    print(f"Original sharpened shape: {sharpened_ms.shape}")
    print(f"Downsampled sharpened shape: {downsampled_sharpened.shape}")
    
    # Print statistics after downsampling
    print_image_stats(downsampled_sharpened, "After downsampling", is_3d=True)
   
if __name__ == "__main__":
    main()
