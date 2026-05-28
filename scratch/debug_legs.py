import json
import re

with open('scratch/extracted_data.json', 'r', encoding='utf-8') as f:
    images_data = json.load(f)

def get_clean_odometer(ocr_raw):
    for text in ocr_raw:
        match = re.search(r'17\d{4,5}', text)
        if match:
            val_str = match.group(0)
            if len(val_str) >= 6:
                return int(val_str[:6])
            elif len(val_str) == 5:
                return int(val_str) * 10
    for text in ocr_raw:
        digits = re.findall(r'\d+', text)
        for d in digits:
            if d.startswith('17'):
                if len(d) >= 6:
                    return int(d[:6])
                else:
                    return int(d)
    return None

for item in images_data:
    item['odo'] = get_clean_odometer(item['ocr_raw'])

images_data.sort(key=lambda x: x['odo'] if x['odo'] else 0)

legs = []
for i in range(len(images_data) - 1):
    img_start = images_data[i]
    img_end = images_data[i+1]
    
    if img_start['city'] != img_end['city']:
        leg = {
            "start_file": img_start['file'],
            "end_file": img_end['file'],
            "start_city": img_start['city'],
            "end_city": img_end['city'],
            "start_odo": img_start['odo'],
            "end_odo": img_end['odo']
        }
        legs.append(leg)

for idx, leg in enumerate(legs, 1):
    print(f"Leg {idx}: {leg['start_file']} -> {leg['end_file']} | {leg['start_city']} -> {leg['end_city']} | {leg['start_odo']} -> {leg['end_odo']}")
