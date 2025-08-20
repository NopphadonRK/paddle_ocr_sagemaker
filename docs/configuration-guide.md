# คู่มือการกำหนดค่า (Configuration Guide)

## 🔧 การตั้งค่าเบื้องต้น

### 1. การตั้งค่า AWS Credentials
```bash
# ตั้งค่าผ่าน AWS CLI
aws configure
# หรือตั้งค่าผ่าน environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### 2. การสร้าง S3 Bucket
```python
import boto3

s3 = boto3.client('s3')
bucket_name = 'your-paddleocr-bucket'

# สร้าง bucket
s3.create_bucket(Bucket=bucket_name)

# ตั้งค่า versioning
s3.put_bucket_versioning(
    Bucket=bucket_name,
    VersioningConfiguration={'Status': 'Enabled'}
)
```

## 📁 โครงสร้างข้อมูลใน S3

### แนวทางการจัดระเบียบไฟล์
```
s3://your-bucket-name/
├── datasets/
│   ├── train/
│   │   ├── images/
│   │   │   ├── img_001.jpg
│   │   │   └── img_002.jpg
│   │   └── annotations/
│   │       └── train_annotations.txt
│   ├── val/
│   │   ├── images/
│   │   └── annotations/
│   └── test/
├── models/
│   ├── checkpoints/
│   ├── pretrained/
│   └── final/
└── configs/
    ├── detection/
    └── recognition/
```

## ⚙️ การกำหนดค่า PaddleOCR

### 1. Detection Model Configuration
```yaml
# configs/det/custom_det_config.yml
Global:
  use_gpu: true
  epoch_num: 500
  log_smooth_window: 20
  print_batch_step: 10
  save_epoch_step: 50
  save_model_dir: "/path/to/s3/models/detection"
  checkpoints: null
  pretrained_model: null
  eval_batch_step: [0, 2000]
  cal_metric_during_train: true

Architecture:
  model_type: det
  algorithm: DB
  Transform:
  Backbone:
    name: MobileNetV3
    scale: 0.5
    model_name: large
  Neck:
    name: DBFPN
    out_channels: 256
  Head:
    name: DBHead
    k: 50

Loss:
  name: DBLoss
  balance_loss: true
  main_loss_type: DiceLoss
  alpha: 5
  beta: 10
  ohem_ratio: 3

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: 0.001
    warmup_epoch: 2
  regularizer:
    name: L2
    factor: 5.0e-05

PostProcess:
  name: DBPostProcess
  thresh: 0.3
  box_thresh: 0.6
  max_candidates: 1000
  unclip_ratio: 1.5

Metric:
  name: DetMetric
  main_indicator: hmean

Train:
  dataset:
    name: SimpleDataSet
    data_dir: /path/to/s3/datasets/train
    label_file_list:
      - /path/to/s3/datasets/train/annotations/train_annotations.txt
    transforms:
      - DecodeImage:
          img_mode: BGR
          channel_first: false
      - DetLabelEncode:
      - IaaAugment:
          augmenter_args:
            - {'type': Fliplr, 'args': {'p': 0.5}}
            - {'type': Affine, 'args': {'rotate': [-10, 10]}}
            - {'type': Resize, 'args': {'size': [0.5, 3]}}
      - EastRandomCropData:
          size: [960, 960]
          max_tries: 50
          keep_ratio: true
      - MakeBorderMap:
          shrink_ratio: 0.4
          thresh_min: 0.3
          thresh_max: 0.7
      - MakeShrinkMap:
          shrink_ratio: 0.4
          min_text_size: 8
      - NormalizeImage:
          scale: 1./255.
          mean: [0.485, 0.456, 0.406]
          std: [0.229, 0.224, 0.225]
          order: 'hwc'
      - ToCHWImage:
      - KeepKeys:
          keep_keys: ['image', 'threshold_map', 'threshold_mask', 'shrink_map', 'shrink_mask']
  loader:
    shuffle: true
    drop_last: false
    batch_size_per_card: 8
    num_workers: 4

Eval:
  dataset:
    name: SimpleDataSet
    data_dir: /path/to/s3/datasets/val
    label_file_list:
      - /path/to/s3/datasets/val/annotations/val_annotations.txt
    transforms:
      - DecodeImage:
          img_mode: BGR
          channel_first: false
      - DetLabelEncode:
      - DetResizeForTest:
          image_shape: [736, 1280]
      - NormalizeImage:
          scale: 1./255.
          mean: [0.485, 0.456, 0.406]
          std: [0.229, 0.224, 0.225]
          order: 'hwc'
      - ToCHWImage:
      - KeepKeys:
          keep_keys: ['image', 'shape', 'polys', 'ignore_tags']
  loader:
    shuffle: false
    drop_last: false
    batch_size_per_card: 1
    num_workers: 2
```

### 2. Recognition Model Configuration
```yaml
# configs/rec/custom_rec_config.yml
Global:
  use_gpu: true
  epoch_num: 300
  log_smooth_window: 20
  print_batch_step: 10
  save_epoch_step: 30
  save_model_dir: "/path/to/s3/models/recognition"
  eval_batch_step: [0, 2000]
  cal_metric_during_train: true
  pretrained_model: null
  checkpoints: null
  character_dict_path: ppocr/utils/ppocr_keys_v1.txt
  character_type: ch
  max_text_length: 25
  infer_mode: false

