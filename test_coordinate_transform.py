"""
Simple test for coordinate transformation functionality.

This script tests the undistort_points function with synthetic data.
"""

import numpy as np
import cv2
from spacecage_undistort.coordinates import undistort_points


def test_undistort_points_basic():
    """Test basic coordinate undistortion with synthetic calibration."""
    print("Test 1: Basic coordinate undistortion")
    print("-" * 60)

    # Create synthetic camera calibration (typical values)
    image_size = (640, 480)
    w, h = image_size

    # Camera matrix (simple centered camera)
    K = np.array([
        [500, 0, w/2],
        [0, 500, h/2],
        [0, 0, 1]
    ], dtype=np.float64)

    # Distortion coefficients (moderate barrel distortion)
    dist = np.array([-0.3, 0.1, 0, 0, 0], dtype=np.float64)

    # New camera matrix (same as K for this test)
    newK = K.copy()

    # Test points (grid of points across the image)
    test_points = np.array([
        [w/2, h/2],      # Center
        [100, 100],       # Top-left
        [w-100, 100],     # Top-right
        [100, h-100],     # Bottom-left
        [w-100, h-100],   # Bottom-right
        [w/4, h/2],       # Left center
        [3*w/4, h/2],     # Right center
    ], dtype=np.float32)

    print(f"Image size: {w}x{h}")
    print(f"Camera matrix K:\n{K}")
    print(f"Distortion coefficients: {dist}")
    print()

    # Undistort the points
    undistorted = undistort_points(test_points, K, dist, newK)

    print("Original points -> Undistorted points:")
    for i, (orig, undist) in enumerate(zip(test_points, undistorted)):
        diff = np.linalg.norm(undist - orig)
        print(f"  {i}: [{orig[0]:6.1f}, {orig[1]:6.1f}] -> [{undist[0]:6.1f}, {undist[1]:6.1f}]  "
              f"(shift: {diff:.2f}px)")

    # Check that center point doesn't move much (should be minimal distortion at center)
    center_shift = np.linalg.norm(undistorted[0] - test_points[0])
    print(f"\nCenter point shift: {center_shift:.2f}px (should be small)")

    # Check that edge points move more (more distortion at edges)
    edge_shifts = [np.linalg.norm(undistorted[i] - test_points[i]) for i in range(1, len(test_points))]
    avg_edge_shift = np.mean(edge_shifts)
    print(f"Average edge point shift: {avg_edge_shift:.2f}px (should be larger than center)")

    print("\nTest 1: PASSED ✓" if avg_edge_shift > center_shift else "Test 1: FAILED ✗")
    print()


def test_undistort_points_with_nan():
    """Test that NaN values are preserved."""
    print("Test 2: NaN handling")
    print("-" * 60)

    # Simple calibration
    K = np.eye(3, dtype=np.float64) * 500
    K[2, 2] = 1
    dist = np.array([-0.1, 0.05, 0, 0, 0], dtype=np.float64)
    newK = K.copy()

    # Test points with some NaN values
    test_points = np.array([
        [100, 100],
        [200, 200],
        [np.nan, np.nan],  # Missing point
        [300, 300],
        [np.nan, 150],     # Partially missing
        [400, 400],
    ], dtype=np.float32)

    print("Points before undistortion:")
    for i, pt in enumerate(test_points):
        print(f"  {i}: [{pt[0]:6.1f}, {pt[1]:6.1f}]")

    # Undistort
    undistorted = undistort_points(test_points, K, dist, newK)

    print("\nPoints after undistortion:")
    for i, pt in enumerate(undistorted):
        print(f"  {i}: [{pt[0]:6.1f}, {pt[1]:6.1f}]")

    # Check that NaN values are still NaN
    nan_mask_before = np.isnan(test_points).any(axis=1)
    nan_mask_after = np.isnan(undistorted).any(axis=1)

    print(f"\nNaN points before: {nan_mask_before.sum()}")
    print(f"NaN points after: {nan_mask_after.sum()}")
    print(f"NaN preservation: {'PASSED ✓' if np.array_equal(nan_mask_before, nan_mask_after) else 'FAILED ✗'}")
    print()


def test_undistort_points_identity():
    """Test with no distortion (identity transformation)."""
    print("Test 3: Identity transformation (no distortion)")
    print("-" * 60)

    # Identity calibration (no distortion)
    K = np.eye(3, dtype=np.float64) * 500
    K[2, 2] = 1
    dist = np.zeros(5, dtype=np.float64)  # No distortion
    newK = K.copy()

    # Test points
    test_points = np.array([
        [100, 100],
        [200, 200],
        [300, 300],
    ], dtype=np.float32)

    print("With zero distortion, points should remain unchanged")

    # Undistort
    undistorted = undistort_points(test_points, K, dist, newK)

    # Check that points are (approximately) unchanged
    max_diff = np.max(np.abs(undistorted - test_points))

    print(f"Maximum point difference: {max_diff:.6f}px")
    print(f"Identity test: {'PASSED ✓' if max_diff < 0.01 else 'FAILED ✗'}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("COORDINATE TRANSFORMATION TESTS")
    print("=" * 60)
    print()

    test_undistort_points_basic()
    test_undistort_points_with_nan()
    test_undistort_points_identity()

    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
