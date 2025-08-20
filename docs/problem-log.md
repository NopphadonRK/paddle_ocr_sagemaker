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

**จำนวนปัญหาทั้งหมด**: 0  
**ปัญหาที่แก้ได้**: 0  
**ปัญหาที่ยังไม่ได้แก้**: 0  

### ปัญหาที่พบบ่อย
- ยังไม่มีข้อมูล

---

## 🔍 ประวัติการแก้ปัญหา

### ตัวอย่างการบันทึกปัญหา (ลบออกเมื่อเริ่มใช้งานจริง)

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
