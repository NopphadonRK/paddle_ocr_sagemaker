"""
Upload Recognition dataset to S3
อัปโหลดข้อมูล Recognition dataset ไปยัง Amazon S3

Usage:
    python upload_to_s3.py --bucket your-bucket-name [options]
    
Requirements:
    - AWS credentials configured (aws configure)
    - S3 bucket created and accessible
"""

import argparse
import sys
from pathlib import Path
import time

# เพิ่ม path สำหรับ import utils
sys.path.append(str(Path(__file__).parent))

try:
    import boto3
    from botocore.exceptions import NoCredentialsError, ClientError
except ImportError:
    print("❌ boto3 not installed. Run: pip install boto3")
    sys.exit(1)

from utils import *

def main():
    parser = argparse.ArgumentParser(description='Upload Recognition dataset to S3')
    parser.add_argument('--bucket', required=True,
                       help='S3 bucket name')
    parser.add_argument('--dataset-dir', default='output/recognition_dataset',
                       help='Local dataset directory')
    parser.add_argument('--s3-prefix', default='recognition-data',
                       help='S3 prefix (folder) for the dataset')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be uploaded without actually uploading')
    parser.add_argument('--skip-existing', action='store_true',
                       help='Skip files that already exist in S3')
    parser.add_argument('--max-files', type=int, default=0,
                       help='Maximum number of files to upload (0 = all)')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    print("☁️  PaddleOCR S3 Dataset Uploader")
    print("="*50)
    
    # ตรวจสอบ dataset directory
    dataset_path = Path(args.dataset_dir)
    if not dataset_path.exists():
        print(f"❌ Dataset directory not found: {args.dataset_dir}")
        print("Please run convert_data.py first to create the dataset")
        return
    
    # ตรวจสอบ AWS credentials
    print("\n🔐 Checking AWS credentials...")
    try:
        s3_client = boto3.client('s3')
        sts_client = boto3.client('sts')
        
        # ตรวจสอบ identity
        identity = sts_client.get_caller_identity()
        print(f"  ✅ AWS Account: {identity.get('Account', 'unknown')}")
        print(f"  ✅ User: {identity.get('Arn', 'unknown').split('/')[-1]}")
        
    except NoCredentialsError:
        print("❌ AWS credentials not found!")
        print("Please run: aws configure")
        return
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        return
    
    # ตรวจสอบ S3 bucket
    print(f"\n🪣 Checking S3 bucket: {args.bucket}")
    try:
        s3_client.head_bucket(Bucket=args.bucket)
        print(f"  ✅ Bucket accessible")
        
        # ตรวจสอบ bucket region
        bucket_location = s3_client.get_bucket_location(Bucket=args.bucket)
        region = bucket_location.get('LocationConstraint') or 'us-east-1'
        print(f"  📍 Region: {region}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ Bucket not found: {args.bucket}")
        elif error_code == '403':
            print(f"❌ Access denied to bucket: {args.bucket}")
        else:
            print(f"❌ Bucket error: {e}")
        return
    
    # สร้างรายการไฟล์ที่จะอัปโหลด
    print(f"\n📂 Scanning dataset files...")
    
    files_to_upload = []
    total_size = 0
    
    for file_path in dataset_path.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(dataset_path)
            s3_key = f"{args.s3_prefix}/{relative_path}"
            file_size = file_path.stat().st_size
            
            files_to_upload.append({
                'local_path': file_path,
                'relative_path': relative_path,
                's3_key': s3_key,
                'size': file_size
            })
            total_size += file_size
    
    if not files_to_upload:
        print("❌ No files found to upload!")
        return
    
    # จำกัดจำนวนไฟล์หากต้องการ
    if args.max_files > 0 and len(files_to_upload) > args.max_files:
        print(f"⚠️  Limiting upload to {args.max_files} files (out of {len(files_to_upload)})")
        files_to_upload = files_to_upload[:args.max_files]
        total_size = sum(f['size'] for f in files_to_upload)
    
    print(f"  📊 Files to upload: {len(files_to_upload)}")
    print(f"  📏 Total size: {format_size(total_size)}")
    print(f"  🎯 S3 destination: s3://{args.bucket}/{args.s3_prefix}/")
    
    # แสดงตัวอย่างไฟล์
    print(f"\n📋 Sample files:")
    for file_info in files_to_upload[:5]:
        size_str = format_size(file_info['size'])
        print(f"  📄 {file_info['relative_path']} ({size_str})")
    
    if len(files_to_upload) > 5:
        print(f"  ... และอีก {len(files_to_upload) - 5} ไฟล์")
    
    # Dry run
    if args.dry_run:
        print(f"\n🔍 DRY RUN - No files will be uploaded")
        print(f"Command to actually upload:")
        print(f"  python {Path(__file__).name} --bucket {args.bucket} --s3-prefix {args.s3_prefix}")
        return
    
    # ยืนยันการอัปโหลด
    if not args.yes:
        print(f"\n⚠️  Ready to upload {len(files_to_upload)} files ({format_size(total_size)}) to S3")
        
        try:
            import sys
            sys.stdout.flush()
            response = input("Continue? (y/N): ").strip().lower()
        except (UnicodeDecodeError, EOFError, KeyboardInterrupt):
            print("\nUpload cancelled")
            return
        except Exception as e:
            print(f"\nInput error: {e}")
            print("Assuming 'no' - upload cancelled")
            return
        
        if response not in ['y', 'yes']:
            print("Upload cancelled")
            return
    
    # เริ่มอัปโหลด
    print(f"\n📤 Starting upload...")
    
    uploaded = 0
    skipped = 0
    failed = 0
    start_time = time.time()
    
    progress_bar = create_progress_bar(len(files_to_upload), "Uploading")
    
    for file_info in files_to_upload:
        try:
            # ตรวจสอบว่าไฟล์มีอยู่ใน S3 แล้วหรือไม่
            if args.skip_existing:
                try:
                    s3_client.head_object(Bucket=args.bucket, Key=file_info['s3_key'])
                    skipped += 1
                    progress_bar.update(1)
                    continue
                except ClientError as e:
                    if e.response['Error']['Code'] != '404':
                        raise
            
            # อัปโหลดไฟล์
            s3_client.upload_file(
                str(file_info['local_path']),
                args.bucket,
                file_info['s3_key']
            )
            
            uploaded += 1
            
            # แสดงความคืบหน้า
            if uploaded <= 5:
                size_str = format_size(file_info['size'])
                print(f"  ✅ {file_info['relative_path']} ({size_str})")
            
        except Exception as e:
            failed += 1
            logging.error(f"Failed to upload {file_info['relative_path']}: {e}")
        
        progress_bar.update(1)
    
    progress_bar.close()
    
    # สรุปผลการอัปโหลด
    elapsed_time = time.time() - start_time
    
    print(f"\n📊 Upload Summary:")
    print(f"  ✅ Uploaded: {uploaded}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  ❌ Failed: {failed}")
    print(f"  ⏱️  Time: {elapsed_time:.1f} seconds")
    
    if uploaded > 0:
        avg_speed = total_size / elapsed_time if elapsed_time > 0 else 0
        print(f"  📈 Average speed: {format_size(avg_speed)}/s")
    
    # บันทึกรายงานการอัปโหลด
    save_upload_report(args, uploaded, skipped, failed, elapsed_time)
    
    # แสดงขั้นตอนถัดไป
    if uploaded > 0:
        print(f"\n✅ Upload completed!")
        print(f"\n🚀 Next steps:")
        print(f"1. Open SageMaker Jupyter Notebook")
        print(f"2. Update S3 paths in notebook:")
        print(f"   S3_BUCKET = '{args.bucket}'")
        print(f"   S3_RECOGNITION_DATA_PREFIX = '{args.s3_prefix}'")
        print(f"3. Start training: ../paddle_ocr_recognition_training.ipynb")
        
        print(f"\n📋 S3 URLs:")
        print(f"  Dataset: s3://{args.bucket}/{args.s3_prefix}/")
        print(f"  Console: https://console.aws.amazon.com/s3/buckets/{args.bucket}/?prefix={args.s3_prefix}/")
    else:
        print(f"\n⚠️  No files were uploaded")
        if failed > 0:
            print(f"Check logs for upload errors")

