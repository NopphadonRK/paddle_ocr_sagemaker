# รูปแบบข้อมูลสำหรับ Text Recognition (Data Format Guide)

## 📋 รูปแบบไฟล์ Annotation สำหรับ Recognition

### รูปแบบมาตรฐานของ PaddleOCR Recognition
ไฟล์ annotation สำหรับ Text Recognition ต้องเป็นไฟล์ text (.txt) โดยแต่ละบรรทัดมีรูปแบบดังนี้:
```
image_path\ttext_content
```

**ไม่มีพิกัด (bounding box coordinates) เหมือน Detection**

### ตัวอย่างไฟล์ Annotation สำหรับ Recognition
```
images/word_001.jpg	สวัสดี
images/word_002.jpg	ยินดีต้อนรับ
images/word_003.jpg	PaddleOCR
images/word_004.jpg	1234567890
images/word_005.jpg	Hello World
images/word_006.jpg	深度学习
images/word_007.jpg	Machine Learning
```

## 🖼️ รูปแบบรูปภาพสำหรับ Recognition

### ไฟล์รูปภาพ (Cropped Text Images)
- **รูปแบบ**: JPG, JPEG, PNG, TIFF, BMP
- **ขนาด**: แนะนำความกว้าง 100-400 pixels, ความสูง 32-64 pixels
- **Aspect Ratio**: โดยปกติ 3:1 ถึง 10:1 (กว้างกว่าสูง)
- **เนื้อหา**: รูปภาพข้อความที่ตัด (cropped) จากรูปภาพต้นฉบับแล้ว
- **Color Space**: RGB หรือ Grayscale

### แนวทางการเตรียมรูปภาพ Recognition
```python
import cv2
import numpy as np

def preprocess_recognition_image(image_path, target_height=32):
    """
    เตรียมรูปภาพสำหรับ Text Recognition
    """
    image = cv2.imread(image_path)
    
    # ปรับขนาดให้มีความสูงเท่ากับ target_height
    h, w = image.shape[:2]
    aspect_ratio = w / h
    new_width = int(target_height * aspect_ratio)
    
    # จำกัดความกว้างสูงสุด
    max_width = 320
    if new_width > max_width:
        new_width = max_width
    
    image = cv2.resize(image, (new_width, target_height))
    
    return image
```

## 📊 โครงสร้างข้อมูลสำหรับ Text Recognition

### รูปแบบ Annotation สำหรับ Recognition
```
image_path	text_content
```

### คุณสมบัติของข้อมูล Recognition
- **Image Path**: เส้นทางไปยังรูปภาพข้อความที่ตัดแล้ว (cropped text image)
- **Text Content**: ข้อความจริงในรูปภาพ (ground truth text)
- **Separator**: Tab character (\t) เท่านั้น
- **Encoding**: UTF-8 สำหรับรองรับหลายภาษา

### ตัวอย่างข้อมูลหลายภาษา
```python
# ภาษาไทย
cropped_images/thai_001.jpg	สวัสดีครับ
cropped_images/thai_002.jpg	ยินดีต้อนรับ

# ภาษาอังกฤษ
cropped_images/eng_001.jpg	Hello World
cropped_images/eng_002.jpg	PaddleOCR

# ภาษาจีน
cropped_images/chi_001.jpg	深度学习
cropped_images/chi_002.jpg	人工智能

# ตัวเลข
cropped_images/num_001.jpg	1234567890
cropped_images/num_002.jpg	2023-08-21
```

## 🔧 เครื่องมือสร้าง Annotation สำหรับ Recognition

