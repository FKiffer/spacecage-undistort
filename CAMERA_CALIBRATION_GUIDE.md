# Camera Calibration Guide

## Understanding Camera Intrinsic Parameters

Camera intrinsic parameters describe the **internal properties** of a camera and lens combination. Think of them as the camera's "fingerprint" for how it transforms the 3D world into a 2D image.

### What Are Intrinsic Parameters?

The intrinsic parameters include:

1. **Focal Length (fx, fy)**: How much the camera "zooms" in the x and y directions
2. **Principal Point (cx, cy)**: The center point of the image sensor
3. **Distortion Coefficients (k1, k2, p1, p2, k3)**: How the lens warps the image (fisheye effect)

These parameters are stored in the **camera matrix K** and **distortion coefficients**.

### Camera Matrix K

```
K = [[fx,  0, cx],
     [ 0, fy, cy],
     [ 0,  0,  1]]
```

Example from calibration:
```
K = [[1227.66,     0, 320.0],
     [    0, 1227.66, 240.0],
     [    0,       0,   1.0]]
```

- `fx = fy = 1227.66`: Focal length (same in both directions due to aspect ratio constraint)
- `cx = 320, cy = 240`: Principal point at image center (for 640×480 image)

### Distortion Coefficients

```
dist = [k1, k2, p1, p2, k3]
```

Example:
```
dist = [-4.12, 9.92, -0.01, 0.02, 0.00]
```

- `k1, k2, k3`: **Radial distortion** (barrel/pinhcushion distortion, fisheye effect)
- `p1, p2`: **Tangential distortion** (lens not perfectly centered)

## When Can You Reuse Calibration Parameters?

### ✅ Safe to Reuse Calibration When:

1. **Same Camera**: Using the exact same physical camera
2. **Same Lens Settings**: No change in:
   - Zoom level
   - Focus ring position
   - Aperture (if adjustable)
3. **Same Mount**: Camera securely mounted, hasn't been removed/reattached
4. **Same Position**: Camera hasn't moved or rotated
5. **Same Angle**: Camera points in the same direction

**Example scenario:**
```bash
# Day 1: Record 5 videos with camera in position A
labelroi video1.mp4  # Label once
spacecage-undistort video1.mp4 --save-calibration camera_posA.yml

# Day 2: Record more videos, camera still in position A
spacecage-undistort video2.mp4 --calibration camera_posA.yml  # Reuse!
spacecage-undistort video3.mp4 --calibration camera_posA.yml  # Reuse!
```

### ❌ Must Recalibrate When:

1. **Camera Moved**: Even slightly
2. **Camera Rotated**: Any change in angle
3. **Zoom Changed**: Focal length is different
4. **Focus Changed**: Especially for close-up work
5. **Different Camera**: Using a different physical camera
6. **Lens Swapped**: Changed to a different lens

**Example scenario:**
```bash
# Day 1: Camera mounted on top of cage
labelroi video1.mp4
spacecage-undistort video1.mp4 --save-calibration camera_top.yml

# Day 2: Camera moved to side of cage - MUST recalibrate!
labelroi video2.mp4  # New labels needed!
spacecage-undistort video2.mp4 --save-calibration camera_side.yml  # New calibration!

# Later: Another video from same side position
spacecage-undistort video3.mp4 --calibration camera_side.yml  # Can reuse side calibration
```

## Why Do Camera Position Changes Matter?

**Important distinction:**

1. **Intrinsic parameters** (K and dist): Properties of the camera/lens
   - These are the same regardless of where you point the camera
   - Describes how the lens bends light

2. **Extrinsic parameters** (rotation and translation): Where the camera is in space
   - This changes when you move the camera
   - Describes the camera's viewpoint

### The Catch: ROI Labels Encode Position!

When you label ROIs, you're creating a correspondence between:
- **3D model grid** (physical 1cm squares in the world)
- **2D image coordinates** (pixels in the video)

