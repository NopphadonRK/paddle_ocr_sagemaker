# คู่มือแก้ไขปัญหา (Troubleshooting Guide)

## 🚨 ปัญหาที่พบบ่อยและวิธีแก้ไข

### 1. ปัญหาการติดตั้ง Dependencies

#### ❌ PaddlePaddle GPU ติดตั้งไม่สำเร็จ
**อาการ**: `pip install paddlepaddle-gpu` ล้มเหลว
**วิธีแก้**:
```bash
# ตรวจสอบ CUDA version
nvidia-smi

# ติดตั้งตาม CUDA version
# สำหรับ CUDA 11.8
pip install paddlepaddle-gpu==2.5.2 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html

# สำหรับ CUDA 11.7
pip install paddlepaddle-gpu==2.5.2 -f https://www.paddlepaddle.org.cn/whl/cu117/

# ถ้ายังไม่ได้ ลองใช้ conda
conda install paddlepaddle-gpu==2.5.2 cudatoolkit=11.8 -c paddle
```

#### ❌ OpenCV import error
**อาการ**: `ImportError: libGL.so.1: cannot open shared object file`
**วิธีแก้**:
```bash
# ติดตั้ง system dependencies
apt-get update
apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1

# หรือใช้ opencv-python-headless
pip uninstall opencv-python
pip install opencv-python-headless
```

### 2. ปัญหา GPU และ CUDA

#### ❌ GPU ไม่ถูกตรวจพบ
**อาการ**: `paddle.is_compiled_with_cuda()` คืนค่า `False`
**วิธีแก้**:
```python
# ตรวจสอบ CUDA installation
import subprocess
result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
print(result.stdout)

# ตรวจสอบ CUDA driver
result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
print(result.stdout)

# ติดตั้ง PaddlePaddle ใหม่
pip uninstall paddlepaddle-gpu
pip install paddlepaddle-gpu==2.5.2 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

#### ❌ CUDA out of memory
**อาการ**: `RuntimeError: (OutOfMemory) Out of memory error on GPU`
**วิธีแก้**:
```python
# ลด batch size
config['Train']['loader']['batch_size_per_card'] = 4

# ลด image size
config['Train']['dataset']['transforms']['EastRandomCropData']['size'] = [640, 640]

