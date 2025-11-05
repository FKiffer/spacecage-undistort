"""Camera calibration for fisheye distortion correction."""

import cv2
import numpy as np
from typing import Tuple, Optional


def calibrate_camera(
    model_pts: np.ndarray,
    image_pts: np.ndarray,
    image_size: Tuple[int, int],
    fix_principal_point: bool = True,
    fix_aspect_ratio: bool = True
) -> Tuple[float, np.ndarray, np.ndarray, list, list]:
    """
    Calibrate camera using OpenCV's calibrateCamera.

    This estimates camera intrinsics (K) and distortion coefficients from
    correspondences between 3D model points and 2D image points.

    Args:
        model_pts: Model points in 3D (N, 3) or will be converted from (N, 2)
        image_pts: Image points in 2D (N, 2)
        image_size: Image dimensions (width, height)
        fix_principal_point: If True, fix principal point at image center
        fix_aspect_ratio: If True, constrain fx ≈ fy

    Returns:
        Tuple of (rms_error, K, dist_coeffs, rvecs, tvecs)
    """
    w, h = image_size

    # Convert 2D model points to 3D (Z=0 plane)
    if model_pts.shape[1] == 2:
        objp = np.column_stack([
            model_pts,
            np.zeros(len(model_pts))
        ]).astype(np.float32).reshape(-1, 1, 3)
    else:
        objp = model_pts.astype(np.float32).reshape(-1, 1, 3)

    imgp = image_pts.astype(np.float32).reshape(-1, 1, 2)

    # Initial camera matrix guess
    K0 = np.array([
        [w, 0, w/2],
        [0, w, h/2],
        [0, 0, 1]
    ], dtype=np.float64)

    dist0 = np.zeros(5, dtype=np.float64)

    # Build calibration flags (use getattr for compatibility with different OpenCV versions)
    def get_flag(name: str, default: int = 0) -> int:
        """Get OpenCV flag if available, otherwise return default."""
        return getattr(cv2, name, default)

    flags = get_flag('CALIB_USE_INTRINSIC_GUESS')

    # Add flags if available in this OpenCV version
    if hasattr(cv2, 'CALIB_FIX_SKEW'):
        flags |= cv2.CALIB_FIX_SKEW

    flags |= get_flag('CALIB_FIX_K3')
    flags |= get_flag('CALIB_FIX_K4')
    flags |= get_flag('CALIB_FIX_K5')
    flags |= get_flag('CALIB_FIX_K6')

    if fix_principal_point:
        flags |= get_flag('CALIB_FIX_PRINCIPAL_POINT')

    if fix_aspect_ratio:
        flags |= get_flag('CALIB_FIX_ASPECT_RATIO')

    # Calibration criteria
    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        400,
        1e-10
    )

    # Run calibration
    rms, K, dist, rvecs, tvecs = cv2.calibrateCamera(
        [objp], [imgp],
        (w, h),
        K0, dist0,
        flags=flags,
        criteria=criteria
    )

    return rms, K, dist, rvecs, tvecs


def create_undistort_maps(
    K: np.ndarray,
    dist: np.ndarray,
    image_size: Tuple[int, int],
    alpha: float = 1.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create undistortion maps for efficient remapping.

    Args:
        K: Camera intrinsic matrix (3, 3)
        dist: Distortion coefficients (5,) or (1, 5)
        image_size: Image dimensions (width, height)
        alpha: Free scaling parameter (0=no black pixels, 1=all pixels visible)

    Returns:
        Tuple of (newK, map1, map2) for cv2.remap
    """
    w, h = image_size

    newK, roi = cv2.getOptimalNewCameraMatrix(
        K, dist, (w, h),
        alpha=alpha,
        newImgSize=(w, h)
    )

    map1, map2 = cv2.initUndistortRectifyMap(
        K, dist, None, newK,
        (w, h),
        cv2.CV_32FC1
    )

    return newK, map1, map2


def undistort_image(
    image: np.ndarray,
    map1: np.ndarray,
    map2: np.ndarray
) -> np.ndarray:
    """
    Apply undistortion to an image using precomputed maps.

    Args:
        image: Input image
        map1: First undistortion map
        map2: Second undistortion map

    Returns:
        Undistorted image
    """
    return cv2.remap(
        image, map1, map2,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT
    )


def save_calibration(
    filepath: str,
    K: np.ndarray,
    dist: np.ndarray,
    image_size: Tuple[int, int],
    rms_error: float
) -> None:
    """
    Save calibration parameters to a YAML file.

    Args:
        filepath: Output file path
        K: Camera intrinsic matrix
        dist: Distortion coefficients
        image_size: Image dimensions (width, height)
        rms_error: RMS reprojection error
    """
    import yaml

    calibration_data = {
        'camera_matrix': K.tolist(),
        'distortion_coefficients': dist.ravel().tolist(),
        'image_width': int(image_size[0]),
        'image_height': int(image_size[1]),
        'rms_error': float(rms_error),
    }

    with open(filepath, 'w') as f:
        yaml.dump(calibration_data, f, default_flow_style=False)


def load_calibration(filepath: str) -> Tuple[np.ndarray, np.ndarray, Tuple[int, int], float]:
    """
    Load calibration parameters from a YAML file.

    Args:
        filepath: Input file path

    Returns:
        Tuple of (K, dist, image_size, rms_error)
    """
    import yaml

    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)

    K = np.array(data['camera_matrix'], dtype=np.float64)
    dist = np.array(data['distortion_coefficients'], dtype=np.float64)
    image_size = (data['image_width'], data['image_height'])
    rms_error = data.get('rms_error', 0.0)

    return K, dist, image_size, rms_error
