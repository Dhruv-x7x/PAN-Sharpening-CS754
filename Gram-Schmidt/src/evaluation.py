import numpy as np
from skimage.metrics import structural_similarity as ssim
from scipy.ndimage import correlate
import os

def calculate_cc(img1, img2):
    """Calculate correlation coefficient between two images."""
    return np.corrcoef(img1.flatten(), img2.flatten())[0, 1]

def calculate_sam(img1, img2):
    """Calculate Spectral Angle Mapper (SAM) between two multispectral images.
    Lower values indicate better spectral quality preservation."""
    # Reshape to handle band dimension properly
    nb_bands = img1.shape[0]
    img1_reshaped = img1.reshape(nb_bands, -1)
    img2_reshaped = img2.reshape(nb_bands, -1)
    
    # Calculate band-wise dot products
    dot_product = np.sum(img1_reshaped * img2_reshaped, axis=0)
    norm_1 = np.sqrt(np.sum(img1_reshaped**2, axis=0))
    norm_2 = np.sqrt(np.sum(img2_reshaped**2, axis=0))
    
    # Avoid division by zero
    epsilon = 1e-10
    cos_angle = np.clip(dot_product / (norm_1 * norm_2 + epsilon), -1.0, 1.0)
    angle = np.arccos(cos_angle)
    
    # Return average SAM in radians and degrees
    sam_radians = np.mean(angle)
    sam_degrees = np.degrees(sam_radians)
    
    return sam_radians, sam_degrees

def calculate_ergas(img1, img2, ratio):
    """Calculate ERGAS (Erreur Relative Globale Adimensionnelle de Synthèse).
    Lower values indicate better quality."""
    nb_bands = img1.shape[0]
    mse = np.zeros(nb_bands)
    means = np.zeros(nb_bands)
    
    for i in range(nb_bands):
        mse[i] = np.mean((img1[i] - img2[i])**2)
        means[i] = np.mean(img2[i])
    
    # Avoid division by zero
    epsilon = 1e-10
    rmse_relative = np.sqrt(mse) / (means + epsilon)
    ergas = 100 * ratio * np.sqrt(np.mean(rmse_relative**2))
    
    return ergas

def calculate_psnr(img1, img2, max_val=None):
    """Calculate Peak Signal-to-Noise Ratio (PSNR).
    Higher values indicate better quality."""
    if max_val is None:
        # Use the maximum value from both images
        max_val = max(np.max(img1), np.max(img2))
    
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return float('inf')
    
    return 20 * np.log10(max_val) - 10 * np.log10(mse)  

def calculate_ssim(img1, img2):
    """Calculate Structural Similarity Index (SSIM).
    Higher values indicate better structural similarity."""
    nb_bands = img1.shape[0]
    ssim_values = np.zeros(nb_bands)
    
    for i in range(nb_bands):
        # Ensure the images are in the proper range for SSIM calculation
        band1 = (img1[i] - np.min(img1[i])) / (np.max(img1[i]) - np.min(img1[i]) + 1e-10)
        band2 = (img2[i] - np.min(img2[i])) / (np.max(img2[i]) - np.min(img2[i]) + 1e-10)
        ssim_values[i] = ssim(band1, band2, data_range=1.0)
    
    return np.mean(ssim_values)

def calculate_mae(img1, img2):
    """Calculate Mean Absolute Error (MAE).
    Lower values indicate better quality."""
    return np.mean(np.abs(img1 - img2))

def calculate_rmse(img1, img2):
    """Calculate Root Mean Square Error (RMSE).
    Lower values indicate better quality."""
    return np.sqrt(np.mean((img1 - img2) ** 2))

