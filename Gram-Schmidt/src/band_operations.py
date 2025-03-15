import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject
import numpy as np
import glob
import os
import cv2

def read_band(filepath):
    """Reads a single band from a raster file."""
    print(f"Reading {filepath}")
    with rasterio.open(filepath) as src:
        band = src.read(1)  # reading the first band
        print(f"Raw band data: {band}")
        print(f"Band stats - Min: {np.min(band)}, Max: {np.max(band)}, Mean: {np.mean(band)}")
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
    for i, (band, meta) in enumerate(zip(ms_list, ms_meta_list)):
        if band.shape != pan_shape:
            print(f"Resampling band {i+1} from shape {band.shape} to match panchromatic resolution {pan_shape}")
            band_resampled = resample_band(band, meta, pan_shape, pan_meta['transform'], pan_meta['crs'])
        else:
            band_resampled = band
            print(f"Band {i+1} already matches panchromatic resolution")
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

    print(f"All TIFF files found: {all_tiff_files}")
    print(f"Band mapping: {bands}")
    print(f"Required bands: {'B2', 'B3', 'B4', 'B8'}")

    # Ensure required bands exist
    required_bands = ['B2', 'B3', 'B4', 'B8']
    for band in required_bands:
        if not bands[band]:
            print(f"ERROR: {band} band not found!")
            return None
    print("All required bands found.")

    # Read required bands
    blue, blue_meta = read_band(bands['B2'][0])
    green, green_meta = read_band(bands['B3'][0])
    red, red_meta = read_band(bands['B4'][0])
    pan, pan_meta = read_band(bands['B8'][0])

    print(f"Blue band shape: {blue.shape}, Green band shape: {green.shape}, Red band shape: {red.shape}, Panchromatic band shape: {pan.shape}")

    ms_list = [blue, green, red]
    ms_meta_list = [blue_meta, green_meta, red_meta]
    band_names = ['Blue', 'Green', 'Red']

    if bands['B5']:  # Optional NIR band
        nir, nir_meta = read_band(bands['B5'][0])
        ms_list.append(nir)
        ms_meta_list.append(nir_meta)
        band_names.append('NIR')
        print("NIR band loaded successfully.")

    print("Loaded multispectral bands:", band_names)
    return ms_list, ms_meta_list, pan, pan_meta

def downsample_image(image, target_shape):
    """Downsamples a 2D image to the target shape using cv2.
    Args:
        image (numpy.ndarray): The input image to downsample.
        target_shape (tuple): Desired shape (height, width) for the output image.
    Returns:
        numpy.ndarray: Downsampled image.
    """
    # cv2.resize expects size as (width, height)
    return cv2.resize(image, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_AREA) # resamples pixel values using area relations by averaging neighboring pixels