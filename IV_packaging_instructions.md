# IV. Packaging CourseMate as Executable

## Overview
To make CourseMate run like other desktop software (clickable icon), we need to package the Python application into an executable file. This process is called "freezing" the application.

## Method: Using PyInstaller

PyInstaller converts Python programs into standalone executables that can run on Windows without requiring Python installation.

### Prerequisites
1. Python installed on your system
2. Install PyInstaller: `pip install pyinstaller`
3. All dependencies installed (customtkinter, etc.)

### Step-by-Step Instructions

#### 1. Prepare Your Environment
```bash
# Navigate to your project directory
cd "c:\Users\lehig\Documents\PHINMA UPANG BS Information Technology\01-01-ITE 260\CourseMate"

# Install required packages if not already installed
pip install customtkinter
```

#### 2. Create the Executable
```bash
# Basic command
pyinstaller --onefile --windowed coursemate.py

# Or with icon (if you have an .ico file)
pyinstaller --onefile --windowed --icon=assets/icons/app.ico coursemate.py
```

**Command Explanation:**
- `--onefile`: Creates a single executable file
- `--windowed`: Prevents console window from appearing
- `--icon`: Uses your app icon for the executable

#### 3. Locate the Executable
After running PyInstaller, find the executable in the `dist` folder:
- `dist/coursemate.exe`

#### 4. Test the Executable
- Double-click `coursemate.exe` to run
- It should work like any other Windows program
- No Python installation required on target machines

### Advanced Options

#### Including Data Files
If you want to include the data file and assets in the executable:
```bash
pyinstaller --onefile --windowed --add-data "Coursemate_data.json;." --add-data "assets;assets" coursemate.py
```

#### Creating an Installer (Optional)
For a more professional distribution, create an installer using tools like:
- **Inno Setup** (free)
- **NSIS** (free)
- **Advanced Installer** (paid)

### Distribution
1. Copy the `.exe` file to target computers
2. Users can place it on desktop or in Programs folder
3. Create shortcuts as needed

### Troubleshooting
- **Missing modules**: Install all dependencies before packaging
- **File not found**: Ensure all paths in code use relative paths or bundled resources
- **Large file size**: PyInstaller bundles everything, expect 20-50MB for GUI apps

### Alternative Methods
- **cx_Freeze**: Another freezing tool
- **Py2Exe**: Windows-specific
- **auto-py-to-exe**: GUI wrapper for PyInstaller

### For Your Group Presentation
- Show the packaging process
- Demonstrate the standalone executable
- Explain how it makes the app accessible to non-technical users
- Mention that the executable includes all necessary components

This packaging makes CourseMate behave like commercial software, ready for distribution and use by anyone with Windows.