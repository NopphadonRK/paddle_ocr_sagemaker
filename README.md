# PaddleOCR Text Recognition Training on Amazon SageMaker

โปรเจคสำหรับเทรน PaddleOCR Text Recognition โมเดลเท่านั้น บน Amazon SageMaker ด้วย GPU Support และการจัดการข้อมูลผ่าน S3

## 📋 ข้อกำหนดของระบบ

### สภาพแวดล้อม
- **Amazon SageMaker Notebook Instance** ที่รองรับ GPU
- **Python 3.8 หรือ 3.9**
- **PaddlePaddle GPU Version** ที่เข้ากันได้
- **Official PaddleOCR Repository** สำหรับเครื่องมือการเทรน

### ไลบรารีหลัก
- PaddlePaddle GPU (2.5.2)
- OpenCV
- Boto3 (สำหรับ S3)
- PyYAML
- NumPy, Pandas

## 🚀 การเริ่มต้นใช้งาน

### 1. เตรียมสภาพแวดล้อม
```bash
# Clone โปรเจค
git clone <repository-url>
cd paddle_ocr_sagemaker

# เปิด Jupyter Notebook
jupyter notebook paddle_ocr_training.ipynb
```

### 2. เตรียมข้อมูล Text Recognition
- อัปโหลดรูปภาพข้อความ (cropped text images) และไฟล์ Annotation ไปยัง S3 bucket
- ตรวจสอบรูปแบบไฟล์ Annotation ให้ถูกต้องสำหรับ Recognition:
  ```
  image_path\ttext_content
  ```
  ตัวอย่าง:
  ```
  images/word_001.jpg	สวัสดี
  images/word_002.jpg	PaddleOCR
  images/word_003.jpg	1234567890
  ```

### 3. การกำหนดค่า
- แก้ไข S3 bucket และ path ใน notebook
- ปรับแต่งพารามิเตอร์การเทรนในไฟล์ `.yml` สำหรับ Recognition
- ตั้งค่า checkpoint saving directory สำหรับ Recognition model

### 4. เริ่มการเทรน Text Recognition
- รันเซลล์ใน notebook ตามลำดับ
- ตรวจสอบการทำงานของ GPU
- เริ่มกระบวนการเทรน Recognition โดยใช้ `tools/train_rec.py`

## 📁 โครงสร้างโปรเจค

```
paddle_ocr_sagemaker/
├── README.md
├── paddle_ocr_recognition_training.ipynb     # Notebook หลักสำหรับการเทรน Text Recognition
├── .github/
│   └── copilot-instructions.md               # คำแนะนำสำหรับ GitHub Copilot
└── docs/
    ├── requirements.md                       # ข้อกำหนดโดยละเอียด
    ├── configuration-guide.md                # คู่มือการกำหนดค่า
    ├── data-format.md                       # รูปแบบข้อมูลและ Annotation สำหรับ Recognition
    ├── troubleshooting.md                   # คู่มือแก้ไขปัญหา
    └── problem-log.md                       # บันทึกปัญหาและการแก้ไข
```

## 🔧 ฟีเจอร์หลัก

### การจัดการข้อมูล
- ✅ การอัปโหลด/ดาวน์โหลดข้อมูล Recognition จาก S3
- ✅ การตรวจสอบรูปแบบไฟล์ Annotation สำหรับ Recognition
- ✅ การแปลงข้อมูลจาก Detection annotation เป็น Recognition format
- ✅ การแบ่งข้อมูล train/validation สำหรับ Recognition

### การกำหนดค่าและการเทรน
- ✅ การโหลดและแก้ไขไฟล์ `.yml` configuration สำหรับ Recognition
- ✅ การปรับแต่ง S3 paths อัตโนมัติ
- ✅ การใช้ `tools/train_rec.py` script
- ✅ การรองรับ command line arguments สำหรับ Recognition

### การจัดการ Model Checkpoints
- ✅ การบันทึก `.pdparams` และ `.pdopt` files สำหรับ Recognition model
- ✅ การ sync checkpoints ไปยัง S3
- ✅ การตรวจสอบความคืบหน้าการเทรน Recognition
- ✅ การ resume จาก checkpoint

## 📊 การติดตามและตรวจสอบ

### Log และ Monitoring
- การแสดงผลความคืบหน้าการเทรน
- การตรวจสอบ GPU usage
- การบันทึก training metrics
- การตรวจสอบ checkpoint files

### ไฟล์ผลลัพธ์
- Recognition Model parameters (`.pdparams`)
- Recognition Optimizer states (`.pdopt`)
- Recognition Training logs และ metrics

## 🎯 รูปแบบข้อมูลที่รองรับ

### Annotation Format สำหรับ Text Recognition
```
image_relative_path	text_content
```
ตัวอย่าง:
```
images/word_001.jpg	สวัสดี
images/word_002.jpg	ยินดีต้อนรับ
images/word_003.jpg	PaddleOCR
images/word_004.jpg	1234567890
```

### Configuration Files สำหรับ Recognition
- **CRNN Model**: `configs/rec/rec_mv3_none_bilstm_ctc.yml`
- **SVTR Model**: `configs/rec/rec_svtr_base.yml`
- **PP-OCRv4 Recognition**: `configs/rec/PP-OCRv4/en_PP-OCRv4_rec.yml`

## ⚠️ สิ่งสำคัญที่ต้องระวัง

1. **ก่อนเริ่มแก้ปัญหาใดๆ ให้อ่าน [docs/problem-log.md](docs/problem-log.md) เสมอ**
2. ตรวจสอบ GPU availability ก่อนเทรน
3. ตรวจสอบรูปแบบ annotation file ให้ถูกต้องสำหรับ Recognition (image_path\ttext)
4. ตั้งค่า S3 permissions ให้เหมาะสม
5. สำรองข้อมูลก่อนเริ่มการเทรน Recognition

## 📚 เอกสารเพิ่มเติม

- [Requirements](docs/requirements.md) - ข้อกำหนดโดยละเอียด
- [Configuration Guide](docs/configuration-guide.md) - คู่มือการตั้งค่า
- [Data Format](docs/data-format.md) - รูปแบบข้อมูลสำหรับ Recognition
- [Troubleshooting](docs/troubleshooting.md) - แก้ไขปัญหา
- [Problem Log](docs/problem-log.md) - บันทึกปัญหา

## 🤝 การสนับสนุน

หากพบปัญหาหรือต้องการความช่วยเหลือ:
1. ตรวจสอบ [docs/problem-log.md](docs/problem-log.md) ก่อน
2. อ่าน [docs/troubleshooting.md](docs/troubleshooting.md)
3. สร้าง Issue ใน GitHub repository

## 📄 License

โปรเจคนี้ใช้ MIT License - ดูรายละเอียดใน [LICENSE](LICENSE) file

---

**หมายเหตุ**: โปรเจคนี้ใช้ Official PaddleOCR Repository เป็นฐาน และปรับแต่งเพื่อเทรนเฉพาะ Text Recognition model บน Amazon SageMaker เท่านั้น
