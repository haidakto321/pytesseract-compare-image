# 📸 Image Comparison Tool

Smart image comparison tool for UI testing with focus detection and OCR text comparison. Automatically detects header regions and compares form content intelligently.

---

## 🎯 Features

✅ **Smart Header Detection** - Automatically excludes header regions  
✅ **OCR Text Comparison** - Detects text differences in forms  
✅ **Focus Detection** - Identifies focused UI elements  
✅ **Clean Reports** - Simple, actionable difference summaries  
✅ **HTML Reports** - Beautiful side-by-side comparison with zoom  
✅ **Keyboard Navigation** - Quick navigation with arrow keys  

---

## 📋 Requirements

### **System Requirements:**
- Windows 10/11 or Ubuntu 20.04+
- **Python 3.11 or 3.12** (recommended)
  - ⚠️ Python 3.14+ not supported yet (package compatibility issues)
  - ⚠️ Python 3.10 and older may have issues
- 2GB RAM minimum
- 500MB disk space

### **External Dependencies:**
- Tesseract OCR (for text recognition)

---

## 🚀 Installation Guide

Choose one of the following installation methods:

---

## Method 1: Online Installation (Internet Required)

### **Step 1: Install Python**

1. Download Python from: https://www.python.org/downloads/
2. Run installer
3. ✅ **IMPORTANT:** Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```bash
   python --version
   ```
   Should show: `Python 3.x.x`

---

### **Step 2: Install Tesseract OCR**

#### **For Windows:**

1. Download installer from:
   ```
   https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. Run `tesseract-ocr-w64-setup-5.x.x.exe`

3. During installation:
   - ✅ Select "Additional language data"
   - ✅ Check Japanese (jpn) if testing Japanese forms

4. Note installation path (usually `C:\Program Files\Tesseract-OCR`)

5. Add Tesseract to PATH:
   - Right-click "This PC" → Properties
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path"
   - Click "Edit" → "New"
   - Add: `C:\Program Files\Tesseract-OCR`
   - Click OK on all dialogs

6. Verify installation:
   ```bash
   tesseract --version
   ```

#### **For Ubuntu/WSL:**

```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-jpn  # For Japanese
```

---

### **Step 3: Install Python Libraries**

1. Open Command Prompt (Windows) or Terminal (Ubuntu)

2. Navigate to project folder:
   ```bash
   cd path\to\image-comparison-tool
   ```

3. Install required packages:
   ```bash
   pip install opencv-python numpy Pillow pytesseract python-docx
   ```

4. Verify installation:
   ```bash
   python -c "import cv2, numpy, PIL, pytesseract; print('All packages installed!')"
   ```

---

### **Step 4: Test the Tool**

```bash
python image_compare.py --help
```

Should show usage instructions. If it works, you're ready! 🎉

---

## Method 2: Offline Installation (No Internet Required)

Use this method to bundle all libraries with your project so other PCs don't need to download anything.

### **Step 1: Prepare Installation Package (One-time, on PC with internet)**

#### **1.1: Install Python** (if not already installed)
- Follow Method 1, Step 1

#### **1.2: Download Tesseract Installer**

Download and save to your project folder:
```
https://github.com/UB-Mannheim/tesseract/wiki
→ Download: tesseract-ocr-w64-setup-5.x.x.exe
→ Save to: installers/tesseract-installer.exe
```

#### **1.3: Download Python Packages**

Create `installers` folder in project:
```bash
mkdir installers
cd installers
```

Download all required packages:
```bash
pip download opencv-python numpy Pillow pytesseract python-docx -d python-packages
```

This downloads ~100MB of .whl files to `installers/python-packages/`

#### **1.4: Create Setup Script**

I'll provide this in the next file (setup.bat)

---

### **Step 2: Deploy to Other PCs**

#### **2.1: Copy Project Folder**

Copy entire project folder to the new PC:
```
image-comparison-tool/
├── image_compare.py
├── installers/
│   ├── tesseract-installer.exe
│   └── python-packages/
│       ├── opencv_python-4.x.x.whl
│       ├── numpy-1.x.x.whl
│       └── ... (other .whl files)
└── setup.bat  (provided below)
```

#### **2.2: Run Setup Script**

On the new PC:

1. Make sure Python is installed (Method 1, Step 1)
2. Double-click `setup.bat`
3. Follow prompts to install Tesseract
4. Script will install all Python packages offline

---

## 📁 Project Structure

```
image-comparison-tool/
├── image_compare.py          # Main comparison script ⭐
├── test_generator.py         # Test image generator (optional)
├── setup.bat                 # Windows setup script
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── installers/               # Offline installation files
│   ├── tesseract-installer.exe
│   └── python-packages/
│       └── *.whl files
└── docs/                     # Documentation
    ├── SIMPLE_CLEAN_APPROACH.md
    ├── NAVIGATION_BUG_FIX.md
    └── HYBRID_IMPLEMENTATION.md
