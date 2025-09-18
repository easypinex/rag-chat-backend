# MarkItDown 多格式檔案轉換器

## 概述

這是一個基於微軟 MarkItDown 函式庫的多格式檔案到 Markdown 轉換器，支援將各種檔案格式轉換為 Markdown 格式，適用於 LLM 和相關文字分析管道。

## 支援的檔案格式

### 文檔格式
- **PDF** (.pdf)
- **PowerPoint** (.pptx, .ppt)
- **Word** (.docx, .doc)
- **Excel** (.xlsx, .xls)

### 圖片格式
- **PNG** (.png)
- **JPEG** (.jpg, .jpeg)
- **GIF** (.gif)
- **BMP** (.bmp)
- **TIFF** (.tiff)
- **WebP** (.webp)

### 音訊格式
- **MP3** (.mp3)
- **WAV** (.wav)
- **FLAC** (.flac)
- **AAC** (.aac)
- **OGG** (.ogg)
- **M4A** (.m4a)

### 網頁格式
- **HTML** (.html, .htm)

### 文字格式
- **CSV** (.csv)
- **JSON** (.json)
- **XML** (.xml)
- **TXT** (.txt)

### 其他格式
- **ZIP** (.zip)
- **EPUB** (.epub)
- **MOBI** (.mobi)

## 功能特色

### 1. 多格式支援
- 支援 29+ 種檔案格式
- 自動識別檔案類型
- 統一的轉換介面

### 2. 頁面分割功能
- **PDF 檔案**：按頁面分割內容
- **PowerPoint 檔案**：按幻燈片分割內容
- **其他格式**：智能內容分割
- 返回 `List[str]` 格式的頁面列表

### 3. Excel 工作表支援
- 將 Excel 檔案轉換為工作表列表
- 使用 `## {標題}` 自動分割工作表
- 每個工作表包含標題和內容
- 返回 `List[Dict[str, str]]` 格式
- 智能識別 Excel 中的不同工作表區域

### 4. 元資料提取
- 提取檔案基本資訊（名稱、類型、大小等）
- 獲取轉換時間戳
- 包含頁面和工作表資訊
- 返回完整的結構化資料

### 5. 批次處理
- 轉換整個目錄的所有支援檔案
- 支援子目錄遞歸處理
- 保持目錄結構

### 6. 特定格式轉換
- 可指定特定副檔名進行轉換
- 例如：只轉換所有 .xlsx 檔案

### 7. 錯誤處理
- 詳細的錯誤日誌
- 失敗檔案清單
- 轉換統計資訊

### 8. 命令列介面
- 靈活的命令列參數
- 支援單一檔案或批次轉換
- 詳細的執行報告

## 使用方法

### 基本使用

```python
from markitdown_converter import MarkitdownConverter

# 建立轉換器實例
converter = MarkitdownConverter(
    input_dir="raw_docs",
    output_dir="converted"
)

# 轉換單一檔案
result = converter.convert_file_to_markdown("document.pdf")
print(f"轉換完成: {result}")

# 轉換整個目錄
results = converter.convert_directory()
print(f"轉換了 {len(results)} 個檔案")

# 轉換特定格式
xlsx_results = converter.convert_by_extension('.xlsx')
print(f"轉換了 {len(xlsx_results)} 個 XLSX 檔案")
```

### 命令列使用

```bash
# 轉換所有支援的檔案
python markitdown_converter.py

# 轉換特定檔案
python markitdown_converter.py --file "document.pdf"

# 轉換特定副檔名
python markitdown_converter.py --extension .xlsx

# 指定輸入和輸出目錄
python markitdown_converter.py --input-dir "input" --output-dir "output"

# 轉換特定子目錄
python markitdown_converter.py --subdir "old_version"
```

## 範例

### 轉換 XLSX 檔案

```python
converter = MarkitdownConverter()

# 轉換 Excel 檔案
xlsx_path = "raw_docs/理賠審核原則.xlsx"
result = converter.convert_file_to_markdown(xlsx_path)
print(f"成功轉換: {result}")
```

