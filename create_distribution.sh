#!/bin/bash
# Script to create a clean distribution package of spacecage-undistort

# Set output filename
OUTPUT="spacecage-undistort-distribution.tar.gz"
ORIGINAL_DIR=$(pwd)

echo "Creating distribution package..."

# Create temporary directory structure
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="$TEMP_DIR/spacecage-undistort"
mkdir -p "$PACKAGE_DIR"

# Copy essential files
echo "Copying essential files..."

# Documentation
cp README.md "$PACKAGE_DIR/"
cp USAGE.md "$PACKAGE_DIR/"
cp CAMERA_CALIBRATION_GUIDE.md "$PACKAGE_DIR/"
cp PROJECT_STRUCTURE.md "$PACKAGE_DIR/"

# Package configuration
cp pyproject.toml "$PACKAGE_DIR/"

# Example code
cp example_usage.py "$PACKAGE_DIR/"

# Git configuration (optional but helpful)
cp .gitignore "$PACKAGE_DIR/"

# Source code directory
cp -r src "$PACKAGE_DIR/"

# Optional: Include one example ROI file (but not the video)
cp 269_18-02-15_1389_Feeder_1.1.rois.yml "$PACKAGE_DIR/example.rois.yml"

# Create the archive
echo "Creating archive..."
cd "$TEMP_DIR"
tar -czf "$OUTPUT" spacecage-undistort/

# Move to original directory
mv "$OUTPUT" "$ORIGINAL_DIR/"

# Cleanup
rm -rf "$TEMP_DIR"

cd "$ORIGINAL_DIR"

echo "✓ Distribution package created: $OUTPUT"
echo ""
echo "Contents:"
tar -tzf "$OUTPUT" | head -20
echo ""
echo "Package size: $(du -h $OUTPUT | cut -f1)"
