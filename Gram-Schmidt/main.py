from src.preprocessing import read_band, resample_band, load_bands, resample_ms_to_pan

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
    
   
if __name__ == "__main__":
    main()
