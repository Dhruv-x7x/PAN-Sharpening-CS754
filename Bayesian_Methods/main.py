from src.bayesian_op import crop_and_straighten, crop_center, calculate_ergas, compute_sam, compute_quality_metrics, blur, synth_pan, loss_map_sar, optimize_map_sar_gd
import numpy as np
import cv2
import tifffile as tiff

FILE_PATH = "" # PATH TO IMAGES (TIFF FILES)
LAMBDA = [0.0842, 0.5375, 0.3784, 0.0000] # IF UNKNOWN, USE UNIFORM OR PERFORM LINEAR REGRESSION OF PAN ON MS. CURRENT VALUES ARE FOR LANDSAT8

def read_data(file_path):
    # Read the TIFF image
    print("Reading the images...\n\n")
    image_b = tiff.imread(file_path + "\LC08_L1TP_B2.tiff")
    image_g = tiff.imread(file_path + "\LC08_L1TP_B3.tiff")
    image_r = tiff.imread(file_path + "\LC08_L1TP_B4.tiff")
    image_ir = tiff.imread(file_path + "\LC08_L1TP_B5.tiff")
    image_pan = tiff.imread(file_path + "\LC08_L1TP_B8.tiff")

    # Check if image is loaded successfully
    if image_b is None:
        print("Failed to load image.")
    else:
        print("Image shape:", image_b.shape)
        # Display the image
    return image_b, image_g, image_r, image_ir, image_pan

def main():

    # READ DATA
    image_b, image_g, image_r, image_ir, image_pan = read_data(FILE_PATH)
    print("blue band shape:", image_b.shape)
    print("red band shape:", image_r.shape)
    print("green band shape:", image_g.shape)
    print("NIR band shape:", image_ir.shape)
    print("PAN band shape:", image_pan.shape)

    # REGISTER IMAGES
    print("Registering MS image to PAN...\n\n")
    image_b = crop_and_straighten(image_b,visualize=False)
    image_g = crop_and_straighten(image_g,visualize=False)
    image_r = crop_and_straighten(image_r,visualize=False)
    image_ir = crop_and_straighten(image_ir,visualize=False)
    image_pan = crop_and_straighten(image_pan,visualize=False)

    # RESIZE TO SAME SHAPE
    image_b =  cv2.resize(image_b, (6348, 6550), interpolation=cv2.INTER_LINEAR)
    image_r =  cv2.resize(image_r, (6348, 6550), interpolation=cv2.INTER_LINEAR)
    image_g =  cv2.resize(image_g, (6348, 6550), interpolation=cv2.INTER_LINEAR)
    image_ir =  cv2.resize(image_ir, (6348, 6550), interpolation=cv2.INTER_LINEAR)

    # STACK IMAGES TO FORM THE MULTI-SPECTRAL IMAGE OF SHAPE (H, W, B)
    print("Stacking the bands to form the MS image...\n\n")
    ms_image = np.stack([image_b,image_g,image_r,image_ir],axis=-1)
    print("MS IMAGE shape:", ms_image.shape)

    # UPSAMPLE TO PAN RESOLUTION
    print("Upsampling to PAN Resolution...\n\n")
    (pan_height,pan_width) = image_pan.shape[:2]
    ms_image_resize = cv2.resize(ms_image, (pan_width, pan_height), interpolation=cv2.INTER_LINEAR) # USE BILINEAR INTERPOLATION AS IS STANDARD
    print("Upsampled MS IMAGE shape:", ms_image_resize.shape)
    ms_image_resized = ms_image_resize.astype(np.float32)

    # SET UP INPUTS TO MAP ESTIMATION
    Y = np.transpose(ms_image_resized, (2, 0, 1))  # shape: (B, H, W)
    x = image_pan.astype(np.float32)  # shape: (H, W)
    lambda_b = np.array(LAMBDA, dtype=np.float32)

    # CROPPING FOR MEMORY EFFICIENCY
    crop_height = image_pan.shape[0] // 2
    crop_width = image_pan.shape[1] // 2
    Y_cropped = crop_center(Y, crop_width, crop_height)
    x_cropped = crop_center(image_pan, crop_width, crop_height).astype(np.float32)
    print("Cropped MS IMAGE shape:", Y_cropped.shape)
    print("Cropped PAN IMAGE shape:", x_cropped.shape)

    # RUN MAP ESTIMATION
    print("Starting up MAP estimation using SAR prior...\n\n")
    Z_sharp = optimize_map_sar_gd(Y_cropped, x_cropped, lambdas=lambda_b)
    Z_sharp_img = np.transpose(Z_sharp, (1, 2, 0)) # (H, W, B)
    Z_sharp_img = np.clip(Z_sharp_img, 0, 65535).astype(np.uint16)
    print("Shape of PAN-Sharpened Image:", Z_sharp_img.shape)

    # DOWNSAMPLING TO ORIGINAL RESOLUTION
    print("Downsampling back to MS resolution...\n\n")
    Z_sharp_MS = cv2.resize(Z_sharp_img, (Z_sharp_img.shape[1] // 2,Z_sharp_img.shape[0] // 2),interpolation=cv2.INTER_AREA)
    Z_sharp_MS = cv2.resize(Z_sharp_MS,(ms_image.shape[1] // 2,ms_image.shape[0] // 2),interpolation=cv2.INTER_AREA)
    print("Shape after downsampling of the pansharpened image:", Z_sharp_MS.shape)

    # CROPPING ORIGINAL MS IMAGE TO COMPARE WITH THE PANSHARPENED IMAGE
    crop_height_ = ms_image.shape[0] // 2
    crop_width_ = ms_image.shape[1] // 2
    ms_image_cropped = crop_center(np.transpose(ms_image,(2,0,1)), crop_width_, crop_height_).astype(np.float32)
    ms_image_cropped = np.transpose(ms_image_cropped,(1,2,0))
    print(f"Original MS shape: {ms_image_cropped.shape} and PAN-Sharpened MS shape: {Z_sharp_MS.shape}")

    # METRICS
    print("Running metrics...\n\n")
    sam_image, mean_sam = compute_sam(ms_image_cropped,Z_sharp_MS)
    psnr = compute_quality_metrics(ms_image_cropped,Z_sharp_MS)
    ergas = calculate_ergas(ms_image_cropped,Z_sharp_MS,4)
    rmse = compute_quality_metrics(ms_image_cropped,Z_sharp_MS,False)
    print(f"PSNR: {psnr}, ERGAS: {ergas}, RMSE: {rmse}, MEAN SAM: {mean_sam}")

    print("End\n")

if __name__ == "__main__":
    main()
