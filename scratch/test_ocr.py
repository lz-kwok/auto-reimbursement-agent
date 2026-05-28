import sys
sys.stdout.reconfigure(encoding='utf-8')

print("Testing pytesseract...")
try:
    import pytesseract
    from PIL import Image
    text = pytesseract.image_to_string(Image.open('1.JPG'), lang='chi_sim')
    print("pytesseract chi_sim output:")
    print(text)
except Exception as e:
    print("pytesseract failed:", e)

print("\nTesting easyocr...")
try:
    import easyocr
    reader = easyocr.Reader(['ch_sim', 'en'])
    result = reader.readtext('1.JPG')
    print("easyocr output:")
    for res in result:
        print(res[1])
except Exception as e:
    print("easyocr failed:", e)
