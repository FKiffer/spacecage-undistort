# Quick Start Guide

## Installation

```bash
cd /path/to/2025-09-19-NASA-SpaceCage
pip install -e .
```

## Step-by-Step Workflow

### 1. Label Your Video Grid Segments

First, install and use labelroi to mark the calibration grid squares in your video:

```bash
# Install labelroi
pip install labelroi

# Open the labeling interface
labelroi 269_18-02-15_1389_Feeder_1.1.mp4
```

**Labeling Instructions:**
1. Click on each visible grid square to create a 4-point polygon
2. Name them sequentially: "segment1", "segment2", etc.
3. Save the file (creates `269_18-02-15_1389_Feeder_1.1.rois.yml`)

**Important Notes:**
- Label at least 3 segments (more is better, 10+ recommended)
- Try to label segments spread across the entire visible grid
- Make sure the polygon corners align with the actual grid square corners
- The tool supports up to 34 segments in different positions

### 2. Run Undistortion

Once you have the ROI file, run the undistortion:

```bash
# Basic usage - auto-detects the .rois.yml file
spacecage-undistort 269_18-02-15_1389_Feeder_1.1.mp4 -o undistorted.mp4

# Save calibration for reuse
spacecage-undistort 269_18-02-15_1389_Feeder_1.1.mp4 \
    -o undistorted.mp4 \
    --save-calibration my_camera_calibration.yml
```

You'll see output like:
```
============================================================
CALIBRATION
============================================================
Loading video: 269_18-02-15_1389_Feeder_1.1.mp4
Loading ROIs: 269_18-02-15_1389_Feeder_1.1.rois.yml
Loaded 34 ROI segments
Creating model grid...
Placing model in video space...
Extracting corner correspondences...
Using 34 segments for calibration
Running camera calibration...
Calibration RMS error: 3.7091 pixels
...

============================================================
VIDEO UNDISTORTION
============================================================
Processing video (5686 frames at 29.97 FPS)...
Output: undistorted.mp4
Undistorting frames: 100%|████████████| 5686/5686 [01:23<00:00, 68.2it/s]

============================================================
SUCCESS!
============================================================
Undistorted video: undistorted.mp4
```

### 3. Using Saved Calibration (Optional)

If you have multiple videos from the **same camera position**, you can reuse the calibration:

```bash
# Process another video without recalibrating
spacecage-undistort another_video.mp4 \
    -o another_undistorted.mp4 \
    --calibration my_camera_calibration.yml
```

**Warning:** Only reuse calibration if:
- Camera hasn't moved
- Camera angle hasn't changed
- Same camera hardware
- Same lens settings (focus, zoom)

If the camera moved, you MUST create new ROI labels for the new video.

## Common Issues and Solutions

### Issue: "ROI file not found"

**Solution:** You forgot to label the video. Run:
```bash
labelroi your_video.mp4
```

### Issue: "Need at least 3 overlapping segments"

**Solution:** Label more grid segments in your video using labelroi.

### Issue: High RMS error (> 10 pixels)

**Possible causes:**
- ROI labels are inaccurate → Re-label with more precision
- Grid squares are unclear in video → Use better lighting or different frame
- Not enough segments labeled → Label more segments (10+ recommended)

### Issue: Camera position changed between videos

**Solution:**
1. Do NOT reuse old calibration
2. Create new ROI labels: `labelroi new_video.mp4`
3. Run calibration again (don't use `--calibration` flag)

## Python API Examples

### Basic Programmatic Usage

```python
from spacecage_undistort import UndistortionPipeline

# Simple undistortion
pipeline = UndistortionPipeline(video_path="video.mp4")
pipeline.calibrate()
pipeline.undistort_video("output.mp4")
```

### Process Single Frame

```python
import cv2
from spacecage_undistort import UndistortionPipeline

# Set up pipeline
pipeline = UndistortionPipeline(video_path="video.mp4")
pipeline.calibrate(save_calibration_path="calibration.yml")

# Undistort a single frame
frame = cv2.imread("frame.jpg")
undistorted = pipeline.undistort_frame(frame)
cv2.imwrite("frame_undistorted.jpg", undistorted)
```

### Load Existing Calibration

```python
from spacecage_undistort import UndistortionPipeline

# Use saved calibration
pipeline = UndistortionPipeline(
    video_path="video2.mp4",
    calibration_path="calibration.yml"
)
pipeline.load_calibration_file()
pipeline.undistort_video("output2.mp4")
```

## Tips for Best Results

1. **Label Quality Matters**: Take time to accurately place polygon corners on grid squares
2. **More Segments = Better**: Label 10+ segments if visible for best calibration
3. **Spread Coverage**: Label segments across the entire visible area, not just one region
4. **Check RMS Error**: After calibration, RMS < 5 pixels is excellent, < 10 is acceptable
5. **Camera Stability**: Keep camera fixed if you want to reuse calibration across videos
6. **Grid Visibility**: Ensure grid squares are clearly visible and well-lit in the video

## File Organization

Suggested project structure:
```
my_experiment/
├── raw_videos/
│   ├── recording1.mp4
│   ├── recording1.rois.yml       # Created by labelroi
│   ├── recording2.mp4
│   └── recording2.rois.yml
├── undistorted/
│   ├── recording1_undistorted.mp4
│   └── recording2_undistorted.mp4
└── calibrations/
    ├── camera1_setup1.yml
    └── camera1_setup2.yml
```

## Getting Help

If you encounter issues:
1. Check this guide and the main README.md
2. Verify your labelroi output is in the correct format
3. Try labeling more segments (minimum 3, recommended 10+)
4. Check the labelroi documentation: https://github.com/talmolab/labelroi