```

---

## 🎯 Usage Guide

### **Basic Usage**

Compare two folders of images:

**Option 1 - Quick script (recommended):**
```bash
compare.bat folder1 folder2
```

**Option 2 - Direct Python:**
```bash
python image_compare.py folder1 folder2
```

**Examples:**
```bash
# Using compare.bat
compare.bat test_images\version1 test_images\version2
compare.bat baseline current

# Or direct Python
python image_compare.py test_images\version1 test_images\version2
```

---

### **Output**

The tool generates:

1. **Console output** - Real-time comparison results
2. **HTML report** - `comparison_report.html` 
3. **Image copies** - `report_images/version1/` and `report_images/version2/`

---

### **Reading Results**

#### **Console Output:**

```
============================================================
Processing form_different_checkbox.png...
  - Extracting text from first image...
  → Header cropped at 12% = 72px (fallback)
    Found 45 text boxes
  - Extracting text from second image...
  → Header cropped at 12% = 72px (fallback)
    Found 47 text boxes
  - Detecting focus elements...

✗ FAIL: form_different_checkbox.png
  Text Match: ✗
    - Form content differs in several fields
    - 💡 Click images to zoom and compare
  Focus Match: ✓

============================================================
SUMMARY
============================================================
Total compared: 15
Passed: 8
Failed: 7
```

---

#### **HTML Report:**

1. Open `comparison_report.html` in browser
2. Use filters: All / Passed / Failed
3. Search by image name
4. Click image names to expand details
5. Click images to zoom
6. Use arrow keys to navigate

**Keyboard Shortcuts:**
- **↑↓** - Navigate between comparison items
- **Click image** - Open zoom view
- **←→** - Switch between Version 1 and Version 2 (in zoom)
- **ESC** - Close zoom view

---

### **Understanding Messages**

| Message | Meaning | Action |
|---------|---------|--------|
| Form content has minor differences | One or two changes | Zoom to inspect |
| Form content differs in several fields | Multiple changes | Review carefully |
| Form content has significant differences | Many changes | Manual review |
| Major content differences detected | Structural changes | Full investigation |

---

## 🔧 Troubleshooting

### **Problem: "ERROR: Unknown compiler" or numpy fails to install**

**Cause:** You're using Python 3.14 which is too new. Packages don't have pre-built wheels yet and try to build from source (requires C++ compiler).

**Solution:**
1. Install Python 3.11 or 3.12 from: https://www.python.org/downloads/
2. Uninstall Python 3.14 if you don't need it
3. Reinstall packages: `python -m pip install -r requirements.txt`

See `PYTHON_VERSION_ISSUE.md` for full details.

---

### **Problem: "tesseract is not recognized"**

**Solution:**
1. Verify Tesseract is installed:
   ```bash
   tesseract --version
   ```
2. If not found, add to PATH (see Step 2 above)
3. Restart Command Prompt

---

### **Problem: "No module named 'cv2'"**

**Solution:**
```bash
pip install opencv-python
```

Or reinstall all packages:
```bash
pip install -r requirements.txt
```

---

### **Problem: "Header cropped at 12%" but should use dynamic detection**

**Explanation:**
- The tool tries dynamic header detection first
- If detection fails, it falls back to 12% crop
- This is normal and works fine for most cases

**If you want to adjust:**
Edit `image_compare.py`, line ~37:
```python
self.default_crop_percentage = 0.15  # Change from 0.12 to 0.15 for larger headers
```

---

### **Problem: Images in HTML report don't load**

**Solution:**
1. Make sure `comparison_report.html` is in the same folder as `report_images/`
2. Open HTML file from local disk (not network drive)
3. Some browsers block local file access - try different browser

---

### **Problem: OCR not detecting text correctly**

**Possible causes:**
1. Image resolution too low (need minimum 1000px width)
2. Text is part of image (not actual text)
3. Poor image quality or blur
4. Language not installed in Tesseract

**Solution:**
- Ensure images are high quality
- For Japanese text: Install Japanese language pack for Tesseract

---

### **Problem: Too many false positives**

**Solution:**
- Images might have minor rendering differences
- Consider if pixel-perfect comparison is needed
- Use visual inspection for edge cases

---

## 📚 Advanced Configuration

### **Adjust Similarity Threshold**

Edit `image_compare.py`, line ~1038:
```python
comparator = SmartImageComparator(
    ignore_case=True,
    similarity_threshold=1.0,  # 1.0 = exact match, 0.95 = 95% similar
    default_crop_percentage=0.12
)
```

---

### **Adjust Header Crop Percentage**

```python
comparator = SmartImageComparator(
    default_crop_percentage=0.15  # Crop top 15% instead of 12%
)
```

---

### **Disable Header Cropping**

Edit `smart_crop_header()` function to return full image:
```python
def smart_crop_header(self, img):
    return img, 0  # No cropping
