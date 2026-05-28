import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook('用车费用明细.xlsx')
sheet = wb.active
print(f"Sheet name: {sheet.title}")

cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
for row_idx in range(5, 14):
    row_cells = []
    for col in cols:
        cell = sheet[f"{col}{row_idx}"]
        val = cell.value
        num_fmt = cell.number_format
        font_name = cell.font.name if cell.font else None
        align = cell.alignment.horizontal if cell.alignment else None
        row_cells.append(f"{col}{row_idx}: {val} (fmt={num_fmt}, font={font_name}, align={align})")
    print(f"Row {row_idx}:")
    for cell_info in row_cells:
        print(f"  {cell_info}")