### 1. การแปลงจาก Detection เป็น Recognition
```python
def convert_detection_to_recognition(detection_annotation_file, images_dir, output_dir):
    """
    แปลง Detection annotation เป็น Recognition annotation
    โดยการตัดรูปภาพตาม bounding box และสร้าง annotation ใหม่
    """
    import json
    import cv2
    import os
    
    recognition_annotations = []
    os.makedirs(output_dir, exist_ok=True)
    
    with open(detection_annotation_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            
            try:
                image_path, annotation_json = line.split('\t')
                annotations = json.loads(annotation_json)
                
                # โหลดรูปภาพต้นฉบับ
                full_image_path = os.path.join(images_dir, image_path)
                image = cv2.imread(full_image_path)
                
                if image is None:
                    continue
                
                for idx, ann in enumerate(annotations):
                    text = ann['transcription']
                    points = ann['points']
                    
                    # ตัดรูปภาพตาม bounding box
                    cropped = crop_text_region(image, points)
                    
                    if cropped is not None:
                        # บันทึกรูปภาพที่ตัด
                        crop_filename = f"crop_{line_num:06d}_{idx:03d}.jpg"
                        crop_path = os.path.join(output_dir, crop_filename)
                        cv2.imwrite(crop_path, cropped)
                        
                        # สร้าง Recognition annotation
                        recognition_annotations.append(f"{crop_filename}\t{text}")
                        
            except Exception as e:
                print(f"Error processing line {line_num}: {e}")
                continue
    
    # บันทึกไฟล์ Recognition annotation
    output_annotation_file = os.path.join(output_dir, 'recognition_annotations.txt')
    with open(output_annotation_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(recognition_annotations))
    
    return output_annotation_file

def crop_text_region(image, points):
    """
    ตัดพื้นที่ข้อความจากรูปภาพ
    """
    import cv2
    import numpy as np
    
    points = np.array(points, dtype=np.int32)
    x, y, w, h = cv2.boundingRect(points)
    
    # เพิ่ม padding
    padding = 5
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(image.shape[1] - x, w + 2 * padding)
    h = min(image.shape[0] - y, h + 2 * padding)
    
    # ตัดรูปภาพ
    cropped = image[y:y+h, x:x+w]
    
    return cropped if cropped.size > 0 else None
```

## ✅ การตรวจสอบคุณภาพข้อมูล

### 1. ตรวจสอบรูปแบบ Annotation
```python
def validate_annotation_quality(annotation_file):
    """
    ตรวจสอบคุณภาพของไฟล์ annotation
    """
    issues = []
    
    with open(annotation_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                parts = line.split('\t')
                if len(parts) != 2:
                    issues.append(f"Line {line_num}: Invalid format")
                    continue
                
                image_path, annotation_json = parts
                annotations = json.loads(annotation_json)
                
                for i, ann in enumerate(annotations):
                    # ตรวจสอบ required fields
                    if 'transcription' not in ann:
                        issues.append(f"Line {line_num}, annotation {i}: Missing transcription")
                    
                    if 'points' not in ann:
                        issues.append(f"Line {line_num}, annotation {i}: Missing points")
                        continue
                    
                    points = ann['points']
                    
                    # ตรวจสอบจำนวนจุด
                    if len(points) != 4:
                        issues.append(f"Line {line_num}, annotation {i}: Must have 4 points")
                    
                    # ตรวจสอบรูปแบบจุด
                    for j, point in enumerate(points):
                        if not isinstance(point, list) or len(point) != 2:
                            issues.append(f"Line {line_num}, annotation {i}, point {j}: Invalid point format")
                    
                    # ตรวจสอบว่าจุดสร้างพื้นที่ที่สมเหตุสมผล
                    if len(points) == 4:
                        area = calculate_polygon_area(points)
                        if area < 10:  # พื้นที่น้อยเกินไป
                            issues.append(f"Line {line_num}, annotation {i}: Text area too small")
            
            except json.JSONDecodeError:
                issues.append(f"Line {line_num}: Invalid JSON")
            except Exception as e:
                issues.append(f"Line {line_num}: {str(e)}")
    
    return issues

def calculate_polygon_area(points):
    """
    คำนวณพื้นที่ของรูปสี่เหลี่ยม
    """
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    return 0.5 * abs(sum(x[i]*y[i+1] - x[i+1]*y[i] for i in range(-1, len(x)-1)))
```

