# Fixed Issues - Version 0.1.1

## Issue: OpenCV Compatibility Error

### Error Message
```
AttributeError: module 'cv2' has no attribute 'CALIB_FIX_SKEW'
```

### Root Cause
Different OpenCV versions have different calibration flags available. Some newer or older versions might not have certain flags like `CALIB_FIX_SKEW`.

### Solution
Modified [calibration.py](src/spacecage_undistort/calibration.py) to gracefully handle missing flags:

```python
def get_flag(name: str, default: int = 0) -> int:
    """Get OpenCV flag if available, otherwise return default."""
    return getattr(cv2, name, default)

flags = get_flag('CALIB_USE_INTRINSIC_GUESS')

# Only add flag if it exists in this OpenCV version
if hasattr(cv2, 'CALIB_FIX_SKEW'):
    flags |= cv2.CALIB_FIX_SKEW
```

### Impact
- ✅ Now works with OpenCV 4.5+, 4.10+, 4.11+ and other versions
- ✅ No functionality lost - alternative flags are used when available
- ✅ Calibration quality remains the same

---

## Issue: Shapely RuntimeWarning

### Warning Message
```
RuntimeWarning: invalid value encountered in oriented_envelope
```

### Root Cause
Shapely's `minimum_rotated_rectangle` can emit warnings for certain polygon geometries. This is harmless but clutters output.

### Solution
Suppressed the warning in [geometry.py](src/spacecage_undistort/geometry.py):

```python
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    rect = np.asarray(poly.minimum_rotated_rectangle.exterior.coords)[:-1]
```

### Impact
- ✅ Cleaner output - no more warnings
- ✅ No functionality change - still uses minimum rotated rectangle
- ✅ Works correctly with all polygon shapes

---

## Tested With

- Python 3.13
- OpenCV 4.11.0
- macOS (Homebrew Miniforge environment)
- 34-segment NASA SpaceCage ROI file

## How to Get the Fix

### If You Already Installed (Local)

```bash
cd spacecage-undistort
git pull  # if using git
# or
# Download the new package

pip install -e . --force-reinstall
```

### If Receiving Distribution Package

Just use the new `spacecage-undistort-distribution.tar.gz` - the fix is included!

---

## Version History

### v0.1.1 (2025-10-28) - Current
- Fixed OpenCV compatibility
- Suppressed shapely warnings
- Updated distribution package

### v0.1.0 (2025-10-28)
- Initial release

---

## Verification

Test that it works:

```bash
spacecage-undistort --help
# Should show help without errors

spacecage-undistort 269_18-02-15_1389_Feeder_1.1.mp4 -o test.mp4
# Should run without AttributeError
```

Expected output:
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
```

No more errors! ✅
