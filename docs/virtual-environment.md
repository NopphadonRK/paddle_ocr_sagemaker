# 🐍 Virtual Environment Setup

คู่มือการตั้งค่า Python Virtual Environment สำหรับโปรเจค PaddleOCR Recognition

## 🎯 วัตถุประสงค์

สร้าง isolated Python environment เพื่อหลีกเลี่ยงปัญหา dependency conflicts และจัดการ packages อย่างเป็นระบบ

## 🚀 การตั้งค่า Virtual Environment

### 1. สร้าง Virtual Environment ที่ root ของโปรเจค

```bash
# เข้าไปยังโฟลเดอร์ root ของโปรเจค
cd paddle_ocr_sagemaker

# สร้าง virtual environment ชื่อ 'venv'
python -m venv venv

# หรือใช้ Python 3 explicitly
python3 -m venv venv
```

### 2. เปิดใช้งาน Virtual Environment

#### บน Linux/macOS:
```bash
source venv/bin/activate
```

#### บน Windows:
```bash
# Command Prompt
venv\Scripts\activate

# PowerShell
venv\Scripts\Activate.ps1
```

#### ตรวจสอบว่าเปิดใช้งานแล้ว:
```bash
# ดู prompt ที่ขึ้นต้นด้วย (venv)
(venv) $ which python
# ควรแสดง path ใน venv directory

(venv) $ python --version
# ตรวจสอบ Python version
```

### 3. ติดตั้ง Dependencies

```bash
# อัปเกรด pip ให้เป็นเวอร์ชันล่าสุด
(venv) $ pip install --upgrade pip

# ติดตั้ง dependencies ทั้งหมดจาก requirements.txt
(venv) $ pip install -r requirements.txt

# ตรวจสอบ packages ที่ติดตั้ง
(venv) $ pip list
```

### 4. ปิดการใช้งาน Virtual Environment

```bash
# เมื่อทำงานเสร็จแล้ว
(venv) $ deactivate
```

## 📁 โครงสร้างโปรเจคหลังติดตั้ง

```
paddle_ocr_sagemaker/
├── venv/                           # Virtual environment (ไม่ commit ใน git)
│   ├── bin/                        # Linux/macOS executables
│   ├── Scripts/                    # Windows executables
│   ├── lib/                        # Installed packages
│   └── pyvenv.cfg                  # Configuration
├── requirements.txt                # Dependencies สำหรับทั้งโปรเจค
├── .gitignore                      # ระบุให้ ignore venv/
├── data_preparation/               # ใช้ venv เดียวกัน
├── paddle_ocr_recognition_training.ipynb
└── docs/
```

## 🔧 การใช้งานใน Subprojects

### สำหรับ data_preparation:
```bash
# เปิดใช้งาน venv ที่ root
source venv/bin/activate

# เข้าไปใน data_preparation
cd data_preparation

# รัน scripts (จะใช้ dependencies จาก root requirements.txt)
(venv) $ python scripts/convert_data.py
(venv) $ python scripts/upload_to_s3.py --bucket my-bucket
```

### สำหรับ Jupyter Notebook:
```bash
# เปิดใช้งาน venv
source venv/bin/activate

# ติดตั้ง kernel สำหรับ Jupyter
(venv) $ python -m ipykernel install --user --name paddle_ocr --display-name "PaddleOCR Recognition"

# เปิด Jupyter Notebook
(venv) $ jupyter notebook

# เลือก kernel "PaddleOCR Recognition" ในตอนรัน notebook
```

## 📋 สคริปต์อำนวยความสะดวก

### setup.sh (Linux/macOS):
```bash
#!/bin/bash
# สร้าง setup script สำหรับ Linux/macOS

echo "🚀 Setting up PaddleOCR Recognition Environment..."

# สร้าง virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# เปิดใช้งาน
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# อัปเกรด pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# ติดตั้ง dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# ติดตั้ง Jupyter kernel
echo "📓 Setting up Jupyter kernel..."
python -m ipykernel install --user --name paddle_ocr --display-name "PaddleOCR Recognition"

echo "✅ Setup completed!"
echo "💡 To activate environment: source venv/bin/activate"
echo "🚀 To start notebook: jupyter notebook"
```

