# รูปแบบข้อมูลและ Annotation (Data Format Guide)

## 📋 รูปแบบไฟล์ Annotation

### รูปแบบมาตรฐานของ PaddleOCR
ไฟล์ annotation ต้องเป็นไฟล์ text (.txt) โดยแต่ละบรรทัดมีรูปแบบดังนี้:
```
image_path\t[{"transcription": "text", "points": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]}]
```

### ตัวอย่างไฟล์ Annotation
```
images/train_001.jpg	[{"transcription": "สวัสดี", "points": [[100, 50], [200, 50], [200, 80], [100, 80]]}, {"transcription": "ยินดีต้อนรับ", "points": [[100, 90], [250, 90], [250, 120], [100, 120]]}]
images/train_002.jpg	[{"transcription": "ข้อความทดสอบ", "points": [[50, 30], [300, 30], [300, 60], [50, 60]]}]
images/train_003.jpg	[{"transcription": "1234567890", "points": [[80, 100], [180, 100], [180, 130], [80, 130]]}]
```

## 🖼️ รูปแบบรูปภาพที่รองรับ

### ไฟล์รูปภาพ
- **รูปแบบ**: JPG, JPEG, PNG, TIFF, BMP
- **ขนาด**: แนะนำความละเอียดระหว่าง 640x480 ถึง 2048x2048 pixels
- **Aspect Ratio**: ไม่จำกัด แต่แนะนำให้ไม่เกิน 10:1
- **Color Space**: RGB หรือ Grayscale

### แนวทางการเตรียมรูปภาพ
```python
import cv2
import numpy as np

def preprocess_image(image_path, target_size=(1024, 1024)):
    """
    เตรียมรูปภาพสำหรับการเทรน
    """
    image = cv2.imread(image_path)
    
    # ปรับขนาดรูปภาพ
    h, w = image.shape[:2]
    if max(h, w) > target_size[0]:
        scale = target_size[0] / max(h, w)
        new_h, new_w = int(h * scale), int(w * scale)
        image = cv2.resize(image, (new_w, new_h))
    
    # ปรับปรุงคุณภาพรูปภาพ
    image = cv2.bilateralFilter(image, 9, 75, 75)
    
    return image
```

## 📊 โครงสร้างข้อมูล JSON

### สำหรับ Text Detection
```json
[
  {
    "transcription": "ข้อความที่ต้องการ detect",
    "points": [
      [x1, y1],  // มุมซ้ายบน
      [x2, y2],  // มุมขวาบน
      [x3, y3],  // มุมขวาล่าง
      [x4, y4]   // มุมซ้ายล่าง
    ]
  }
]
```

### คุณสมบัติของพิกัด (Points)
- **จำนวนจุด**: ต้องมี 4 จุดเสมอ (quadrilateral)
- **ลำดับจุด**: เรียงตามเข็มนาฬิกา เริ่มจากมุมซ้ายบน
- **ระบบพิกัด**: (0,0) อยู่ที่มุมซ้ายบนของรูปภาพ
- **ประเภทข้อมูล**: integer หรือ float

### ตัวอย่างข้อมูล Points
```python
# รูปสี่เหลี่ยมมุมฉาก
points_rectangle = [[100, 50], [300, 50], [300, 100], [100, 100]]

# รูปสี่เหลี่ยมเอียง
points_rotated = [[120, 40], [280, 60], [270, 110], [110, 90]]

# ข้อความโค้ง
points_curved = [[100, 50], [300, 45], [305, 95], [95, 100]]
```

## 🔧 เครื่องมือสร้าง Annotation

### 1. การใช้ LabelMe
```python
def convert_labelme_to_paddleocr(labelme_json_path, image_base_dir):
    """
    แปลงไฟล์ LabelMe JSON เป็นรูปแบบ PaddleOCR
    """
    import json
    
    with open(labelme_json_path, 'r', encoding='utf-8') as f:
        labelme_data = json.load(f)
    
    image_path = labelme_data['imagePath']
    annotations = []
    
    for shape in labelme_data['shapes']:
        if shape['shape_type'] == 'polygon' and len(shape['points']) >= 4:
            annotation = {
                'transcription': shape['label'],
                'points': shape['points'][:4]  # ใช้เฉพาะ 4 จุดแรก
            }
            annotations.append(annotation)
    
    # สร้างบรรทัด annotation
    relative_path = os.path.relpath(image_path, image_base_dir)
    annotation_line = f"{relative_path}\t{json.dumps(annotations, ensure_ascii=False)}"
    
    return annotation_line
```

### 2. การใช้ CVAT (Computer Vision Annotation Tool)
```python
def convert_cvat_to_paddleocr(cvat_xml_path):
    """
    แปลงไฟล์ CVAT XML เป็นรูปแบบ PaddleOCR
    """
    import xml.etree.ElementTree as ET
    
    tree = ET.parse(cvat_xml_path)
    root = tree.getroot()
    
    annotations = {}
    
    for image in root.findall('.//image'):
        image_name = image.get('name')
        image_annotations = []
        
        for polygon in image.findall('.//polygon'):
            points_str = polygon.get('points')
            label = polygon.get('label', '')
            
            # แปลง points string เป็น list
            points = []
            for point_str in points_str.split(';'):
                x, y = map(float, point_str.split(','))
                points.append([int(x), int(y)])
            
            if len(points) >= 4:
                annotation = {
                    'transcription': label,
                    'points': points[:4]
                }
                image_annotations.append(annotation)
        
        if image_annotations:
            annotations[image_name] = image_annotations
    
    return annotations
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
