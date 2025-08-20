# ข้อกำหนดของระบบ (System Requirements)

## 🖥️ สภาพแวดล้อมการใช้งาน

### Amazon SageMaker
- **Instance Type**: `ml.g4dn.xlarge` หรือสูงกว่า (สำหรับ GPU training)
- **Storage**: อย่างน้อย 50GB EBS volume
- **Network**: เชื่อมต่อ Internet สำหรับดาวน์โหลด dependencies
- **IAM Role**: สิทธิ์เข้าถึง S3, SageMaker, และ CloudWatch

### Python Environment
- **Python Version**: 3.8.x หรือ 3.9.x
- **Package Manager**: pip (ล่าสุด)
- **Virtual Environment**: แนะนำใช้ conda หรือ venv

## 📦 Dependencies หลัก

### PaddlePaddle
```bash
# PaddlePaddle GPU version (จำเป็น)
pip install paddlepaddle-gpu==2.5.2 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

### Computer Vision และ Image Processing
```bash
pip install opencv-python==4.8.0.74
pip install imgaug==0.4.0
pip install Pillow==10.0.0
```

### Text Processing และ OCR
```bash
pip install pyclipper==1.3.0
pip install python-Levenshtein==0.21.1
pip install shapely==2.0.1
```

### Machine Learning และ Data Science
```bash
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install scikit-learn==1.3.0
```

### AWS Integration
```bash
pip install boto3==1.28.17
pip install sagemaker==2.175.0
pip install awscli==1.29.17
```

### Utilities
```bash
pip install tqdm==4.65.0
pip install pyyaml==6.0.1
pip install lmdb==1.4.1
pip install visualdl==2.5.1
```

## 🔧 Hardware Requirements

### GPU Requirements
- **CUDA Version**: 11.2 หรือสูงกว่า
- **GPU Memory**: อย่างน้อย 8GB (แนะนำ 16GB+)
- **Driver**: NVIDIA Driver 460.x หรือสูงกว่า

### CPU และ Memory
- **CPU Cores**: อย่างน้อย 4 cores
- **RAM**: อย่างน้อย 16GB (แนะนำ 32GB+)
- **Storage**: อย่างน้อย 100GB available space

## 🌐 Network Requirements

### Internet Connectivity
- เชื่อมต่อ Internet สำหรับ:
  - ดาวน์โหลด PaddleOCR repository
  - ติดตั้ง Python packages
  - เข้าถึง AWS services

### AWS Services Access
- **Amazon S3**: อัปโหลด/ดาวน์โหลดข้อมูลและ models
- **Amazon SageMaker**: รัน training jobs
- **Amazon CloudWatch**: monitoring และ logging

## 📊 ข้อมูลและ Storage

### Training Data Requirements
- **Image Formats**: JPG, PNG, TIFF
- **Annotation Format**: Text files ด้วย JSON structure
- **Data Size**: ขึ้นอยู่กับ dataset (แนะนำ 1000+ samples)

### S3 Bucket Configuration
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::YOUR-ACCOUNT:role/SageMakerExecutionRole"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

## 🔐 Security Requirements

### IAM Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "sagemaker:CreateTrainingJob",
        "sagemaker:DescribeTrainingJob",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### VPC Configuration (Optional)
- เพื่อความปลอดภัยเพิ่มเติม
- การควบคุม network access
- การเชื่อมต่อกับ on-premises systems

## 🚀 Performance Recommendations

### Instance Selection
- **Development**: `ml.g4dn.xlarge` (1 GPU, 4 vCPUs, 16GB RAM)
- **Training**: `ml.g4dn.2xlarge` (1 GPU, 8 vCPUs, 32GB RAM)
- **Heavy Training**: `ml.p3.2xlarge` (1 V100 GPU, 8 vCPUs, 61GB RAM)

### Storage Optimization
- ใช้ EBS gp3 volumes สำหรับ better IOPS
- เก็บข้อมูลใน S3 Standard หรือ S3 Standard-IA
- ใช้ S3 Transfer Acceleration สำหรับ large datasets

## 📋 Pre-installation Checklist

### ก่อนเริ่มติดตั้ง ตรวจสอบ:
- [ ] SageMaker instance เปิดใช้งานแล้ว
- [ ] IAM role มีสิทธิ์ที่จำเป็น
- [ ] S3 bucket ถูกสร้างและกำหนดค่าแล้ว
- [ ] Internet connectivity ทำงานปกติ
- [ ] Python 3.8/3.9 พร้อมใช้งาน

### การตรวจสอบ GPU
```python
import paddle
print(f"PaddlePaddle version: {paddle.__version__}")
print(f"CUDA available: {paddle.is_compiled_with_cuda()}")
if paddle.is_compiled_with_cuda():
    print(f"GPU count: {paddle.device.cuda.device_count()}")
```

### การตรวจสอบ AWS Connectivity
```python
import boto3
s3 = boto3.client('s3')
try:
    s3.list_buckets()
    print("AWS S3 connection successful")
except Exception as e:
    print(f"AWS connection failed: {e}")
```

## 🔄 Version Compatibility Matrix

| Component | Supported Versions | Recommended |
|-----------|-------------------|-------------|
| Python | 3.8.x, 3.9.x | 3.9.x |
| PaddlePaddle | 2.4.x, 2.5.x | 2.5.2 |
| CUDA | 11.2+, 11.7+, 11.8+ | 11.8 |
| OpenCV | 4.7.x, 4.8.x | 4.8.0 |
| SageMaker SDK | 2.170+| 2.175.0 |

---

**หมายเหตุ**: ข้อกำหนดเหล่านี้อาจเปลี่ยนแปลงตามการอัปเดตของ dependencies แต่ละตัว ควรตรวจสอบเวอร์ชันล่าสุดเป็นระยะ
