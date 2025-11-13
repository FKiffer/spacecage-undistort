"""Main undistortion pipeline."""

import cv2
import numpy as np
import sleap_io as sio
from pathlib import Path
from tqdm import tqdm
from typing import Optional, Tuple

from .roi import (
    load_rois,
    create_model_grid,
    place_model_in_video_space
)
from .geometry import (
    extract_canonical_corners,
    extract_centroid_correspondences
)
from .calibration import (
    calibrate_camera,
    create_undistort_maps,
    undistort_image,
    save_calibration,
    load_calibration
)


class UndistortionPipeline:
    """
    Complete pipeline for video undistortion using calibration grid.

    This class handles:
    1. Loading ROI labels from video
    2. Creating model grid geometry
    3. Camera calibration
    4. Video undistortion
    """

    def __init__(
        self,
        video_path: str,
        roi_path: Optional[str] = None,
        calibration_path: Optional[str] = None
    ):
        """
        Initialize undistortion pipeline.

        Args:
            video_path: Path to input video file
            roi_path: Path to ROI YAML file (auto-detected if None)
            calibration_path: Path to saved calibration file (will calibrate if None)
        """
        self.video_path = Path(video_path)

        if roi_path is None:
            roi_path = self.video_path.with_suffix('.rois.yml')
        self.roi_path = Path(roi_path)

        self.calibration_path = Path(calibration_path) if calibration_path else None

        # Will be populated during calibration
        self.K = None
        self.dist = None
        self.newK = None
        self.map1 = None
        self.map2 = None
        self.rms_error = None
        self.image_size = None

    def calibrate(
        self,
        save_calibration_path: Optional[str] = None,
        side_length_m: float = 0.01
    ) -> dict:
        """
        Perform camera calibration.

        Args:
            save_calibration_path: If provided, save calibration to this path
            side_length_m: Physical side length of grid squares in meters (default 1cm)

        Returns:
            Dictionary with calibration results
        """
        print(f"Loading video: {self.video_path}")
        video = sio.load_video(str(self.video_path))
        frame0 = video[0]
        h, w = frame0.shape[:2]
        self.image_size = (w, h)

        print(f"Loading ROIs: {self.roi_path}")
        if not self.roi_path.exists():
            raise FileNotFoundError(
                f"ROI file not found: {self.roi_path}\n"
                f"Please create ROI labels using labelroi:\n"
                f"https://github.com/talmolab/labelroi"
            )

        video_polygons = load_rois(self.roi_path)
        print(f"Loaded {len(video_polygons)} ROI segments")

        print("Creating model grid...")
        model_polygons = create_model_grid(side_length_m=side_length_m)

        print("Placing model in video space...")
        placed_model = place_model_in_video_space(model_polygons, video_polygons)

        print("Extracting corner correspondences...")
        roi_keys, model_quads, video_quads = extract_canonical_corners(
            placed_model, video_polygons
        )
        print(f"Using {len(roi_keys)} segments for calibration")

        # Extract centroid correspondences
        model_pts, image_pts = extract_centroid_correspondences(
            placed_model, video_polygons, roi_keys
        )

        print("Running camera calibration...")
        self.rms_error, self.K, self.dist, rvecs, tvecs = calibrate_camera(
            model_pts, image_pts, self.image_size
        )

        print(f"Calibration RMS error: {self.rms_error:.4f} pixels")
        print(f"Camera matrix K:\n{self.K}")
        print(f"Distortion coefficients: {self.dist.ravel()}")

        print("Creating undistortion maps...")
        self.newK, self.map1, self.map2 = create_undistort_maps(
            self.K, self.dist, self.image_size, alpha=1.0
        )

        if save_calibration_path:
            print(f"Saving calibration to: {save_calibration_path}")
            save_calibration(
                save_calibration_path,
                self.K, self.dist,
                self.image_size,
                self.rms_error
            )

        return {
            'rms_error': self.rms_error,
            'K': self.K,
            'dist': self.dist,
            'newK': self.newK,
            'num_segments': len(roi_keys)
        }

    def load_calibration_file(self, calibration_path: Optional[str] = None) -> None:
        """
        Load calibration from file.

        Args:
            calibration_path: Path to calibration YAML file
        """
        if calibration_path is None:
            if self.calibration_path is None:
                raise ValueError("No calibration path provided")
            calibration_path = self.calibration_path

        print(f"Loading calibration from: {calibration_path}")
        self.K, self.dist, self.image_size, self.rms_error = load_calibration(
            str(calibration_path)
        )

        print(f"Loaded calibration with RMS error: {self.rms_error:.4f} pixels")

        self.newK, self.map1, self.map2 = create_undistort_maps(
            self.K, self.dist, self.image_size, alpha=1.0
        )

    def undistort_video(
        self,
        output_path: str,
        use_existing_calibration: bool = False,
        crf: int = 25
    ) -> None:
        """
        Undistort the entire video.

        Args:
            output_path: Path for output video file
            use_existing_calibration: If True and calibration_path exists, load it
            crf: Constant Rate Factor for video encoding (default 25, lower = higher quality)
        """
        # Ensure we have calibration
        if self.map1 is None or self.map2 is None:
            if use_existing_calibration and self.calibration_path and self.calibration_path.exists():
                self.load_calibration_file()
            else:
                print("No calibration found, performing calibration first...")
                self.calibrate()

        print(f"Loading video: {self.video_path}")
        video = sio.load_video(str(self.video_path))

        # Get FPS
        import imageio.v3 as iio
        meta = iio.immeta(str(self.video_path), exclude_applied=False)
        fps = meta.get("fps") or (meta.get("video") or {}).get("fps") or 30.0
        fps = float(fps)

        print(f"Processing video ({len(video)} frames at {fps:.2f} FPS)...")
        print(f"Output: {output_path}")

        with sio.VideoWriter(str(output_path), fps=fps, crf=crf) as writer:
            for frame in tqdm(video, desc="Undistorting frames"):
                undistorted = undistort_image(frame, self.map1, self.map2)
                writer(undistorted)

        print(f"Done! Undistorted video saved to: {output_path}")

    def undistort_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Undistort a single frame.

        Args:
            frame: Input frame

        Returns:
            Undistorted frame
        """
        if self.map1 is None or self.map2 is None:
            raise RuntimeError("Calibration not performed. Run calibrate() first.")

        return undistort_image(frame, self.map1, self.map2)
