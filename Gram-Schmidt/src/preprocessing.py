import rasterio


def read_band(filepath):
    """Reads a single band from a raster file."""
    print(f"Reading {filepath}")
    with rasterio.open(filepath) as src:
        band = src.read(1)  # reading the first band
        meta = src.meta
    return band, meta