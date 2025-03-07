from src.preprocessing import read_band, resample_band, load_bands

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
    
    # Testing resampling
    print("\nTesting resampling:")
    # Read band 8 (panchromatic band)
    pan_filepath = "data/LC08_L1TP_B8.tiff"
    pan_band, pan_meta = read_band(pan_filepath)
    
    # Read band 4 (red band) as an example of multispectral band
    ms_filepath = "data/LC08_L1TP_B4.tiff"
    ms_band, ms_meta = read_band(ms_filepath)
    
    print(f"Panchromatic band shape: {pan_band.shape}")
    print(f"Multispectral band shape: {ms_band.shape}")
    
    # Resample multispectral band to match panchromatic resolution
    resampled_ms = resample_band(
        ms_band,
        ms_meta,
        target_shape=pan_band.shape,
        target_transform=pan_meta['transform'],
        target_crs=pan_meta['crs']
    )
    
    print(f"Resampled multispectral band shape: {resampled_ms.shape}")
   
if __name__ == "__main__":
    main()
