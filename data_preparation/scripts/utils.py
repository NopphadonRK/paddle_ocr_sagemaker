"""
Utility functions for data preparation
ฟังก์ชันสำหรับใช้ร่วมกันในการเตรียมข้อมูล
"""

import os
import json
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from tqdm import tqdm
import logging

# ตั้งค่า logging
# สร้าง directory ก่อน
Path('output/validation_reports').mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/validation_reports/processing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def setup_directories():
    """สร้าง directories ที่จำเป็น"""
    directories = [
        'output/recognition_dataset/images/train',
        'output/recognition_dataset/images/val', 
        'output/recognition_dataset/annotations',
        'output/recognition_dataset/metadata',
        'output/validation_reports'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory: {directory}")

def load_image_safely(image_path):
    """โหลดรูปภาพอย่างปลอดภัย"""
    try:
        # ลองใช้ OpenCV ก่อน
        img = cv2.imread(str(image_path))
        if img is not None:
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # ถ้าไม่ได้ ใช้ PIL
        img = Image.open(image_path)
        return np.array(img.convert('RGB'))
        
    except Exception as e:
        logging.error(f"Cannot load image {image_path}: {e}")
        return None

def save_image_safely(image, output_path, quality=95):
    """บันทึกรูปภาพอย่างปลอดภัย"""
    try:
        # แปลงกลับเป็น PIL Image
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # บันทึกด้วยคุณภาพที่กำหนด
        image.save(output_path, 'JPEG', quality=quality, optimize=True)
        return True
        
    except Exception as e:
        logging.error(f"Cannot save image {output_path}: {e}")
        return False

def resize_image_keep_ratio(image, target_height=32, max_width=512, min_width=16):
    """ปรับขนาดรูปภาพโดยคงสัดส่วน"""
    if image is None:
        return None
    
    height, width = image.shape[:2]
    
    # คำนวณความกว้างใหม่
    ratio = target_height / height
    new_width = int(width * ratio)
    
    # จำกัดความกว้าง
    new_width = max(min_width, min(new_width, max_width))
    
    # ปรับขนาด
    resized = cv2.resize(image, (new_width, target_height), interpolation=cv2.INTER_AREA)
    
    return resized

def parse_label_file(label_file_path, image_dir):
    """แปลงไฟล์ label หลากหลายรูปแบบ"""
    logging.info(f"Parsing label file: {label_file_path}")
    
    labels = []
    
    try:
        with open(label_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # ลองแปลงรูปแบบต่างๆ
            image_path, text = parse_label_line(line, image_dir)
            
            if image_path and text:
                labels.append({
                    'image_path': image_path,
                    'text': text,
                    'line_number': line_num
                })
            else:
                logging.warning(f"Could not parse line {line_num}: {line}")
    
    except Exception as e:
        logging.error(f"Error reading label file: {e}")
        return []
    
    logging.info(f"Parsed {len(labels)} labels successfully")
    return labels

def parse_label_line(line, image_dir):
    """แปลงบรรทัด label ในรูปแบบต่างๆ"""
    # รูปแบบ 1: image_path\ttext (มาตรฐาน Recognition)
    if '\t' in line:
        parts = line.split('\t', 1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
    
    # รูปแบบ 2: image_path text (คั่นด้วย space)
    parts = line.split(' ', 1)
    if len(parts) == 2:
        image_path = parts[0].strip()
        text = parts[1].strip()
        
        # ตรวจสอบว่าเป็นชื่อไฟล์รูปภาพจริง
        if any(image_path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp']):
            return image_path, text
    
    # รูปแบบ 3: JSON format
    if line.startswith('{') and line.endswith('}'):
        try:
            data = json.loads(line)
            if 'image' in data and 'text' in data:
                return data['image'], data['text']
        except json.JSONDecodeError:
            pass
    
    # รูปแบบ 4: เฉพาะข้อความ (ให้หาไฟล์รูปภาพที่ตรงกัน)
    # สมมติว่าไฟล์รูปภาพมีชื่อเป็น img_001.jpg, img_002.jpg, ...
    if not any(ext in line for ext in ['.jpg', '.jpeg', '.png', '.bmp']):
        # หาไฟล์รูปภาพที่อาจจะตรงกัน
        image_files = list(Path(image_dir).glob('*.*'))
        if image_files:
            # ใช้ไฟล์แรกที่เจอ (ควรปรับให้ตรงกับลำดับ)
            return str(image_files[0].name), line.strip()
    
    return None, None

def validate_image_text_pair(image_path, text, image_dir):
    """ตรวจสอบคู่รูปภาพและข้อความ"""
    full_image_path = Path(image_dir) / image_path
    
    # ตรวจสอบว่าไฟล์รูปภาพมีอยู่
    if not full_image_path.exists():
        return False, f"Image file not found: {full_image_path}"
    
    # ตรวจสอบว่าโหลดรูปภาพได้
    image = load_image_safely(full_image_path)
    if image is None:
        return False, f"Cannot load image: {full_image_path}"
    
    # ตรวจสอบขนาดรูปภาพ
    height, width = image.shape[:2]
    if height < 8 or width < 8:
        return False, f"Image too small: {width}x{height}"
    
    # ตรวจสอบข้อความ
    if not text or len(text.strip()) == 0:
        return False, "Empty text content"
    
    # ตรวจสอบความยาวข้อความ
    if len(text) > 100:  # ปรับตามความเหมาะสม
        return False, f"Text too long: {len(text)} characters"
    
    return True, "Valid"

def split_data(labels, train_ratio=0.8, seed=42):
    """แบ่งข้อมูลเป็น train/validation"""
    np.random.seed(seed)
    
    # สับข้อมูล
    shuffled_indices = np.random.permutation(len(labels))
    
    # แบ่งข้อมูล
    train_size = int(len(labels) * train_ratio)
    
    train_indices = shuffled_indices[:train_size]
    val_indices = shuffled_indices[train_size:]
    
    train_labels = [labels[i] for i in train_indices]
    val_labels = [labels[i] for i in val_indices]
    
    logging.info(f"Split data: {len(train_labels)} train, {len(val_labels)} validation")
    
    return train_labels, val_labels

def create_character_dict(labels):
    """สร้าง character dictionary จากข้อมูล"""
    characters = set()
    
    for label in labels:
        text = label['text']
        for char in text:
            characters.add(char)
    
    # เรียงตัวอักษร
    sorted_chars = sorted(list(characters))
    
    # เพิ่มตัวอักษรพิเศษ
    special_chars = ['<blank>', '<eos>', '<sos>', '<unk>']
    char_dict = special_chars + sorted_chars
    
    logging.info(f"Created character dictionary with {len(char_dict)} characters")
    
    return char_dict

def save_dataset_metadata(train_labels, val_labels, char_dict, output_dir):
    """บันทึกข้อมูล metadata ของ dataset"""
    metadata = {
        'dataset_info': {
            'total_samples': len(train_labels) + len(val_labels),
            'train_samples': len(train_labels),
            'val_samples': len(val_labels),
            'train_ratio': len(train_labels) / (len(train_labels) + len(val_labels)),
        },
        'character_info': {
            'total_characters': len(char_dict),
            'character_list': char_dict
        },
        'text_statistics': calculate_text_statistics(train_labels + val_labels)
    }
    
    # บันทึก metadata
    with open(f"{output_dir}/metadata/dataset_info.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # บันทึก character dictionary
    with open(f"{output_dir}/metadata/character_dict.txt", 'w', encoding='utf-8') as f:
        for char in char_dict:
            f.write(f"{char}\n")
    
    logging.info(f"Saved metadata to {output_dir}/metadata/")
    
    return metadata

def calculate_text_statistics(labels):
    """คำนวณสถิติของข้อความ"""
    text_lengths = [len(label['text']) for label in labels]
    
    return {
        'min_length': min(text_lengths) if text_lengths else 0,
        'max_length': max(text_lengths) if text_lengths else 0,
        'avg_length': sum(text_lengths) / len(text_lengths) if text_lengths else 0,
        'total_characters': sum(text_lengths)
    }

def create_progress_bar(total, desc="Processing"):
    """สร้าง progress bar"""
    return tqdm(total=total, desc=desc, unit="items")

def log_processing_summary(processed, failed, output_file="output/validation_reports/summary.txt"):
    """บันทึกสรุปการประมวลผล"""
    summary = f"""
DATA PROCESSING SUMMARY
{'='*50}

Total processed: {processed + failed}
Successful: {processed}
Failed: {failed}
Success rate: {(processed / (processed + failed) * 100):.1f}%

Generated files:
- Training images: output/recognition_dataset/images/train/
- Validation images: output/recognition_dataset/images/val/
- Annotations: output/recognition_dataset/annotations/
- Metadata: output/recognition_dataset/metadata/

Next steps:
1. Review validation reports in output/validation_reports/
2. Upload dataset to S3: python scripts/upload_to_s3.py
3. Start training: ../paddle_ocr_recognition_training.ipynb
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(summary)
