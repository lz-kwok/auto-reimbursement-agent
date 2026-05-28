import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def parse_gps(ocr_raw):
    lat = None
    lng = None
    
    # 1. Find latitude
    for idx, text in enumerate(ocr_raw):
        if any(w in text for w in ['北纬', 'J纬', '纬']):
            for offset in [1, 2]:
                if idx + offset < len(ocr_raw):
                    val = ocr_raw[idx + offset]
                    digits = "".join(re.findall(r'\d+', val))
                    if len(digits) in [4, 5]:
                        if digits.startswith('8'):
                            digits = '3' + digits[1:]
                        if len(digits) == 5:
                            lat = f"北纬 {digits[:2]}°{digits[3:]}'"
                        elif len(digits) == 4:
                            lat = f"北纬 {digits[:2]}°{digits[2:]}'"
                        break
            if lat:
                break
                
    # 2. Find longitude
    for idx, text in enumerate(ocr_raw):
        if any(w in text for w in ['东经', '经']):
            for offset in [1, 2]:
                if idx + offset < len(ocr_raw):
                    val = ocr_raw[idx + offset]
                    digits = "".join(re.findall(r'\d+', val))
                    if len(digits) in [5, 6]:
                        if len(digits) == 6:
                            lng = f"东经 {digits[:3]}°{digits[4:]}'"
                        elif len(digits) == 5:
                            lng = f"东经 {digits[:3]}°{digits[3:]}'"
                        break
            if lng:
                break
                
    if lat and lng:
        return f"{lat}, {lng}"
    elif lat:
        return lat
    elif lng:
        return lng
    return ""

with open('scratch/extracted_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Parsed GPS coordinates for each image:")
for item in data:
    gps = parse_gps(item['ocr_raw'])
    print(f"  {item['file']}: {gps}")
