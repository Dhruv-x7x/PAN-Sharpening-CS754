Sources : 
[1] https://www.tandfonline.com/doi/epdf/10.5721/EuJRS20144702?needAccess=true
[2] https://www.mdpi.com/2072-4292/10/4/622?utm_source=chatgpt.com

Note : both these sources are using the QuickBird dataset. 

--- Spatial Metrics ---
Correlation Coefficient (CC): 0.9923 (Better than both)
Peak Signal-to-Noise Ratio (PSNR): 36.9582 dB (Better than [1], no data for [2])
Structural Similarity Index (SSIM): 0.9442 (Better than [2], no data for [1])
Mean Absolute Error (MAE): 0.0097 (No data for both)
Root Mean Square Error (RMSE): 0.0142 (Better than both)

--- Spectral Metrics ---
Spectral Angle Mapper (SAM) in radians: 0.5226 radians 
Spectral Angle Mapper (SAM) in degrees: 29.9439 degrees (Worse than [2] indicating spectral distorsion)
ERGAS: 23.2893 (Worse than [2])


Conslusion : While our implementation is performing amazingly regarding the spatial resolution, we have a lot of spectral distortion, which is a common problem of this method. 
