from PIL import Image
from PIL.ExifTags import TAGS
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for f in sorted(os.listdir('.')):
    if f.lower().endswith('.jpg'):
        try:
            img = Image.open(f)
            exif = img._getexif()
            if exif:
                print(f"=== {f} ===")
                for tag, val in exif.items():
                    tag_name = TAGS.get(tag, tag)
                    # Safe print of value
                    try:
                        print(f"  {tag_name}: {val}")
                    except Exception as e:
                        print(f"  {tag_name}: <error printing value: {e}>")
            else:
                print(f"=== {f} (No EXIF) ===")
        except Exception as e:
            print(f"Error reading {f}: {e}")
