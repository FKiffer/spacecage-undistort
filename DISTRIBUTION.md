# Distribution Guide

## Quick Distribution Package

### Option 1: Use the Distribution Script (Recommended)

```bash
./create_distribution.sh
```

This creates `spacecage-undistort-distribution.tar.gz` with only the essential files.

### Option 2: One-Line Command

```bash
tar -czf spacecage-undistort.tar.gz \
  README.md \
  USAGE.md \
  CAMERA_CALIBRATION_GUIDE.md \
  PROJECT_STRUCTURE.md \
  pyproject.toml \
  example_usage.py \
  .gitignore \
  src/
```

### Option 3: Zip Format (for Windows users)

```bash
zip -r spacecage-undistort.zip \
  README.md \
  USAGE.md \
  CAMERA_CALIBRATION_GUIDE.md \
  PROJECT_STRUCTURE.md \
  pyproject.toml \
  example_usage.py \
  .gitignore \
  src/
```

## What's Included

✅ **Essential files:**
- `README.md` - Main documentation
- `USAGE.md` - Quick start guide
- `CAMERA_CALIBRATION_GUIDE.md` - Calibration details
- `PROJECT_STRUCTURE.md` - Project overview
- `pyproject.toml` - Package configuration
- `example_usage.py` - Python API examples
- `.gitignore` - Git ignore patterns
- `src/` - All Python source code

## What's NOT Included

❌ **Excluded (to keep package small):**
- `*.mp4` - Video files (too large, users have their own)
- `*.ipynb` - Jupyter notebooks (development only)
- `*.png` - Images (not needed for functionality)
- `undistorted.mp4` - Output files (users generate their own)
- `.venv/` - Virtual environment (users create their own)
- `__pycache__/` - Python cache files
- `*.pyc` - Compiled Python files
- `uv.lock` - Lock file (not needed)
- `.python-version` - Python version file (specified in pyproject.toml)
- `main.py` - Old file (superseded by the package)

## For Recipients

After receiving the package:

```bash
# Extract
tar -xzf spacecage-undistort.tar.gz
cd spacecage-undistort

# Install
pip install -e .

# Verify installation
spacecage-undistort --help

# Use with your own videos
spacecage-undistort your_video.mp4 -o output.mp4
```

## Package Size

Expected size: **~50-100 KB** (compressed)

Compare to full directory with videos: **~30 MB**

## Sharing Methods

### Email
- Package is small enough to email directly
- Most email systems support attachments up to 25 MB

### Shared Drive (Google Drive, Dropbox, etc.)
```bash
# Upload spacecage-undistort.tar.gz to shared drive
# Share link with recipients
```

### USB/Physical Media
- Copy the .tar.gz or .zip file
- Include a README with installation instructions

### Internal Server
```bash
# Host on internal server
scp spacecage-undistort.tar.gz user@server:/path/to/share/
```

## Verification

After creating the package, verify contents:

```bash
# List contents
tar -tzf spacecage-undistort.tar.gz

# Check size
du -h spacecage-undistort.tar.gz

# Test extraction
mkdir test_extract
cd test_extract
tar -xzf ../spacecage-undistort.tar.gz
cd spacecage-undistort
pip install -e .
spacecage-undistort --help
```