This correspondence depends on:
- The grid's position relative to the camera ← **This changes!**
- How the camera projects 3D to 2D ← This is what we calibrate

**Therefore:**
- If camera moves → Grid appears different in image → Need new ROI labels
- New ROI labels → Can recalculate intrinsic parameters (or reuse if camera hardware didn't change)

## Best Practices

### Organizing Multiple Camera Setups

```
calibrations/
├── camera1_top_view.yml      # Camera 1, mounted on top
├── camera1_side_view.yml     # Camera 1, mounted on side
├── camera2_top_view.yml      # Camera 2, mounted on top
└── README.txt                # Notes about each setup
```

### Naming Convention

Use descriptive names that capture the setup:
```bash
# Include: camera ID, position, date
spacecage-undistort video.mp4 --save-calibration cam1_top_20250128.yml
spacecage-undistort video.mp4 --save-calibration cam2_side_20250128.yml
```

### Calibration Quality Metrics

After calibration, check the RMS error:

```
RMS error: 3.71 pixels  ← Excellent!
RMS error: 8.50 pixels  ← Good
RMS error: 15.2 pixels  ← Check ROI labels for errors
```

**What affects calibration quality:**
1. **Number of segments**: More is better (minimum 3, recommended 10+)
2. **ROI labeling accuracy**: Precise corner placement matters
3. **Grid visibility**: Clear, well-lit grid squares
4. **Segment distribution**: Spread across the entire visible area

## Troubleshooting

### "I have 10 videos from the same camera setup"

✅ **Best approach:**
```bash
# Label the first video
labelroi video1.mp4

# Calibrate and save
spacecage-undistort video1.mp4 -o out1.mp4 --save-calibration my_setup.yml

# Reuse for remaining videos
spacecage-undistort video2.mp4 -o out2.mp4 --calibration my_setup.yml
spacecage-undistort video3.mp4 -o out3.mp4 --calibration my_setup.yml
# ... and so on
```

### "Camera moved between recording sessions"

❌ **Don't do this:**
```bash
spacecage-undistort new_video.mp4 --calibration old_calibration.yml  # Wrong!
```

✅ **Do this:**
```bash
# Create new ROI labels for new camera position
labelroi new_video.mp4

# Calibrate with new position
spacecage-undistort new_video.mp4 -o output.mp4 --save-calibration new_position.yml
```

### "Same camera, slightly different angle"

Even a small rotation requires new ROI labels, but you might get reasonable results reusing the intrinsic parameters if the camera hardware truly hasn't changed. However, for best accuracy, always recalibrate with new ROI labels.

## Technical Deep Dive

### What Happens During Calibration?

1. **Load ROIs**: Read labeled grid squares from video
2. **Create 3D model**: Generate ideal 3D grid (1cm squares at Z=0)
3. **Match correspondences**: Find which 3D points map to which 2D pixels
4. **Solve for K and dist**: Use OpenCV's `calibrateCamera` to estimate parameters
5. **Compute undistortion maps**: Create lookup tables for fast remapping

### Why We Use Grid Squares

Grid squares provide:
- **Known geometry**: We know they're exactly 1cm × 1cm
- **Multiple points**: Each square gives 4 corner correspondences
- **Distributed coverage**: Squares across the image constrain different parts of the distortion model

This is similar to classic checkerboard calibration, but adapted for the NASA SpaceCage setup.

## Summary

| Scenario | Action |
|----------|--------|
| Same camera, same position, new recording | ✅ Reuse calibration |
| Same camera, moved to new position | ❌ New ROI labels + recalibrate |
| Same camera, rotated/tilted | ❌ New ROI labels + recalibrate |
| Different camera, any position | ❌ New ROI labels + recalibrate |
| Zoom/focus changed | ❌ New ROI labels + recalibrate |

**Key insight:** Camera position changes require new ROI labels, which effectively means recalibration (though you could theoretically reuse intrinsic parameters with new extrinsics, the tool recalculates everything for simplicity and accuracy).
