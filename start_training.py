#!/usr/bin/env python3
"""
Start Training Script
สคริปต์เตรียมการเทรนโมเดล PaddleOCR Recognition
"""

import json
import os
import sys
import subprocess
from pathlib import Path

def load_config():
    """โหลด AWS configuration"""
    try:
        with open('aws-config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("❌ aws-config.json not found! Run setup first.")
        return None

def set_environment(config):
    """ตั้งค่า environment variables"""
    creds = config['credentials']
    settings = config['aws_settings']
    
    env_vars = {
        'AWS_ACCESS_KEY_ID': creds['aws_access_key_id'],
        'AWS_SECRET_ACCESS_KEY': creds['aws_secret_access_key'],
        'AWS_SESSION_TOKEN': creds['aws_session_token'],
        'AWS_DEFAULT_REGION': settings['region'],
        'S3_BUCKET': settings['s3_bucket_name'],
        'SAGEMAKER_REGION': settings['sagemaker_region']
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("✅ Environment variables set")

def check_data_upload():
    """ตรวจสอบว่าข้อมูลถูกอัปโหลดแล้วหรือไม่"""
    import boto3
    
    try:
        s3 = boto3.client('s3')
        bucket = os.environ['S3_BUCKET']
        
        # ตรวจสอบไฟล์สำคัญ
        required_files = [
            'recognition-data/annotations/train_annotation.txt',
            'recognition-data/annotations/val_annotation.txt',
            'recognition-data/metadata/character_dict.txt',
            'recognition-data/metadata/dataset_info.json'
        ]
        
        print("🔍 Checking uploaded data...")
        for file_key in required_files:
            try:
                s3.head_object(Bucket=bucket, Key=file_key)
                print(f"  ✅ {file_key}")
            except:
                print(f"  ❌ {file_key} - missing!")
                return False
        
        # นับจำนวนรูปภาพ
        paginator = s3.get_paginator('list_objects_v2')
        train_count = 0
        val_count = 0
        
        for page in paginator.paginate(Bucket=bucket, Prefix='recognition-data/images/train/'):
            if 'Contents' in page:
                train_count += len(page['Contents'])
        
        for page in paginator.paginate(Bucket=bucket, Prefix='recognition-data/images/val/'):
            if 'Contents' in page:
                val_count += len(page['Contents'])
        
        print(f"  📊 Training images: {train_count}")
        print(f"  📊 Validation images: {val_count}")
        
        if train_count > 0 and val_count > 0:
            print("✅ Data upload verified")
            return True
        else:
            print("❌ No images found in S3")
            return False
            
    except Exception as e:
        print(f"❌ Error checking S3 data: {e}")
        return False

def start_jupyter():
    """เริ่ม Jupyter notebook"""
    print("🚀 Starting Jupyter Notebook...")
    print("")
    print("📋 Instructions:")
    print("1. Jupyter will open in your browser")
    print("2. Open: paddle_ocr_recognition_training.ipynb")
    print("3. Select kernel: Python (venv)")
    print("4. Run cells sequentially")
    print("")
    print("🎯 The notebook is configured for your current S3 bucket:")
    print(f"   Bucket: {os.environ.get('S3_BUCKET', 'N/A')}")
    print(f"   Region: {os.environ.get('AWS_DEFAULT_REGION', 'N/A')}")
    print("")
    
    try:
        # เริ่ม Jupyter
        cmd = [sys.executable, '-m', 'jupyter', 'notebook', 'paddle_ocr_recognition_training.ipynb']
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Jupyter notebook stopped")
    except Exception as e:
        print(f"❌ Error starting Jupyter: {e}")
        print("💡 Try: pip install jupyter")

def main():
    print("🎯 PaddleOCR Training Launcher")
    print("="*50)
    
    # 1. Load configuration
    config = load_config()
    if not config:
        sys.exit(1)
    
    # 2. Set environment
    set_environment(config)
    
    # 3. Check data upload
    if not check_data_upload():
        print("\n❌ Data not ready. Please run:")
        print("   cd data_preparation")
        print("   python scripts/upload_to_s3.py --bucket sagemaker-ocr-train-bucket --yes")
        sys.exit(1)
    
    # 4. Start training interface
    print("\n🎉 Ready to start training!")
    print("")
    
    choice = input("Start Jupyter notebook now? (y/N): ").strip().lower()
    if choice in ['y', 'yes']:
        start_jupyter()
    else:
        print("📝 Manual start:")
        print("   jupyter notebook paddle_ocr_recognition_training.ipynb")

if __name__ == "__main__":
    main()
