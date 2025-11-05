# Quick Reference Card

## Version
**Current:** 0.1.1 (Fixed OpenCV compatibility)

## Installation
```bash
pip install -e .
```

## Basic Usage
```bash
# Undistort a video
spacecage-undistort video.mp4 -o undistorted.mp4

# Save calibration for reuse
spacecage-undistort video.mp4 -o undistorted.mp4 --save-calibration calib.yml

# Use existing calibration
spacecage-undistort video2.mp4 -o undistorted2.mp4 --calibration calib.yml
```

## Prerequisites
1. Label ROIs first: `labelroi video.mp4`
2. This creates: `video.rois.yml`

## When to Relabel ROIs
- ❌ Camera moved
- ❌ Camera rotated
- ❌ Different camera
- ✅ Same camera, same position → reuse calibration

## File Sizes
- Distribution package: 22 KB
- Full directory: ~30 MB (includes videos)

## Common Issues

### `AttributeError: module 'cv2' has no attribute 'CALIB_FIX_SKEW'`
**Fixed in v0.1.1** - Update to latest version

### `ROI file not found`
Run: `labelroi your_video.mp4` first

### `Need at least 3 overlapping segments`
Label more grid segments (10+ recommended)

## Quick Commands

### Create Distribution Package
```bash
./create_distribution.sh
```

### Share Package
- Email: Attach `spacecage-undistort-distribution.tar.gz`
- USB: Copy the .tar.gz file
- Drive: Upload to Google Drive/Dropbox

### Recipient Installation
```bash
tar -xzf spacecage-undistort-distribution.tar.gz
cd spacecage-undistort
pip install -e .
```

## Python API
```python
from spacecage_undistort import UndistortionPipeline

pipeline = UndistortionPipeline("video.mp4")
pipeline.calibrate()
pipeline.undistort_video("output.mp4")
```

## Files Needed for Recipients
- ✅ Distribution package (22 KB)
- ✅ Python 3.9+
- ✅ Their own videos
- ✅ labelroi tool

## Files NOT Needed
- ❌ Your videos
- ❌ Your ROI files (unless same camera position)
- ❌ Your calibration files (unless same camera position)
- ❌ Jupyter notebooks

## Documentation Files
- `README.md` - Full documentation
- `USAGE.md` - Step-by-step guide
- `CAMERA_CALIBRATION_GUIDE.md` - Calibration explained
- `SHARING_INSTRUCTIONS.md` - How to share
- `FIXED_ISSUES.md` - Version 0.1.1 fixes
- `CHANGELOG.md` - Version history

## Help
```bash
spacecage-undistort --help
```

## Links
- labelroi: https://github.com/talmolab/labelroi
