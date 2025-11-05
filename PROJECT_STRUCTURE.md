# Project Structure

## Overview

This is a complete, portable undistortion pipeline for NASA SpaceCage videos.

```
2025-09-19-NASA-SpaceCage/
├── README.md                          # Main documentation
├── USAGE.md                           # Quick start guide
├── PROJECT_STRUCTURE.md               # This file
├── pyproject.toml                     # Package configuration
├── .gitignore                         # Git ignore patterns
├── example_usage.py                   # Python API examples
│
├── src/spacecage_undistort/          # Main package
│   ├── __init__.py                   # Package initialization
│   ├── cli.py                        # Command-line interface
│   ├── undistort.py                  # Main pipeline class
│   ├── calibration.py                # Camera calibration
│   ├── roi.py                        # ROI loading and grid creation
│   └── geometry.py                   # Geometric utilities
│
├── pilot_undistortion.eda.*.ipynb    # Original notebooks (for reference)
├── 269_18-02-15_1389_Feeder_1.1.mp4  # Example video
└── 269_18-02-15_1389_Feeder_1.1.rois.yml  # Example ROI labels
```

## Module Descriptions

### `src/spacecage_undistort/`

- **`__init__.py`**: Package entry point, exports main classes
- **`cli.py`**: Command-line interface (`spacecage-undistort` command)
- **`undistort.py`**: Main `UndistortionPipeline` class
- **`calibration.py`**: Camera calibration using OpenCV
- **`roi.py`**: ROI file loading and model grid generation
- **`geometry.py`**: Polygon processing and corner extraction

## Key Features

### Command-Line Interface
```bash
spacecage-undistort video.mp4 -o output.mp4
```

### Python API
```python
from spacecage_undistort import UndistortionPipeline

pipeline = UndistortionPipeline(video_path="video.mp4")
pipeline.calibrate()
pipeline.undistort_video("output.mp4")
```

### Calibration Saving/Loading
- Save: `--save-calibration calibration.yml`
- Load: `--calibration calibration.yml`

## Installation

```bash
pip install -e .
```

This installs:
- Python package: `spacecage_undistort`
- CLI tool: `spacecage-undistort`

## Dependencies

Core dependencies:
- opencv-python: Camera calibration and image processing
- numpy: Numerical operations
- shapely: Polygon geometry
- sleap-io: Video I/O
- pyyaml: Configuration file handling
- tqdm: Progress bars

## Workflow

1. **Label ROIs** (one-time per camera position):
   ```bash
   labelroi video.mp4
   ```

2. **Undistort video**:
   ```bash
   spacecage-undistort video.mp4 -o undistorted.mp4
   ```

3. **Reuse calibration** (same camera position):
   ```bash
   spacecage-undistort video2.mp4 -o undistorted2.mp4 --calibration calibration.yml
   ```

## Testing

To test with the example video:

```bash
# Make sure you have the ROI file
ls 269_18-02-15_1389_Feeder_1.1.rois.yml

# Run undistortion
spacecage-undistort 269_18-02-15_1389_Feeder_1.1.mp4 -o test_output.mp4
```

## Distribution

To share this tool with others:

1. **Share the entire directory**
2. They run: `pip install -e .`
3. They use: `spacecage-undistort`

Or create a distributable package:
```bash
pip install build
python -m build
# Shares dist/*.whl file
```

## Maintenance

- Main code: `src/spacecage_undistort/`
- Documentation: `README.md`, `USAGE.md`
- Examples: `example_usage.py`
- Configuration: `pyproject.toml`
