# Remote Sensing and Pan Sharpening Notes

## I. Introduction

Pan sharpening aims at increasing spatial resolution of multispectral images while preserving spectral information.

The spatial resolution of a remote sensing system is the area of the ground captured by one pixel. In remote-sensing it is usually measured in meteres or feet.

The instantaneous field of view (IFOV) is the ground area sensed at a given instant of time.

Reflectance is the ratio of the amount of light reflected by a surface to the amount of light incident to it.

Spectral resolution is the electromagnetic bandwidth of the signals captured. A higher spectral resolution corresponds to a narrower bandwidth, because it can capture smaller variations in the spectral information this way.

Radiometric accuracy is a measure of how accurate the system can measure the spectral reflectance percentage.

- **Multispectral data (MS)**: Images with 3 to 15 spectral bands
- **Hyperspectral data (HS)**: Images with hundreds or thousands of spectral bands

Along with the HS or MS image, the satellites provide a panchromatic image (PAN) which is a grayscale image containing reflectance data representative of a wide range of wavelengths from visible to thermal infrared. Panchromatic images have a high spatial resolution as it integrates light from multiple wavelengths, allowing more energy to be captured per pixel.

The problem in remote sensing is that there is a tradeoff between the IFOV and the signal-to-noise (SNR) ratio. Multi-spectral images have reduced spectral bandwidth compared to panchromatic images because MS images are meant to have high spectral resolution. This reduction in bandwidth means that the IFOV of MS sensors will have to be small and this limits the spatial resolution of MS images because they do not collect enough photons to counter the noise and ultimately suffer from a bad SNR. The goal of pansharpening is to combine the best of both worlds, that is, use the PAN image to increase the spatial resolution of MS images which have a high spectral resolution.

## II. Pre-processing

Several factors can lead to:
- **Geometric errors** (distorts shape, position, alignement of objects)
- **Radiometric errors** (affects the brightness of pixels)

Causes for geometric errors includes Earth's curvature, movement of the platform and sensor imperfections. Causes for radiometric errors include solar radiation, atmospheric effects or limitations of the instrumentation.

It is necessary for many applications to make corrections in geometry and brightness before use. Through correction techniques, one can map the pixels of an image to geographic coordinates which is known as georeferencing or geocoding.

Geo-satellite data have several levels of standard preprocessing (Levels 0, 1A, 1B, 2, 3, 4) defined by EOSDIS. Higher levels of preprocessing correspond to more metadata and corrections. Majority of the data is preprocessed up to Level 1.

For PANsharpening, at least geometric and radiometric corrections need to be performed on the satellite data, which is provided for by Level 1 standard preprocessed data. However, there are still many errors unaccounted for by telemetric corrections, such as:

- object disappearance or appearance
- contrast inversion due to different spectral bands or times of image acquizition.
- images of fast moving objects

The following preprocessing steps are described as ideal for remote-sensing in the paper:
- Image Registration: Feature-based matching of pixels that correspond to the same point on the ground across multiple images.
- Image Upsampling and Interpolation: If an image is not up to the required resolution, we upsample it using some method of interpolation. For remote-sensing applications, methods such as bilinear interpolation and unsharp masking are preferred. 
- Histogram Matching: Helps to reduce spectral distortion. 

### II.1 Image Registration

Many applications of remote sensing image data require two or more scenes
of the same geographical region, acquired at different dates or from different
sensors, in order to be processed together. In this case, the role of image
registration is to make the pixels in the two images precisely coincide to the
same points on the ground.

Two images can be registered to each other by registering each to a map coordinate base separately, or one image can be chosen as a master to which the other is to be registered.

Due to the use of different sensors, this can be quite complicated, here are some problems image registration tries to solve :

- Feature absence or presence 
- Contrast reversal (bright region might appear darker in another image)
- Multiple intensity values in one image that need to be mapped to a single intensity value in the other
- Considerably dissimilar images of the same scene produced by the image sensor when configured with different imaging parameters

Two types of image registration methods : 
- Area-based methods (Fourier methods, cross correlation, mutual information). Not well suited for the multisensor image registration problem
- Feature-based methods, extract and match common features, more suitable. (Spatial relations, invariant descriptors, relaxation, pyramidal and wavelet decompositions)

### II.2 Image Up-Sampling and Interpolation

When the registered remote sensing image is too coarse and does not meet
the required resolution, up-sampling may be needed to obtain a higher res-
olution version of the image. 

The up-sampling process may involve interpolation, usually performed via convolution of the image with an interpolation kernel 

Methods that can be used for remote sensing images: 

- Bilinear interpolation (creates a new pixel in the target image from a weighted average of its 4 nearest neighboring pixels in the source image)
- Interpolation with smoothing filter (weighted average of the pixels contained in the area spanned by the filter mask)
- Interpolation with sharpening filter (enhances details that have been blurred). This method can create aliasing. Solution : Interpolation with unsharp masking

