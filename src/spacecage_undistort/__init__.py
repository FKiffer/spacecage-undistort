"""NASA SpaceCage Video Undistortion Tool

A tool for undistorting fisheye camera videos using calibration grid segments.
Also includes coordinate transformation for tracking labels (SLEAP files).
"""

__version__ = "0.1.1"

from .undistort import UndistortionPipeline
from .roi import load_rois, create_model_grid
from .coordinates import (
    undistort_points,
    transform_slp_coordinates,
    batch_transform_slp_files
)

__all__ = [
    "UndistortionPipeline",
    "load_rois",
    "create_model_grid",
    "undistort_points",
    "transform_slp_coordinates",
    "batch_transform_slp_files"
]