def format_size(size_bytes):
    """แปลงขนาดไฟล์เป็นรูปแบบที่อ่านง่าย"""
    if size_bytes == 0:
        return "0B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f}TB"

def save_upload_report(args, uploaded, skipped, failed, elapsed_time):
    """บันทึกรายงานการอัปโหลด"""
    report_dir = Path("output/validation_reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / "s3_upload_report.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("S3 UPLOAD REPORT\n")
        f.write("="*40 + "\n\n")
        f.write(f"Bucket: {args.bucket}\n")
        f.write(f"S3 Prefix: {args.s3_prefix}\n")
        f.write(f"Local Dataset: {args.dataset_dir}\n")
        f.write(f"Upload Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("RESULTS\n")
        f.write("-" * 20 + "\n")
        f.write(f"Uploaded: {uploaded}\n")
        f.write(f"Skipped: {skipped}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"Duration: {elapsed_time:.1f} seconds\n\n")
        
        f.write("S3 PATHS\n")
        f.write("-" * 20 + "\n")
        f.write(f"Dataset URL: s3://{args.bucket}/{args.s3_prefix}/\n")
        f.write(f"Images: s3://{args.bucket}/{args.s3_prefix}/images/\n")
        f.write(f"Annotations: s3://{args.bucket}/{args.s3_prefix}/annotations/\n")
        f.write(f"Metadata: s3://{args.bucket}/{args.s3_prefix}/metadata/\n")
    
    print(f"\n📋 Upload report saved: {report_file}")

if __name__ == "__main__":
    main()
