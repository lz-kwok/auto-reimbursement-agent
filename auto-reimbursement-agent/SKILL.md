---
name: auto-reimbursement-agent
description: "Automatically extracts date, location (city), and odometer mileage from dashboard pictures (usually with watermarks) and fills the vehicle travel reimbursement sheet (用车费用明细.xlsx). It inserts new rows, calculates travel and fuel fees via formulas, and appends a compressed photo log at the end of the sheet."
---

# Auto Reimbursement Agent

This skill automates the extraction of travel information from dashboard photos and formats it into the standard vehicle reimbursement sheet.

## Trigger Scenarios

Use this skill when:
1. The user provides a set of dashboard photos containing odometer readings, timestamps, and locations (typically watermark cameras like 水印相机).
2. The user wants to fill out or update `用车费用明细.xlsx` to claim vehicle mileage fees.
3. The user wants to archive compressed dashboard photos inside the Excel sheet as an audit log.

## Reusable Automation Script

This skill bundles an automation script at `scripts/auto_reimburse.py`. It uses `easyocr` and `pillow` to extract data, sorts them by odometer mileage, constructs travel legs based on location changes, dynamically inserts rows in the Excel template, updates Excel formulas, and inserts compressed dashboard pictures.

### How to Run the Automation Script

To execute the entire flow automatically, run:
```bash
python C:\Users\GXY\.gemini\config\skills\auto-reimbursement-agent\scripts\auto_reimburse.py
```
*(Note: Replace `auto_reimburse.py` path with the correct local path in your environment if needed.)*

## Manual Workflow Details

If running the automation script is not possible, follow this step-by-step process:

### Step 1: Data Extraction
1. **Odometer Mileage**: Look for a 6-digit number on the instrument cluster (dashboard). Often the OCR might match longitude (`11xxxx`) or latitude (`31xxxx`/`32xxxx`). Use the heuristic: odometer mileage is generally in a different range (e.g. starting with `17` in this dataset) and ends with `km` or resembles it.
2. **City**: Extract from the watermark position. E.g., `南京市·龙池翠洲` $\rightarrow$ `南京市`.
3. **Date**: Extract from the watermark date (e.g., `2026.04.02` $\rightarrow$ `2026-04-02`).

### Step 2: Trip Construction
Sort all images by their odometer readings. Construct a travel leg whenever the city name changes between consecutive images:
- **Leg Date**: Use the date of the second (arrival) image.
- **Start City**: City of the first image.
- **End City**: City of the second image.
- **Start Odometer**: Mileage of the first image.
- **End Odometer**: Mileage of the second image.

### Step 3: Excel Writing and Insertion
1. Load `用车费用明细.xlsx`.
2. Find the row index of `合计：` in Column B.
3. If the number of travel legs exceeds the number of empty rows between Row 5 and the `合计：` row:
   - Calculate `rows_to_insert = num_legs - existing_slots`.
   - **CRITICAL**: In `openpyxl`, you must remove any merged cells at or below Row 13 before calling `insert_rows`. Call `insert_rows(total_row_idx, rows_to_insert)`. Save and reload the workbook. This avoids throwing `AttributeError: 'MergedCell' object attribute 'value' is read-only`.
   - Re-merge the signature row (e.g. `C22:D22`) and final amount cell (e.g. `G25:I25`) at their new shifted indices.
4. Populate Column A (Date), Column C (Start City), Column D (Start Odometer), Column E (End City), and Column F (End Odometer) for each leg.
5. In each leg row, write formulas for Column H (`=F[row]-D[row]`) and Column I (`=H[row]*0.8`).
6. Update the `合计：` row formulas: Column H (`=SUM(H5:H[total-1])`), Column I (`=SUM(I5:I[total-1])`), Column K (`=SUM(K5:K[total-1])`).
7. Update the summary table below `合计：` (total mileage, total toll fees, and final reimbursement amount `=C[summary_row]*0.8+E[summary_row]+F[summary_row]`).

### Step 4: Photo Log Attachment
1. Resize each dashboard photo to **15%** of its width and height (e.g. from `1080x1440` to `162x216` pixels) using PIL. Save them with JPEG quality `70` to keep the Excel file lightweight (~160 KB instead of >7 MB).
2. Starting from 2 rows below the summary section (e.g. Row 27), create a Photo Log Header: `车辆仪表照片`, `对应图片文件名`, `仪表盘总里程 (km)`, `照片水印地点`, `经纬度`, `拍摄日期`.
3. Set Column B width to `22`, Column E to `30`, Column F to `30`, and Column G to `15`.
4. For each photo:
   - Set the row height to `165pt` so the image fits without overflowing.
   - Embed the compressed image in Column B.
   - Fill in Column C (Filename), Column D (Odometer), Column E (Watermark location), Column F (GPS coordinates), and Column G (Date) next to it. Apply border styling.
