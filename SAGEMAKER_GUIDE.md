# 🚀 SageMaker Training Scripts Guide

## 📋 Available Scripts

### 1. **Main Management Script**
```bash
./sagemaker_management.sh [command]
```

**Commands:**
- `status` - ตรวจสอบสถานะ instance และ Jupyter URL
- `start` - เปิด SageMaker instance
- `stop` - ปิด instance (ประหยัดค่าใช้จ่าย)
- `jupyter` - เปิด Jupyter ใน browser
- `check-data` - ตรวจสอบข้อมูลใน S3
- `monitor` - ติดตาม progress การเทรน
- `download` - ดาวน์โหลดผลลัพธ์จาก S3
- `cleanup` - ลบ instance และข้อมูล

### 2. **Quick Launcher**
```bash
./launch_training.sh
```
- ตรวจสอบพร้อมใช้งาน
- เปิด Jupyter พร้อมคำแนะนำ
- แสดงขั้นตอนการเทรน

### 3. **Training Monitor**
```bash
./monitor_training.sh
```
- ติดตาม progress แบบ real-time
- แสดงการสร้าง model checkpoints
- แจ้งเตือนเมื่อเทรนเสร็จ

## 🎯 การใช้งานทีละขั้นตอน

### **ขั้นตอนที่ 1: เริ่มต้น**
```bash
# ตรวจสอบสถานะ
./sagemaker_management.sh status

# ถ้า instance หยุด ให้เปิด
./sagemaker_management.sh start
```

### **ขั้นตอนที่ 2: เริ่มเทรน**
```bash
# เปิด Jupyter และเริ่มเทรน
./launch_training.sh
```

หรือ
```bash
# เปิด Jupyter เฉยๆ
./sagemaker_management.sh jupyter
```

### **ขั้นตอนที่ 3: ติดตามการเทรน**
```bash
# ใน terminal ใหม่
./monitor_training.sh

# หรือใช้คำสั่งเดียว
./sagemaker_management.sh monitor
```

### **ขั้นตอนที่ 4: หลังเทรนเสร็จ**
```bash
# ดาวน์โหลดผลลัพธ์
./sagemaker_management.sh download

# ปิด instance เพื่อประหยัด
./sagemaker_management.sh stop
```

## ⚡ Quick Commands

### **เช็คด่วน**
```bash
# ตรวจสอบทุกอย่าง
./sagemaker_management.sh status
./sagemaker_management.sh check-data
```

### **เริ่มเทรนด่วน**
```bash
# ถ้าพร้อมแล้ว
./launch_training.sh
```

### **หยุดฉุกเฉิน**
```bash
# หยุด instance
./sagemaker_management.sh stop
```

## 📊 การใช้งานใน Jupyter Notebook

### **Notebook: `paddle_ocr_sagemaker_training.ipynb`**

**รัน Cells ตามลำดับ:**

1. **Cell 1**: Environment Setup (2-3 นาที)
   - ติดตั้ง dependencies
   - ตรวจสอบ GPU

2. **Cell 2**: AWS Configuration (30 วินาที)
   - ตั้งค่า S3 bucket (ตรวจสอบชื่อ bucket)
   - ตรวจสอบ credentials

3. **Cell 3**: PaddleOCR Setup (1-2 นาที)
   - Clone PaddleOCR repository
   - ติดตั้ง requirements

4. **Cell 4**: Download Data (2-5 นาที)
   - ดาวน์โหลดข้อมูลจาก S3
   - ตรวจสอบไฟล์สำคัญ

5. **Cell 5**: Training Config (30 วินาที)
   - สร้าง configuration file
   - ตั้งค่า CRNN model

6. **Cell 6**: Start Training (30-60 นาที)
   - เริ่มเทรนโมเดล
   - แสดง progress real-time

7. **Cell 7**: Test Model (2-3 นาที)
   - ทดสอบโมเดลที่เทรนแล้ว
   - แสดงผลลัพธ์

8. **Cell 8**: Upload Results (2-5 นาที)
   - อัปโหลดผลลัพธ์กลับ S3
   - สร้าง summary report

## 💰 Cost Management

### **Instance Costs:**
- `ml.g4dn.xlarge`: ~$1.00/hour
- Training time: 45-75 minutes
- Total cost: ~$1.25 per training run

### **ประหยัดค่าใช้จ่าย:**
```bash
# หยุด instance เมื่อไม่ใช้
./sagemaker_management.sh stop

# เปิดเฉพาะเมื่อใช้
./sagemaker_management.sh start
```

## 🔧 Troubleshooting

### **Instance ไม่เริ่ม:**
```bash
# ตรวจสอบสถานะ
./sagemaker_management.sh status

# ลองเริ่มใหม่
./sagemaker_management.sh start
```

### **ไม่เข้า Jupyter ได้:**
```bash
# ดู URL
./sagemaker_management.sh status

# เปิด browser manual
./sagemaker_management.sh jupyter
```

### **ข้อมูลใน S3 หาไม่เจอ:**
```bash
# ตรวจสอบข้อมูล
./sagemaker_management.sh check-data

# อัปโหลดใหม่ (ถ้าจำเป็น)
cd data_preparation
python scripts/upload_to_s3.py
```

### **Training ไม่เริ่ม:**
1. ตรวจสอบ Cell 2 ใน notebook (S3_BUCKET name)
2. ตรวจสอบ GPU availability
3. ตรวจสอบ PaddleOCR repository

## 📞 Support Commands

```bash
# ดูคำแนะนำทั้งหมด
./sagemaker_management.sh help

# ตรวจสอบ configuration
cat sagemaker_management.sh | grep -E "INSTANCE_NAME|S3_BUCKET|REGION"

# ดู log ล่าสุด
./sagemaker_management.sh monitor
```

---

**🎯 Ready to start training? Run:**
```bash
./launch_training.sh
```
