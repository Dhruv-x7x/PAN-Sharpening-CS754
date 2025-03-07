import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject
import numpy as np
import glob
import os

def read_band(filepath):
    """Reads a single band from a raster file."""
    print(f"Reading {filepath}")
    with rasterio.open(filepath) as src:
        band = src.read(1)  # reading the first band
        meta = src.meta
    return band, meta

def resample_band(band, src_meta, target_shape, target_transform, target_crs):
    """
    Resamples a band to the target shape using bilinear interpolation.
    Args:
        band (numpy.ndarray): The input band to resample.
        src_meta (dict): Metadata of the source band.
        target_shape (tuple): Desired shape (height, width) for the output band.
        target_transform (Affine): Affine transformation for the target band.
        target_crs (CRS): Coordinate reference system for the target band.
    Returns:
        numpy.ndarray: Resampled band.
    """
    dst_band = np.empty(target_shape, dtype=band.dtype)
    reproject(
        source=band,
        destination=dst_band,
        src_transform=src_meta['transform'],
        src_crs=src_meta['crs'],
        dst_transform=target_transform,
        dst_crs=target_crs,
        resampling=Resampling.bilinear
    )
    return dst_band

def resample_ms_to_pan(ms_list, ms_meta_list, pan_shape, pan_meta):
    """
    Resamples each multispectral band to the panchromatic resolution if needed.
    Args:
        ms_list (list): List of multispectral bands.
        ms_meta_list (list): List of metadata for each multispectral band.
        pan_shape (tuple): Shape of the panchromatic band.
        pan_meta (dict): Metadata of the panchromatic band.
    Returns:
        numpy.ndarray: Array of resampled multispectral bands.
    """
    resampled_ms = []
    for band, meta in zip(ms_list, ms_meta_list):
        if band.shape != pan_shape:
            print("Resampling a multispectral band to match panchromatic resolution.")
            band_resampled = resample_band(band, meta, pan_shape, pan_meta['transform'], pan_meta['crs'])
        else:
            band_resampled = band
        resampled_ms.append(band_resampled)
    return np.array(resampled_ms)

def load_bands(data_folder):
    """Loads multispectral and panchromatic bands from the given folder."""
    all_tiff_files = glob.glob(os.path.join(data_folder, "*.tif")) + glob.glob(os.path.join(data_folder, "*.tiff"))
    
    # Identify bands
    band_map = {
        'B2': '_B2.', 'B3': '_B3.', 'B4': '_B4.', 'B5': '_B5.', 'B8': '_B8.'
    }
    bands = {name: [f for f in all_tiff_files if identifier in f] for name, identifier in band_map.items()}

    # Ensure required bands exist
    required_bands = ['B2', 'B3', 'B4', 'B8']
    for band in required_bands:
        if not bands[band]:
            print(f"ERROR: {band} band not found!")
            return None

    # Read required bands
    blue, blue_meta = read_band(bands['B2'][0])
    green, green_meta = read_band(bands['B3'][0])
    red, red_meta = read_band(bands['B4'][0])
    pan, pan_meta = read_band(bands['B8'][0])

    ms_list = [blue, green, red]
    ms_meta_list = [blue_meta, green_meta, red_meta]

    if bands['B5']:  # Optional NIR band
        nir, nir_meta = read_band(bands['B5'][0])
        ms_list.append(nir)
        ms_meta_list.append(nir_meta)

    return ms_list, ms_meta_list, pan, pan_meta