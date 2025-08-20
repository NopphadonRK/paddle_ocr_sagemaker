# PaddleOCR Training on Amazon SageMaker

โปรเจคสำหรับเทรน PaddleOCR บน Amazon SageMaker ด้วย GPU Support และการจัดการข้อมูลผ่าน S3

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

### 2. เตรียมข้อมูล
- อัปโหลดรูปภาพและไฟล์ Annotation ไปยัง S3 bucket
- ตรวจสอบรูปแบบไฟล์ Annotation ให้ถูกต้อง:
  ```
  image_path\t[{"transcription": "text", "points": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]}]
  ```

### 3. การกำหนดค่า
- แก้ไข S3 bucket และ path ใน notebook
- ปรับแต่งพารามิเตอร์การเทรนในไฟล์ `.yml`
- ตั้งค่า checkpoint saving directory

### 4. เริ่มการเทรน
- รันเซลล์ใน notebook ตามลำดับ
- ตรวจสอบการทำงานของ GPU
- เริ่มกระบวนการเทรน

## 📁 โครงสร้างโปรเจค

```
paddle_ocr_sagemaker/
├── README.md
├── paddle_ocr_training.ipynb     # Notebook หลักสำหรับการเทรน
├── .github/
│   └── copilot-instructions.md   # คำแนะนำสำหรับ GitHub Copilot
└── docs/
    ├── requirements.md           # ข้อกำหนดโดยละเอียด
    ├── configuration-guide.md    # คู่มือการกำหนดค่า
    ├── data-format.md           # รูปแบบข้อมูลและ Annotation
    ├── troubleshooting.md       # คู่มือแก้ไขปัญหา
    └── problem-log.md           # บันทึกปัญหาและการแก้ไข
```

## 🔧 ฟีเจอร์หลัก

### การจัดการข้อมูล
- ✅ การอัปโหลด/ดาวน์โหลดข้อมูลจาก S3
- ✅ การตรวจสอบรูปแบบไฟล์ Annotation
- ✅ การแปลงข้อมูลจาก LabelMe เป็น PaddleOCR format
- ✅ การแบ่งข้อมูล train/validation

### การกำหนดค่าและการเทรน
- ✅ การโหลดและแก้ไขไฟล์ `.yml` configuration
- ✅ การปรับแต่ง S3 paths อัตโนมัติ
- ✅ การใช้ `tools/train.py` script
- ✅ การรองรับ command line arguments

### การจัดการ Model Checkpoints
- ✅ การบันทึก `.pdparams` และ `.pdopt` files
- ✅ การ sync checkpoints ไปยัง S3
- ✅ การตรวจสอบความคืบหน้าการเทรน
- ✅ การ resume จาก checkpoint

## 📊 การติดตามและตรวจสอบ

### Log และ Monitoring
- การแสดงผลความคืบหน้าการเทรน
- การตรวจสอบ GPU usage
- การบันทึก training metrics
- การตรวจสอบ checkpoint files

### ไฟล์ผลลัพธ์
- Model parameters (`.pdparams`)
- Optimizer states (`.pdopt`)
- Training logs และ metrics

## 🎯 รูปแบบข้อมูลที่รองรับ

### Annotation Format
```
image_relative_path	[{"transcription": "ข้อความจริง", "points": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]}]
```

### Configuration Files
- **Detection Model**: `configs/det/det_mv3_db.yml`
- **Recognition Model**: `configs/rec/rec_mv3_none_bilstm_ctc.yml`

## ⚠️ สิ่งสำคัญที่ต้องระวัง

1. **ก่อนเริ่มแก้ปัญหาใดๆ ให้อ่าน [docs/problem-log.md](docs/problem-log.md) เสมอ**
2. ตรวจสอบ GPU availability ก่อนเทรน
3. ตรวจสอบรูปแบบ annotation file ให้ถูกต้อง
4. ตั้งค่า S3 permissions ให้เหมาะสม
5. สำรองข้อมูลก่อนเริ่มการเทรน

## 📚 เอกสารเพิ่มเติม

- [Requirements](docs/requirements.md) - ข้อกำหนดโดยละเอียด
- [Configuration Guide](docs/configuration-guide.md) - คู่มือการตั้งค่า
- [Data Format](docs/data-format.md) - รูปแบบข้อมูล
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

**หมายเหตุ**: โปรเจคนี้ใช้ Official PaddleOCR Repository เป็นฐาน และปรับแต่งเพื่อใช้งานบน Amazon SageMaker เท่านั้น
