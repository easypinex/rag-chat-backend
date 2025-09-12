# Markitdown 轉換器服務

此服務使用微軟的 [markitdown](https://github.com/microsoft/markitdown) 函式庫提供 PDF 到 Markdown 的轉換功能。

## 功能特色

- 轉換單一 PDF 檔案為 Markdown
- 批次轉換目錄中的所有 PDF 檔案
- 支援子目錄處理
- 保持輸出中的目錄結構
- 完整的錯誤處理和日誌記錄
- 轉換統計資訊

## 安裝

所需的相依套件已包含在專案的 `requirements.txt` 中：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```python
from service.markdown.markitdown_converter import MarkitdownConverter

# 初始化轉換器
converter = MarkitdownConverter()

# 轉換 old_version 目錄中的所有 PDF
results = converter.convert_old_version_docs()
print(f"已轉換 {len(results)} 個檔案")
```

### 轉換單一檔案

```python
# 轉換特定的 PDF 檔案
result = converter.convert_pdf_to_markdown("raw_docs/old_version/example.pdf")
print(f"轉換至: {result}")
```

### 使用自訂目錄轉換

```python
# 使用自訂的輸入和輸出目錄
converter = MarkitdownConverter(
    input_dir="custom_input",
    output_dir="custom_output"
)

results = converter.convert_directory()
```

### 轉換特定子目錄

```python
# 轉換特定子目錄中的 PDF
results = converter.convert_directory("old_version/dm")
```

### 取得轉換統計資訊

```python
stats = converter.get_conversion_stats()
print(f"輸入 PDF: {stats['input_pdfs_count']}")
print(f"輸出 MD: {stats['output_mds_count']}")
```

## 命令列使用

您也可以從命令列使用轉換器：

```bash
# 轉換 old_version 目錄中的所有 PDF
python -m service.markdown.markitdown_converter

# 轉換特定檔案
python -m service.markdown.markitdown_converter --file "raw_docs/old_version/example.pdf"

# 使用自訂目錄轉換
python -m service.markdown.markitdown_converter --input-dir "custom_input" --output-dir "custom_output"

# 轉換特定子目錄
python -m service.markdown.markitdown_converter --subdir "old_version/dm"
```

## 目錄結構

```
service/markdown/
├── __init__.py
├── markitdown_converter.py    # 主要轉換器類別
├── test_markitdown_converter.py  # 測試案例
├── example_usage.py           # 使用範例
└── README.md                  # 本檔案
```

## 輸出

轉換後的 markdown 檔案預設儲存至 `markdown/converted/`，保持輸入的原始目錄結構。

例如：
- `raw_docs/old_version/example.pdf` → `markdown/converted/old_version/example.md`
- `raw_docs/old_version/dm/file.pdf` → `markdown/converted/old_version/dm/file.md`

## 錯誤處理

轉換器包含完整的錯誤處理：

- 檔案未找到錯誤
- 無效檔案類型錯誤（非 PDF 檔案）
- 轉換錯誤與詳細日誌記錄
- 批次轉換失敗的優雅處理

## 測試

執行測試套件：

```bash
python -m pytest service/markdown/test_markitdown_converter.py -v
```

## 範例

詳細使用範例請參閱 `example_usage.py`。

## 相依套件

- `markitdown[all]>=0.0.1a0` - 微軟的 markitdown 函式庫
- `pathlib` - 路徑操作（內建）
- `logging` - 日誌記錄（內建）