def evaluate_pansharpening(fused_ms, reference_ms, ratio=4):
    """Evaluate pansharpening results using multiple metrics.
    
    Args:
        fused_ms: The pansharpened multispectral image [nb_bands, h, w]
        reference_ms: The reference multispectral image [nb_bands, h, w]
        ratio: The resolution ratio between PAN and MS
        
    Returns:
        Dictionary containing evaluation metrics
    """
    print("\nCalculating evaluation metrics...")
    
    # Normalize images band-by-band before evaluation
    fused_norm = np.zeros_like(fused_ms, dtype=np.float32)
    ref_norm = np.zeros_like(reference_ms, dtype=np.float32)
    
    print("Normalizing images for fair comparison (band-by-band)...")
    for i in range(fused_ms.shape[0]):
        # Min-max normalization to [0, 1] range for each band individually
        fused_min, fused_max = np.min(fused_ms[i]), np.max(fused_ms[i])
        ref_min, ref_max = np.min(reference_ms[i]), np.max(reference_ms[i])
        
        # Avoid division by zero
        fused_range = fused_max - fused_min
        ref_range = ref_max - ref_min
        
        if fused_range == 0:
            fused_range = 1e-10
        if ref_range == 0:
            ref_range = 1e-10
            
        fused_norm[i] = (fused_ms[i] - fused_min) / fused_range
        ref_norm[i] = (reference_ms[i] - ref_min) / ref_range
        
        print(f"  - Band {i+1} - Fused: min={fused_min:.4f}, max={fused_max:.4f}, Reference: min={ref_min:.4f}, max={ref_max:.4f}")
    
    metrics = {}
    
    # Calculate correlation coefficient
    print("Calculating Correlation Coefficient (CC)...")
    band_cc = [calculate_cc(fused_norm[i], ref_norm[i]) for i in range(fused_norm.shape[0])]
    metrics['CC'] = np.mean(band_cc)
    print(f"  - Band CCs: {[f'{cc:.4f}' for cc in band_cc]}")
    print(f"  - Average CC: {metrics['CC']:.4f}")
    
    # Calculate PSNR
    print("Calculating Peak Signal-to-Noise Ratio (PSNR)...")
    band_psnr = [calculate_psnr(fused_norm[i:i+1], ref_norm[i:i+1], max_val=1.0) for i in range(fused_norm.shape[0])]
    metrics['PSNR'] = np.mean(band_psnr)
    print(f"  - Band PSNRs: {[f'{psnr:.4f}' for psnr in band_psnr]}")
    print(f"  - Average PSNR: {metrics['PSNR']:.4f} dB")
    
    # Calculate SSIM
    print("Calculating Structural Similarity Index (SSIM)...")
    metrics['SSIM'] = calculate_ssim(fused_norm, ref_norm)
    print(f"  - SSIM: {metrics['SSIM']:.4f}")
    
    # Calculate MAE
    print("Calculating Mean Absolute Error (MAE)...")
    band_mae = [calculate_mae(fused_norm[i:i+1], ref_norm[i:i+1]) for i in range(fused_norm.shape[0])]
    metrics['MAE'] = np.mean(band_mae)
    print(f"  - Band MAEs: {[f'{mae:.4f}' for mae in band_mae]}")
    print(f"  - Average MAE: {metrics['MAE']:.4f}")
    
    # Calculate RMSE
    print("Calculating Root Mean Square Error (RMSE)...")
    band_rmse = [calculate_rmse(fused_norm[i:i+1], ref_norm[i:i+1]) for i in range(fused_norm.shape[0])]
    metrics['RMSE'] = np.mean(band_rmse)
    print(f"  - Band RMSEs: {[f'{rmse:.4f}' for rmse in band_rmse]}")
    print(f"  - Average RMSE: {metrics['RMSE']:.4f}")
    
    # Calculate spectral metrics
    print("Calculating Spectral Angle Mapper (SAM)...")
    sam_radians, sam_degrees = calculate_sam(fused_ms, reference_ms)  # Use original values for spectral metrics
    metrics['SAM (radians)'] = sam_radians
    metrics['SAM (degrees)'] = sam_degrees
    print(f"  - SAM: {sam_degrees:.4f} degrees")
    
    # Calculate ERGAS
    print("Calculating ERGAS...")
    metrics['ERGAS'] = calculate_ergas(fused_ms, reference_ms, ratio)  # Use original values for ERGAS
    print(f"  - ERGAS: {metrics['ERGAS']:.4f}")
    
    print("All metrics calculated successfully!")
    return metrics

