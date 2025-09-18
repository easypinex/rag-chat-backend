# 統一 Markdown 轉換器

整合 Marker 和 Markitdown 轉換器，提供統一的接口和數據格式。

## 功能特點

- **統一接口**: 一個 `convert_file` 方法處理所有格式
- **自動路由**: 根據檔案格式自動選擇合適的轉換器
- **統一數據模型**: 所有轉換結果都使用相同的數據結構
- **向後兼容**: 不重寫現有邏輯，只是包裝和統一
- **靈活輸出**: 可以返回對象或保存到檔案
- **完整元數據**: 包含所有必要的統計和元數據信息

## 支援的格式

### Marker 轉換器 (docx, pdf, pptx)
- `.docx` - Microsoft Word 文檔
- `.pdf` - PDF 文檔
- `.pptx` - Microsoft PowerPoint 簡報

### Markitdown 轉換器 (excel 和其他)
- `.xlsx`, `.xls` - Excel 試算表
- `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp` - 圖片
- `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.m4a` - 音頻
- `.html`, `.htm` - HTML 文檔
- `.csv`, `.json`, `.xml`, `.txt` - 數據文件
- `.zip`, `.epub`, `.mobi` - 壓縮和電子書

## 安裝依賴

```bash
# Marker 依賴
pip install marker-pdf[full] beautifulsoup4

# Markitdown 依賴
pip install markitdown
```

## 基本使用

```python
from service.markdown_integrate import UnifiedMarkdownConverter

# 初始化轉換器
converter = UnifiedMarkdownConverter()

# 轉換 PDF (使用 Marker)
result = converter.convert_file("document.pdf")
print(f"檔案: {result.metadata.file_name}")
print(f"總頁數: {result.metadata.total_pages}")
print(f"總表格數: {result.metadata.total_tables}")
print(f"使用轉換器: {result.metadata.converter_used}")

# 轉換 Excel (使用 Markitdown)
result = converter.convert_file("spreadsheet.xlsx", save_to_file=True)
print(f"轉換完成，保存至: {result.output_path}")

# 檢查支援的格式
formats = converter.get_supported_formats()
print(f"Marker 支援: {formats['marker']}")
print(f"Markitdown 支援: {formats['markitdown']}")
```

## 進階使用

### 自定義配置

```python
# 自定義 Marker 模型位置
marker_locations = {
    "model_path": "/path/to/models"
}

# 自定義 Markitdown 目錄
converter = UnifiedMarkdownConverter(
    marker_model_locations=marker_locations,
    markitdown_input_dir="custom_input",
    markitdown_output_dir="custom_output"
)
```

### 處理轉換結果

```python
result = converter.convert_file("document.pdf")

# 訪問完整內容
print(f"完整內容長度: {len(result.content)}")

# 訪問頁面信息
if result.pages:
    for page in result.pages:
        print(f"第 {page.page_number} 頁:")
        print(f"  標題: {page.title}")
        print(f"  內容長度: {page.content_length}")
        print(f"  區塊數量: {page.block_count}")
        print(f"  表格數量: {page.table_count}")
        
        # 訪問表格信息
        if page.tables:
            for table in page.tables:
                print(f"    表格: {table.title}")
                print(f"    行數: {table.row_count}, 列數: {table.column_count}")

# 訪問元數據
metadata = result.metadata
print(f"檔案大小: {metadata.file_size} bytes")
print(f"轉換時間: {metadata.conversion_timestamp}")
print(f"額外信息: {metadata.additional_info}")
```

### 檢查轉換器狀態

```python
# 檢查轉換器可用性
status = converter.get_converter_status()
print(f"Marker 可用: {status['marker']}")
print(f"Markitdown 可用: {status['markitdown']}")

# 檢查檔案格式支援
if converter.is_supported("document.pdf"):
    print("PDF 格式支援")
else:
    print("PDF 格式不支援")
```

## 數據模型

### ConversionResult
統一轉換結果，包含：
- `content`: 完整的 markdown 內容
- `pages`: 頁面列表（可能為 None）
- `metadata`: 元數據信息
- `output_path`: 輸出檔案路徑（如果保存到檔案）

### PageInfo
頁面信息，包含：
- `page_number`: 頁碼
- `title`: 頁面標題（可能為 None）
- `content`: 頁面內容
- `content_length`: 內容長度
- `block_count`: 區塊數量
- `block_types`: 區塊類型分布
- `tables`: 表格列表（可能為 None）
- `table_count`: 表格數量

### TableInfo
表格信息，包含：
- `table_id`: 表格 UUID
- `title`: 表格標題
- `content`: 表格 Markdown 內容
- `row_count`: 行數
- `column_count`: 列數
- `start_line`: 起始行號
- `end_line`: 結束行號

### ConversionMetadata
轉換元數據，包含：
- `file_name`: 檔案名稱
- `file_path`: 檔案路徑
- `file_type`: 檔案類型
- `file_size`: 檔案大小
- `total_pages`: 總頁數
- `total_tables`: 總表格數
- `total_content_length`: 總內容長度
- `conversion_timestamp`: 轉換時間戳
- `converter_used`: 使用的轉換器
- `additional_info`: 額外信息

## 錯誤處理

```python
try:
    result = converter.convert_file("document.pdf")
except FileNotFoundError:
    print("檔案不存在")
except ValueError as e:
    print(f"格式不支援: {e}")
except RuntimeError as e:
    print(f"轉換器不可用: {e}")
```

## 注意事項

1. **依賴檢查**: 確保已安裝所需的轉換器依賴
2. **格式支援**: 不同格式使用不同的轉換器，功能可能有所差異
3. **性能考慮**: Marker 轉換器需要較多資源，建議在性能較好的環境使用
4. **錯誤處理**: 建議使用 try-catch 處理轉換過程中的錯誤

## 架構設計

```
markdown_integrate/
├── __init__.py              # 模組初始化
├── unified_converter.py     # 統一轉換器主類
├── data_models.py          # 統一數據模型
├── format_router.py        # 格式路由器
└── README.md              # 文檔
```

統一轉換器整合了現有的 Marker 和 Markitdown 轉換器，提供一致的接口和數據格式，讓使用者可以無縫處理不同格式的檔案。
