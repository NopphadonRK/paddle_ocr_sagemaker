"""
Validate Recognition dataset
ตรวจสอบความถูกต้องของข้อมูล Recognition dataset

Usage:
    python validate_data.py [options]
"""

import argparse
import sys
from pathlib import Path
import json

# เพิ่ม path สำหรับ import utils
sys.path.append(str(Path(__file__).parent))

from utils import *

def main():
    parser = argparse.ArgumentParser(description='Validate Recognition dataset')
    parser.add_argument('--dataset-dir', default='output/recognition_dataset',
                       help='Dataset directory to validate')
    parser.add_argument('--check-images', action='store_true', default=True,
                       help='Check if image files exist and are valid')
    parser.add_argument('--check-text', action='store_true', default=True,
                       help='Check text content validity')
    parser.add_argument('--max-samples', type=int, default=100,
                       help='Maximum samples to check in detail (0 = all)')
    
    args = parser.parse_args()
    
    print("🔍 PaddleOCR Recognition Dataset Validator")
    print("="*50)
    
    dataset_path = Path(args.dataset_dir)
    if not dataset_path.exists():
        print(f"❌ Dataset directory not found: {args.dataset_dir}")
        return
    
    # ตรวจสอบโครงสร้างโฟลเดอร์
    print("\n📁 Checking directory structure...")
    required_dirs = [
        'images/train',
        'images/val', 
        'annotations',
        'metadata'
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = dataset_path / dir_name
        if dir_path.exists():
            print(f"  ✅ {dir_name}")
        else:
            print(f"  ❌ {dir_name}")
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"\n❌ Missing directories: {missing_dirs}")
        print("Please run convert_data.py first to create proper structure")
        return
    
    # ตรวจสอบไฟล์ annotation
    print("\n📝 Checking annotation files...")
    
    train_annotation = dataset_path / 'annotations/train_annotation.txt'
    val_annotation = dataset_path / 'annotations/val_annotation.txt'
    
    validation_results = {
        'train': validate_annotation_file(train_annotation, dataset_path, 'train', args),
        'val': validate_annotation_file(val_annotation, dataset_path, 'val', args)
    }
    
    # ตรวจสอบ metadata
    print("\n📊 Checking metadata...")
    metadata_file = dataset_path / 'metadata/dataset_info.json'
    char_dict_file = dataset_path / 'metadata/character_dict.txt'
    
    metadata_valid = True
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"  ✅ dataset_info.json")
            print(f"    - Total samples: {metadata.get('dataset_info', {}).get('total_samples', 'unknown')}")
            print(f"    - Train samples: {metadata.get('dataset_info', {}).get('train_samples', 'unknown')}")
            print(f"    - Val samples: {metadata.get('dataset_info', {}).get('val_samples', 'unknown')}")
            print(f"    - Characters: {metadata.get('character_info', {}).get('total_characters', 'unknown')}")
        except Exception as e:
            print(f"  ❌ dataset_info.json (invalid JSON: {e})")
            metadata_valid = False
    else:
        print(f"  ❌ dataset_info.json (not found)")
        metadata_valid = False
    
    if char_dict_file.exists():
        try:
            with open(char_dict_file, 'r', encoding='utf-8') as f:
                char_count = len(f.readlines())
            print(f"  ✅ character_dict.txt ({char_count} characters)")
        except Exception as e:
            print(f"  ❌ character_dict.txt (error reading: {e})")
            metadata_valid = False
    else:
        print(f"  ❌ character_dict.txt (not found)")
        metadata_valid = False
    
    # สรุปผลการตรวจสอบ
    print("\n📈 Validation Summary:")
    print("="*30)
    
    total_valid = validation_results['train']['valid'] + validation_results['val']['valid']
    total_invalid = validation_results['train']['invalid'] + validation_results['val']['invalid']
    total_samples = total_valid + total_invalid
    
    print(f"📊 Overall Statistics:")
    print(f"  Total samples: {total_samples}")
    print(f"  Valid samples: {total_valid}")
    print(f"  Invalid samples: {total_invalid}")
    if total_samples > 0:
        print(f"  Validity rate: {(total_valid / total_samples * 100):.1f}%")
    
    print(f"\n📋 Training Set:")
    print(f"  Valid: {validation_results['train']['valid']}")
    print(f"  Invalid: {validation_results['train']['invalid']}")
    print(f"  Issues: {len(validation_results['train']['issues'])}")
    
    print(f"\n📋 Validation Set:")
    print(f"  Valid: {validation_results['val']['valid']}")
    print(f"  Invalid: {validation_results['val']['invalid']}")
    print(f"  Issues: {len(validation_results['val']['issues'])}")
    
    # แสดงปัญหาที่พบ
    all_issues = validation_results['train']['issues'] + validation_results['val']['issues']
    if all_issues:
        print(f"\n⚠️  Issues Found ({len(all_issues)}):")
        for issue in all_issues[:10]:  # แสดง 10 ปัญหาแรก
            print(f"  • {issue}")
        
        if len(all_issues) > 10:
            print(f"  ... และอีก {len(all_issues) - 10} ปัญหา")
    
    # บันทึกรายงานการตรวจสอบ
    save_validation_report(validation_results, dataset_path, metadata_valid)
    
    # แนะนำขั้นตอนถัดไป
    if total_valid > 0:
        print(f"\n✅ Dataset validation completed!")
        if total_invalid == 0:
            print(f"🎯 Perfect! All data is valid.")
            print(f"\n🚀 Next steps:")
            print(f"1. Upload to S3: python scripts/upload_to_s3.py")
            print(f"2. Start training: ../paddle_ocr_recognition_training.ipynb")
        else:
            print(f"⚠️  Some issues found. Check validation report.")
            print(f"\n🔧 Recommended actions:")
            print(f"1. Fix issues in source data")
            print(f"2. Re-run: python scripts/convert_data.py")
            print(f"3. Re-validate: python scripts/validate_data.py")
    else:
        print(f"\n❌ No valid data found!")
        print(f"Please check your input data and re-run convert_data.py")

