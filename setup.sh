#!/bin/bash
# setup.sh - สคริปต์ตั้งค่าโปรเจค PaddleOCR Recognition Training

echo "🚀 Setting up PaddleOCR Recognition Environment..."

# ตรวจสอบ Python version
python_version=$(python3 --version 2>&1)
echo "🐍 Python version: $python_version"

# สร้าง virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        echo "💡 Try: sudo apt-get install python3-venv"
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# เปิดใช้งาน virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# ตรวจสอบว่า activation สำเร็จ
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# อัปเกรด pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# ติดตั้ง dependencies
echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install some dependencies"
    echo "💡 Check requirements.txt and try manual installation"
fi

# ติดตั้ง Jupyter kernel
echo "📓 Setting up Jupyter kernel..."
python -m ipykernel install --user --name paddle_ocr --display-name "PaddleOCR Recognition"

if [ $? -eq 0 ]; then
    echo "✅ Jupyter kernel installed"
else
    echo "⚠️  Jupyter kernel installation failed (optional)"
fi

# ตรวจสอบการติดตั้งหลัก packages
echo "🔍 Verifying key packages..."
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)" 2>/dev/null || echo "❌ OpenCV not installed"
python -c "import numpy; print('✅ NumPy:', numpy.__version__)" 2>/dev/null || echo "❌ NumPy not installed"
python -c "import PIL; print('✅ Pillow:', PIL.__version__)" 2>/dev/null || echo "❌ Pillow not installed"
python -c "import boto3; print('✅ Boto3:', boto3.__version__)" 2>/dev/null || echo "❌ Boto3 not installed"

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Start Jupyter: jupyter notebook"
echo "  3. Select kernel: 'PaddleOCR Recognition'"
echo "  4. Open: paddle_ocr_recognition_training.ipynb"
echo ""
echo "📂 Data preparation:"
echo "  cd data_preparation"
echo "  python scripts/create_demo_data.py  # สร้างข้อมูลทดสอบ"
echo "  python scripts/convert_data.py     # แปลงข้อมูลจริง"
echo ""
echo "💡 Troubleshooting: docs/virtual-environment.md"