### 2. ตรวจสอบการกระจายของข้อมูล
```python
def analyze_dataset_distribution(annotation_file):
    """
    วิเคราะห์การกระจายของ dataset
    """
    text_lengths = []
    text_counts_per_image = []
    character_frequency = {}
    
    with open(annotation_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                parts = line.split('\t')
                annotations = json.loads(parts[1])
                
                image_text_count = len(annotations)
                text_counts_per_image.append(image_text_count)
                
                for ann in annotations:
                    text = ann['transcription']
                    text_lengths.append(len(text))
                    
                    # นับความถี่ของตัวอักษร
                    for char in text:
                        character_frequency[char] = character_frequency.get(char, 0) + 1
                        
            except:
                continue
    
    # สถิติพื้นฐาน
    stats = {
        'total_images': len(text_counts_per_image),
        'total_text_instances': sum(text_counts_per_image),
        'avg_text_per_image': np.mean(text_counts_per_image),
        'avg_text_length': np.mean(text_lengths),
        'unique_characters': len(character_frequency),
        'most_common_chars': sorted(character_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
    }
    
    return stats
```

## 📝 ตัวอย่างการสร้างข้อมูลสำหรับ Recognition

### รูปแบบ Annotation สำหรับ Text Recognition
```
cropped_image_path\ttext_content
```

### ตัวอย่าง Recognition Annotation
```
rec_images/word_001.jpg	สวัสดี
rec_images/word_002.jpg	ยินดีต้อนรับ
rec_images/word_003.jpg	1234567890
rec_images/word_004.jpg	ABC-123
```

### การสร้างข้อมูล Recognition จาก Detection Data
```python
def create_recognition_dataset(detection_annotation_file, image_dir, output_dir):
    """
    สร้าง dataset สำหรับ recognition จาก detection annotations
    """
    import cv2
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    rec_annotations = []
    
    with open(detection_annotation_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            
            try:
                image_path, annotation_json = line.split('\t')
                annotations = json.loads(annotation_json)
                
                # โหลดรูปภาพ
                full_image_path = os.path.join(image_dir, image_path)
                image = cv2.imread(full_image_path)
                
                if image is None:
                    continue
                
                for ann_idx, ann in enumerate(annotations):
                    text = ann['transcription']
                    points = ann['points']
                    
                    # ตัดรูปภาพตาม bounding box
                    cropped = crop_text_region(image, points)
                    
                    if cropped is not None:
                        # บันทึกรูปภาพที่ตัดแล้ว
                        crop_filename = f"crop_{line_num:06d}_{ann_idx:03d}.jpg"
                        crop_path = os.path.join(output_dir, crop_filename)
                        cv2.imwrite(crop_path, cropped)
                        
                        # เพิ่ม annotation สำหรับ recognition
                        rec_annotations.append(f"{crop_filename}\t{text}")
                        
            except Exception as e:
                print(f"Error processing line {line_num}: {e}")
                continue
    
    # บันทึกไฟล์ annotation สำหรับ recognition
    rec_annotation_file = os.path.join(output_dir, 'rec_annotations.txt')
    with open(rec_annotation_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rec_annotations))
    
    return rec_annotation_file

def crop_text_region(image, points):
    """
    ตัดพื้นที่ข้อความจากรูปภาพ
    """
    import cv2
    import numpy as np
    
    # หา bounding rectangle
    points = np.array(points, dtype=np.int32)
    x, y, w, h = cv2.boundingRect(points)
    
    # เพิ่ม padding
    padding = 5
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(image.shape[1] - x, w + 2 * padding)
    h = min(image.shape[0] - y, h + 2 * padding)
    
    # ตัดรูปภาพ
    cropped = image[y:y+h, x:x+w]
    
    return cropped if cropped.size > 0 else None
```

---

**หมายเหตุ**: รูปแบบข้อมูลต้องสอดคล้องกับ PaddleOCR อย่างเคร่งครัด หากรูปแบบไม่ถูกต้องจะทำให้การเทรนไม่สำเร็จ
