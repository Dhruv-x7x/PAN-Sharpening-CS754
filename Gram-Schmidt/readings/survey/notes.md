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

### II.2 Image up-sampling and interpolation

When the registered remote sensing image is too coarse and does not meet
the required resolution, up-sampling may be needed to obtain a higher res-
olution version of the image. 

The up-sampling process may involve interpolation, usually performed via convolution of the image with an interpolation kernel 

Methods that can be used for remote sensing images: 

- Bilinear interpolation (creates a new pixel in the target image from a weighted average of its 4 nearest neighboring pixels in the source image)
- Interpolation with smoothing filter (weighted average of the pixels contained in the area spanned by the filter mask)
- Interpolation with sharpening filter (enhances details that have been blurred). This method can create aliasing. Solution : Interpolation with unsharp masking

### II.3 Histogram matching

Some pansharpening algorithms assume that the spectral characteristics of
the PAN image match those of each band of the MS image or match those
of a transformed image based on the MS image, which is not always the case. 

Matching the histograms of the PAN image and MS bands
will minimize brightness mismatching during the fusion process, which may
help to reduce the spectral distortion in the pansharpened image



## III. Gram Schimdt (GS)

Part of the Component Substituion family because it is using a linear transformation and substitution for some components in the transformed domain. 

Algorithm : Component substitution pansharpening
1. Upsample the MS image to the size of the PAN image.
2. Forward transform the MS image to the desired components.
3. Match the histogram of the PAN image with the MS component to be substi-
tuted.
4. Replace the MS component with the histogram-matched PAN image.
5. Backward transform the components to obtain the pansharpened image

CS methods are substituting a component of the transformed MS image with a component from the PAN image. These methods are meaningful only if these components contain the same spectral information. 

Improper construction of the MS component introduce high spectral distortion. 

Easy to implement and results in good geometrical quality. Does not take into account dissimilarities between PAN and MS, highly depends on correlation between bands. 

GS is used to orthogonalize matrix data or bands of a digital image removing redundant (i.e., correlated) information that is contained in multiple bands. It has been modified for PANSharpening : the mean of each band is subtracted from each pixel in the band before the orthogonalization is performed to produce a more accurate outcome

In GS-based pansharpening, a lower resolution PAN band needs to be
simulated and used as the first band of the input to the GS transformation,
together to the MS image.

To simulate this band, there are two methods :

1) The LRMS bands are combined into a single lower resolution PAN (LR PAN) as the weighted mean of MS image. These weights depend on the spectral response of the MS bands and high resolution PAN (HR PAN) image and on the optical transmittance of the PAN band.
2) The second method simulates the LR PAN image by blurring and sub-sampling
the observed PAN image

Comparison : Method 1 exhibits outstanding spatial quality, but spectral distortions may occur. This distortion is due to the fact
that the average of the MS spectral bands is not likely to have the same
radiometry as the PAN image. The second method is unaffected by spectral
distortion but generally suffers from a lower sharpness and spatial enhance-
ment. This is due to the injection mechanism of high-pass details taken from
PAN, which is embedded into the inverse GS transformation, carried out
by using the full resolution PAN, while the forward transformation uses the
low resolution approximation of PAN obtained by resampling the decimated
PAN image provided by the user

## IV. Quality Assessment


1. Any pansharpened image once downsampled to its original spatial reso-
lution should be as similar as possible to the original image.
2. Any pansharpened image should be as similar as possible to the image
that a corresponding sensor would observe with the same high spatial
resolution.
3. The MS set of pansharpened images should be as similar as possible to
the MS set of images that a corresponding sensor would observe with
the same high spatial resolution.

Consistency property : 1
Synthesis property : 2 and 3

The reference image is the MS image at the resolution of the PAN image.

The consistency property is verified by downnsampling the fused image from the higher spatial resolution h to their original spatial resolution l using suitable filters.

To verify the synthesis properties, the original PAN at resolution h and MS at resolution l are downsampled to their lower resolutions l and v respectively. Then, PAN at resolution l and MS at resolution v are fused to obtain fused MS at resolution l that can be then compared with the original MS image. The quality assessed at resolution l is assumed to be close to the quality at resolution h

### IV.1 Visual Analysis

Assess the global image quality (geometric shape, size of objects, spatial details, local contrast). 

1) spectral preservation of features in each MS band where the appearance of the objects in the pansharpened images are analyzed in each band based on the
appearance of the same objects in the original MS images
2) multispectral synthesis in pansharpened images, where different color composites of the fused images are analyzed and compared with that of original images to verify that MS characteristics of objects at higher spatial resolution is similar to that in the original images
3) synthesis of images close to actual images at high resolution as defined by the synthesis property of pansharpened images, that cannot be directly verified but can be analyzed from our knowledge of the spectra of objects present in the lower spatial resolutions.

### IV.2 Quantitative Analysis

#### Spectral Quality Assessment 

To measure the spectral distortion due to
the pansharpening process, each merged image is compared to the reference
MS image : SAM, RM, CC, RMSE, SSIM

1) Spectral Angle Mapper (SAM): SAM denotes the absolute value of the
angle between two vectors, whose elements are the values of the pixels
for the different bands of the HRMS image and the MS image at each image location.

2) Relative-shift mean (RM): the percentage of variation between the mean of the reference image and the pansharpened image

3) Correlation coefficient (CC): The CC between each band of the ref-
erence and the pansharpened image indicates the spectral integrity of
pansharpened image

4) Root mean square error (RMSE): The RMSE between each band of the
reference and the pansharpened image measures the changes in radiance
of the pixel values

5) Structure Similarity Index (SSIM): a perceptual measure that combines several factors related to the way humans perceive the quality of the images.


While these parameters only evaluate the difference in spectral informa-
tion between each band of the merged and the reference image, in order
to estimate the global spectral quality of the merged images the following
parameters are used : ERGAS, MSSIM

1)  Erreur relative globale adimensionnelle de synth ́ese (ERGAS) index: a global quality index sensitive to mean shifting and dynamic
range change

2) Mean SSIM (MSSIM) index and the average quality index (Qavg):  are used to evaluate the overall image SSIM by averaging


#### Spatial Quality Assessment 

To assess the spatial quality of a pansharp-
ened image, its spatial detail information must be compared to the that
present in the reference HR MS image.

Looks kind of fuzzy. Several authors proposed several methods, it doesn't seem to be some agreement on standard methds (from what I have udnerstood)


### Quality Assessment without a reference

Will come back to it in case I need it 