# ใช้ gradient accumulation
config['Global']['grad_clip'] = {'type': 'ClipGradByNorm', 'clip_norm': 5.0}
```

### 3. ปัญหาข้อมูลและ Annotation

#### ❌ Annotation format ผิด
**อาการ**: Training ไม่เริ่ม หรือ error ระหว่าง data loading
**วิธีแก้**:
```python
# ตรวจสอบรูปแบบไฟล์
def debug_annotation_file(annotation_file):
    with open(annotation_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 5:  # ตรวจสอบเฉพาะ 5 บรรทัดแรก
                break
            
            print(f"Line {i+1}: {repr(line)}")
            
            try:
                parts = line.strip().split('\t')
                print(f"  Parts count: {len(parts)}")
                
                if len(parts) == 2:
                    image_path, annotation_json = parts
                    annotations = json.loads(annotation_json)
                    print(f"  Image: {image_path}")
                    print(f"  Annotations count: {len(annotations)}")
                    
                    for j, ann in enumerate(annotations):
                        print(f"    Annotation {j}: {ann}")
                        
            except Exception as e:
                print(f"  Error: {e}")
```

#### ❌ รูปภาพหาไม่เจอ
**อาการ**: `FileNotFoundError` ระหว่าง training
**วิธีแก้**:
```python
# ตรวจสอบ path ของรูปภาพ
def check_image_paths(annotation_file, image_base_dir):
    missing_images = []
    
    with open(annotation_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                image_path = line.strip().split('\t')[0]
                full_path = os.path.join(image_base_dir, image_path)
                
                if not os.path.exists(full_path):
                    missing_images.append((line_num, image_path, full_path))
                    
            except:
                continue
    
    if missing_images:
        print(f"Found {len(missing_images)} missing images:")
        for line_num, rel_path, full_path in missing_images[:10]:
            print(f"  Line {line_num}: {rel_path} -> {full_path}")
    else:
        print("All images found!")
```

### 4. ปัญหาการเทรน

#### ❌ Training ไม่เริ่ม
**อาการ**: Script รันแล้วแต่ไม่มี log หรือ progress
**วิธีแก้**:
```bash
# เพิ่ม verbose logging
export GLOG_v=3
export GLOG_logtostderr=1

# รัน training ด้วย Python -u เพื่อ unbuffered output
python -u tools/train.py -c configs/your_config.yml

# ตรวจสอบ config file
python -c "
import yaml
with open('configs/your_config.yml', 'r') as f:
    config = yaml.safe_load(f)
print(yaml.dump(config, default_flow_style=False))
"
```

#### ❌ Loss ไม่ลดลง
**อาการ**: Training loss ติดค่าสูงหรือไม่เปลี่ยนแปลง
**วิธีแก้**:
```python
# ลด learning rate
config['Optimizer']['lr']['learning_rate'] = 0.0001

# เพิ่ม warmup epochs
config['Optimizer']['lr']['warmup_epoch'] = 5

# ตรวจสอบ data augmentation
# ลองปิด augmentation ที่รุนแรง
config['Train']['dataset']['transforms'] = [
    {'DecodeImage': {'img_mode': 'BGR', 'channel_first': False}},
    {'DetLabelEncode': {}},
    # ลบ IaaAugment ออกชั่วคราว
    {'NormalizeImage': {'scale': '1./255.', 'mean': [0.485, 0.456, 0.406], 'std': [0.229, 0.224, 0.225], 'order': 'hwc'}},
    {'ToCHWImage': {}},
    {'KeepKeys': {'keep_keys': ['image', 'threshold_map', 'threshold_mask', 'shrink_map', 'shrink_mask']}}
]
```

### 5. ปัญหา S3 และ AWS

#### ❌ S3 access denied
**อาการ**: `botocore.exceptions.ClientError: An error occurred (AccessDenied)`
**วิธีแก้**:
```python
# ตรวจสอบ AWS credentials
import boto3
session = boto3.Session()
credentials = session.get_credentials()
print(f"Access Key: {credentials.access_key}")
print(f"Secret Key: {credentials.secret_key[:10]}...")

# ตรวจสอบ IAM permissions
s3 = boto3.client('s3')
try:
    s3.list_buckets()
    print("S3 access OK")
except Exception as e:
    print(f"S3 access failed: {e}")

# ตรวจสอบ bucket policy
try:
    response = s3.get_bucket_policy(Bucket='your-bucket-name')
    print("Bucket policy:", response['Policy'])
except Exception as e:
    print(f"Cannot get bucket policy: {e}")
```

#### ❌ S3 upload/download ช้า
**อาการ**: การถ่ายโอนข้อมูลใช้เวลานาน
**วิธีแก้**:
```python
# ใช้ multipart upload
import boto3
from boto3.s3.transfer import TransferConfig

config = TransferConfig(
    multipart_threshold=1024 * 25,  # 25MB
    max_concurrency=10,
    multipart_chunksize=1024 * 25,
    use_threads=True
)

s3_client = boto3.client('s3')
s3_client.upload_file(
    'large_file.zip', 
    'your-bucket', 
    'key', 
    Config=config
)

# ใช้ S3 Transfer Acceleration
s3_client = boto3.client(
    's3',
    config=boto3.session.Config(
        s3={'use_accelerate_endpoint': True}
    )
)
```

### 6. ปัญหา Memory และ Performance

#### ❌ Out of Memory (RAM)
**อาการ**: `MemoryError` หรือ system ค้าง
**วิธีแก้**:
```python
# ลด num_workers
config['Train']['loader']['num_workers'] = 2

# ลด batch size
config['Train']['loader']['batch_size_per_card'] = 4

# ใช้ data prefetch
config['Train']['loader']['use_shared_memory'] = False

# เพิ่ม memory monitoring
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
```

#### ❌ Training ช้า
**อาการ**: Training ใช้เวลานานเกินปกติ
**วิธีแก้**:
```python
# ปรับ IO optimization
config['Train']['loader']['num_workers'] = min(8, os.cpu_count())
config['Train']['loader']['prefetch_factor'] = 2

# ลด image augmentation
# ใช้เฉพาะ augmentation ที่จำเป็น

# เพิ่ม mixed precision training (ถ้า GPU รองรับ)
config['Global']['use_amp'] = True
config['Global']['scale_loss'] = 128.0
```

## 🔧 เครื่องมือ Debug

### 1. การตรวจสอบ Configuration
```python
def validate_config(config_path):
    """
    ตรวจสอบความถูกต้องของ config file
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    required_keys = [
        'Global', 'Architecture', 'Loss', 'Optimizer', 
        'PostProcess', 'Metric', 'Train', 'Eval'
    ]
    
    missing_keys = []
    for key in required_keys:
        if key not in config:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"Missing required keys: {missing_keys}")
        return False
    
    # ตรวจสอบ paths
    train_data_dir = config['Train']['dataset']['data_dir']
    if not os.path.exists(train_data_dir):
        print(f"Train data directory not found: {train_data_dir}")
        return False
    
    print("Configuration validation passed!")
    return True
```

### 2. การทดสอบ Data Loading
```python
def test_data_loading(config_path):
    """
    ทดสอบการโหลดข้อมูล
    """
    import paddle
    from ppocr.data import build_dataloader
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    try:
        train_dataloader = build_dataloader(config, 'Train', device='gpu')
        
        print("Testing data loading...")
        for i, batch in enumerate(train_dataloader):
            if i >= 3:  # ทดสอบเฉพาะ 3 batch แรก
                break
            
            print(f"Batch {i}: {batch['image'].shape}")
            
        print("Data loading test passed!")
        return True
        
    except Exception as e:
        print(f"Data loading test failed: {e}")
        return False
```

### 3. การตรวจสอบ Model
```python
def test_model_creation(config_path):
    """
    ทดสอบการสร้าง model
    """
    import paddle
    from ppocr.modeling.architectures import build_model
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    try:
        model = build_model(config['Architecture'])
        model.eval()
        
        # ทดสอบ forward pass
        if config['Architecture']['model_type'] == 'det':
            dummy_input = paddle.randn([1, 3, 640, 640])
        else:
            dummy_input = paddle.randn([1, 3, 32, 320])
        
        output = model(dummy_input)
        print(f"Model test passed! Output shape: {output.shape}")
        return True
        
    except Exception as e:
        print(f"Model test failed: {e}")
        return False
```

## 📊 Performance Monitoring

### การติดตาม Training Progress
```python
import time
import psutil
import paddle

class TrainingMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.step_times = []
        
    def log_step(self, step, loss, lr):
        current_time = time.time()
        step_time = current_time - self.start_time
        self.step_times.append(step_time)
        
        # Memory usage
        memory_usage = psutil.virtual_memory().percent
        gpu_memory = paddle.device.cuda.memory_reserved() / 1024**3
        
        # Estimated time remaining
        if len(self.step_times) > 10:
            avg_step_time = sum(self.step_times[-10:]) / 10
            steps_remaining = 1000 - step  # สมมติ total 1000 steps
            eta = avg_step_time * steps_remaining
            
            print(f"Step: {step}, Loss: {loss:.4f}, LR: {lr:.6f}")
            print(f"Memory: {memory_usage:.1f}%, GPU: {gpu_memory:.1f}GB")
            print(f"ETA: {eta/3600:.2f} hours")
```

---

**หมายเหตุ**: หากพบปัญหาที่ไม่อยู่ในคู่มือนี้ ให้บันทึกใน `problem-log.md` เพื่อใช้อ้างอิงในอนาคต
