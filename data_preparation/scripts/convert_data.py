"""
Convert existing data to PaddleOCR Recognition format
แปลงข้อมูลเดิมให้เป็นรูปแบบที่เหมาะสำหรับ Recognition training

Usage:
    python convert_data.py [options]
    
Options:
    --input-images: Path to input images directory (default: input/images)
    --input-labels: Path to input labels file (default: input/labels.txt)
    --output-dir: Output directory (default: output/recognition_dataset)
    --target-height: Target image height in pixels (default: 32)
    --train-ratio: Training data ratio (default: 0.8)
"""

import argparse
import sys
from pathlib import Path

# เพิ่ม path สำหรับ import utils
sys.path.append(str(Path(__file__).parent))

from utils import *

def main():
    parser = argparse.ArgumentParser(description='Convert data to Recognition format')
    parser.add_argument('--input-images', default='input/images', 
                       help='Path to input images directory')
    parser.add_argument('--input-labels', default='input/labels.txt',
                       help='Path to input labels file')
    parser.add_argument('--output-dir', default='output/recognition_dataset',
                       help='Output directory')
    parser.add_argument('--target-height', type=int, default=32,
                       help='Target image height in pixels')
    parser.add_argument('--train-ratio', type=float, default=0.8,
                       help='Training data ratio')
    parser.add_argument('--max-width', type=int, default=512,
                       help='Maximum image width')
    parser.add_argument('--min-width', type=int, default=16,
                       help='Minimum image width')
    
    args = parser.parse_args()
    
    print("🚀 PaddleOCR Recognition Data Converter")
    print("="*50)
    
    # ตรวจสอบ input files
    if not Path(args.input_images).exists():
        print(f"❌ Input images directory not found: {args.input_images}")
        return
    
    if not Path(args.input_labels).exists():
        print(f"❌ Input labels file not found: {args.input_labels}")
        return
    
    # สร้าง directories
    setup_directories()
    
    # Step 1: Parse labels
    print("\n📝 Step 1: Parsing label file...")
    labels = parse_label_file(args.input_labels, args.input_images)
    
    if not labels:
        print("❌ No valid labels found!")
        return
    
    print(f"✅ Found {len(labels)} labels")
    
    # Step 2: Validate data
    print("\n🔍 Step 2: Validating image-text pairs...")
    valid_labels = []
    error_log = []
    
    progress_bar = create_progress_bar(len(labels), "Validating")
    
    for label in labels:
        is_valid, message = validate_image_text_pair(
            label['image_path'], 
            label['text'], 
            args.input_images
        )
        
        if is_valid:
            valid_labels.append(label)
        else:
            error_log.append(f"Line {label['line_number']}: {message}")
            logging.warning(f"Invalid data at line {label['line_number']}: {message}")
        
        progress_bar.update(1)
    
    progress_bar.close()
    
    print(f"✅ Valid pairs: {len(valid_labels)}")
    print(f"❌ Invalid pairs: {len(error_log)}")
    
    if not valid_labels:
        print("❌ No valid data found!")
        return
    
    # บันทึก error log
    if error_log:
        with open('output/validation_reports/validation_errors.txt', 'w', encoding='utf-8') as f:
            f.write("VALIDATION ERRORS\n")
            f.write("="*50 + "\n\n")
            for error in error_log:
                f.write(f"{error}\n")
    
    # Step 3: Split data
    print("\n📊 Step 3: Splitting data...")
    train_labels, val_labels = split_data(valid_labels, args.train_ratio)
    
    # Step 4: Process images
    print("\n🖼️  Step 4: Processing and resizing images...")
    
    processed_count = 0
    failed_count = 0
    
    # Process training images
    train_annotation_lines = []
    progress_bar = create_progress_bar(len(train_labels), "Processing train images")
    
    for label in train_labels:
        success = process_single_image(
            label, args.input_images, 
            'output/recognition_dataset/images/train',
            args.target_height, args.max_width, args.min_width
        )
        
        if success:
            # สร้างบรรทัด annotation
            new_image_path = f"images/train/{Path(label['image_path']).stem}_resized.jpg"
            train_annotation_lines.append(f"{new_image_path}\t{label['text']}")
            processed_count += 1
        else:
            failed_count += 1
        
        progress_bar.update(1)
    
    progress_bar.close()
    
    # Process validation images
    val_annotation_lines = []
    progress_bar = create_progress_bar(len(val_labels), "Processing val images")
    
    for label in val_labels:
        success = process_single_image(
            label, args.input_images,
            'output/recognition_dataset/images/val',
            args.target_height, args.max_width, args.min_width
        )
        
        if success:
            # สร้างบรรทัด annotation
            new_image_path = f"images/val/{Path(label['image_path']).stem}_resized.jpg"
            val_annotation_lines.append(f"{new_image_path}\t{label['text']}")
            processed_count += 1
        else:
            failed_count += 1
        
        progress_bar.update(1)
    
    progress_bar.close()
    
    # Step 5: Save annotations
    print("\n📋 Step 5: Saving annotations...")
    
    # บันทึก train annotation
    with open('output/recognition_dataset/annotations/train_annotation.txt', 'w', encoding='utf-8') as f:
        for line in train_annotation_lines:
            f.write(f"{line}\n")
    
    # บันทึก val annotation
    with open('output/recognition_dataset/annotations/val_annotation.txt', 'w', encoding='utf-8') as f:
        for line in val_annotation_lines:
            f.write(f"{line}\n")
    
    print(f"✅ Saved train annotation: {len(train_annotation_lines)} entries")
    print(f"✅ Saved val annotation: {len(val_annotation_lines)} entries")
    
    # Step 6: Create metadata
    print("\n📊 Step 6: Creating metadata...")
    
    char_dict = create_character_dict(valid_labels)
    metadata = save_dataset_metadata(
        train_labels, val_labels, char_dict,
        'output/recognition_dataset'
    )
    
    # Step 7: Summary
    print("\n📈 Step 7: Generating summary...")
    log_processing_summary(processed_count, failed_count)
    
    # แสดงตัวอย่างผลลัพธ์
    print("\n🎯 Sample results:")
    print("Training annotation (first 5 lines):")
    for line in train_annotation_lines[:5]:
        print(f"  {line}")
    
    if len(train_annotation_lines) > 5:
        print(f"  ... and {len(train_annotation_lines) - 5} more")
    
    print(f"\n✅ Data conversion completed!")
    print(f"📁 Output directory: output/recognition_dataset/")
    print(f"📊 Statistics: {metadata['text_statistics']}")
    print(f"🔤 Characters: {metadata['character_info']['total_characters']}")
    
    print(f"\n🚀 Next steps:")
    print(f"1. Review results in: output/validation_reports/")
    print(f"2. Upload to S3: python scripts/upload_to_s3.py")
    print(f"3. Start training: ../paddle_ocr_recognition_training.ipynb")

def process_single_image(label, input_dir, output_dir, target_height, max_width, min_width):
    """ประมวลผลรูปภาพหนึ่งไฟล์"""
    try:
        # โหลดรูปภาพ
        input_path = Path(input_dir) / label['image_path']
        image = load_image_safely(input_path)
        
        if image is None:
            return False
        
        # ปรับขนาด
        resized_image = resize_image_keep_ratio(
            image, target_height, max_width, min_width
        )
        
        if resized_image is None:
            return False
        
        # สร้างชื่อไฟล์ใหม่
        output_filename = f"{Path(label['image_path']).stem}_resized.jpg"
        output_path = Path(output_dir) / output_filename
        
        # บันทึกรูปภาพ
        success = save_image_safely(resized_image, output_path)
        
        return success
        
    except Exception as e:
        logging.error(f"Error processing {label['image_path']}: {e}")
        return False

if __name__ == "__main__":
    main()
