"""
Demo script สำหรับสร้างข้อมูลตัวอย่าง
ใช้สำหรับทดสอบระบบ data preparation

Usage:
    python create_demo_data.py
"""

import sys
from pathlib import Path

# เพิ่ม path สำหรับ import utils
sys.path.append(str(Path(__file__).parent))

try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
except ImportError:
    print("❌ Required packages not installed. Run:")
    print("pip install Pillow numpy")
    sys.exit(1)

def create_demo_data():
    """สร้างข้อมูลตัวอย่างสำหรับทดสอบ"""
    print("🎨 Creating demo data for testing...")
    
    # ข้อความตัวอย่าง
    sample_texts = [
        "สวัสดีครับ",
        "PaddleOCR", 
        "ภาษาไทย",
        "Hello World",
        "1234567890",
        "Recognition Test",
        "สำเร็จแล้ว",
        "Machine Learning",
        "Text Detection",
        "Deep Learning"
    ]
    
    # สร้างโฟลเดอร์ demo
    demo_dir = Path("input/demo_images")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    # สร้างรูปภาพตัวอย่าง
    created_images = []
    
    for i, text in enumerate(sample_texts, 1):
        # สร้างรูปภาพ
        img_width = max(200, len(text) * 15)  # ปรับความกว้างตามข้อความ
        img_height = 60
        
        # สร้างพื้นหลังสีขาว
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)
        
        # เขียนข้อความ (ใช้ font เริ่มต้น)
        try:
            # คำนวณตำแหน่งกลาง
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (img_width - text_width) // 2
            y = (img_height - text_height) // 2
            
            draw.text((x, y), text, fill='black')
            
        except Exception as e:
            print(f"⚠️  Could not draw text '{text}': {e}")
            # วาดกรอบแทน
            draw.rectangle([10, 10, img_width-10, img_height-10], outline='black', width=2)
            draw.text((15, 15), f"Text {i}", fill='black')
        
        # บันทึกรูปภาพ
        img_filename = f"demo_{i:03d}.jpg"
        img_path = demo_dir / img_filename
        img.save(img_path, 'JPEG', quality=95)
        
        created_images.append({
            'filename': img_filename,
            'text': text,
            'path': img_path
        })
        
        print(f"  ✓ Created: {img_filename} -> '{text}'")
    
    # สร้างไฟล์ labels ตัวอย่าง
    labels_file = Path("input/demo_labels.txt")
    
    with open(labels_file, 'w', encoding='utf-8') as f:
        for img_info in created_images:
            # เขียนในรูปแบบ tab-separated
            f.write(f"demo_images/{img_info['filename']}\t{img_info['text']}\n")
    
    print(f"\n✅ Demo data created:")
    print(f"  📁 Images: {demo_dir} ({len(created_images)} files)")
    print(f"  📝 Labels: {labels_file}")
    
    print(f"\n🧪 Test the system:")
    print(f"  python scripts/convert_data.py --input-images input/demo_images --input-labels input/demo_labels.txt")
    print(f"  python scripts/validate_data.py")

def create_sample_labels_file():
    """สร้างไฟล์ labels ตัวอย่างหลายรูปแบบ"""
    
    # ตัวอย่างรูปแบบต่างๆ
    samples = {
        'tab_separated.txt': [
            "img_001.jpg\tสวัสดีครับ",
            "img_002.jpg\tPaddleOCR",
            "img_003.jpg\tHello World"
        ],
        'space_separated.txt': [
            "img_001.jpg สวัสดีครับ",
            "img_002.jpg PaddleOCR", 
            "img_003.jpg Hello World"
        ],
        'json_lines.txt': [
            '{"image": "img_001.jpg", "text": "สวัสดีครับ"}',
            '{"image": "img_002.jpg", "text": "PaddleOCR"}',
            '{"image": "img_003.jpg", "text": "Hello World"}'
        ]
    }
    
    sample_dir = Path("input/samples")
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    for filename, lines in samples.items():
        file_path = sample_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(f"{line}\n")
        
        print(f"✓ Created sample: {file_path}")

if __name__ == "__main__":
    print("🚀 Demo Data Creator for PaddleOCR Recognition")
    print("="*50)
    
    try:
        create_demo_data()
        create_sample_labels_file()
        
        print(f"\n🎯 Demo data ready!")
        print(f"You can now test the data preparation system.")
        
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        print(f"Please check that required packages are installed:")