def validate_annotation_file(annotation_file, dataset_root, split_name, args):
    """ตรวจสอบไฟล์ annotation"""
    result = {
        'valid': 0,
        'invalid': 0,
        'issues': [],
        'text_stats': {
            'min_length': float('inf'),
            'max_length': 0,
            'total_chars': 0,
            'unique_chars': set()
        }
    }
    
    if not annotation_file.exists():
        result['issues'].append(f"{split_name}: Annotation file not found")
        return result
    
    print(f"  📝 Checking {split_name}_annotation.txt...")
    
    with open(annotation_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"    📊 Total lines: {len(lines)}")
    
    # ตรวจสอบจำนวนที่จะเช็คในรายละเอียด
    max_check = len(lines) if args.max_samples == 0 else min(args.max_samples, len(lines))
    
    progress_bar = create_progress_bar(max_check, f"Validating {split_name}")
    
    for line_num, line in enumerate(lines[:max_check], 1):
        line = line.strip()
        if not line:
            continue
        
        # ตรวจสอบรูปแบบ tab-separated
        if '\t' not in line:
            result['issues'].append(f"{split_name} line {line_num}: No tab separator found")
            result['invalid'] += 1
            progress_bar.update(1)
            continue
        
        parts = line.split('\t', 1)
        if len(parts) != 2:
            result['issues'].append(f"{split_name} line {line_num}: Expected 2 parts, got {len(parts)}")
            result['invalid'] += 1
            progress_bar.update(1)
            continue
        
        image_path, text = parts
        
        # ตรวจสอบ image path
        if args.check_images:
            full_image_path = dataset_root / image_path
            if not full_image_path.exists():
                result['issues'].append(f"{split_name} line {line_num}: Image not found: {image_path}")
                result['invalid'] += 1
                progress_bar.update(1)
                continue
            
            # ตรวจสอบว่าโหลดรูปภาพได้
            image = load_image_safely(full_image_path)
            if image is None:
                result['issues'].append(f"{split_name} line {line_num}: Cannot load image: {image_path}")
                result['invalid'] += 1
                progress_bar.update(1)
                continue
        
        # ตรวจสอบข้อความ
        if args.check_text:
            if not text.strip():
                result['issues'].append(f"{split_name} line {line_num}: Empty text content")
                result['invalid'] += 1
                progress_bar.update(1)
                continue
            
            # เก็บสถิติข้อความ
            text_len = len(text)
            result['text_stats']['min_length'] = min(result['text_stats']['min_length'], text_len)
            result['text_stats']['max_length'] = max(result['text_stats']['max_length'], text_len)
            result['text_stats']['total_chars'] += text_len
            result['text_stats']['unique_chars'].update(text)
            
            # ตรวจสอบความยาวข้อความ
            if text_len > 100:
                result['issues'].append(f"{split_name} line {line_num}: Text too long ({text_len} chars): {text[:50]}...")
            elif text_len == 0:
                result['issues'].append(f"{split_name} line {line_num}: Empty text")
        
        result['valid'] += 1
        progress_bar.update(1)
    
    progress_bar.close()
    
    # ปรับสถิติ
    if result['text_stats']['min_length'] == float('inf'):
        result['text_stats']['min_length'] = 0
    
    print(f"    ✅ Valid: {result['valid']}")
    print(f"    ❌ Invalid: {result['invalid']}")
    if result['text_stats']['total_chars'] > 0:
        print(f"    📝 Text length: {result['text_stats']['min_length']}-{result['text_stats']['max_length']} chars")
        print(f"    🔤 Unique characters: {len(result['text_stats']['unique_chars'])}")
    
    return result

