import math
import os.path as osp
from typing import List, Optional

import cv2
import numpy as np
from PIL import Image
from skimage import feature, transform

from fundus_circle_cropping.circle_em import circle_em


def get_mask(ratios: List[float], target_resolution: int = 1024):
    """Get mask from radius ratios.

    Args:
        ratios: Ratios for radius in mask horizontally and vertically.
        target_resolution: Target image resolution after resize.

    Return:
        Mask.
    """
    Y, X = np.ogrid[:target_resolution, :target_resolution]
    r = target_resolution / 2
    dist_from_center = np.sqrt((X - r) ** 2 + (Y - r) ** 2)
    mask = dist_from_center <= r

    if ratios[0] < 1:
        mask &= Y >= (r - r * ratios[0])
    if ratios[1] < 1:
        mask &= Y <= (r + r * ratios[1])

    if ratios[2] < 1:
        mask &= X >= (r - r * ratios[2])
    if ratios[3] < 1:
        mask &= X <= (r + r * ratios[3])
    return mask


def square_padding(im: np.ndarray, add_pad: int = 100) -> np.ndarray:
    """Set image into the center and pad around.

    To better find edges and the corresponding circle in the fundus images.

    Args:
        im: Fundus image.
        add_pad: Constant border padding.

    Return:
        Padded image.
    """
    dim_y, dim_x = im.shape[:2]
    dim_larger = max(dim_x, dim_y)
    x_pad = (dim_larger - dim_x) // 2 + add_pad
    y_pad = (dim_larger - dim_y) // 2 + add_pad
    return np.pad(im, ((y_pad, y_pad), (x_pad, x_pad), (0, 0)))


def fundus_image(
    x: np.ndarray,
    x_id: str,
    image_folder: str,
    file_extension: Optional[str] = "png",
    mask_folder: Optional[str] = None,
    resize_shape: int = 1024,
    resize_canny_edge: int = 1000,
    sigma_scale: int = 50,
    circle_fit_steps: int = 100,
    λ: float = 0.01,
    fit_largest_contour: bool = False,
    remove_rectangles: bool = True,
    minimal_save: bool = False,
):
    """Preprocess fundus images.

    Image is tightly cropped around circle found in fundus images.
    Additionally the corresponding circle mask is saved.

    Args:
        x: Image to preprocess.
        x_id: Image ID.
        image_folder: Folder to save preprocessed image.
        file_extension: File extension (e.g. jpeg or png) for the saved images
            (fundus and its mask).
        mask_folder: Folder to save circle masks. Not needed for minimal save.
        resize_shape: Target image shape.
        resize_canny_edge: Image size for canny edge detection.
        sigma_scale: Scale for sigma parameter of canny edge detection,
            sigma = resize_canny_edge / sigma_scale.
        circle_fit_steps: Number of steps for circle fitting.
        λ: Decay constant of exponential function.
        fit_largest_contour: Find contours in points and only fit circle to
            largest
        remove_rectangles: Remove little rectangles on the edges of fundus
            images.
        minimal_save: If True only the pixels that are not background pixels
            are saved and the ratios to reconstruct the mask are returned.

    Returns:
        If minimal_save is True ratios for mask reconstruction are returned.
        If image could not be preprocessed (failure case).
    """
    failure = False

    is_RGB = len(x.shape) == 3

    # simple hack to check for single-channel images: FA, ICGA, etc...
    if not is_RGB:
        x = np.asarray(Image.fromarray(x).convert(mode="RGB"))

    # Pad image to square.
    x_square_padded = square_padding(x)

    # Detect outer circle.
    height, _, _ = x_square_padded.shape
    # Resize image for canny edge detection (scales bad with image size).
    x_resized = np.array(
        Image.fromarray(x_square_padded).resize((resize_canny_edge,) * 2)
    )
    x_gray = x_resized.mean(axis=-1)
    edges = feature.canny(
        x_gray,
        sigma=resize_canny_edge / sigma_scale,
        low_threshold=0.99,
        high_threshold=1,
    )
    # If no edges are found, the image is skipped (e.g. for completely black
    # images).
    if np.all(edges == 0):
        print(f"No edges found, skip image with id {x_id}.\n")
        return None, True
    # Restore original image size.
    edges_resized = np.array(Image.fromarray(edges).resize((height,) * 2))

    if fit_largest_contour:
        contours, _ = cv2.findContours(
            edges_resized.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )
        # Sort contours by number of points.
        contours_sorted = sorted(contours, key=lambda x: x.shape[0], reverse=True)
        points = contours_sorted[0].squeeze().T  # take the largest contour
    else:
        points = np.flip(np.array(edges_resized.nonzero()), axis=0)

    x_init = height / 2
    r_init = height / 2 - 100
    # Initialize circle parameters (initial guess is close to the largest
    # possible circle).
    circle_init = (x_init, x_init, r_init)
    x_c, y_c, r = circle_em(points, circle_init, circle_fit_steps, λ)

    if math.isnan(x_c) or math.isnan(y_c) or math.isnan(r):
        print(f"Wrong circle found, skip id {x_id}.\n")
        return None, True

    # Create masked image.
    masked_img = x_square_padded.copy()

    # Tight crop around circle.
    masked_img = masked_img[
        int(y_c - r) : int(y_c + r) + 1, int(x_c - r) : int(x_c + r) + 1, :
    ]
    if masked_img.size == 0:
        print(f"Wrong circle found, skip id {x_id}.\n")
        return None, True

    # Resize image.
    # Transforms image to float64 and to a value range of (0,1).
    masked_img = transform.resize(masked_img, (resize_shape,) * 2, anti_aliasing=True)

    # Define ratios to create mask.
    h, w = x.shape[:2]
    h_pad = w_pad = x_square_padded.shape[0]
    h_diff = h_pad - h
    w_diff = w_pad - w

    r_ht_ratio = (y_c - h_diff / 2) / r
    r_hb_ratio = (h_pad - y_c - h_diff / 2) / r
    r_wl_ratio = (x_c - w_diff / 2) / r
    r_wr_ratio = (w_pad - x_c - w_diff / 2) / r

    ratios = [
        r_ht_ratio.item(),
        r_hb_ratio.item(),
        r_wl_ratio.item(),
        r_wr_ratio.item(),
    ]

    mask = get_mask(ratios, target_resolution=resize_shape)
    # Remove little rectangles on the edges of fundus images (cast them also as black background pixels).
    if remove_rectangles:
        masked_img[~mask] = 0.0

    # convert back to single channel, 0-1 range
    if not is_RGB:
        # masked_img = Image.fromarray(masked_img).convert(model='L') #.convert(mode='F')
        masked_img = masked_img[
            :, :, 0
        ]  # np.asarray(masked_img, dtype=np.float32) # / 255

    Image.fromarray((masked_img * 255).astype(np.uint8)).save(
        osp.join(image_folder, f"{x_id}.{file_extension}")
    )

    if minimal_save:
        # Save only the data with the information needed later for training.
        np.save(osp.join(image_folder, f"{x_id}"), masked_img[mask])
        return ratios, failure

    else:
        Image.fromarray((mask * 255).astype(np.uint8)).save(
            osp.join(mask_folder, f"{x_id}.{file_extension}")
        )
        return None, failure
