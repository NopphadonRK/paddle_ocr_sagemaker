# GitHub Copilot Instructions สำหรับ PaddleOCR Text Recognition SageMaker Project

## 🎯 บริบทของโปรเจค

โปรเจคนี้เป็นระบบสำหรับเทรน PaddleOCR Text Recognition โมเดลเท่านั้น บน Amazon SageMaker โดยใช้:
- Official PaddleOCR Repository เป็นหลัก (เฉพาะส่วน Recognition)
- Amazon S3 สำหรับจัดเก็บข้อมูลและ model checkpoints
- GPU-enabled SageMaker instances
- Python 3.8/3.9 compatibility
- **เฉพาะ Text Recognition training (ไม่รวม Detection)**

## 📋 กฎการทำงานสำคัญ

### 🚨 ก่อนแก้ปัญหาใดๆ
**ให้อ่าน `docs/problem-log.md` เสมอก่อนเริ่มแก้ปัญหา**

### 📝 หลังแก้ปัญหา
**ทุกครั้งที่แก้ปัญหา (ไม่ว่าจะสำเร็จหรือไม่) ให้บันทึกใน `docs/problem-log.md`**

### 🔄 การอัปเดตโครงสร้างโปรเจค (สำคัญมาก!)
**ทุกครั้งที่มีการเพิ่ม ลบ แก้ไข สิ่งใดก็ตามที่มีผลกระทบต่อโครงสร้างโปรเจค โค้ด หรือสิ่งสำคัญอื่นๆ ให้ดำเนินการดังนี้:**

1. **อ่านและตรวจสอบไฟล์ทั้งหมดในโปรเจค** ที่อาจได้รับผลกระทบ
2. **อัปเดตไฟล์ทั้งหมดให้สอดคล้อง** กับการเปลี่ยนแปลงที่เกิดขึ้น
3. **ไฟล์ที่ต้องตรวจสอบและอัปเดตเสมอ:**
   - `README.md` - เอกสารหลัก
   - `requirements.txt` - dependencies
   - `setup.sh` และ `setup.bat` - scripts ตั้งค่า
   - `.gitignore` - ไฟล์ที่ไม่ commit
   - `docs/*.md` - เอกสารทั้งหมด
   - `.github/copilot-instructions.md` - คำแนะนำนี้
   - `data_preparation/README.md` และ `QUICKSTART.md`
   - ไฟล์ config และ scripts ต่างๆ
4. **ตรวจสอบ cross-references** ระหว่างไฟล์ให้ถูกต้อง
5. **ทดสอบการทำงาน** หลังการเปลี่ยนแปลง
6. **บันทึกการเปลี่ยนแปลง** ใน `docs/problem-log.md`

**ตัวอย่างกรณีที่ต้องอัปเดตทั้งโปรเจค:**
- เปลี่ยนชื่อ directory หรือ file
- เปลี่ยน virtual environment structure
- เพิ่ม/ลบ dependencies ใหม่
- แก้ไข configuration หรือ setup process
- เปลี่ยน file paths หรือ import statements
- เพิ่ม/ลบ scripts หรือ tools ใหม่

## 🛠️ แนวทางการเขียนโค้ด

### การจัดการ Virtual Environment
```python
# ใช้ virtual environment ที่ root ของโปรเจค
# ตรวจสอบว่าอยู่ใน venv ก่อนเริ่มงาน
import sys
if 'venv' not in sys.executable:
    print("⚠️ Please activate virtual environment: source venv/bin/activate")

# ติดตั้ง dependencies เพิ่มเติม (ถ้าจำเป็น)
!pip install new-package  # ใน Jupyter
# หรือ: pip install new-package  # ใน terminal
```

### การจัดการ Dependencies
```python
# ใช้ PaddlePaddle GPU version เสมอ
pip install paddlepaddle-gpu==2.5.2

# ตรวจสอบ GPU availability ก่อนเทรน
import paddle
assert paddle.is_compiled_with_cuda(), "GPU not available"
```

### การจัดการไฟล์กำหนดค่า
```python
# โหลดและแก้ไข .yml config files จาก PaddleOCR repo
with open(base_config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# อัปเดต S3 paths และพารามิเตอร์การเทรน
config['Train']['dataset']['data_dir'] = s3_data_path
config['Global']['save_model_dir'] = s3_model_path
```

### รูปแบบ Annotation ที่ถูกต้องสำหรับ Recognition
```
image_path\ttext_content
```
ตัวอย่าง:
```
images/word_001.jpg	สวัสดี
images/word_002.jpg	PaddleOCR
images/word_003.jpg	1234567890
```

## 🔧 Best Practices

### S3 Integration
- ใช้ boto3 สำหรับการจัดการ S3
- สร้าง functions สำหรับ upload/download แบบ reusable
- ตรวจสอบ S3 permissions ก่อนเริ่มงาน