### setup.bat (Windows):
```batch
@echo off
echo 🚀 Setting up PaddleOCR Recognition Environment...

REM สร้าง virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM เปิดใช้งาน
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM อัปเกรด pip
echo ⬆️  Upgrading pip...
pip install --upgrade pip

REM ติดตั้ง dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM ติดตั้ง Jupyter kernel
echo 📓 Setting up Jupyter kernel...
python -m ipykernel install --user --name paddle_ocr --display-name "PaddleOCR Recognition"

echo ✅ Setup completed!
echo 💡 To activate environment: venv\Scripts\activate
echo 🚀 To start notebook: jupyter notebook
pause
```

## 🔄 การจัดการ Dependencies

### เพิ่ม Package ใหม่:
```bash
# เปิดใช้งาน venv
source venv/bin/activate

# ติดตั้ง package ใหม่
(venv) $ pip install new-package==1.0.0

# อัปเดต requirements.txt
(venv) $ pip freeze > requirements.txt
```

### อัปเดต Dependencies:
```bash
# เปิดใช้งาน venv
source venv/bin/activate

# อัปเดต packages
(venv) $ pip install --upgrade -r requirements.txt

# หรืออัปเดตทีละตัว
(venv) $ pip install --upgrade package-name
```

## 🧹 การล้างข้อมูล

### ลบ Virtual Environment:
```bash
# ปิดการใช้งาน venv ก่อน
deactivate

# ลบโฟลเดอร์ venv
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# สร้างใหม่
python -m venv venv
```

### ล้างข้อมูล pip cache:
```bash
(venv) $ pip cache purge
```

## ⚠️ ข้อควรระวัง

1. **ไม่ commit โฟลเดอร์ venv ใน git**
   - ใส่ `venv/` ใน `.gitignore`

2. **ใช้ venv เดียวสำหรับทั้งโปรเจค**
   - ไม่สร้าง venv แยกใน subprojects

3. **ระบุ Python version ให้ชัด**
   - ใช้ `python3 -m venv venv` ถ้ามี Python หลายเวอร์ชัน

4. **ตรวจสอบ activation ก่อนใช้งาน**
   - ดู prompt ที่ขึ้นต้นด้วย `(venv)`

## 🔗 Integration กับ SageMaker

### สำหรับ SageMaker Notebook Instance:
```bash
# ใน SageMaker terminal
cd /home/ec2-user/SageMaker/paddle_ocr_sagemaker

# สร้าง venv
python3 -m venv venv
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# สร้าง custom kernel
python -m ipykernel install --user --name paddle_ocr --display-name "PaddleOCR Recognition"
```

### การใช้งานใน Jupyter:
1. เปิด Jupyter Notebook
2. เลือก Kernel → Change Kernel → PaddleOCR Recognition
3. รัน code ตามปกติ

## 📞 การแก้ไขปัญหา

### venv สร้างไม่ได้:
```bash
# ติดตั้ง python3-venv (Ubuntu/Debian)
sudo apt-get install python3-venv

# หรือใช้ virtualenv
pip install virtualenv
virtualenv venv
```

### pip ติดตั้งไม่ได้:
```bash
# อัปเกรด pip
python -m pip install --upgrade pip

# หรือใช้ --user flag
pip install --user package-name
```

### Jupyter kernel หาไม่เจอ:
```bash
# ลิสต์ kernels ที่มี
jupyter kernelspec list

# ลบ kernel เก่า
jupyter kernelspec remove paddle_ocr

# สร้างใหม่
python -m ipykernel install --user --name paddle_ocr --display-name "PaddleOCR Recognition"
```
