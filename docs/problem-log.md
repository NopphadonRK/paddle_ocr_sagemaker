# บันทึกปัญหาและการแก้ไข (Problem Log)

> **⚠️ สำคัญ**: ก่อนเริ่มแก้ปัญหาใดๆ ให้อ่านไฟล์นี้เสมอเพื่อดูว่าเคยมีการแก้ปัญหาคล้ายกันหรือไม่
> 
> **📝 หลังแก้ปัญหา**: ทุกครั้งที่แก้ปัญหา (ไม่ว่าจะสำเร็จหรือไม่) ให้บันทึกในไฟล์นี้

---

## 📋 รูปแบบการบันทึก

### สำหรับปัญหาใหม่
```markdown
## [วันที่] - [ชื่อปัญหา]

**ปัญหา**: [อธิบายปัญหาโดยละเอียด]

**สาเหตุ**: [สาเหตุที่เป็นไปได้]

**วิธีแก้ที่ลอง**:
1. [วิธีที่ 1] - ❌/✅ [ผลลัพธ์]
2. [วิธีที่ 2] - ❌/✅ [ผลลัพธ์]

**วิธีแก้ที่ได้ผล**: [วิธีการที่สำเร็จ]

**หมายเหตุ**: [ข้อสังเกตเพิ่มเติม]

**แท็ก**: #gpu #s3 #training #dependencies (เลือกที่เกี่ยวข้อง)
```

---

## 📊 สถิติปัญหา

**จำนวนปัญหาทั้งหมด**: 3  
**ปัญหาที่แก้ได้**: 3  
**ปัญหาที่ยังไม่ได้แก้**: 0  

### ปัญหาที่พบบ่อย
- Virtual environment configuration issues
- Directory setup for logging
- Project structure consistency

---

## 🔍 ประวัติการแก้ปัญหา

## [2025-08-20] - PaddlePaddle GPU Installation Failed

**ปัญหา**: ติดตั้ง PaddlePaddle GPU version ไม่สำเร็จ เกิด error "Could not find a version that satisfies the requirement paddlepaddle-gpu"

**สาเหตุ**: CUDA version ไม่ตรงกับ PaddlePaddle version ที่ต้องการ

**วิธีแก้ที่ลอง**:
1. `pip install paddlepaddle-gpu` - ❌ ล้มเหลว
2. `conda install paddlepaddle-gpu` - ❌ ล้มเหลว  
3. ตรวจสอบ CUDA version ด้วย `nvidia-smi` - ✅ พบว่าเป็น CUDA 11.8
4. ใช้ wheel URL ที่ตรงกับ CUDA version - ✅ สำเร็จ

**วิธีแก้ที่ได้ผล**: 
```bash
pip install paddlepaddle-gpu==2.5.2 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

**หมายเหตุ**: ต้องตรวจสอบ CUDA version ก่อนทุกครั้ง และใช้ wheel URL ที่ตรงกับ CUDA version

**แท็ก**: #dependencies #gpu #cuda

---

## [2025-08-20] - S3 Access Denied Error

**ปัญหา**: ไม่สามารถอัปโหลดไฟล์ไปยัง S3 ได้ เกิด error "AccessDenied: Access Denied"

**สาเหตุ**: IAM role ไม่มีสิทธิ์เข้าถึง S3 bucket

**วิธีแก้ที่ลอง**:
1. ตรวจสอบ AWS credentials - ✅ credentials ถูกต้อง
2. ตรวจสอบ bucket name - ✅ ชื่อ bucket ถูกต้อง
3. เปลี่ยน bucket policy - ❌ ยังไม่ได้ผล
4. อัปเดต IAM role permissions - ✅ สำเร็จ

**วิธีแก้ที่ได้ผล**: 
เพิ่ม permissions ใน IAM role:
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:DeleteObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::bucket-name",
    "arn:aws:s3:::bucket-name/*"
  ]
}
```

**หมายเหตุ**: ต้องแน่ใจว่า IAM role มีสิทธิ์ทั้ง bucket และ object level

**แท็ก**: #s3 #aws #permissions

---

## [2025-08-20] - GPU Out of Memory During Training

**ปัญหา**: Training หยุดด้วย error "CUDA out of memory" หลังจากรันได้ไม่กี่ steps

