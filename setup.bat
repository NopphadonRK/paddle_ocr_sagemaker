@echo off
REM setup.bat - สคริปต์ตั้งค่าโปรเจค PaddleOCR Recognition Training สำหรับ Windows

echo 🚀 Setting up PaddleOCR Recognition Environment...

REM ตรวจสอบ Python version
python --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM สร้าง virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo ❌ Failed to create virtual environment
        echo 💡 Make sure Python and pip are installed properly
        pause
        exit /b 1
    )
) else (
    echo ✅ Virtual environment already exists
)

REM เปิดใช้งาน virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM อัปเกรด pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM ติดตั้ง dependencies
echo 📥 Installing dependencies from requirements.txt...
pip install -r requirements.txt

if %ERRORLEVEL% equ 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ Failed to install some dependencies
    echo 💡 Check requirements.txt and try manual installation
)

REM ติดตั้ง Jupyter kernel
echo 📓 Setting up Jupyter kernel...
python -m ipykernel install --user --name paddle_ocr --display-name "PaddleOCR Recognition"

if %ERRORLEVEL% equ 0 (
    echo ✅ Jupyter kernel installed
) else (
    echo ⚠️  Jupyter kernel installation failed (optional)
)

REM ตรวจสอบการติดตั้งหลัก packages
echo 🔍 Verifying key packages...
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)" 2>nul || echo ❌ OpenCV not installed
python -c "import numpy; print('✅ NumPy:', numpy.__version__)" 2>nul || echo ❌ NumPy not installed
python -c "import PIL; print('✅ Pillow:', PIL.__version__)" 2>nul || echo ❌ Pillow not installed
python -c "import boto3; print('✅ Boto3:', boto3.__version__)" 2>nul || echo ❌ Boto3 not installed

echo.
echo 🎉 Setup completed!
echo.
echo 📋 Next steps:
echo   1. Activate environment: venv\Scripts\activate
echo   2. Start Jupyter: jupyter notebook
echo   3. Select kernel: 'PaddleOCR Recognition'
echo   4. Open: paddle_ocr_recognition_training.ipynb
echo.
echo 📂 Data preparation:
echo   cd data_preparation
echo   python scripts\create_demo_data.py  # สร้างข้อมูลทดสอบ
echo   python scripts\convert_data.py     # แปลงข้อมูลจริง
echo.
echo 💡 Troubleshooting: docs\virtual-environment.md

pause
