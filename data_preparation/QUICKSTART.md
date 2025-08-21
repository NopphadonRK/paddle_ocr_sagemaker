# 🚀 Quick Start Guide - Data Preparation

เริ่มต้นเตรียมข้อมูลสำหรับ PaddleOCR Recognition ใน 5 นาที!

## ✅ เช็คลิสต์ก่อนเริ่ม

- [ ] มีรูปภาพข้อความในโฟลเดอร์
- [ ] มีไฟล์ labels.txt หรือไฟล์ป้ายกำกับ
- [ ] ติดตั้ง Python 3.8+ แล้ว
- [ ] มี AWS Account และ S3 Bucket พร้อมใช้งาน

## 🎯 ขั้นตอนด่วน

### 1️⃣ วางข้อมูลต้นฉบับ (2 นาที)

```bash
# คัดลอกรูปภาพของคุณ
cp /path/to/your/text_images/* input/images/

# คัดลอกไฟล์ labels
cp /path/to/your/labels.txt input/

# ตรวจสอบข้อมูล
ls input/images/ | head -5    # ดูรูปภาพ 5 ไฟล์แรก
head -5 input/labels.txt      # ดู labels 5 บรรทัดแรก
```

### 2️⃣ ติดตั้ง Dependencies (1 นาที)

```bash
pip install opencv-python pillow boto3 tqdm pyyaml
```

### 3️⃣ แปลงข้อมูลทั้งหมด (1 คำสั่ง)

```bash
# รันสคริปต์หลัก - จะทำทุกอย่างให้อัตโนมัติ
python scripts/convert_data.py

# ถ้าต้องการควบคุมมากขึ้น ใช้คำสั่งแยก:
# python scripts/resize_images.py
# python scripts/validate_data.py
```

### 4️⃣ ตั้งค่า AWS และอัปโหลด (1 นาที)

```bash
# ตั้งค่า AWS (ครั้งเดียว)
aws configure
# ใส่ Access Key, Secret Key, Region

# อัปโหลดไปยัง S3
python scripts/upload_to_s3.py --bucket your-paddleocr-bucket
```

## 📊 ผลลัพธ์ที่คาดหวัง

หลังรันเสร็จจะได้:

```
output/recognition_dataset/
├── images/
│   ├── train/           # รูปภาพ training (ขนาด 32-48px height)
│   └── val/             # รูปภาพ validation
├── annotations/
│   ├── train_annotation.txt    # image_path\ttext_content
│   └── val_annotation.txt
└── metadata/
    ├── dataset_info.json       # ข้อมูลสถิติ
    └── character_dict.txt      # ตัวอักษรที่พบ
```

## 🎯 ตัวอย่างผลลัพธ์

### ไฟล์ Annotation ที่ได้:
```
images/train/img_001.jpg	สวัสดีครับ
images/train/img_002.jpg	PaddleOCR
images/train/img_003.jpg	ภาษาไทย
images/train/img_004.jpg	1234567890
```

### รูปภาพที่ปรับขนาดแล้ว:
- ความสูง: 32px (หรือตามที่กำหนด)
- ความกว้าง: ปรับตามสัดส่วนของข้อความ
- คุณภาพ: คงความชัดเจนไว้

## ⚡ การแก้ไขปัญหาเร็ว

### ❌ รูปภาพโหลดไม่ได้
```bash
# ตรวจสอบรูปแบบไฟล์
file input/images/*.jpg | head -5

# แปลงรูปแบบหากจำเป็น
mogrify -format jpg input/images/*.png
```

### ❌ Labels ไม่ถูกต้อง
```bash
# ดูรูปแบบไฟล์ labels
head -10 input/labels.txt

# หากรูปแบบแปลก ให้แก้ไขใน scripts/convert_data.py
```

### ❌ S3 อัปโหลดไม่ได้
```bash
# ตรวจสอบ AWS credentials
aws sts get-caller-identity

# ทดสอบ S3 access
aws s3 ls s3://your-bucket-name
```

## 🚀 ไปต่อที่ Training

เมื่อเสร็จแล้ว:
1. **เปิด** `../paddle_ocr_recognition_training.ipynb`
2. **ตั้งค่า S3 paths** ในเซลล์ที่ 2
3. **เริ่มเทรน** Recognition model!

## 📱 การติดต่อ

หากติดปัญหา:
- ตรวจสอบ `output/validation_reports/error_log.txt`
- อ่าน `../docs/troubleshooting.md`
- บันทึกปัญหาใน `../docs/problem-log.md`

---
**🎯 เป้าหมาย: ใช้เวลาไม่เกิน 5 นาทีในการเตรียมข้อมูล!**
