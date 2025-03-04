# Remote Sensing and Pan Sharpening Notes

## I. Introduction

Pan sharpening aims at increasing spatial resolution of multispectral images while preserving spectral information.

The spatial resolution of a remote sensing system is the area of the ground captured by one pixel.

The instantaneous field of view (IFOV) is the ground area sensed at a given instant of time

The reflectance is the ratio of the amount of light reflected by a surface to the amount of light incident to it.

Spectral resolution is the electromagnetic bandwidth of the signals captured. A higher spectral resolution corresponds to a narrower bandwidth, because it can therefore distinguishes a lot better finer differences in wavelengths.

- **Multispectral data (MS)**: Images with 4 to 7 spectral bands
- **Hyperspectral data (HS)**: Images with hundreds or thousands spectral bands

Along with the HS or MS image, the satellites provide a panchromatic image (PAN) which is a grayscale image containing reflectance data representative of a wide range of wavelengths from visible to thermal infrared. The panchromatic image is having a high spatial resolution as it integrates light from multiple wavelengths, allowing more energy to be captured per pixel.

Remote sensing systems needs to deal with a trade off between IFOV and signal to noise ratio (SNR).

## II. Pre-processing

Several factors can lead to:
- **Geometric errors** (distort shape, position, alignement of objects)
- **Radiometric errors** (affects the brightness of pixels)

Causes for geometric errors includes Earth's curvature, movement of the platform and sensor impreferctions. Causes for radiometric errors include solar radiation, atmospheric effects or limitations of the instrumentation.

It is necessary for many applications to make corrections in geometry and brightness before use. Through correction techniques, one can map the pixels of an image to geographic coordinates which is known as georeferencing or geocoding.

Data products are having several levels of preprocessing (Level 0, Level 1A, Level 1B…). Most of the datasets are built on Level 1.

For PANsharpening, at least geometric and radiometric corrections need to be performed on the satellite data. But however differences can appear across images such as object appearance or disappearance due to different spectral bands / different time acquisition.

The data needs to be processed to a standard level and further pre processed for pan sharpening which may include registration, re sampling and histogram matching of MS and PAN images.

### II.1 Image registration

Many applications of remote sensing image data require two or more scenes
of the same geographical region, acquired at different dates or from different
sensors, in order to be processed together. In this case, the role of image
registration is to make the pixels in the two images precisely coincide to the
same points on the ground.

Two images can be registered to each other
by registering each to a map coordinate base separately, or one image can be
chosen as a master to which the other is to be registered 

Due to the use of different sensors, this can be quite complicated, here are some problems image registration try to solve :

- Feature absence or presence 
- Contrast reversal (bright region might appear darker in another image)
- Multiple intensity values in one image that need to be mapped to a single intensity value in the other
- Considerably dissimilar images of the same scene produced by the image sensor when configured with different imaging parameters

Two types of image registration methods : 
- Area-based methods (Fourier methods, cross correlation, mutual information). Not well suited for the multisensor image registration problem
- Feature-based methods, extract and match common features, more suitable. (Spatial relations, invariant descriptors, relaxation, pyramidal and wavelet decompositions)