def print_metrics(metrics):
    """Print the evaluation metrics in a formatted way."""
    print("\nPansharpening Evaluation Metrics:")
    print("---------------------------------")
    print("--- Spatial Metrics ---")
    print(f"Correlation Coefficient (CC): {metrics['CC']:.4f} (higher is better)")
    print(f"Peak Signal-to-Noise Ratio (PSNR): {metrics['PSNR']:.4f} dB (higher is better)")
    print(f"Structural Similarity Index (SSIM): {metrics['SSIM']:.4f} (higher is better)")
    print(f"Mean Absolute Error (MAE): {metrics['MAE']:.4f} (lower is better)")
    print(f"Root Mean Square Error (RMSE): {metrics['RMSE']:.4f} (lower is better)")
    print("--- Spectral Metrics ---")
    print(f"Spectral Angle Mapper (SAM) in radians: {metrics['SAM (radians)']:.4f} radians (lower is better)")
    print(f"Spectral Angle Mapper (SAM) in degrees: {metrics['SAM (degrees)']:.4f} degrees (lower is better)")
    print(f"ERGAS: {metrics['ERGAS']:.4f} (lower is better)")

def save_metrics_to_file(metrics, filename='pansharpening_results.txt'):
    """Save the evaluation metrics to a text file."""
    print("\nSaving metrics to file...")
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"Created results directory: {results_dir}")

    results_file_path = os.path.join(results_dir, filename)
    with open(results_file_path, 'w') as f:
        f.write("=== Pansharpening Evaluation Results ===\n\n")
        f.write("--- Spatial Metrics ---\n")
        f.write(f"Correlation Coefficient (CC): {metrics['CC']:.4f} (higher is better)\n")
        f.write(f"Peak Signal-to-Noise Ratio (PSNR): {metrics['PSNR']:.4f} dB (higher is better)\n")
        f.write(f"Structural Similarity Index (SSIM): {metrics['SSIM']:.4f} (higher is better)\n")
        f.write(f"Mean Absolute Error (MAE): {metrics['MAE']:.4f} (lower is better)\n")
        f.write(f"Root Mean Square Error (RMSE): {metrics['RMSE']:.4f} (lower is better)\n")
        f.write("\n--- Spectral Metrics ---\n")
        f.write(f"Spectral Angle Mapper (SAM) in radians: {metrics['SAM (radians)']:.4f} radians (lower is better)\n")
        f.write(f"Spectral Angle Mapper (SAM) in degrees: {metrics['SAM (degrees)']:.4f} degrees (lower is better)\n")
        f.write(f"ERGAS: {metrics['ERGAS']:.4f} (lower is better)\n")
    
    print(f"Metrics saved to: {results_file_path}")

def evaluate_and_save_pansharpening(fused_ms, reference_ms, ratio=4, filename='pansharpening_results.txt'):
    """Evaluate pansharpening results and save the metrics to a file."""
    print("\n=== Starting Pansharpening Evaluation ===")
    print(f"Fused MS shape: {fused_ms.shape}")
    print(f"Reference MS shape: {reference_ms.shape}")
    print(f"Resolution ratio: {ratio}")
    
    # Calculate all metrics
    metrics = evaluate_pansharpening(fused_ms, reference_ms, ratio)
    
    # Print and save metrics
    print_metrics(metrics)
    save_metrics_to_file(metrics, filename)
    print("\n=== Pansharpening Evaluation Completed ===")
    
    return metrics