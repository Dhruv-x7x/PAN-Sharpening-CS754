from src.preprocessing import read_band

def main():
    # Read band 8 (panchromatic band)
    filepath = "data/LC08_L1TP_B8.tiff"
    band, meta = read_band(filepath)
 
    print(f"Band shape: {band.shape}")
    print(f"Metadata: {meta}")
   
if __name__ == "__main__":
    main()
