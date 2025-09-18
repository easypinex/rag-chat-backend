# 快速開始指南

## 🚀 主要檔案

- **`marker_converter.py`** - 轉換器（推薦使用）

## 📖 基本使用

### 轉換器（帶頁碼）

```python
from marker_converter import MarkerConverter, PagesResult

# 建立轉換器
converter = MarkerConverter()

# 轉換 PDF（帶頁碼標記）
markdown_content: str = converter.marker_to_markdown("input.pdf")

# 獲取頁面列表和資訊
result: PagesResult = converter.marker_pages("input.pdf")
```

#### 兩種方法的適用場景

**1. `marker_to_markdown()` - 完整轉換**
- **適用場景**: 需要完整的 Markdown 文檔，包含頁碼標記
- **輸出**: 單一字符串，包含所有頁面內容和 `## Page N` 標記
- **用途**: 生成完整的 Markdown 文檔，適合閱讀和分享

**2. `marker_pages()` - 頁面列表和資訊**
- **適用場景**: 需要逐頁處理、分析內容或獲取頁面統計資訊
- **輸出**: PagesResult 對象，包含：
  - `file_name`: 檔案名稱
  - `total_pages`: 總頁數
  - `pages`: 每頁的內容和資訊列表
    - `page_number`: 頁碼
    - `content`: 頁面 Markdown 內容
    - `content_length`: 內容長度
    - `block_count`: 區塊數量
    - `block_types`: 區塊類型分布
    - `tables`: 頁面中的表格列表 (List[TableInfo])
    - `table_count`: 表格數量
- **用途**: 頁面級別的分析、處理、重新組織和統計分析

#### 使用範例

```python
# 範例 1: 生成完整文檔
markdown_content: str = converter.marker_to_markdown("report.pdf")
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown_content)

# 範例 2: 逐頁處理和分析
result: PagesResult = converter.marker_pages("report.pdf")
print(f"檔案: {result['file_name']}")
print(f"總頁數: {result['total_pages']}")

for page in result['pages']:
    print(f"第 {page['page_number']} 頁: {page['content_length']} 字元")
    print(f"區塊數量: {page['block_count']}")
    print(f"區塊類型: {page['block_types']}")
    print(f"表格數量: {page['table_count']}")
    
    # 處理表格資訊
    if page['table_count'] > 0:
        for table in page['tables']:
            print(f"  📊 表格 {table['table_id']}: {table['title']}")
            print(f"    尺寸: {table['row_count']}行 × {table['column_count']}列")
            print(f"    位置: 第{table['start_line']}-{table['end_line']}行")
    
    # 可以對每頁內容進行個別處理
    content = page['content']
```

#### 表格處理範例

```python
# 專門處理表格資訊
result: PagesResult = converter.marker_pages("document.pdf")

# 收集所有表格
all_tables = []
for page in result['pages']:
    for table in page['tables']:
        all_tables.append({
            'page': page['page_number'],
            'table': table
        })

print(f"總共找到 {len(all_tables)} 個表格")

# 處理每個表格
for item in all_tables:
    page_num = item['page']
    table = item['table']
    
    print(f"\n📊 第 {page_num} 頁的表格:")
    print(f"  ID: {table['table_id']}")
    print(f"  標題: {table['title']}")
    print(f"  尺寸: {table['row_count']}行 × {table['column_count']}列")
    print(f"  位置: 第{table['start_line']}-{table['end_line']}行")
    print(f"  內容預覽:")
    
    # 顯示表格前幾行
    lines = table['content'].split('\n')
    for i, line in enumerate(lines[:3]):
        print(f"    {i+1}: {line}")
    if len(lines) > 3:
        print(f"    ... 還有 {len(lines) - 3} 行")
```

## 🧪 測試和範例

### 執行演示
```bash
python examples/example_usage.py
```

### 執行測試
```bash
python tests/test_conversion_advanced.py
```

### 查看範例
```bash
python examples/example_usage.py
```

### 類型檢查
```bash
python examples/test_marker_types.py
```

### 頁面類型檢查
```bash
python examples/check_page_types.py
```

### 新 API 測試
```bash
python examples/test_new_api.py
```

## 📁 目錄結構

- **`examples/`** - 使用範例和演示
- **`tests/`** - 測試檔案
- **`docs/`** - 詳細文檔
- **`converted/`** - 轉換輸出目錄

## ✨ 主要特色

- ✅ 頁碼標記（## Page N）
- ✅ 智能表格轉換和提取
- ✅ 複雜表格保留 HTML
- ✅ 表格資訊詳細分析（尺寸、位置、標題）
- ✅ 批量轉換支援
- ✅ 完整錯誤處理
- ✅ 明確的類型標注
- ✅ 智能頁面分割
- ✅ 詳細的頁面分析
- ✅ 整合的頁面資訊
- ✅ 表格統計和處理

## 🔧 安裝依賴

```bash
pip install marker-pdf[full] beautifulsoup4
```

## 📚 更多資訊

- **`README.md`** - 完整文檔和進階用法
- **`docs/CURRENT_STATUS.md`** - 當前實現狀況總結
- **`docs/IMPLEMENTATION_SUMMARY.md`** - 詳細實現說明
- **`docs/MARKER_OUTPUT_TYPES.md`** - Marker 輸出類型說明
- **`docs/API_CHANGES.md`** - API 變更總結
