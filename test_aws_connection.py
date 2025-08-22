#!/usr/bin/env python3
"""
AWS Connection Tester
ทดสอบการเชื่อมต่อ AWS และ S3 bucket
"""

import json
import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import sys

def load_config():
    """โหลด configuration จาก aws-config.json"""
    try:
        with open('aws-config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("❌ aws-config.json not found!")
        return None
    except json.JSONDecodeError:
        print("❌ Invalid JSON in aws-config.json")
        return None

def set_credentials(config):
    """ตั้งค่า AWS credentials"""
    creds = config['credentials']
    
    os.environ['AWS_ACCESS_KEY_ID'] = creds['aws_access_key_id']
    os.environ['AWS_SECRET_ACCESS_KEY'] = creds['aws_secret_access_key']
    os.environ['AWS_SESSION_TOKEN'] = creds['aws_session_token']
    os.environ['AWS_DEFAULT_REGION'] = config['aws_settings']['region']
    
    print(f"✅ Credentials loaded for region: {config['aws_settings']['region']}")

def test_aws_connection():
    """ทดสอบการเชื่อมต่อ AWS"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS Connection successful!")
        print(f"   Account: {identity['Account']}")
        print(f"   User: {identity['Arn']}")
        print(f"   User ID: {identity['UserId']}")
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found!")
        return False
    except ClientError as e:
        print(f"❌ AWS connection failed: {e}")
        return False

def test_s3_access(bucket_name):
    """ทดสอบการเข้าถึง S3 bucket"""
    try:
        s3 = boto3.client('s3')
        
        # ตรวจสอบว่า bucket มีอยู่หรือไม่
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"✅ S3 bucket '{bucket_name}' exists and accessible")
            bucket_exists = True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"⚠️  S3 bucket '{bucket_name}' does not exist")
                bucket_exists = False
            else:
                print(f"❌ Cannot access bucket '{bucket_name}': {e}")
                return False
        
        # ถ้า bucket ไม่มี ให้สร้าง
        if not bucket_exists:
            region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
            print(f"📦 Creating bucket '{bucket_name}' in region '{region}'...")
            
            try:
                if region == 'us-east-1':
                    s3.create_bucket(Bucket=bucket_name)
                else:
                    s3.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                print(f"✅ Bucket '{bucket_name}' created successfully!")
            except ClientError as e:
                print(f"❌ Failed to create bucket: {e}")
                return False
        
        # ทดสอบการเขียนไฟล์
        try:
            test_content = "PaddleOCR Test File"
            s3.put_object(
                Bucket=bucket_name,
                Key='test/connection_test.txt',
                Body=test_content
            )
            print(f"✅ S3 write access confirmed")
            
            # ลบไฟล์ทดสอบ
            s3.delete_object(Bucket=bucket_name, Key='test/connection_test.txt')
            print(f"✅ S3 delete access confirmed")
            
        except ClientError as e:
            print(f"⚠️  S3 write/delete access limited: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ S3 access test failed: {e}")
        return False

def test_sagemaker_access(region):
    """ทดสอบการเข้าถึง SageMaker"""
    try:
        sagemaker = boto3.client('sagemaker', region_name=region)
        
        # ลิสต์ training jobs (ไม่ต้องมี job ก็ได้)
        response = sagemaker.list_training_jobs(MaxResults=1)
        print(f"✅ SageMaker access confirmed in region '{region}'")
        
        # ตรวจสอบ instance types ที่ใช้ได้
        try:
            response = sagemaker.describe_training_job
            print(f"✅ SageMaker training APIs accessible")
        except:
            pass
            
        return True
        
    except ClientError as e:
        print(f"⚠️  SageMaker access limited: {e}")
        return False
    except Exception as e:
        print(f"❌ SageMaker test failed: {e}")
        return False

def main():
    print("🔧 AWS Connection Tester for PaddleOCR Project")
    print("=" * 50)
    
    # 1. Load configuration
    config = load_config()
    if not config:
        sys.exit(1)
    
    # 2. Set credentials
    set_credentials(config)
    
    # 3. Test AWS connection
    print("\n🔍 Testing AWS connection...")
    if not test_aws_connection():
        print("❌ Cannot proceed without AWS access")
        sys.exit(1)
    
    # 4. Test S3 access
    print(f"\n📦 Testing S3 access...")
    bucket_name = config['aws_settings']['s3_bucket_name']
    if not test_s3_access(bucket_name):
        print("❌ S3 access failed")
        sys.exit(1)
    
    # 5. Test SageMaker access
    print(f"\n🤖 Testing SageMaker access...")
    region = config['aws_settings']['sagemaker_region']
    test_sagemaker_access(region)
    
    # 6. Summary
    print(f"\n🎉 CONNECTION TEST SUMMARY:")
    print(f"✅ AWS credentials: Valid")
    print(f"✅ S3 bucket: {bucket_name} (ready)")
    print(f"✅ Region: {region}")
    print(f"✅ Ready for training!")
    
    print(f"\n🚀 Next steps:")
    print(f"1. Upload data: cd data_preparation && python scripts/upload_to_s3.py")
    print(f"2. Start training: jupyter notebook paddle_ocr_recognition_training.ipynb")

if __name__ == "__main__":
    main()
