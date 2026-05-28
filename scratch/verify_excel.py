import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook('用车费用明细.xlsx')
sheet = wb.active

print(f"Verifying Excel sheet {sheet.title} rows 5 to 22:")
for r in range(5, 23):
    row_vals = [sheet.cell(row=r, column=c).value for c in range(1, 13)]
    print(f"Row {r}: {row_vals}")
