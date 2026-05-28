import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook('用车费用明细.xlsx')
sheet = wb.active

print("Image count:", len(sheet._images))
for i, img in enumerate(sheet._images):
    anchor = getattr(img, 'anchor', None)
    # Check anchor attributes
    anchor_str = "None"
    if anchor:
        if isinstance(anchor, str):
            anchor_str = anchor
        else:
            # openpyxl uses Anchor or OneCellAnchor objects
            # typically they have a _from attribute with row and col (0-based)
            from_marker = getattr(anchor, '_from', None)
            if from_marker:
                col = getattr(from_marker, 'col', None)
                row = getattr(from_marker, 'row', None)
                anchor_str = f"Row {row+1}, Col {col+1}" # convert to 1-based
            else:
                anchor_str = str(anchor)
    print(f"Image {i+1}: path={getattr(img, 'path', 'N/A')}, anchor={anchor_str}")
