# 📂 Data Preparation for PaddleOCR Text Recognition

คู่มือการเตรียมข้อมูลสำหรับการเทรน PaddleOCR Text Recognition models

## 🎯 วัตถุประสงค์

เตรียมข้อมูลรูปภาพข้อความและไฟล์ annotation ให้อยู่ในรูปแบบที่เหมาะสมสำหรับการเทรน Recognition model บน SageMaker

## 📁 โครงสร้าง Directory

```
data_preparation/
├── README.md                    # คู่มือนี้
├── QUICKSTART.md               # คู่มือเริ่มต้นอย่างเร็ว
├── scripts/                    # Scripts สำหรับประมวลผลข้อมูล
│   ├── convert_data.py         # แปลงข้อมูลเป็น Recognition format
│   ├── resize_images.py        # ปรับขนาดรูปภาพ
│   ├── validate_data.py        # ตรวจสอบความถูกต้องของข้อมูล
│   ├── upload_to_s3.py         # อัปโหลดไปยัง S3
│   └── utils.py                # ฟังก์ชันสำหรับใช้ร่วมกัน
├── input/                      # วางข้อมูลต้นฉบับที่นี่
│   ├── images/                 # รูปภาพต้นฉบับ
│   └── labels.txt              # ไฟล์ label ต้นฉบับ
└── output/                     # ผลลัพธ์ที่ประมวลผลแล้ว
    ├── recognition_dataset/    # ข้อมูลพร้อมสำหรับเทรน
    └── validation_reports/     # รายงานการตรวจสอบ
```

## 🚀 การเริ่มต้นอย่างเร็ว

### ขั้นตอนที่ 1: วางข้อมูลต้นฉบับ
```bash
# วางรูปภาพของคุณใน input/images/
cp /path/to/your/images/* input/images/

# วางไฟล์ labels.txt ใน input/
cp /path/to/your/labels.txt input/
```

### ขั้นตอนที่ 2: ติดตั้ง Dependencies
```bash
pip install opencv-python pillow boto3 tqdm
```

### ขั้นตอนที่ 3: แปลงข้อมูล
```bash
# แปลงข้อมูลทั้งหมด (รัน script หลัก)
python scripts/convert_data.py

# หรือรันทีละขั้นตอน
python scripts/resize_images.py      # ปรับขนาดรูปภาพ
python scripts/validate_data.py     # ตรวจสอบข้อมูล
```

### ขั้นตอนที่ 4: อัปโหลดไปยัง S3
```bash
# ตั้งค่า AWS credentials ก่อน
aws configure

# อัปโหลดข้อมูล
python scripts/upload_to_s3.py --bucket your-bucket-name
```

## 📝 รูปแบบข้อมูลที่รองรับ

### Input Format (รูปแบบเริ่มต้น)
- **รูปภาพ**: ไฟล์ `.jpg`, `.png`, `.jpeg` ในโฟลเดอร์ `input/images/`
- **Labels**: ไฟล์ `labels.txt` ที่มีรูปแบบใดก็ได้ (script จะแปลงให้)

### Output Format (รูปแบบสำหรับ Recognition)
- **รูปภาพ**: ขนาด 32-48px height, ความกว้างตามสัดส่วน
- **Annotation**: รูปแบบ `image_path\ttext_content`

## 🔧 การปรับแต่ง Scripts

### การปรับขนาดรูปภาพ
แก้ไขใน `scripts/resize_images.py`:
```python
TARGET_HEIGHT = 32  # เปลี่ยนความสูงที่ต้องการ
MIN_WIDTH = 16      # ความกว้างขั้นต่ำ
MAX_WIDTH = 512     # ความกว้างสูงสุด
```

### การแบ่งข้อมูล Train/Validation
แก้ไขใน `scripts/convert_data.py`:
```python
TRAIN_RATIO = 0.8   # สัดส่วน training data (80%)
VAL_RATIO = 0.2     # สัดส่วน validation data (20%)
```

## 📊 การตรวจสอบผลลัพธ์

หลังจากรัน scripts แล้ว ตรวจสอบผลลัพธ์ที่:
- `output/recognition_dataset/` - ข้อมูลพร้อมสำหรับเทรน
- `output/validation_reports/` - รายงานการตรวจสอบ

## ⚠️ ข้อควรระวัง

1. **ตรวจสอบไฟล์ input** ก่อนรัน scripts
2. **สำรองข้อมูล** ต้นฉบับก่อนประมวลผล
3. **ตรวจสอบ validation reports** หลังแปลงข้อมูล
4. **ทดสอบอัปโหลด S3** ด้วยข้อมูลเล็กๆ ก่อน

## 🔗 ขั้นตอนถัดไป

เมื่อเตรียมข้อมูลเสร็จแล้ว:
1. ไปที่ Jupyter Notebook หลัก: `../paddle_ocr_recognition_training.ipynb`
2. ตั้งค่า S3 paths ให้ตรงกับที่อัปโหลดไว้
3. เริ่มการเทรน Recognition model

## 📞 การแก้ไขปัญหา

หากเกิดปัญหา:
1. ตรวจสอบ `output/validation_reports/error_log.txt`
2. อ่าน `../docs/troubleshooting.md`
3. บันทึกปัญหาใน `../docs/problem-log.md`
