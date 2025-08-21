"""
Resize images for PaddleOCR Recognition training
ปรับขนาดรูปภาพสำหรับการเทรน Recognition

Usage:
    python resize_images.py [options]
"""

import argparse
import sys
from pathlib import Path

# เพิ่ม path สำหรับ import utils
sys.path.append(str(Path(__file__).parent))

from utils import *

def main():
    parser = argparse.ArgumentParser(description='Resize images for Recognition training')
    parser.add_argument('--input-dir', default='input/images',
                       help='Input images directory')
    parser.add_argument('--output-dir', default='output/resized_images',
                       help='Output directory for resized images')
    parser.add_argument('--target-height', type=int, default=32,
                       help='Target image height in pixels')
    parser.add_argument('--max-width', type=int, default=512,
                       help='Maximum image width')
    parser.add_argument('--min-width', type=int, default=16,
                       help='Minimum image width')
    parser.add_argument('--quality', type=int, default=95,
                       help='JPEG quality (1-100)')
    
    args = parser.parse_args()
    
    print("🖼️  PaddleOCR Image Resizer")
    print("="*40)
    
    # ตรวจสอบ input directory
    input_path = Path(args.input_dir)
    if not input_path.exists():
        print(f"❌ Input directory not found: {args.input_dir}")
        return
    
    # สร้าง output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # หาไฟล์รูปภาพทั้งหมด
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(input_path.glob(f'*{ext}'))
        image_files.extend(input_path.glob(f'*{ext.upper()}'))
    
    if not image_files:
        print(f"❌ No image files found in {args.input_dir}")
        return
    
    print(f"📊 Found {len(image_files)} images to process")
    print(f"🎯 Target size: height={args.target_height}px, width={args.min_width}-{args.max_width}px")
    
    # ประมวลผลรูปภาพ
    processed = 0
    failed = 0
    size_stats = []
    
    progress_bar = create_progress_bar(len(image_files), "Resizing images")
    
    for image_file in image_files:
        try:
            # โหลดรูปภาพ
            image = load_image_safely(image_file)
            if image is None:
                failed += 1
                continue
            
            # บันทึกขนาดเดิม
            original_height, original_width = image.shape[:2]
            
            # ปรับขนาด
            resized_image = resize_image_keep_ratio(
                image, 
                args.target_height, 
                args.max_width, 
                args.min_width
            )
            
            if resized_image is None:
                failed += 1
                continue
            
            # สร้างชื่อไฟล์ใหม่
            output_filename = f"{image_file.stem}_resized.jpg"
            output_file_path = output_path / output_filename
            
            # บันทึกรูปภาพ
            success = save_image_safely(resized_image, output_file_path, args.quality)
            
            if success:
                processed += 1
                
                # เก็บสถิติ
                new_height, new_width = resized_image.shape[:2]
                size_stats.append({
                    'original': (original_width, original_height),
                    'resized': (new_width, new_height),
                    'ratio': new_width / original_width
                })
                
                # แสดงตัวอย่าง
                if processed <= 5:
                    print(f"  ✓ {image_file.name}: {original_width}x{original_height} -> {new_width}x{new_height}")
            else:
                failed += 1
                
        except Exception as e:
            logging.error(f"Error processing {image_file}: {e}")
            failed += 1
        
        progress_bar.update(1)
    
    progress_bar.close()
    
    # สรุปผลลัพธ์
    print(f"\n📈 Resize Summary:")
    print(f"  ✅ Processed: {processed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📁 Output: {args.output_dir}")
    
    if size_stats:
        # คำนวณสถิติ
        avg_original_width = sum(s['original'][0] for s in size_stats) / len(size_stats)
        avg_resized_width = sum(s['resized'][0] for s in size_stats) / len(size_stats)
        avg_ratio = sum(s['ratio'] for s in size_stats) / len(size_stats)
        
        print(f"\n📊 Size Statistics:")
        print(f"  Original width (avg): {avg_original_width:.1f}px")
        print(f"  Resized width (avg): {avg_resized_width:.1f}px")
        print(f"  Scale ratio (avg): {avg_ratio:.3f}")
        print(f"  Height: {args.target_height}px (all images)")
    
    # บันทึกรายงาน
    report_file = "output/validation_reports/resize_report.txt"
    Path("output/validation_reports").mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("IMAGE RESIZE REPORT\n")
        f.write("="*50 + "\n\n")
        f.write(f"Input directory: {args.input_dir}\n")
        f.write(f"Output directory: {args.output_dir}\n")
        f.write(f"Target height: {args.target_height}px\n")
        f.write(f"Width range: {args.min_width}-{args.max_width}px\n")
        f.write(f"JPEG quality: {args.quality}%\n\n")
        f.write(f"Results:\n")
        f.write(f"  Total files: {len(image_files)}\n")
        f.write(f"  Processed: {processed}\n")
        f.write(f"  Failed: {failed}\n")
        f.write(f"  Success rate: {(processed / len(image_files) * 100):.1f}%\n\n")
        
        if size_stats:
            f.write("Size Statistics:\n")
            f.write(f"  Average original width: {avg_original_width:.1f}px\n")
            f.write(f"  Average resized width: {avg_resized_width:.1f}px\n")
            f.write(f"  Average scale ratio: {avg_ratio:.3f}\n")
    
    print(f"\n📋 Report saved: {report_file}")
    
    if processed > 0:
        print(f"\n🚀 Next steps:")
        print(f"1. Check resized images in: {args.output_dir}")
        print(f"2. Update annotation file to point to resized images")
        print(f"3. Validate data: python scripts/validate_data.py")

if __name__ == "__main__":
    main()