**สาเหตุ**: Batch size ใหญ่เกินไปสำหรับ GPU memory ที่มี

**วิธีแก้ที่ลอง**:
1. ลด batch_size_per_card จาก 16 เป็น 8 - ❌ ยังไม่พอ
2. ลด batch_size_per_card เป็น 4 - ✅ ได้ผล แต่ช้า
3. ลด image size จาก 960x960 เป็น 640x640 - ✅ ได้ผลและเร็วขึ้น
4. ใช้ gradient accumulation - ✅ ได้ผลดี

**วิธีแก้ที่ได้ผล**: 
```yaml
# ใน config file
Train:
  loader:
    batch_size_per_card: 4
    
# และลด image size
EastRandomCropData:
  size: [640, 640]
```

**หมายเหตุ**: สำหรับ GPU 8GB ใช้ batch size 4 และ image size 640x640 เหมาะสม

**แท็ก**: #gpu #memory #training

---

## 🔍 ประวัติการแก้ปัญหา

## [2025-08-21] - เปลี่ยน Virtual Environment จาก .venv เป็น venv

**ปัญหา**: โครงสร้าง virtual environment ใช้ชื่อ `.venv` ซึ่งไม่สอดคล้องกับมาตรฐานและเอกสารส่วนใหญ่ที่ใช้ `venv`

**สาเหตุ**: การตั้งค่าเริ่มต้นใช้ `.venv` (hidden directory) แต่เอกสารและ setup scripts ใช้ `venv`

**วิธีแก้ที่ลอง**:
1. ลบ `.venv` directory และสร้าง `venv` ใหม่ - ✅ สำเร็จ
2. อัปเดต `.gitignore` เพื่อลบ `.venv/` - ✅ สำเร็จ
3. ตรวจสอบและอัปเดตไฟล์ทั้งหมดในโปรเจค - ✅ สำเร็จ

**วิธีแก้ที่ได้ผล**: 
1. `rm -rf .venv`
2. `python3 -m venv venv` 
3. อัปเดต `.gitignore` ลบ `.venv/`
4. configure_python_environment ใหม่
5. ติดตั้ง dependencies อีกครั้ง
6. เพิ่มกฎการอัปเดตโครงสร้างโปรเจคใน copilot instructions

**หมายเหตุ**: ทุกไฟล์เอกสารใช้ `venv` อยู่แล้ว เลยไม่ต้องแก้ไข setup scripts และเอกสาร

**แท็ก**: #virtual-environment #project-structure #setup

---

## [2025-08-21] - Data Conversion Script FileNotFoundError

**ปัญหา**: รัน `convert_data.py` แล้วเกิด error "FileNotFoundError: [Errno 2] No such file or directory: 'output/validation_reports/processing.log'"

**สาเหตุ**: logging configuration ใน `utils.py` พยายามสร้าง log file ก่อนที่ directory จะถูกสร้าง

**วิธีแก้ที่ลอง**:
1. เพิ่ม `Path('output/validation_reports').mkdir(parents=True, exist_ok=True)` ก่อน logging setup - ✅ สำเร็จ

**วิธีแก้ที่ได้ผล**: แก้ไข `utils.py` ให้สร้าง directory ก่อน setup logging

**หมายเหตุ**: ควรตรวจสอบ directory dependencies ในไฟล์ที่มีการใช้ file I/O

**แท็ก**: #data-preparation #logging #directory

---

## [2025-08-21] - AWS Configuration Setup สำเร็จ

**สรุปผลลัพธ์**: ตั้งค่า AWS configuration สำหรับการเทรน PaddleOCR บน SageMaker สำเร็จแล้ว

**ข้อมูลที่ได้รับจากผู้ใช้**:
- S3 Bucket: `sagemaker-ocr-train-bucket`
- AWS Region: `ap-southeast-1`
- SageMaker Instance: `ml.g4dn.xlarge`
- AWS Profile: `484468818942_AIEngineer`
- Credentials: Temporary session token (expires periodically)

**ไฟล์ที่สร้างขึ้น**:
- `aws-config.json` - Complete AWS configuration (in .gitignore)
- `.env` - Environment variables file (in .gitignore)
- `AWS_CONFIG_README.md` - คู่มือการใช้งาน AWS config
- `test_aws_connection.py` - สคริปต์ทดสอบการเชื่อมต่อ AWS

