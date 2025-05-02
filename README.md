# Pan-Sharpening Project

## Introduction

This project explores **pan-sharpening** techniques using Landsat 8 satellite imagery. We implement and evaluate selected methods to enhance the spatial resolution of multispectral images using a higher-resolution panchromatic band.

## Research Papers

To gain an initial understanding of the topic, we reviewed and summarized key points from the paper titled:
[1] **"A survey of classical methods and new trends in pansharpening of multispectral images"**.  

Implementation of Bayesian methods required reading an additional paper because the summary provided in [1] was insufficient. We referenced the paper titled:
[2] **"Variational posterior distribution approximation in Bayesian super resolution reconstruction of multispectral images"**

These papers, along with our notes, can be found in the folder **`readings/survey/`**. Some notes are direct excerpts from the papers themselves.

## Dataset

### Source
**Landsat 8** images from **[USGS Earth Explorer](https://earthexplorer.usgs.gov/)** (Landsat Collection 2 Level-1).

We specifically selected **Landsat Collection 2 Level-1 (L1TP) GeoTIFF products**, as they provide the best radiometric and geometric corrections for analysis.

### **Selected Bands**
We use the following bands for our **multispectral (MS) and panchromatic (PAN) images**:  

| **Band** | **Description** | **Resolution** |
|----------|---------------|--------------|
| **Band 2** | Blue | 30m |
| **Band 3** | Green | 30m |
| **Band 4** | Red | 30m |
| **Band 5** | Near-Infrared (NIR) | 30m  |
| **Band 8** | **Panchromatic** | **15m** |

The **panchromatic band (Band 8, 15m resolution)** is used to enhance the **multispectral bands (Bands 2, 3, 4, 30m resolution)** through **pansharpening**.

### **Selection Criteria**  
To ensure high-quality data, we carefully followed these selection criteria:
1. **Cloud Cover ≤ 10%** → To minimize distortions from clouds.
2. **High Spatial Detail** → Selected areas with a mix of **urban features and vegetation** for clear contrast.
3. **Sun Elevation ≥ 30°** → To ensure good illumination and avoid excessive shadows.
4. **Level-1 (L1TP) GeoTIFF** → Chose **L1TP** products for the best accuracy in geometry and radiometric calibration.

### **Selected Study Area**
The area chosen for this project is **Tokyo**, as it provides:
- **High urban detail** (roads, buildings, bridges).
- **Green areas** like vegetation and mountains.

### **Implemented Methods**

Currently, the following pan-sharpening methods are implemented:

-   **Gram-Schmidt:** See the `Gram-Schmidt/` directory for implementation details and results.
-   **High Pass Filtering :** See the `High Pass Filtering/` directory for implementation details and results.
---



