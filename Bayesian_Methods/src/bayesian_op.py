import numpy as np
import cv2
import matplotlib.pyplot as plt
import tifffile as tiff
import gc
from skimage.metrics import peak_signal_noise_ratio, structural_similarity, mean_squared_error
from scipy.stats import pearsonr
import os
from scipy.ndimage import gaussian_filter, laplace
from scipy.optimize import minimize

def crop_and_straighten(img, threshold=10, visualize=False):
    if len(img.shape) == 2 or img.shape[2] == 1:
        gray = img if len(img.shape) == 2 else img[:, :, 0]
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Normalize to 8-bit for contour processing
    gray_8bit = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    gray_8bit = gray_8bit.astype(np.uint8)

    # Create binary mask for valid region
    _, mask = cv2.threshold(gray_8bit, threshold, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("No valid region found!")

    # Largest contour
    cnt = max(contours, key=cv2.contourArea)
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.intp(box)
    # print(box)

    width, height = int(rect[1][0]), int(rect[1][1])
    dst_pts = np.array([[0, height-1],
                        [0, 0],
                        [width-1, 0],
                        [width-1, height-1]], dtype="float32")
    src_pts = box.astype("float32")

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(img, M, (width, height))

    if visualize:
        plt.imshow(warped, cmap='gray' if len(warped.shape) == 2 else None)
        plt.title("Straightened & Cropped Image")
        plt.axis("off")
        plt.show()

    return warped


def compute_quality_metrics(ref_img, test_img, PSNR=True):
    assert ref_img.shape == test_img.shape, "Images must have the same shape"
    assert ref_img.ndim == 3, "Images must be H x W x C"

    psnr_list = []
    cc_list = []
    ssim_list = []
    rmse_list = []

    for i in range(ref_img.shape[2]):
        ref_band = ref_img[:, :, i].astype(np.float64)
        test_band = test_img[:, :, i].astype(np.float64)

        # Use fixed data range for uint16 images
        data_range = 65535.0

        if PSNR:
          psnr_val = peak_signal_noise_ratio(ref_band, test_band, data_range=data_range)
          psnr_list.append(psnr_val)


        # cc_val, _ = pearsonr(ref_band.flatten(), test_band.flatten())
        # ssim_val = structural_similarity(ref_band, test_band, data_range=data_range)
        else:
          rmse_val = np.sqrt(mean_squared_error(ref_band, test_band))
          mean_ref = np.mean(ref_band)
          rel_rmse = rmse_val / mean_ref if mean_ref != 0 else 0
          rmse_list.append(rel_rmse)


        # cc_list.append(cc_val)
        # ssim_list.append(ssim_val)

        if PSNR:
            return {
              "PSNR": np.mean(psnr_list)
            }
        else:
            return {
                "RMSE": np.mean(rmse_list)
            }

def calculate_ergas(original_ms, pansharpened_ms, ratio):
    if original_ms.shape != pansharpened_ms.shape:
        raise ValueError("Images must be the same shape. Resample the original MS image first.")

    N = original_ms.shape[2]
    ergas_sum = 0

    for i in range(N):
        ref_band = original_ms[:, :, i].astype(np.float64)
        pan_band = pansharpened_ms[:, :, i].astype(np.float64)

        rmse = np.sqrt(mean_squared_error(ref_band, pan_band))
        mean_val = np.mean(ref_band)

        ergas_sum += (rmse / mean_val) ** 2

    ergas = 100 * (ratio) * np.sqrt(ergas_sum / N)
    return ergas


def compute_sam(img1, img2, eps=1e-8):
    # Flatten spatial dimensions
    X = img1.reshape(-1, img1.shape[-1]).astype(np.float32)
    Y = img2.reshape(-1, img2.shape[-1]).astype(np.float32)

    # Compute dot product and norms
    dot_product = np.sum(X * Y, axis=1)
    norm_x = np.linalg.norm(X, axis=1)
    norm_y = np.linalg.norm(Y, axis=1)

    # Avoid division by zero
    denom = np.clip(norm_x * norm_y, eps, None)

    # Compute angle (in radians)
    sam = np.arccos(np.clip(dot_product / denom, -1.0, 1.0))
    sam_map = sam.reshape(img1.shape[0], img1.shape[1])

    mean_sam = np.mean(sam)

    sam_map_safe = np.clip(sam_map, 1e-6, None)

    # Normalize to [0, 1]
    sam_map_norm = sam_map_safe / np.max(sam_map_safe)

    # Apply log transform
    sam_log = np.log1p(sam_map_norm)  # log(1 + x)

    # Normalize again and scale to 0-255
    sam_log_norm = (sam_log / np.max(sam_log)) * 255
    return sam_log_norm.astype(np.uint8) , mean_sam

def visualize_sam_map(sam_map, cmap='inferno'):
    plt.figure(figsize=(8, 6))
    plt.imshow(np.degrees(sam_map), cmap=cmap)
    plt.colorbar(label='SAM (degrees)')
    plt.title("Spectral Angle Mapper (SAM) Map")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def blur(image, sigma=1.2):
    """Apply Gaussian blur to simulate sensor MTF."""
    return gaussian_filter(image, sigma=sigma)


def synth_pan(z, lambdas):
    """Simulate PAN image from multispectral image using spectral weights."""
    return np.tensordot(lambdas, z, axes=(0, 0))  # shape (H, W)


def loss_map_sar(Z, Y, x, lambdas, alpha, beta):
    """Compute the MAP loss with SAR prior."""
    B, H, W  = Z.shape
    loss_val = 0.0

    for b in range(B):
        zb = Z[b]
        yb = Y[b]
        smooth = laplace(zb)
        loss_val += beta * np.sum((blur(zb) - yb) ** 2)
        loss_val += alpha * np.sum(smooth ** 2)

    x_hat = synth_pan(Z, lambdas)
    loss_val += beta * np.sum((x_hat - x) ** 2)

    return loss_val

def optimize_map_sar_gd(Y, x, lambdas, alpha=0.001, beta=1.0, sigma_blur=1.2, lr=0.05, max_iter=50):
    """
    Gradient descent of MAP-SAR
    """
    Y = Y.astype(np.float32)
    x = x.astype(np.float32)
    Z = Y.copy()
    for it in range(max_iter):
        grad = np.zeros_like(Z)

        for b in range(Z.shape[0]):
            zb = Z[b]
            yb = Y[b]

            # Gradient of the MS term
            diff_ms = blur(zb) - yb
            grad_ms = gaussian_filter(diff_ms, sigma=sigma_blur)

            # Gradient of SAR prior (Laplacian)
            grad_sar = laplace(laplace(zb))  # second derivative

            # Gradient of the PAN term
            pan_residual = synth_pan(Z) - x
            grad_pan = lambdas[b] * pan_residual

            grad[b] = beta * grad_ms + alpha * grad_sar + beta * grad_pan

        # Gradient descent update
        Z -= lr * grad

        if it % 10 == 0:
            print(f"Iteration {it}: gradient norm = {np.linalg.norm(grad):.2f}") # doesn't have to go to zero, just 1e-3 times the original ideally

    return Z

def crop_center(img, cropx, cropy):
    """
    Crop image from the center, half the original size.
    """
    y, x = img.shape[-2:]
    startx = x // 2 - cropx // 2
    starty = y // 2 - cropy // 2
    if img.ndim == 3:
        return img[:, starty:starty + cropy, startx:startx + cropx]
    else:
        return img[starty:starty + cropy, startx:startx + cropx]