import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject
import numpy as np

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