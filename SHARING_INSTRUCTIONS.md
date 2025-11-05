# How to Share This Tool

## TL;DR - Quick Commands

### Create Distribution Package
```bash
./create_distribution.sh
```
This creates `spacecage-undistort-distribution.tar.gz` (only **21 KB**!)

### Share the Package
- Email it (tiny file, easy to send)
- Upload to shared drive (Google Drive, Dropbox, etc.)
- Copy to USB drive
- Or share the entire directory if on same network

---

## What's the Difference?

Your directory contains:
- ✅ Essential tool files (~21 KB compressed)
- ❌ Your personal videos (~30 MB)
- ❌ Jupyter notebooks (~4 MB, development only)
- ❌ Other documents and images

**The distribution package includes ONLY what others need to use the tool.**

---

## Method 1: Distribution Package (Recommended)

### Step 1: Create the Package
```bash
cd /root/vast/leo/2025-09-19-NASA-SpaceCage
./create_distribution.sh
```

Output: `spacecage-undistort-distribution.tar.gz` (21 KB)

### Step 2: Share It
Email, shared drive, USB, etc.

### Step 3: Recipient Usage
```bash
# Extract
tar -xzf spacecage-undistort-distribution.tar.gz
cd spacecage-undistort

# Install
pip install -e .

# Use with their videos
spacecage-undistort their_video.mp4 -o output.mp4
```

**What's Included:**
- ✅ All source code (src/)
- ✅ Documentation (README, USAGE, guides)
- ✅ Package config (pyproject.toml)
- ✅ Example ROI file (for reference)
- ✅ .gitignore (if they use git)

**What's NOT Included:**
- ❌ Your videos (they use their own)
- ❌ Jupyter notebooks (not needed for usage)
- ❌ Images (not needed for functionality)
- ❌ Development files

---

## Method 2: Share Entire Directory

If you're on the same network or sharing via shared drive:

```bash
# From parent directory
cd /root/vast/leo
tar -czf spacecage-full.tar.gz 2025-09-19-NASA-SpaceCage/
```

This includes everything (notebooks, videos, etc.) - useful if they want to see your development work.

**Size:** ~30 MB (vs 21 KB for distribution package)

---

## Method 3: GitHub (For Public/Team Sharing)

### Setup (one-time)
```bash
cd /root/vast/leo/2025-09-19-NASA-SpaceCage

# Initialize git
git init
git add .
git commit -m "Initial commit: SpaceCage undistortion tool"

# Create repo on GitHub (via website), then:
git remote add origin https://github.com/YOUR_USERNAME/spacecage-undistort.git
git branch -M main
git push -u origin main
```

### Recipients Clone
```bash
git clone https://github.com/YOUR_USERNAME/spacecage-undistort.git
cd spacecage-undistort
pip install -e .
```

**Benefits:**
- Easy updates (git pull)
- Issue tracking
- Collaboration
- Version control

**Note:** Videos won't be pushed (too large, in .gitignore)

---

## Method 4: Simple File List Command

If you just want specific files without the script:

```bash
tar -czf spacecage-tool.tar.gz \
  README.md \
  USAGE.md \
  CAMERA_CALIBRATION_GUIDE.md \
  PROJECT_STRUCTURE.md \
  DISTRIBUTION.md \
  SHARING_INSTRUCTIONS.md \
  pyproject.toml \
  example_usage.py \
  .gitignore \
  src/
```

---

## Comparison Table

| Method | Size | Speed | Use Case |
|--------|------|-------|----------|
| **Distribution Script** | 21 KB | Fast | Share with others who just need the tool |
| **Full Directory** | 30 MB | Slow | Share development work, includes notebooks |
| **GitHub** | 21 KB* | Fast | Team collaboration, public sharing |
| **Specific Files** | 21 KB | Fast | Custom selection of files |

*GitHub doesn't store large files (videos excluded by .gitignore)

---

## What Recipients Need

After receiving the package, they need:

1. **Python 3.9+** installed
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **pip** (usually comes with Python)
   ```bash
   pip --version
   ```

3. **labelroi** to create ROI files
   ```bash
   pip install labelroi
   ```

4. **Their own videos** to process

---

## Common Questions

### Q: Can they use my ROI files?
**A:** Only if their camera is in the EXACT same position/angle as yours. Otherwise, they must create their own using `labelroi`.

### Q: Can they use my calibration files?
**A:** Same as above - only if camera hasn't moved. See [CAMERA_CALIBRATION_GUIDE.md](CAMERA_CALIBRATION_GUIDE.md) for details.

### Q: Do I need to include the Jupyter notebooks?
**A:** No, they're for development/reference only. The tool works without them.

### Q: What if they don't have labelroi?
**A:** They need to install it: `pip install labelroi`. Link in documentation: https://github.com/talmolab/labelroi

### Q: Can they run this on Windows?
**A:** Yes! Python and all dependencies work on Windows, macOS, and Linux.

---

## Verification Checklist

Before sharing, verify:

- [ ] Package created successfully
  ```bash
  ls -lh spacecage-undistort-distribution.tar.gz
  ```

- [ ] Contains all essential files
  ```bash
  tar -tzf spacecage-undistort-distribution.tar.gz
  ```

- [ ] Size is reasonable (~21 KB)
  ```bash
  du -h spacecage-undistort-distribution.tar.gz
  ```

- [ ] Test extraction works
  ```bash
  mkdir test && cd test
  tar -xzf ../spacecage-undistort-distribution.tar.gz
  cd spacecage-undistort
  pip install -e .
  spacecage-undistort --help
  ```

---

## Quick Reference

### Create Package
```bash
./create_distribution.sh
```

### Check Package
```bash
tar -tzf spacecage-undistort-distribution.tar.gz
```

### Share Package
- Email: Attach `spacecage-undistort-distribution.tar.gz`
- Drive: Upload to Google Drive/Dropbox, share link
- USB: Copy file to USB drive

### Recipient Installation
```bash
tar -xzf spacecage-undistort-distribution.tar.gz
cd spacecage-undistort
pip install -e .
spacecage-undistort --help
```

---

## Support

Include this in your sharing message:

> **Installation:**
> 1. Extract: `tar -xzf spacecage-undistort-distribution.tar.gz`
> 2. Navigate: `cd spacecage-undistort`
> 3. Install: `pip install -e .`
>
> **Quick Start:**
> 1. Label your video: `labelroi your_video.mp4`
> 2. Undistort: `spacecage-undistort your_video.mp4 -o output.mp4`
>
> **Documentation:**
> - README.md - Full documentation
> - USAGE.md - Quick start guide
> - CAMERA_CALIBRATION_GUIDE.md - When to reuse calibration
>
> **Questions?** See the documentation or contact [your contact info]
