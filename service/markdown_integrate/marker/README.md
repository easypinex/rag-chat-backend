# Marker2 - 基於 Marker 套件的 PDF 轉換器

這個模組提供了基於 [Marker](https://github.com/VikParuchuri/marker) 套件的 PDF 到 Markdown 轉換功能。

## 功能特色

- ✅ **轉換器**: 使用 Marker 獲取每頁結構化數據
- ✅ **頁碼支援**: 轉換器支援在 Markdown 中插入頁碼標記
- ✅ **表格轉換**: 智能將 HTML 表格轉換為 Markdown 表格
- ✅ **複雜表格處理**: 自動檢測並保留包含 rowspan/colspan 的複雜表格
- ✅ **批量轉換**: 支援批量處理多個 PDF 檔案
- ✅ **完整測試**: 包含單元測試和整合測試

## 目錄結構

```
service/markdown_integrate/marker/
├── marker_converter.py           # 轉換器（主要）
├── README.md                     # 說明文檔
├── __init__.py                   # 模組初始化
├── examples/                     # 使用範例
│   └── example_usage.py          # 進階轉換器範例
├── tests/                        # 測試檔案
│   ├── test_marker_converter.py  # 轉換器測試
│   ├── test_conversion.py        # 轉換測試
│   └── test_conversion_advanced.py   # 進階轉換測試
├── docs/                         # 文檔
│   └── IMPLEMENTATION_SUMMARY.md # 實現總結
└── converted/                    # 轉換輸出目錄
    └── *.md                      # 轉換後的 Markdown 檔案
```

## 安裝依賴

```bash
pip install marker-pdf[full]
```

## 基本使用

### 轉換器（結構化轉換）

```python
from service.markdown_integrate.marker import MarkerConverter

# 建立轉換器
converter = MarkerConverter()

# 轉換單一 PDF 檔案（帶頁碼）
markdown_content = converter.convert_pdf_to_markdown("path/to/file.pdf")

# 獲取頁面結構資訊和內容
result = converter.marker_pages("path/to/file.pdf")
print(f"檔案: {result['file_name']}")
print(f"總頁數: {result['total_pages']}")

# 逐頁處理
for page in result['pages']:
    print(f"第 {page['page_number']} 頁: {page['content_length']} 字元")
    print(f"區塊數量: {page['block_count']}")
    print(f"區塊類型: {page['block_types']}")
    content = page['content']  # 頁面內容
```

### 批量轉換

```python
# 批量轉換目錄中的所有 PDF 檔案
results = converter.convert_multiple_pdfs(
    "path/to/pdf/directory",
    "path/to/output/directory"
)

# 結果是一個字典，key 為檔案名，value 為轉換後的內容
for filename, content in results.items():
    print(f"{filename}: {len(content)} 字元")
```

### 獲取檔案資訊

```python
# 獲取 PDF 檔案的詳細資訊
info = converter.get_conversion_info("path/to/file.pdf")
print(f"檔案大小: {info['file_size_mb']} MB")
print(f"修改時間: {info['modified_time']}")
```

## 進階使用

### 自定義模型位置

```python
# 使用自定義模型位置
model_locations = {
    "layout_model": "/path/to/layout/model",
    "ocr_model": "/path/to/ocr/model",
    "edit_model": "/path/to/edit/model"
}

converter = MarkerConverter(model_locations)
```

### 便利函數

```python
from service.markdown_integrate.marker import create_marker_converter

# 使用便利函數建立轉換器
converter = create_marker_converter()
```

## 測試

### 執行單元測試

```bash
cd service/markdown_integrate/marker
python -m pytest tests/test_marker_converter.py -v
```

### 執行轉換測試

```bash
cd service/markdown_integrate/marker
python tests/test_conversion.py
python tests/test_conversion_advanced.py
```

### 執行使用範例

```bash
cd service/markdown_integrate/marker
python examples/example_usage.py
python examples/type_examples.py
```

### 執行轉換測試

```bash
cd service/markdown_integrate/marker
python tests/test_conversion.py
python tests/test_conversion_advanced.py
```

## 轉換器比較

| 功能 | 標準轉換器 | JSON 轉換器 |
|------|------------|-------------|
| 轉換速度 | 快 | 中等 |
| 頁碼支援 | 無 | 有 |
| 表格轉換 | 基礎 | 智能 |
| 結構化數據 | 無 | 有 |
| 複雜表格處理 | 無 | 有 |
| 頁面分析 | 無 | 有 |
| 記憶體使用 | 中等 | 較高 |

## 進階功能

### 表格轉換特色

JSON 轉換器提供智能表格轉換：

- **簡單表格**: 自動轉換為 Markdown 表格格式
- **複雜表格**: 檢測 rowspan/colspan 並保留原始 HTML
- **表格清理**: 自動處理空行和格式問題

### 頁面結構分析

```python
# 獲取詳細的頁面結構資訊和內容
result = converter.marker_pages("document.pdf")
for page in result['pages']:
    print(f"第 {page['page_number']} 頁:")
    print(f"  - 內容長度: {page['content_length']} 字元")
    print(f"  - 區塊數量: {page['block_count']}")
    print(f"  - 區塊類型: {page['block_types']}")
    print(f"  - 內容預覽: {page['content'][:100]}...")
```

### 類型定義

### 主要類型

```python
from marker_converter import (
    MarkerConverter, 
    PagesResult,
    PageContent
)

# 明確的類型提示
converter = MarkerConverter()
result: PagesResult = converter.marker_pages("document.pdf")

# 檢查頁面內容和資訊
print(f"檔案: {result['file_name']}")
print(f"總頁數: {result['total_pages']}")

for page in result['pages']:
    print(f"第 {page['page_number']} 頁: {page['content_length']} 字元")
    print(f"  - 區塊數量: {page['block_count']}")
    print(f"  - 區塊類型: {page['block_types']}")
    print(f"  - 內容預覽: {page['content'][:100]}...")
```

### Marker 輸出類型

```python
from marker.renderers.markdown import MarkdownOutput

# Marker 轉換器返回 MarkdownOutput 對象
rendered: MarkdownOutput = self.converter(input_pdf)

# MarkdownOutput 主要屬性：
# - markdown: str - 完整的 Markdown 內容
# - images: Dict - 圖片信息
# - metadata: Dict - 元數據信息
markdown_content: str = rendered.markdown
images_info: dict = rendered.images
metadata_info: dict = rendered.metadata
```

## 注意事項

1. **模型下載**: 首次使用時，Marker 會自動下載所需的 AI 模型，這可能需要一些時間和網路流量。

2. **記憶體需求**: Marker 需要較多的記憶體來運行 AI 模型，建議至少 8GB RAM。

3. **GPU 支援**: 如果有 CUDA 相容的 GPU，Marker 會自動使用 GPU 加速轉換過程。

4. **檔案格式**: 目前主要支援 PDF 格式的轉換。

## 錯誤處理

轉換器會自動處理常見的錯誤情況：

- 檔案不存在
- 目錄不存在
- Marker 套件未安裝
- 模型載入失敗
- 轉換過程中的錯誤

所有錯誤都會記錄到日誌中，並拋出適當的異常。

## 與原始 markdown 模組的差異

| 功能 | markdown 模組 | markdown2 模組 |
|------|---------------|----------------|
| 轉換引擎 | markitdown | Marker |
| AI 模型 | 無 | 有 (OCR + Layout + Edit) |
| 轉換品質 | 基礎 | 高品質 |
| 圖片處理 | 基礎 | 進階 |
| 表格識別 | 基礎 | 精確 |
| 記憶體需求 | 低 | 高 |
| 轉換速度 | 快 | 中等 |

## 範例輸出

轉換後的 Markdown 檔案會包含：

- 正確的標題層級
- 格式化的表格
- 圖片引用
- 保持原始佈局結構
- 高品質的文字識別

## 疑難排解

### 常見問題

1. **ImportError**: 確保已安裝 `marker-pdf[full]`
2. **記憶體不足**: 嘗試關閉其他應用程式或使用更小的 PDF 檔案
3. **模型下載失敗**: 檢查網路連線，或手動下載模型檔案

### 日誌設定

```python
import logging
logging.basicConfig(level=logging.INFO)
```

這樣可以查看詳細的轉換過程和錯誤資訊。
