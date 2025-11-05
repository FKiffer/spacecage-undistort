"""
Example: Transform SLEAP tracking coordinates to match undistorted videos.

This script demonstrates how to use the coordinate transformation functionality
to update tracking labels after undistorting videos.

Workflow:
1. First, undistort your video and save calibration
2. Then, transform the SLEAP labels to match the undistorted video

"""

from pathlib import Path
from spacecage_undistort import transform_slp_coordinates

# Example 1: Transform a single SLEAP file
# -----------------------------------------
# After undistorting your video, you have:
#   - original_video.mp4 (original video)
#   - original_video_undistorted.mp4 (undistorted video)
#   - calibration.yml (calibration file from spacecage-undistort)
#   - labels.slp (SLEAP labels for original video)

def example_single_file():
    """Transform a single SLEAP file."""

    # Paths to your files
    input_slp = "labels.slp"
    output_slp = "labels_undistorted.slp"
    calibration_file = "calibration.yml"

    # Transform the coordinates
    transform_slp_coordinates(
        slp_input_path=input_slp,
        slp_output_path=output_slp,
        calibration_path=calibration_file,
        undistorted_video_suffix="_undistorted"  # matches your video naming
    )

    print(f"Transformed labels saved to: {output_slp}")
    print("You can now open the undistorted video with the transformed labels in SLEAP!")


# Example 2: Transform with custom video path mapping
# ----------------------------------------------------

def example_custom_video_paths():
    """Transform with explicit video path mapping."""

    # If your undistorted videos have custom names or locations
    video_mapping = {
        "/path/to/original_video.mp4": "/path/to/output/undistorted_video.mp4",
        "/path/to/another_video.mp4": "/path/to/output/another_undistorted.mp4",
    }

    transform_slp_coordinates(
        slp_input_path="labels.slp",
        slp_output_path="labels_undistorted.slp",
        calibration_path="calibration.yml",
        video_path_mapping=video_mapping
    )


# Example 3: Using the CLI
# -------------------------
"""
You can also use the command-line interface:

# Single file
spacecage-transform-coords labels.slp \\
    -o labels_undistorted.slp \\
    --calibration calibration.yml

# Batch transform multiple files
spacecage-transform-coords labels1.slp labels2.slp labels3.slp \\
    -o output_directory/ \\
    --calibration calibration.yml

# Custom video suffix
spacecage-transform-coords labels.slp \\
    -o labels_undistorted.slp \\
    --calibration calibration.yml \\
    --video-suffix _my_custom_suffix
"""


# Example 4: Complete workflow from scratch
# ------------------------------------------

def example_complete_workflow():
    """Complete workflow: calibrate, undistort video, transform coordinates."""

    from spacecage_undistort import UndistortionPipeline

    # Step 1: Undistort the video and save calibration
    print("Step 1: Undistorting video...")
    pipeline = UndistortionPipeline(
        video_path="original_video.mp4",
        roi_path="original_video.rois.yml"  # Created with labelroi
    )

    # Calibrate and save calibration file
    pipeline.calibrate(save_calibration_path="calibration.yml")

    # Undistort the video
    pipeline.undistort_video(output_path="original_video_undistorted.mp4")

    # Step 2: Transform the SLEAP labels
    print("\nStep 2: Transforming coordinates...")
    transform_slp_coordinates(
        slp_input_path="labels.slp",
        slp_output_path="labels_undistorted.slp",
        calibration_path="calibration.yml"
    )

    print("\nComplete! You now have:")
    print("  - Undistorted video: original_video_undistorted.mp4")
    print("  - Transformed labels: labels_undistorted.slp")
    print("  - Calibration file: calibration.yml (can reuse for other videos)")


if __name__ == "__main__":
    print("This is an example script. Edit the paths and run the function you need.")
    print("See the function docstrings for more information.")

    # Uncomment to run:
    # example_single_file()
    # example_custom_video_paths()
    # example_complete_workflow()