```

---

## 🎓 How It Works

### **1. Image Loading**
- Loads both images from specified folders
- Images must have matching filenames

### **2. Header Detection (Hybrid Approach)**
- Tries dynamic color detection first
- Falls back to 12% percentage crop if detection fails
- Physically removes header from comparison

### **3. Text Extraction (OCR)**
- Uses Tesseract OCR to extract text
- Only analyzes text below header region
- Filters out low-confidence OCR results

### **4. Text Comparison**
- Compares text content from both images
- Calculates similarity percentage
- Generates clean summary message

### **5. Focus Detection**
- Detects text cursors
- Detects rounded borders (focus rings)
- Detects bold text
- Compares focus positions

### **6. Report Generation**
- Creates HTML report with side-by-side comparison
- Copies images to report folder
- Generates clean, actionable messages

---

## 📝 Tips & Best Practices

### **For Best Results:**

✅ **Image Quality**
- Use high-resolution screenshots (minimum 1000px width)
- Ensure text is clear and readable
- Avoid compression artifacts

✅ **Consistent Capture**
- Take screenshots at same zoom level
- Same window size
- Same browser/app state

✅ **File Naming**
- Use descriptive names: `form_login.png`, `form_register.png`
- Keep names consistent between version folders
- Avoid special characters

✅ **Folder Organization**
```
test_images/
├── version1/
│   ├── form_login.png
│   ├── form_register.png
│   └── form_profile.png
└── version2/
    ├── form_login.png
    ├── form_register.png
    └── form_profile.png
```

---

## 🆘 Support

### **Getting Help**

1. Check troubleshooting section above
2. Review documentation in `docs/` folder
3. Verify all dependencies are installed
4. Test with sample images first

### **Common Issues**

- 95% of issues are missing Tesseract or incorrect PATH
- Make sure to restart Command Prompt after installing Tesseract
- Try the test command: `tesseract --version`

---

## 📜 License

This tool is provided as-is for internal testing purposes.

---

## 🎉 Quick Start Summary

### **For First-Time Setup:**

```bash
# 1. Install Python (with PATH)
# 2. Install Tesseract OCR
# 3. Install Python packages
pip install opencv-python numpy Pillow pytesseract python-docx

# 4. Run comparison
python image_compare.py folder1 folder2

# 5. Open comparison_report.html
```

### **For Daily Use:**

```bash
python image_compare.py test_images/version1 test_images/version2
```

That's it! 🚀

---

## 📊 Version History

**v1.0** - Initial release
- Basic image comparison
- OCR text detection
- Focus element detection

**v2.0** - Smart header detection
- Hybrid header cropping
- Dynamic color detection
- Percentage fallback

**v3.0** - Simple clean approach
- Removed complex field detection
- Clean summary messages
- Improved user experience
- Fixed navigation bugs

---

**Last Updated:** January 2026
