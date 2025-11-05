"""Geometric utilities for polygon processing and corner extraction."""

import re
import numpy as np
from shapely.geometry import Polygon
from typing import Dict, List


SEGMENT_RE = re.compile(r"^segment(\d+)$", re.IGNORECASE)


def segment_number(key: str) -> int:
    """Extract segment number for sorting."""
    m = SEGMENT_RE.match(key)
    return int(m.group(1)) if m else 10**9


def quad_from_polygon(poly: Polygon, eps: float = 1e-6) -> np.ndarray:
    """
    Extract 4 unique vertices from a polygon.

    If polygon is not a quad, uses minimum rotated rectangle.

    Args:
        poly: Input polygon
        eps: Tolerance for duplicate vertex detection

    Returns:
        Array of 4 vertices (4, 2)
    """
    coords = np.asarray(poly.exterior.coords)[:-1]  # Drop closing duplicate

    # Remove duplicate vertices
    if len(coords) > 1:
        uniq = [coords[0]]
        for p in coords[1:]:
            if np.linalg.norm(p - uniq[-1]) > eps:
                uniq.append(p)
        coords = np.array(uniq)

    if coords.shape[0] == 4:
        return coords.astype(float)

    # Use minimum rotated rectangle if not a quad
    # Suppress shapely warnings about oriented_envelope
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        rect = np.asarray(poly.minimum_rotated_rectangle.exterior.coords)[:-1]

    assert rect.shape[0] == 4, "Minimum rotated rectangle did not produce 4 vertices"
    return rect.astype(float)


def canonical_order_ccw(quads: np.ndarray, y_up: bool) -> np.ndarray:
    """
    Order quad vertices counter-clockwise starting from top-left corner.

    Args:
        quads: Quad vertices (4, 2)
        y_up: If True, Y increases upward (metric). If False, Y increases downward (pixels)

    Returns:
        Reordered vertices (4, 2)
    """
    q = quads.copy()
    c = q.mean(axis=0)  # Centroid

    # Compute angles from centroid
    dy = (q[:, 1] - c[1]) * (1.0 if y_up else -1.0)
    dx = (q[:, 0] - c[0])
    ang = np.arctan2(dy, dx)

    # Sort counter-clockwise
    order = np.argsort(ang)
    q = q[order]

    # Find top-left corner to start
    if y_up:
        start = np.lexsort((q[:, 0], -q[:, 1]))[0]  # Max Y, then min X
    else:
        start = np.lexsort((q[:, 0], q[:, 1]))[0]  # Min Y, then min X

    return np.roll(q, -start, axis=0)


def extract_canonical_corners(
    model_polygons: Dict[str, Polygon],
    video_polygons: Dict[str, Polygon]
) -> tuple:
    """
    Extract canonical corner points from model and video polygons.

    Returns corners in consistent order for correspondence matching.

    Args:
        model_polygons: Model polygons in metric space (Y-up)
        video_polygons: Video polygons in pixel space (Y-down)

    Returns:
        Tuple of (roi_keys, model_quads, video_quads)
        where quads are dicts mapping segment names to (4,2) arrays
    """
    # Find common segments
    common = set(model_polygons.keys()).intersection(video_polygons.keys())
    roi_keys = sorted([k for k in common if SEGMENT_RE.match(k)], key=segment_number)

    if len(roi_keys) < 3:
        raise ValueError(f"Need at least 3 overlapping segments, found {len(roi_keys)}")

    model_quads = {}
    video_quads = {}

    for key in roi_keys:
        # Extract quads with canonical ordering
        m_quad = quad_from_polygon(model_polygons[key])
        v_quad = quad_from_polygon(video_polygons[key])

        model_quads[key] = canonical_order_ccw(m_quad, y_up=True)
        video_quads[key] = canonical_order_ccw(v_quad, y_up=False)

    return roi_keys, model_quads, video_quads


def extract_centroid_correspondences(
    model_polygons: Dict[str, Polygon],
    video_polygons: Dict[str, Polygon],
    roi_keys: List[str]
) -> tuple:
    """
    Extract centroid points for correspondence matching.

    Args:
        model_polygons: Model polygons
        video_polygons: Video polygons
        roi_keys: List of segment keys to use

    Returns:
        Tuple of (model_centroids, video_centroids) as (N, 2) arrays
    """
    def centroid_xy(poly: Polygon) -> np.ndarray:
        c = poly.centroid
        return np.array([c.x, c.y], dtype=np.float32)

    model_pts = np.vstack([
        centroid_xy(model_polygons[k]) for k in roi_keys
    ]).astype(np.float32)

    video_pts = np.vstack([
        centroid_xy(video_polygons[k]) for k in roi_keys
    ]).astype(np.float32)

    return model_pts, video_pts
