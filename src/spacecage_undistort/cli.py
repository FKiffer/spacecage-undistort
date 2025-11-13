"""Command-line interface for SpaceCage video undistortion."""

import argparse
import sys
from pathlib import Path
from .undistort import UndistortionPipeline
from .coordinates import transform_slp_coordinates, batch_transform_slp_files


def main_video():
    """Main function for video undistortion."""
    parser = argparse.ArgumentParser(
        description="NASA SpaceCage Video Undistortion Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calibrate and undistort a video (ROI file auto-detected)
  spacecage-undistort video.mp4 -o undistorted.mp4

  # Save calibration for reuse
  spacecage-undistort video.mp4 -o undistorted.mp4 --save-calibration calib.yml

  # Use existing calibration
  spacecage-undistort video2.mp4 -o undistorted2.mp4 --calibration calib.yml

  # Only perform calibration without undistorting
  spacecage-undistort video.mp4 --calibrate-only --save-calibration calib.yml

  # Specify ROI file explicitly
  spacecage-undistort video.mp4 -o output.mp4 --rois custom_rois.yml
        """
    )

    parser.add_argument(
        'video',
        type=str,
        help='Input video file path'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output undistorted video path (default: <input>_undistorted.mp4)'
    )

    parser.add_argument(
        '--rois',
        type=str,
        default=None,
        help='ROI YAML file path (default: auto-detect from video path)'
    )

    parser.add_argument(
        '--calibration',
        type=str,
        default=None,
        help='Load calibration from this file instead of calibrating'
    )

    parser.add_argument(
        '--save-calibration',
        type=str,
        default=None,
        help='Save calibration parameters to this file for reuse'
    )

    parser.add_argument(
        '--calibrate-only',
        action='store_true',
        help='Only perform calibration, do not undistort video'
    )

    parser.add_argument(
        '--side-length',
        type=float,
        default=0.01,
        help='Physical side length of grid squares in meters (default: 0.01 = 1cm)'
    )

    parser.add_argument(
        '--crf',
        type=int,
        default=25,
        help='Constant Rate Factor for video encoding (default: 25, lower = higher quality, range: 0-51)'
    )

    args = parser.parse_args()

    # Validate inputs
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output is None and not args.calibrate_only:
        output_path = video_path.parent / f"{video_path.stem}_undistorted.mp4"
    else:
        output_path = args.output

    # Initialize pipeline
    try:
        pipeline = UndistortionPipeline(
            video_path=str(video_path),
            roi_path=args.rois,
            calibration_path=args.calibration
        )

        # Perform calibration if needed
        if args.calibration is None:
            print("=" * 60)
            print("CALIBRATION")
            print("=" * 60)
            calibration_result = pipeline.calibrate(
                save_calibration_path=args.save_calibration,
                side_length_m=args.side_length
            )
            print()
            print("Calibration Summary:")
            print(f"  RMS Error: {calibration_result['rms_error']:.4f} pixels")
            print(f"  Segments Used: {calibration_result['num_segments']}")
            print()
        else:
            pipeline.load_calibration_file(args.calibration)
            print()

        # Undistort video if requested
        if not args.calibrate_only:
            print("=" * 60)
            print("VIDEO UNDISTORTION")
            print("=" * 60)
            pipeline.undistort_video(
                output_path=str(output_path),
                use_existing_calibration=True,
                crf=args.crf
            )
            print()
            print("=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            print(f"Undistorted video: {output_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print()
        print("To create ROI labels, use labelroi from Talmo's lab:")
        print("https://github.com/talmolab/labelroi")
        print()
        print("Example:")
        print(f"  labelroi {video_path}")
        sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main_coordinates():
    """Main function for coordinate transformation."""
    parser = argparse.ArgumentParser(
        description="Transform SLEAP tracking coordinates to match undistorted videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transform a single SLEAP file
  spacecage-transform-coords labels.slp -o labels_undistorted.slp --calibration calib.yml

  # Batch transform multiple files
  spacecage-transform-coords labels1.slp labels2.slp -o output_dir/ --calibration calib.yml

  # Specify custom video path mapping
  spacecage-transform-coords labels.slp -o output.slp --calibration calib.yml \\
      --video-suffix _undistorted_v2
        """
    )

    parser.add_argument(
        'slp_files',
        type=str,
        nargs='+',
        help='Input SLEAP .slp file(s)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='Output path (file for single input, directory for batch)'
    )

    parser.add_argument(
        '--calibration',
        type=str,
        required=True,
        help='Path to calibration YAML file from spacecage-undistort'
    )

    parser.add_argument(
        '--video-suffix',
        type=str,
        default='_undistorted',
        help='Suffix to add to video filenames (default: _undistorted)'
    )

    args = parser.parse_args()

    # Validate inputs
    for slp_file in args.slp_files:
        if not Path(slp_file).exists():
            print(f"Error: SLEAP file not found: {slp_file}", file=sys.stderr)
            sys.exit(1)

    calib_path = Path(args.calibration)
    if not calib_path.exists():
        print(f"Error: Calibration file not found: {calib_path}", file=sys.stderr)
        sys.exit(1)

    try:
        # Single file or batch mode?
        if len(args.slp_files) == 1:
            # Single file mode
            slp_input = args.slp_files[0]
            slp_output = args.output

            print("=" * 60)
            print("COORDINATE TRANSFORMATION")
            print("=" * 60)
            print()

            transform_slp_coordinates(
                slp_input,
                slp_output,
                str(calib_path),
                undistorted_video_suffix=args.video_suffix
            )

            print()
            print("=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            print(f"Transformed coordinates: {slp_output}")

        else:
            # Batch mode
            output_dir = Path(args.output)
            if output_dir.suffix == '.slp':
                print("Error: For multiple input files, output must be a directory", file=sys.stderr)
                sys.exit(1)

            print("=" * 60)
            print("BATCH COORDINATE TRANSFORMATION")
            print("=" * 60)
            print()

            batch_transform_slp_files(
                args.slp_files,
                str(calib_path),
                str(output_dir),
                output_suffix='_undistorted'
            )

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point - delegates to video or coordinate transformation."""
    # Check if we're being called as the coordinate transformer
    import sys
    if 'transform-coords' in sys.argv[0] or 'transform_coords' in sys.argv[0]:
        main_coordinates()
    else:
        main_video()


if __name__ == '__main__':
    main()