**การรักษาความปลอดภัย**:
- เพิ่มไฟล์ credentials ทั้งหมดเข้า `.gitignore`
- ใช้ temporary session token (ปลอดภัยกว่า permanent keys)
- สร้างคู่มือการใช้งานและข้อควรระวัง

**ขั้นตอนต่อไป**:
1. ทดสอบการเชื่อมต่อ: `python test_aws_connection.py`
2. สร้าง S3 bucket และ upload ข้อมูล
3. เริ่มการเทรนโมเดลบน SageMaker

**หมายเหตุ**: Session token อาจหมดอายุ ต้องอัปเดตใหม่เป็นระยะ

**แท็ก**: #aws #s3 #sagemaker #credentials #security

---

## [2025-08-21] - Data Conversion สำเร็จสมบูรณ์

**สรุปผลลัพธ์**: การแปลงข้อมูลจากรูปแบบเดิมเป็น PaddleOCR Recognition format สำเร็จแล้ว

**รายละเอียด**:
- ข้อมูลทั้งหมด: 5,000 รายการ
- Train set: 4,000 รายการ (80%)
- Validation set: 1,000 รายการ (20%)
- Character dictionary: 14 ตัวอักษร (0-9 + special tokens)
- รูปภาพถูก resize เป็นความสูง 32 pixels
- Annotation format: `image_path\ttext_content` (ถูกต้องสำหรับ PaddleOCR)

**ไฟล์ที่สร้างขึ้น**:
- `output/recognition_dataset/images/train/` - รูปภาพ training (4,000 ไฟล์)
- `output/recognition_dataset/images/val/` - รูปภาพ validation (1,000 ไฟล์)
- `output/recognition_dataset/annotations/train_annotation.txt` - annotation training
- `output/recognition_dataset/annotations/val_annotation.txt` - annotation validation
- `output/recognition_dataset/metadata/character_dict.txt` - character dictionary
- `output/recognition_dataset/metadata/dataset_info.json` - dataset metadata

**ขั้นตอนต่อไป**:
1. Upload ข้อมูลไปยัง S3: `python scripts/upload_to_s3.py`
2. เริ่มการเทรน: `../paddle_ocr_recognition_training.ipynb`

**แท็ก**: #data-preparation #conversion #success

---

<!-- 
เริ่มบันทึกปัญหาใหม่ที่นี่
ให้ใช้รูปแบบเดียวกับตัวอย่างข้างบน
อย่าลืมอัปเดตสถิติด้านบนด้วย
-->

---

## 📚 แนวทางการป้องกันปัญหา

### ก่อนเริ่มโปรเจค
1. ✅ ตรวจสอบ CUDA version และ compatibility
2. ✅ ทดสอบ AWS credentials และ S3 access
3. ✅ ตรวจสอบ GPU memory และกำหนด batch size ที่เหมาะสม
4. ✅ ทดสอบ data loading ด้วยข้อมูลตัวอย่างเล็กๆ

### ระหว่างการเทรน
1. ✅ Monitor GPU memory usage อย่างสม่ำเสมอ
2. ✅ Backup checkpoint เป็นระยะ
3. ✅ ตรวจสอบ S3 upload/download status
4. ✅ เก็บ log ของ training process

### หลังแก้ปัญหา
1. ✅ บันทึกปัญหาและวิธีแก้ในไฟล์นี้
2. ✅ อัปเดต documentation ที่เกี่ยวข้อง
3. ✅ แชร์ความรู้กับทีม
4. ✅ ทดสอบ solution ใน environment อื่น

---

## 🔗 ลิงก์ที่เป็นประโยชน์

- [PaddleOCR GitHub Issues](https://github.com/PaddlePaddle/PaddleOCR/issues)
- [AWS SageMaker Troubleshooting](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-mkt-troubleshooting.html)
- [CUDA Compatibility Guide](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/)
- [Boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)

---

**การใช้งาน**: 
1. ค้นหาด้วย Ctrl+F (ใช้แท็กหรือคำสำคัญ)
2. เพิ่มปัญหาใหม่ที่ส่วนล่างของไฟล์
3. อัปเดตสถิติเมื่อมีการเปลี่ยนแปลง
4. ลบตัวอย่างข้างบนเมื่อเริ่มใช้งานจริง
