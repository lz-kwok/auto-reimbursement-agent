import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/extracted_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for d in data:
    print(f"File: {d['file']}")
    print(f"  Parsed Mileage: {d['mileage']}")
    print(f"  Location: {d['location']}")
    print(f"  Date: {d['date']}")
    print(f"  OCR raw:")
    for text in d['ocr_raw']:
        print(f"    - {text}")
