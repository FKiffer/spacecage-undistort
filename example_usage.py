#!/usr/bin/env python3
"""Example usage of the SpaceCage undistortion pipeline."""

from spacecage_undistort import UndistortionPipeline

# Example 1: Basic usage - calibrate and undistort in one go
def example_basic():
    """Basic example: calibrate and undistort a video."""
    pipeline = UndistortionPipeline(
        video_path="269_18-02-15_1389_Feeder_1.1.mp4"
        # roi_path is auto-detected as "269_18-02-15_1389_Feeder_1.1.rois.yml"
    )

    # Perform calibration
    calibration = pipeline.calibrate(
        save_calibration_path="my_calibration.yml",
        side_length_m=0.01  # 1cm grid squares
    )

    print(f"Calibration RMS error: {calibration['rms_error']:.4f} pixels")
    print(f"Number of segments used: {calibration['num_segments']}")

    # Undistort the video
    pipeline.undistort_video("undistorted_output.mp4")


# Example 2: Reuse existing calibration
def example_reuse_calibration():
    """Example: Load existing calibration and undistort a new video."""
    pipeline = UndistortionPipeline(
        video_path="another_video.mp4",
        calibration_path="my_calibration.yml"
    )

    # Load the saved calibration
    pipeline.load_calibration_file()

    # Undistort using the loaded calibration
    pipeline.undistort_video("another_undistorted.mp4")


# Example 3: Undistort a single frame
def example_single_frame():
    """Example: Undistort a single image frame."""
    import cv2

    # Set up and calibrate
    pipeline = UndistortionPipeline(video_path="269_18-02-15_1389_Feeder_1.1.mp4")
    pipeline.calibrate()

    # Load and undistort a single frame
    frame = cv2.imread("frame.jpg")
    undistorted_frame = pipeline.undistort_frame(frame)

    # Save the result
    cv2.imwrite("frame_undistorted.jpg", undistorted_frame)


# Example 4: Calibrate only (don't undistort video)
def example_calibrate_only():
    """Example: Perform calibration and save it for later use."""
    pipeline = UndistortionPipeline(video_path="269_18-02-15_1389_Feeder_1.1.mp4")

    calibration = pipeline.calibrate(
        save_calibration_path="saved_calibration.yml"
    )

    print("Calibration saved!")
    print(f"Camera matrix K:\n{calibration['K']}")
    print(f"Distortion coefficients: {calibration['dist'].ravel()}")
    print(f"RMS error: {calibration['rms_error']:.4f} pixels")


if __name__ == "__main__":
    # Run the basic example
    # Uncomment to try different examples:

    # example_basic()
    # example_reuse_calibration()
    # example_single_frame()
    # example_calibrate_only()

    print("Uncomment one of the example functions to run it!")
    print("See example_usage.py for different usage patterns.")
