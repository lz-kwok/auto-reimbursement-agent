import os
import sys
import json
import re
import urllib.parse
from PIL import Image
from PIL.ExifTags import TAGS
import easyocr

sys.stdout.reconfigure(encoding='utf-8')

# Initialize easyocr reader
print("Initializing easyocr...")
reader = easyocr.Reader(['ch_sim', 'en'])

def get_location_from_exif(img_path):
    try:
        img = Image.open(img_path)
        exif = img._getexif()
        if exif:
            for tag, val in exif.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == 'UserComment':
                    # UserComment is usually bytes, like b'ASCII\x00\x00\x00StoryCamera=...'
                    comment_str = ""
                    if isinstance(val, bytes):
                        # Try to decode
                        for encoding in ['utf-8', 'gbk', 'latin-1']:
                            try:
                                comment_str = val.decode(encoding)
                                break
                            except Exception:
                                pass
                    else:
                        comment_str = str(val)
                    
                    if "StoryCamera=" in comment_str:
                        # Extract the JSON part
                        json_part = comment_str.split("StoryCamera=")[1].strip()
                        # Clean up any non-JSON prefixes/suffixes
                        # Often it is URL-encoded
                        decoded_json = urllib.parse.unquote(json_part)
                        # Remove any null characters or trailing junk
                        decoded_json = re.sub(r'[\x00-\x1f]', '', decoded_json)
                        try:
                            data = json.loads(decoded_json)
                            pos_name = data.get("pos", {}).get("name", "")
                            if pos_name:
                                return pos_name
                        except Exception as e:
                            print(f"Error parsing JSON in {img_path}: {e}. Data: {repr(decoded_json)}")
    except Exception as e:
         print(f"Error reading EXIF in {img_path}: {e}")
    return None

def extract_data_from_img(img_path):
    # Location
    loc = get_location_from_exif(img_path)
    
    # Run OCR
    print(f"Running OCR on {img_path}...")
    result = reader.readtext(img_path)
    ocr_texts = [res[1] for res in result]
    
    date_str = None
    mileage = None
    city = None
    
    # Parse OCR texts
    for t in ocr_texts:
        t_clean = t.strip()
        
        # 1. Parse Date (format like 2026.04.02 or 2026-04-02)
        date_match = re.search(r'(\d{4})[.-](\d{2})[.-](\d{2})', t_clean)
        if date_match:
            date_str = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
            
        # 2. Parse Mileage (e.g. 170760km or 170760 km or just 170760)
        # Odometer is usually 6 digits. Let's look for numbers around 170000+
        # Let's extract digits from strings containing 'km' or 'KM'
        if 'km' in t_clean.lower():
            digits = re.findall(r'\d+', t_clean)
            if digits:
                val = int(digits[0])
                # Usually odometer is > 10000, fuel range is < 1000
                if val >= 10000:
                    mileage = val
        else:
            # Maybe just digits, e.g. "170760"
            digits = re.findall(r'^\d{6}$', t_clean)
            if digits:
                mileage = int(digits[0])
                
        # 3. If location not found in EXIF, look for city in OCR (contains '市')
        if not loc and '市' in t_clean:
            loc = t_clean
            
    # Clean up city
    if loc:
        # e.g., "南京市·龙池翠洲" -> "南京市"
        # Split by dot or colon
        parts = re.split(r'[·:：\-]', loc)
        city = parts[0].strip()
        
    return {
        "file": img_path,
        "date": date_str,
        "city": city,
        "location": loc,
        "mileage": mileage,
        "ocr_raw": ocr_texts
    }

image_dir = 'photos' if os.path.exists('photos') else '.'
image_files = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.lower().endswith('.jpg')])
all_data = []

for f in image_files:
    data = extract_data_from_img(f)
    all_data.append(data)
    print(f"File: {f} | Date: {data['date']} | City: {data['city']} | Mileage: {data['mileage']} | Location: {data['location']}")

with open('scratch/extracted_data.json', 'w', encoding='utf-8') as jf:
    json.dump(all_data, jf, ensure_ascii=False, indent=2)
print("Finished extraction.")