### 轉換 PowerPoint 檔案

```python
# 轉換所有 PowerPoint 檔案
pptx_results = converter.convert_by_extension('.pptx')
for result in pptx_results:
    print(f"轉換完成: {result}")
```

### 頁面分割使用

```python
# 轉換檔案為頁面列表
pages = converter.convert_file_to_pages("document.pdf")
print(f"總共 {len(pages)} 頁")

# 處理每一頁
for i, page in enumerate(pages):
    print(f"第 {i+1} 頁: {len(page)} 字元")
    # 進行頁面特定的處理
```

### Excel 工作表使用

```python
# 轉換 Excel 檔案為工作表列表（自動按 ## 標題分割）
sheets = converter.convert_excel_to_sheets("data.xlsx")
print(f"總共 {len(sheets)} 個工作表")

# 處理每個工作表
for sheet in sheets:
    print(f"工作表: {sheet['title']}")
    print(f"內容長度: {len(sheet['content'])} 字元")
    print(f"內容預覽: {sheet['content'][:100]}...")

# 實際範例：理賠審核原則.xlsx 被分割為 18 個工作表
# 1. 應備文件 (1096 字元)
# 2. 急診 (814 字元)  
# 3. 門診 (1062 字元)
# 4. 住院 (2412 字元)
# 5. 手術 (4913 字元)
# ... 等等
```

### 元資料提取使用

```python
# 獲取完整的轉換結果和元資料
result = converter.convert_file_with_metadata("document.pdf")

print(f"檔案名稱: {result['file_name']}")
print(f"檔案類型: {result['file_type']}")
print(f"頁面數: {len(result['pages'])}")
print(f"檔案大小: {result['metadata']['file_size']} bytes")

# 如果是 Excel 檔案，還包含工作表資訊
if 'sheets' in result:
    print(f"工作表數: {len(result['sheets'])}")
```

### 批次轉換多種格式

```python
# 轉換目錄中的所有支援檔案
results = converter.convert_directory()
print(f"總共轉換了 {len(results)} 個檔案")

# 取得轉換統計
stats = converter.get_conversion_stats()
print(f"輸入檔案數: {stats['input_files_count']}")
print(f"輸出檔案數: {stats['output_mds_count']}")
print(f"支援格式: {', '.join(stats['supported_extensions'])}")
```

## 轉換結果

### Excel 轉換結果
- 保持表格結構
- 轉換為 Markdown 表格格式
- 保留資料完整性
- 支援工作表分割

### PowerPoint 轉換結果
- 保持幻燈片結構
- 轉換為標題和內容
- 保留圖片引用
- 支援頁面分割

### PDF 轉換結果
- 保持文檔結構
- 轉換為 Markdown 格式
- 保留文字和格式
- 支援頁面分割

## 錯誤處理

轉換器會處理以下常見錯誤：
- 檔案不存在
- 不支援的檔案格式
- 加密或受保護的檔案
- 損壞的檔案

失敗的檔案會記錄在日誌中，並在轉換完成後顯示失敗清單。

## 依賴項目

- `markitdown`: 微軟的多格式轉換函式庫
- `pathlib`: 檔案路徑處理
- `logging`: 日誌記錄

## 安裝

```bash
pip install markitdown
```

## 注意事項

1. 某些加密或受保護的檔案可能無法轉換
2. 大型檔案轉換可能需要較長時間
3. 轉換結果的品質取決於原始檔案的結構和內容
4. 建議在轉換前備份重要檔案

## 更新日誌

### v2.0.0
- 新增多格式支援（25+ 種格式）
- 新增特定格式轉換功能
- 改進錯誤處理和日誌記錄
- 新增命令列介面
- 保持向後相容性

### v1.0.0
- 基本 PDF 轉換功能
- 目錄批次轉換
- 基本錯誤處理