def save_validation_report(validation_results, dataset_path, metadata_valid):
    """บันทึกรายงานการตรวจสอบ"""
    report_dir = Path("output/validation_reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / "validation_report.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("RECOGNITION DATASET VALIDATION REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(f"Dataset directory: {dataset_path}\n")
        f.write(f"Validation time: {logging.Formatter().formatTime(logging.makeLogRecord({}))}\n\n")
        
        # สรุปผลรวม
        total_valid = validation_results['train']['valid'] + validation_results['val']['valid']
        total_invalid = validation_results['train']['invalid'] + validation_results['val']['invalid']
        
        f.write("SUMMARY\n")
        f.write("-" * 20 + "\n")
        f.write(f"Total samples: {total_valid + total_invalid}\n")
        f.write(f"Valid samples: {total_valid}\n")
        f.write(f"Invalid samples: {total_invalid}\n")
        if total_valid + total_invalid > 0:
            f.write(f"Validity rate: {(total_valid / (total_valid + total_invalid) * 100):.1f}%\n")
        f.write(f"Metadata valid: {'Yes' if metadata_valid else 'No'}\n\n")
        
        # รายละเอียดแต่ละ split
        for split_name, results in validation_results.items():
            f.write(f"{split_name.upper()} SET\n")
            f.write("-" * 20 + "\n")
            f.write(f"Valid samples: {results['valid']}\n")
            f.write(f"Invalid samples: {results['invalid']}\n")
            f.write(f"Issues found: {len(results['issues'])}\n")
            
            if results['text_stats']['total_chars'] > 0:
                f.write(f"Text length range: {results['text_stats']['min_length']}-{results['text_stats']['max_length']} chars\n")
                f.write(f"Unique characters: {len(results['text_stats']['unique_chars'])}\n")
            
            f.write("\n")
        
        # รายการปัญหา
        all_issues = validation_results['train']['issues'] + validation_results['val']['issues']
        if all_issues:
            f.write("ISSUES FOUND\n")
            f.write("-" * 20 + "\n")
            for issue in all_issues:
                f.write(f"• {issue}\n")
    
    print(f"\n📋 Validation report saved: {report_file}")

if __name__ == "__main__":
    main()