### II.3 Histogram Matching

Some pansharpening algorithms assume that the spectral characteristics of
the PAN image match those of each band of the MS image or match those
of a transformed image based on the MS image, which is not always the case. 

Matching the histograms of the PAN image and MS bands
will minimize brightness mismatching during the fusion process, which may
help to reduce the spectral distortion in the pansharpened image

$$
Stretched_{PAN}(i, j) = (PAN(i, j) - \mu_{PAN}) \frac{\sigma_b}{\sigma_{PAN}} + \mu_b
$$

Where $\mu_b$ is the mean of MS image band $b$.

## III. Methods of PAN-Sharpening

### III.1 Gram Schimdt (GS)

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

### III.2 Bayesian Method

This method belongs to the statistical family of methods. It converts the whole problem into one of statistical inference. The high-resolution multi-spectral (HRMS) image is a posterior and our job is to model how HRMS degrades to produce low-resolution MS (LRMS) image and PAN image. 

Let's say that the HRMS image is $z$ and our goal is to recover the best possible $z$. We have three things to work on:

- $x$: High-resolution PAN image
- $y$: Low-resolution MS image
- Spectral and Spatial characteristics of $z$

First we model the likelihood of seeing $y$ and $x$ given $z$ which models the degradation process. $z$ gets blurred and downsampled to give $y$ while it gets reprojected, spectrally, to give $x$. 

$$
p(y, x | z)
$$

Next, we add prior knowledge about $z$, that is, $p(z)$. For example, we can assume that HRMS is smooth (Total Variation prior) or have sharp edges or be sparse in some basis (wavelet, MRF, etc.)

Using Bayes' law,

$$
p(z | y, x) = \frac{p(y, x | z)p(z)}{p(y, x)}
$$

We find the probability of observing HRMS given the LRMS and PAN image data. Bayesian methods infer z by finding the most probable $z$ or averaging over all $z$. There are many ways to decide on the prior such as Total Variation, Markov Random Fields, SAR, Stochastic Mixing Models, etc.

#### Priors

- **Non-Informative Priors**: $p(z) \propto 1$. This prior was used by Fasbender and Hardie. It simply means that there is no preference for any one solution, we rely entirely on the observed data. 
- **Interpolated Prior with Covariance**: Interpolate to give a initial $z$ which serves as our guess for HRMS. This prior is a gaussian centered at the interpolated image with a covariance matrix describing uncertainty.
- **Simultaneous Auto-Regressive Model Prior**: 

$$
p(z) = \prod_{b=1}^{B} p(z_b) \propto \prod_{b=1}^{B} \exp\left(-\frac{1}{2} \alpha_b |cz_b|^2\right)
$$

where:
  - $z_b$: band $b$ of HRMS image
  - $C$: Laplacian operator which detects edges (2nd order spatial variations)
  - $\alpha_b$: Inverse of variance, controls smoothing. 

Big changes such as sharp edges are penalized.

- **Total Variation**: Favors piece-wise smoothness and preserves edges. 
- **MRFs**: Can encode complex local dependencies.
- **Stochastic Mixing Models**: Useful when MS and PAN are spectrally mismatched.

#### Degradation Models

For LRMS,

$$
y = g_s(z) + n_s
$$

where $g_s(z)$ downsamples and blurs $z$ to simulate $y$. $n_s$ is the noise in the MS image. 

For PAN, 

$$
x = g_p(z) + n_p
$$

where $g_p(z)$ projects $z$ into a single PAN band and $n_p$ is the noise in PAN image. 

#### Objective Function

Model degradation from $z$ (HRMS) to:

- $y$ (LRMS):

  $$y = Hz + n_s, \quad n_s \sim \mathcal{N}(0, \beta^{-1}I) \Rightarrow p(y|z) \propto \exp\left(-\frac{\beta}{2}\|y - Hz\|^2\right)$$

- $x$ (PAN):

  $$x = \sum_{b=1}^{B} \lambda_b z_b + n_p, \quad n_p \sim \mathcal{N}(0, \sigma^2) \Rightarrow p(x|z) \propto \exp\left(-\frac{1}{2\sigma^2}\|x - Gz\|^2\right)$$

  - Where $Gz = \sum_b \lambda_b z_b$

Use a Simultaneous Autoregressive (SAR) prior:

$$p(z) \propto \exp\left(-\frac{1}{2}\sum_{b=1}^{B} \alpha_b \|C z_b\|^2\right)$$

So we can write the overall objective function as minimizing,

$$\mathcal{L}(z) = \frac{\beta}{2}\|y - Hz\|^2 + \frac{1}{2\sigma^2}\|x - Gz\|^2 + \sum_{b}\frac{\alpha_b}{2}\|Cz_b\|^2$$

Similar objective function was used by Mateos et. al. in [2].

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
