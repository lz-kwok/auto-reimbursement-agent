import openpyxl
import datetime

# Load the workbook
wb = openpyxl.load_workbook('用车费用明细.xlsx')
sheet = wb.active

# Row 5: Trip 1 (1.JPG to 2.JPG)
sheet['A5'] = datetime.date(2026, 4, 2)
sheet['C5'] = "南京市"
sheet['D5'] = 170760
sheet['E5'] = "合肥市"
sheet['F5'] = 170958

# Row 6: Trip 2 (2.JPG to 3.JPG)
sheet['A6'] = datetime.date(2026, 4, 3)
sheet['C6'] = "合肥市"
sheet['D6'] = 170958
sheet['E6'] = "南京市"
sheet['F6'] = 171167

# Save the workbook
wb.save('用车费用明细.xlsx')
print("Successfully filled trip details into 用车费用明细.xlsx")
