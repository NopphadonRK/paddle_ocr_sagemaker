# 🚀 SageMaker Scripts Usage Guide
# คู่มือการใช้งาน Scripts สำหรับ SageMaker

## 📋 Scripts ที่มี:

### 1. **load_aws_env.sh** - โหลด AWS Credentials
```bash
# ใช้สำหรับโหลด AWS credentials ก่อนรัน scripts อื่น
./load_aws_env.sh [command]

# ตัวอย่าง:
./load_aws_env.sh ./quick_start_sagemaker.sh
```

### 2. **quick_start_sagemaker.sh** - เริ่มใช้งานด่วน
```bash
# เข้าถึง SageMaker instance อย่างรวดเร็ว
./load_aws_env.sh ./quick_start_sagemaker.sh
```
**ผลลัพธ์:**
- ตรวจสอบสถานะ instance
- เปิด instance (ถ้าปิดอยู่)
- แสดง Jupyter URL
- เปิด browser (macOS)

### 3. **sagemaker_status.sh** - ตรวจสอบสถานะ
```bash
# ตรวจสอบสถานะครบครัน
./load_aws_env.sh ./sagemaker_status.sh all

# ตรวจสอบเฉพาะ instance
./load_aws_env.sh ./sagemaker_status.sh status

# ตรวจสอบข้อมูลใน S3
./load_aws_env.sh ./sagemaker_status.sh s3

# ดู Jupyter URL
./load_aws_env.sh ./sagemaker_status.sh url

# หยุด instance
./load_aws_env.sh ./sagemaker_status.sh stop
```

### 4. **training_monitor.sh** - ติดตามการเทรน
```bash
# ดูสถานะการเทรนทั้งหมด
./load_aws_env.sh ./training_monitor.sh

# ดูเฉพาะ logs
./load_aws_env.sh ./training_monitor.sh logs

# ดูสรุปการเทรน
./load_aws_env.sh ./training_monitor.sh summary

# ดูการใช้งาน S3
./load_aws_env.sh ./training_monitor.sh s3
```

### 5. **cleanup_sagemaker.sh** - จัดการต้นทุน
```bash
# ดูต้นทุนปัจจุบัน
./load_aws_env.sh ./cleanup_sagemaker.sh costs

# หยุด instance เพื่อประหยัด
./load_aws_env.sh ./cleanup_sagemaker.sh stop

# ดาวน์โหลด results
./load_aws_env.sh ./cleanup_sagemaker.sh download

# ลบ instance (ระวัง!)
./load_aws_env.sh ./cleanup_sagemaker.sh delete

# ล้าง S3 storage
./load_aws_env.sh ./cleanup_sagemaker.sh s3
```

## 🎯 Workflow แนะนำ:

### **🚀 เริ่มต้นการเทรน:**
```bash
# 1. ตรวจสอบทุกอย่าง
./load_aws_env.sh ./sagemaker_status.sh all

# 2. เข้า SageMaker
./load_aws_env.sh ./quick_start_sagemaker.sh

# 3. เปิด paddle_ocr_sagemaker_training.ipynb
# 4. รัน cells ตามลำดับ
```

### **📊 ระหว่างการเทรน:**
```bash
# ติดตามความคืบหน้า
./load_aws_env.sh ./training_monitor.sh

# ดูการใช้งาน S3
./load_aws_env.sh ./training_monitor.sh s3
```

### **🏁 หลังเสร็จสิ้น:**
```bash
# ดาวน์โหลด results
./load_aws_env.sh ./cleanup_sagemaker.sh download

# หยุด instance เพื่อประหยัด
./load_aws_env.sh ./cleanup_sagemaker.sh stop

# ดูต้นทุนที่เกิดขึ้น
./load_aws_env.sh ./cleanup_sagemaker.sh costs
```

## 💡 Tips:

### **การประหยัดต้นทุน:**
```bash
# หยุด instance เมื่อไม่ใช้งาน
./load_aws_env.sh ./cleanup_sagemaker.sh stop

# ดูต้นทุนปัจจุบัน
./load_aws_env.sh ./cleanup_sagemaker.sh costs
```

### **การแก้ปัญหา:**
```bash
# ตรวจสอบ credentials
./load_aws_env.sh aws sts get-caller-identity

# ตรวจสอบ S3 access
./load_aws_env.sh aws s3 ls s3://sagemaker-ocr-train-bucket/

# ตรวจสอบ instance
./load_aws_env.sh aws sagemaker describe-notebook-instance --notebook-instance-name paddle-ocr-training
```

## 🚨 ข้อควรระวัง:

### **ต้นทุน:**
- Instance `ml.g4dn.xlarge` ≈ $0.736/hour
- หยุด instance เมื่อไม่ใช้งาน
- S3 storage ≈ $0.023/GB/month

### **ความปลอดภัย:**
- อย่าแชร์ AWS credentials
- ลบ instance เมื่อเสร็จงาน
- สำรองข้อมูลสำคัญ

### **การใช้งาน:**
- ใช้ `load_aws_env.sh` ก่อนรัน scripts ทุกครั้ง
- ตรวจสอบ credentials หมดอายุทุก 12 ชั่วโมง
- บันทึกผลลัพธ์ก่อนลบ instance

## 📞 ช่วยเหลือ:

หากมีปัญหา:
1. ตรวจสอบ AWS credentials
2. ตรวจสอบ internet connection
3. ดู error messages ใน terminal
4. ตรวจสอบ AWS Console

---
**หมายเหตุ:** ทุก scripts ต้องรันผ่าน `load_aws_env.sh` เพื่อโหลด AWS credentials
