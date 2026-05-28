# 自动公车报销与行车记录管理系统 (Auto-Reimbursement Agent)

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![EasyOCR](https://img.shields.io/badge/OCR-EasyOCR-orange)
![openpyxl](https://img.shields.io/badge/Library-openpyxl-green)
![Pillow](https://img.shields.io/badge/Library-Pillow-blue)

本系统是一套专为企业公车报销设计的自动化管理工具。通过图像识别（OCR）与元数据解析技术，自动提取行车仪表盘照片中的**日期、城市地点、经纬度坐标及里程数**，智能生成行程链并填入报销明细表，同时对照片进行高比例压缩并嵌入 Excel 表格，生成防篡改且包含 GPS 信息的行车凭证 Log。

---

## 核心功能

*   **智能数据及经纬度提取**：使用 `EasyOCR` 提取仪表盘照片中的字面日期、地点及数字；通过专用正则启发式提取并解析水印中的经纬度（纬度/经度，支持对非标准数字如 8 开头纬度进行修正）；支持基于相同地理名称对缺失的经纬度进行智能对齐和补全。
*   **行程链自动重构**：自动将所有照片按时间先后和里程递增顺序进行排序，监测相邻照片的位置切换。当检测到位置改变时，自动将行程划分为往返的“行程 Leg”（例如南京 $\rightarrow$ 合肥，合肥 $\rightarrow$ 南京），并记录起止公里数。
*   **Excel 模板智能兼容**：支持在 `用车费用明细.xlsx` 的 `合计` 行上方动态插入多行数据。不仅完整继承原单元格样式（字体、居中、边框），还**完美克服了 openpyxl 插入行时不会自动平移合并单元格的局限**，自动重算和绑定所有汇总公式。
*   **轻量化照片存证 Log**：将所有仪表盘原图（每张约 350KB）按 **15% 等比例缩放压缩**，在报销单下方建立包含“经纬度”与“拍摄日期”双维度的仪表照片存证看板（B列:照片，C列:文件名，D列:总里程，E列:水印地点，F列:经纬度，G列:拍摄日期）。将包含 21 张照片的 Excel 文件体积压缩在 **160 KB** 左右，实现轻量化保存。
*   **集成式 Custom Skill**：在 IDE 的配置目录中固化了 `auto-reimbursement-agent` 技能，并提供了一键式一站式脚本，便于在 IDE 终端或后续 Agent 流水线中随时复用。

---

## 技术栈

*   **核心语言**：Python 3.13+
*   **图像识别 (OCR)**：EasyOCR (基于 PyTorch 深度学习框架)
*   **图片处理**：Pillow (PIL)
*   **Excel 操控**：openpyxl
*   **元数据解析**：urllib.parse, re (正则库)

---

## 快速开始

### 1. 环境准备

确保您的操作系统上已安装 Python 3.8+。随后安装所需的依赖库：

```bash
pip install easyocr openpyxl pillow torch
```

*注：如在 Windows 环境下未检测到 GPU，EasyOCR 会自动以 CPU 模式运行，不影响识别精度。*

### 2. 项目目录结构

```
baoxiao/
├── photos/                                     # 21张现场车辆仪表盘原始照片
├── 用车费用明细.xlsx                           # 待填充的报销单模板（填充后大小约 160KB）
├── compressed/                                 # 压缩后的仪表盘存证照片临时存放目录 (15% 尺寸)
├── scratch/                                    # 调试与验证脚本目录
│   ├── extract_all_data.py                     # OCR及元数据提取脚本
│   ├── process_and_fill.py                     # 行程 legs 生成及表格数据写入脚本
│   ├── fix_excel_merged.py                     # 合并单元格防重叠与公式重写修正脚本
│   ├── insert_images.py                        # 图像等比例压缩与仪表看板插入脚本
│   ├── verify_excel.py                         # 检查Excel行数据及公式是否写对的脚本
│   ├── verify_images.py                        # 检查照片存证行及照片数是否对齐的脚本
│   └── inspect_excel_images.py                 # openpyxl 图像锚点属性底层探针脚本
└── README.md                                   # 本说明文档
```

### 3. 一键自动运行

该功能的完整核心步骤已打包为自动化脚本，存放于工程目录下的 `auto-reimbursement-agent/scripts/auto_reimburse.py`。

要在一行命令中完成**全部照片识别、行程计算、Excel 报销录入、公式修正和压缩照片存证**，请在项目根目录下执行以下命令：

```bash
python auto-reimbursement-agent/scripts/auto_reimburse.py
```

执行完毕后，控制台将输出以下信息：
```text
Found 21 images. Initializing EasyOCR...
Extracting: ./1.JPG
...
Generated 16 legs.
Inserting 3 rows at Row 18...
Adding merged range C22:D22
Adding merged range G25:I25
Inserting Photo Log starting from Row 27...
Successfully processed reimbursement flow and updated 用车费用明细.xlsx!
```

您可以直接用 Excel 打开 `用车费用明细.xlsx`，报销明细表将完全重构展示，且下方会生成排版规整的车辆仪表盘照片 log。

---

## Custom Skill (自定义技能) 使用说明

本项目所封装的 **自动报销Agent (auto-reimbursement-agent)** 技能已集成至 IDE 系统中。后续在 IDE 智能助手窗口内，可以通过以下方式快速使用该 Skill：

### 1. 自动触发 (Heuristic Trigger)
当您在对话框向 AI 助手描述以下任务时，IDE 系统检测到相关意图，将**自动读取并挂载**此 Skill，获取完整流程规范：
*   *“帮我把这几张公车仪表盘照片录入到报销单里”*
*   *“提取当前目录下所有照片的里程和城市，更新用车明细表”*
*   *“请处理一下公车报销明细，并生成照片存证 Log”*

### 2. 显式指令触发 (Explicit Call)
您也可以直接在对话框中指定助手调用该 Skill，让助手自动定位并运行打包逻辑：
> **提示语推荐**：`请使用 auto-reimbursement-agent 技能处理工作区照片，完成公车报销。`

### 3. AI 助手执行 Skill 的逻辑
当 Skill 被挂载后，AI 助手将遵循其内嵌的 `SKILL.md` 指导：
1. **自动安装依赖**：助手将自动检测并安装必要依赖（`easyocr`、`pillow`、`openpyxl`）。
2. **一键式脚本执行**：助手会自动定位并在后台终端运行其携带的 `scripts/auto_reimburse.py` 一键脚本，无须您手动干预。
3. **完成并回报**：运行完成后，助手会使用校验机制（如读取单元格及锚定图片数）检查 Excel 文件完整性，向您展示完成报告。

## 报销报表公式结构说明

自动生成的 Excel 报表中内置了以下动态计算公式，在源数据修改时会实时重算：
*   **行驶里程数 (H列)**：`=F[Row]-D[Row]`
*   **油费计算 (I列，0.8元/km)**：`=H[Row]*0.8`
*   **总里程合计 (H21)**：`=SUM(H5:H20)`
*   **油费合计 (I21)**：`=SUM(I5:I20)`
*   **过路费合计 (K21)**：`=SUM(K5:K20)`
*   **实报金额 (G25)**：`=C25*0.8+E25+F25` (实报里程费 + 过路费 + 停车费)

---

## 许可证

本项目采用 [MIT License](LICENSE) 授权。
