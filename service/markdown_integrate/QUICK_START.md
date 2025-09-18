# 快速開始指南

## 安裝依賴

```bash
# 安裝 Marker 依賴
pip install marker-pdf[full] beautifulsoup4

# 安裝 Markitdown 依賴  
pip install markitdown
```

## 基本使用

```python
from service.markdown_integrate import UnifiedMarkdownConverter

# 1. 初始化轉換器
converter = UnifiedMarkdownConverter()

# 2. 轉換檔案
result = converter.convert_file("document.pdf")

# 3. 查看結果
print(f"檔案: {result.metadata.file_name}")
print(f"頁數: {result.metadata.total_pages}")
print(f"內容: {result.content[:100]}...")
```

## 支援的格式

### Marker 轉換器
- `.pdf` - PDF 文檔
- `.docx` - Word 文檔  
- `.pptx` - PowerPoint 簡報

### Markitdown 轉換器
- `.xlsx`, `.xls` - Excel 試算表
- `.png`, `.jpg`, `.jpeg` - 圖片
- `.html`, `.htm` - HTML 文檔
- `.csv`, `.json`, `.xml`, `.txt` - 數據文件

## 進階使用

### 保存到檔案
```python
result = converter.convert_file("document.pdf", save_to_file=True)
print(f"保存至: {result.output_path}")
```

### 處理頁面信息
```python
result = converter.convert_file("document.pdf")

if result.pages:
    for page in result.pages:
        print(f"第 {page.page_number} 頁:")
        print(f"  標題: {page.title}")
        print(f"  內容長度: {page.content_length}")
        print(f"  表格數量: {page.table_count}")
```

### 錯誤處理
```python
try:
    result = converter.convert_file("document.pdf")
except FileNotFoundError:
    print("檔案不存在")
except ValueError:
    print("格式不支援")
except RuntimeError:
    print("轉換器不可用")
```

## 測試

```bash
# 運行測試
python -m service.markdown_integrate.test_unified_converter

# 運行示例
python -m service.markdown_integrate.example_usage
```

## 故障排除

### 轉換器不可用
```python
status = converter.get_converter_status()
print(f"Marker: {status['marker']}")
print(f"Markitdown: {status['markitdown']}")
```

### 檢查格式支援
```python
if converter.is_supported("document.pdf"):
    print("PDF 格式支援")
else:
    print("PDF 格式不支援")
```

### 獲取支援的格式
```python
formats = converter.get_supported_formats()
print(f"Marker: {formats['marker']}")
print(f"Markitdown: {formats['markitdown']}")
```
