"""ROI (Region of Interest) handling for calibration grid segments."""

import re
import yaml
import numpy as np
from pathlib import Path
from shapely.geometry import Polygon
from shapely import affinity
from typing import Dict, Optional, Tuple


def normalize_segment_name(name: str) -> Optional[str]:
    """
    Map various spellings to 'segmentN' format.

    Accepts 'Segment1', 'segment_01', 'seg-1', etc.
    Returns 'segmentN' or None if not a numbered segment.

    Args:
        name: The segment name to normalize

    Returns:
        Normalized segment name or None
    """
    s = str(name).strip().lower()
    # Pull out the last integer anywhere in the string
    m = re.search(r'(\d+)(?!.*\d)', s)
    if not m:
        return None
    n = int(m.group(1))
    return f"segment{n}"


def load_rois(roi_path: Path) -> Dict[str, Polygon]:
    """
    Load ROI polygons from YAML file.

    Args:
        roi_path: Path to .rois.yml file

    Returns:
        Dictionary mapping segment names to Shapely Polygons
    """
    with open(roi_path, "r") as f:
        rois_data = yaml.safe_load(f) or {}

    roi_polygons = {}
    for roi in rois_data.get("rois", []):
        key = normalize_segment_name(roi.get("name", ""))
        if key is None:
            continue  # Ignore non-segment items

        coords = roi.get("coordinates") or roi.get("points") or []
        if not coords:
            continue

        # Ensure polygon is closed
        if coords[0] != coords[-1]:
            coords = coords + [coords[0]]

        poly = Polygon(coords)
        if not poly.is_valid or poly.is_empty:
            continue

        roi_polygons[key] = poly

    return roi_polygons


def create_model_grid(
    segment_offsets: Optional[Dict[str, Tuple[int, int]]] = None,
    side_length_m: float = 0.01
) -> Dict[str, Polygon]:
    """
    Create a model grid of square segments in metric coordinates.

    The grid is defined by integer offsets (i, j) where each unit represents
    one square. The physical size is determined by side_length_m (default 1cm).

    Args:
        segment_offsets: Dictionary mapping segment names to (i, j) grid positions.
                        If None, uses the default 34-segment NASA SpaceCage layout.
        side_length_m: Physical side length of each square in meters (default 0.01 = 1cm)

    Returns:
        Dictionary mapping segment names to Shapely Polygons in metric coordinates
    """
    if segment_offsets is None:
        # Default NASA SpaceCage 34-segment layout
        segment_offsets = {
            "segment1": (0, 0),
            "segment2": (-1, 0),
            "segment3": (1, 0),
            "segment4": (1, 1),
            "segment5": (0, 1),
            "segment6": (-1, 1),
            "segment7": (-1, -1),
            "segment8": (0, -1),
            "segment9": (1, -1),
            "segment10": (-1, -2),
            "segment11": (0, -2),
            "segment12": (1, -2),
            "segment13": (2, 1),
            "segment14": (2, 0),
            "segment15": (2, -1),
            "segment16": (2, -2),
            "segment17": (3, 1),
            "segment18": (3, 0),
            "segment19": (-2, 0),
            "segment20": (-2, -1),
            "segment21": (-2, -2),
            "segment22": (-3, -1),
            "segment23": (-3, -2),
            "segment24": (-2, 1),
            "segment25": (-3, 0),
            "segment26": (-4, 0),
            "segment27": (-4, -1),
            "segment28": (-4, -2),
            "segment29": (3, -1),
            "segment30": (3, -2),
            "segment31": (2, 2),
            "segment32": (3, 2),
            "segment33": (3, -3),
            "segment34": (-3, 1),
        }

    def _square_from_offset(i: int, j: int) -> Polygon:
        """Create square with lower-left at (i*side, j*side)."""
        x0, y0 = i * side_length_m, j * side_length_m
        return Polygon([
            (x0, y0),
            (x0 + side_length_m, y0),
            (x0 + side_length_m, y0 + side_length_m),
            (x0, y0 + side_length_m)
        ])

    return {
        name: _square_from_offset(i, j)
        for name, (i, j) in segment_offsets.items()
    }


def fit_similarity_transform(
    src_pts: np.ndarray,
    dst_pts: np.ndarray
) -> Tuple[float, np.ndarray, np.ndarray]:
    """
    Fit similarity transform (scale + rotation + translation) using Kabsch algorithm.

    Args:
        src_pts: Source points (N, 2)
        dst_pts: Destination points (N, 2)

    Returns:
        Tuple of (scale, rotation_matrix, translation_vector)
    """
    src = np.asarray(src_pts, float)
    dst = np.asarray(dst_pts, float)
    assert src.shape == dst.shape and src.shape[0] >= 2

    mu_s, mu_d = src.mean(axis=0), dst.mean(axis=0)
    X, Y = src - mu_s, dst - mu_d
    H = X.T @ Y
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T

    # Fix reflection
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T

    scale = S.sum() / (X**2).sum()
    t = mu_d - scale * (R @ mu_s)

    return scale, R, t


def place_model_in_video_space(
    model_polygons: Dict[str, Polygon],
    video_polygons: Dict[str, Polygon]
) -> Dict[str, Polygon]:
    """
    Transform model polygons from metric space to video pixel space.

    Uses centroids of common segments to estimate similarity transform.

    Args:
        model_polygons: Model grid in metric coordinates
        video_polygons: Labeled ROIs in video pixel coordinates

    Returns:
        Transformed model polygons in pixel space
    """
    common = sorted(set(model_polygons.keys()).intersection(video_polygons.keys()))

    if len(common) < 3:
        raise ValueError(f"Need at least 3 common segments, found {len(common)}")

    # Get centroids
    src = np.array([model_polygons[k].centroid.coords[0] for k in common])
    dst = np.array([video_polygons[k].centroid.coords[0] for k in common])

    # Fit transform
    scale, R, t = fit_similarity_transform(src, dst)

    # Apply transform to all model polygons
    placed = {}
    for name, poly in model_polygons.items():
        xy = np.asarray(poly.exterior.coords)
        xy_transformed = (scale * (xy @ R.T)) + t
        placed[name] = Polygon(xy_transformed)

    return placed