### Error Handling
```python
try:
    # การดำเนินการหลัก
    result = train_model(config)
except Exception as e:
    # บันทึกข้อผิดพลาดใน problem-log.md
    log_error_to_file(str(e), "problem-log.md")
    raise
```

### Configuration Management
- ใช้ไฟล์ .yml จาก PaddleOCR official repo (configs/rec/) เป็นฐาน
- แก้ไขเฉพาะส่วนที่จำเป็น (S3 paths, epochs, learning rate, character dictionary)
- สำรองไฟล์ config เดิมก่อนแก้ไข
- ใช้ CRNN, SVTR หรือ PP-OCRv4 architecture สำหรับ Recognition

## 📁 โครงสร้างโค้ดที่แนะนำ

### Virtual Environment Structure
```
paddle_ocr_sagemaker/
├── venv/                        # Virtual environment สำหรับทั้งโปรเจค
├── requirements.txt             # Dependencies รวม
├── setup.sh / setup.bat         # สคริปต์ตั้งค่า
├── data_preparation/            # ใช้ venv เดียวกัน
│   └── scripts/                 # Python scripts ใช้ venv หลัก
└── notebook.ipynb               # ใช้ custom kernel จาก venv
```

### Notebook Structure
1. Virtual Environment & GPU Check
2. Repository Cloning & Dependencies
3. S3 Configuration & Data Management
4. Annotation Validation
5. Configuration File Preparation
6. Training Execution
7. Checkpoint Management
8. Progress Monitoring

### Function Naming Convention
```python
# การจัดการข้อมูล Recognition
def upload_recognition_data_to_s3()
def download_recognition_data_from_s3()
def validate_recognition_annotation_format()
def convert_detection_to_recognition_format()

# การเทรน Recognition
def create_recognition_training_config()
def start_recognition_training()
def monitor_recognition_training_progress()

# การจัดการ checkpoints
def sync_recognition_checkpoints_to_s3()
def download_recognition_checkpoints_from_s3()
```

## 🚫 สิ่งที่ควรหลีกเลี่ยง

### ❌ ห้ามทำ
- อย่าแก้ไข PaddleOCR source code โดยตรง
- อย่าใช้ local paths แทน S3 paths ในระบบ production
- อย่าข้าม GPU availability check
- อย่าเริ่มแก้ปัญหาโดยไม่อ่าน problem-log.md ก่อน
- อย่าสร้าง virtual environment แยกใน subprojects
- อย่า commit โฟลเดอร์ venv/ ใน git

### ⚠️ ระวัง
- Memory usage เมื่อโหลดข้อมูลขนาดใหญ่
- S3 download/upload timeouts
- PaddlePaddle version compatibility
- CUDA driver compatibility
- Virtual environment activation ก่อนรัน scripts

## 🎯 เป้าหมายของโค้ด

### Primary Goals
1. ใช้ Official PaddleOCR training tools (เฉพาะ Recognition)
2. รองรับ S3 data pipeline สำหรับ Recognition data
3. GPU-optimized training สำหรับ Recognition models
4. Automatic checkpoint management สำหรับ Recognition
5. Error resilience และ recovery

### Secondary Goals
1. User-friendly logging
2. Progress monitoring
3. Configuration flexibility
4. Data format validation

## 📊 การ Debug และ Monitoring

### ข้อมูลที่ต้องติดตาม
- GPU memory usage
- Training loss และ accuracy
- S3 upload/download progress
- Checkpoint file sizes และ timestamps

### การ Logging
```python
# ใช้ structured logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Starting training with config: {config_path}")
logger.error(f"Training failed: {error_message}")
```

## 🔄 การจัดการ Updates

### เมื่อมี PaddleOCR Updates
1. ตรวจสอบ compatibility กับ current setup
2. ทดสอบใน sandbox environment ก่อน
3. อัปเดต requirements และ documentation
4. บันทึกการเปลี่ยนแปลงใน problem-log.md

### เมื่อมี AWS SageMaker Updates
1. ตรวจสอบ instance types และ pricing
2. ทดสอบ GPU compatibility
3. อัปเดต boto3 และ sagemaker SDK

## 📚 เอกสารอ้างอิง

### สำคัญที่สุด
- [docs/problem-log.md](../docs/problem-log.md) - **อ่านก่อนแก้ปัญหาทุกครั้ง**
- [docs/troubleshooting.md](../docs/troubleshooting.md) - แนวทางแก้ปัญหา
- [docs/data-format.md](../docs/data-format.md) - รูปแบบข้อมูล

### เอกสารเสริม
- [PaddleOCR Official Docs](https://github.com/PaddlePaddle/PaddleOCR)
- [AWS SageMaker Developer Guide](https://docs.aws.amazon.com/sagemaker/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

---

**หมายเหตุสำคัญ**: การปฏิบัติตามแนวทางเหล่านี้จะช่วยให้การพัฒนาและบำรุงรักษาโปรเจคเป็นไปอย่างมีประสิทธิภาพและลดการเกิดปัญหาซ้ำ
