# Changelog

All notable changes to the SpaceCage Undistortion Tool will be documented in this file.

## [0.1.1] - 2025-10-28

### Fixed
- **OpenCV Compatibility**: Fixed `AttributeError: module 'cv2' has no attribute 'CALIB_FIX_SKEW'`
  - Made calibration flags compatible with different OpenCV versions
  - Added fallback for missing calibration flags (lines 53-73 in [calibration.py](src/spacecage_undistort/calibration.py))
  - Uses `getattr()` and `hasattr()` to check for flag availability
  - Tested with OpenCV 4.11.0 and compatible with older versions

- **Shapely Warnings**: Suppressed harmless RuntimeWarning from shapely's oriented_envelope
  - Added warning filter in [geometry.py](src/spacecage_undistort/geometry.py#L46-L49)
  - Does not affect functionality, only suppresses expected warnings

### Technical Details

**Problem**: Different OpenCV versions have different calibration flags available. Python 3.13 with newer OpenCV might not have `CALIB_FIX_SKEW` flag.

**Solution**:
```python
def get_flag(name: str, default: int = 0) -> int:
    """Get OpenCV flag if available, otherwise return default."""
    return getattr(cv2, name, default)

flags = get_flag('CALIB_USE_INTRINSIC_GUESS')
if hasattr(cv2, 'CALIB_FIX_SKEW'):
    flags |= cv2.CALIB_FIX_SKEW
# ... etc
```

This ensures the tool works across OpenCV 4.x versions.

## [0.1.0] - 2025-10-28

### Added
- Initial release
- Camera calibration using grid segments
- Video undistortion pipeline
- Command-line interface (`spacecage-undistort`)
- Python API for programmatic use
- Calibration saving/loading functionality
- Comprehensive documentation:
  - README.md
  - USAGE.md
  - CAMERA_CALIBRATION_GUIDE.md
  - PROJECT_STRUCTURE.md
  - DISTRIBUTION.md
  - SHARING_INSTRUCTIONS.md

### Features
- Support for up to 34 grid segments
- Automatic ROI file detection
- Fisheye lens distortion correction
- Progress bars for video processing
- OpenCV-based camera calibration
- ROI labeling integration with labelroi

### Requirements
- Python ≥ 3.9
- opencv-python ≥ 4.5.0
- numpy ≥ 1.20.0
- shapely ≥ 2.0.0
- sleap-io ≥ 0.5.0
- Other dependencies in pyproject.toml