Architecture:
  model_type: rec
  algorithm: CRNN
  Transform:
  Backbone:
    name: MobileNetV3
    scale: 0.5
    model_name: large
  Neck:
    name: SequenceEncoder
    encoder_type: rnn
    hidden_size: 48
  Head:
    name: CTCHead
    mid_channels: 96
    fc_decay: 0.00002

Loss:
  name: CTCLoss

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: 0.001
  regularizer:
    name: L2
    factor: 0.00001

PostProcess:
  name: CTCLabelDecode

Metric:
  name: RecMetric
  main_indicator: acc

Train:
  dataset:
    name: SimpleDataSet
    data_dir: /path/to/s3/datasets/train
    label_file_list:
      - /path/to/s3/datasets/train/annotations/train_rec_annotations.txt
    transforms:
      - DecodeImage:
          img_mode: BGR
          channel_first: false
      - RecAug:
      - RecLabelEncode:
      - RecResizeImg:
          image_shape: [3, 32, 320]
      - KeepKeys:
          keep_keys: ['image', 'label', 'length']
  loader:
    shuffle: true
    batch_size_per_card: 256
    drop_last: true
    num_workers: 8

Eval:
  dataset:
    name: SimpleDataSet
    data_dir: /path/to/s3/datasets/val
    label_file_list:
      - /path/to/s3/datasets/val/annotations/val_rec_annotations.txt
    transforms:
      - DecodeImage:
          img_mode: BGR
          channel_first: false
      - RecLabelEncode:
      - RecResizeImg:
          image_shape: [3, 32, 320]
      - KeepKeys:
          keep_keys: ['image', 'label', 'length']
  loader:
    shuffle: false
    drop_last: false
    batch_size_per_card: 256
    num_workers: 4
```

## 🔧 การปรับแต่งพารามิเตอร์

### Performance Tuning
```python
def optimize_config_for_gpu(config, gpu_memory_gb):
    """
    ปรับแต่ง configuration ตาม GPU memory
    """
    if gpu_memory_gb >= 16:
        config['Train']['loader']['batch_size_per_card'] = 16
        config['Train']['loader']['num_workers'] = 8
    elif gpu_memory_gb >= 8:
        config['Train']['loader']['batch_size_per_card'] = 8
        config['Train']['loader']['num_workers'] = 4
    else:
        config['Train']['loader']['batch_size_per_card'] = 4
        config['Train']['loader']['num_workers'] = 2
    
    return config
```

### Learning Rate Scheduling
```yaml
# สำหรับ dataset ขนาดเล็ก (< 1000 samples)
Optimizer:
  lr:
    name: Cosine
    learning_rate: 0.0001
    warmup_epoch: 5

# สำหรับ dataset ขนาดกลาง (1000-10000 samples)
Optimizer:
  lr:
    name: Cosine
    learning_rate: 0.001
    warmup_epoch: 2

# สำหรับ dataset ขนาดใหญ่ (> 10000 samples)
Optimizer:
  lr:
    name: Cosine
    learning_rate: 0.01
    warmup_epoch: 1
```

## 📊 การตั้งค่า Monitoring

### 1. VisualDL Integration
```python
# เพิ่มใน training script
from visualdl import LogWriter

writer = LogWriter(logdir='./log/paddle_ocr_training')

# Log training metrics
writer.add_scalar(tag='train/loss', step=step, value=loss)
writer.add_scalar(tag='train/accuracy', step=step, value=accuracy)
```

### 2. CloudWatch Metrics
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def log_metric_to_cloudwatch(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='PaddleOCR/Training',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow()
            }
        ]
    )
```

## 🔒 การตั้งค่าความปลอดภัย

### 1. S3 Bucket Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowSageMakerAccess",
      "Effect": "Allow",
      "Principal": {
        "Service": "sagemaker.amazonaws.com"
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

### 2. VPC Configuration
```python
# สำหรับ SageMaker Training Job
vpc_config = {
    'SecurityGroupIds': ['sg-xxxxxxxx'],
    'Subnets': ['subnet-xxxxxxxx', 'subnet-yyyyyyyy']
}
```

## 🚀 การ Deploy และ Inference

### Model Serving Configuration
```yaml
# configs/inference/inference_config.yml
Global:
  use_gpu: false
  enable_mkldnn: true
  cpu_threads: 10
  det_algorithm: DB
  rec_algorithm: CRNN

det:
  det_model_dir: ./models/det
  det_limit_side_len: 960
  det_limit_type: max
  det_thresh: 0.3
  det_box_thresh: 0.6
  det_unclip_ratio: 1.6
  use_dilation: false
  det_score_mode: fast

rec:
  rec_model_dir: ./models/rec
  rec_image_shape: "3, 32, 320"
  rec_char_type: ch
  rec_batch_num: 6
  max_text_length: 25
  rec_char_dict_path: ./ppocr/utils/ppocr_keys_v1.txt
  use_space_char: true
```

---

**หมายเหตุ**: การกำหนดค่าอาจต้องปรับแต่งตามลักษณะของข้อมูลและทรัพยากรที่มี ควรทดสอบกับข้อมูลตัวอย่างก่อนนำไปใช้จริง
