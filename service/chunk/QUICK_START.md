# Chunk 分割器快速開始指南

## 🚀 快速開始

Chunk 分割器是一個強大的文檔分割工具，專門為處理 PDF 文件而設計。它能夠智能地將文檔分割成適合 RAG 系統的 chunks，同時保持內容的完整性和語義連貫性。

## 📋 主要功能

- **智能分割策略**: 自動檢測文件類型，選擇最適合的分割模式
- **基於頁面分割**: 使用 PDF 的原始頁面結構進行分割（有頁面信息時）
- **基本分割模式**: 支援沒有頁面結構的文件（如 Excel、Word）
- **智能合併**: 自動合併過短的標題 chunks
- **表格處理**: 保持表格完整性，避免跨 chunk 分割
- **內容正規化**: 清理多餘符號，優化 LLM 輸入
- **豐富 metadata**: 包含檔名、頁碼、標題級數等信息
- **Excel 導出**: 支援詳細的 Excel 分析報告

## 🛠️ 安裝依賴

```bash
pip install langchain langchain-text-splitters openpyxl pandas
```

## 📖 基本使用

### 1. 簡單分割

```python
from service.chunk import ChunkSplitter
from service.markdown_integrate import UnifiedMarkdownConverter

# 轉換 PDF 到 Markdown
converter = UnifiedMarkdownConverter()
result = converter.convert_file("your_file.pdf")

# 分割內容
splitter = ChunkSplitter()
chunks = splitter.split_markdown(input_data=result)

print(f"分割完成: {len(chunks)} 個 chunks")
```

### 2. 自定義參數

```python
# 創建自定義分割器
splitter = ChunkSplitter(
    chunk_size=1000,           # 每個 chunk 的最大字符數
    chunk_overlap=200,         # chunk 之間的重疊字符數
    normalize_output=True,     # 啟用內容正規化
    keep_tables_together=True # 保持表格完整性
)

chunks = splitter.split_markdown(
    input_data=result,
    output_excel=True,         # 輸出 Excel 文件
    output_path="output/chunks.xlsx",
    md_output_path="output/chunks.md"
)
```

### 3. 分析結果

```python
# 基本統計
total_chunks = len(chunks)
total_length = sum(len(chunk.page_content) for chunk in chunks)
avg_length = total_length / total_chunks

print(f"總 chunks: {total_chunks}")
print(f"平均長度: {avg_length:.1f}")

# 頁碼分布
page_numbers = [chunk.metadata.get('page_number') for chunk in chunks]
unique_pages = len(set(page_numbers))
print(f"頁碼覆蓋: {unique_pages} 頁")

# 表格 chunks
table_chunks = [chunk for chunk in chunks if chunk.metadata.get('is_table', False)]
print(f"表格 chunks: {len(table_chunks)}")
```

## 🎯 進階功能

### 處理不同文件類型

Chunk 分割器會自動檢測文件類型並選擇最適合的分割策略：

```python
# PDF 文件（有頁面結構）
pdf_result = converter.convert_file("document.pdf")
pdf_chunks = splitter.split_markdown(input_data=pdf_result)

# Excel 文件（可能有或沒有頁面結構）
excel_result = converter.convert_file("data.xlsx")
excel_chunks = splitter.split_markdown(input_data=excel_result)

# 檢查分割模式
print(f"PDF chunks 頁碼覆蓋: {sum(1 for c in pdf_chunks if c.metadata.get('page_number'))}/{len(pdf_chunks)}")
print(f"Excel chunks 頁碼覆蓋: {sum(1 for c in excel_chunks if c.metadata.get('page_number'))}/{len(excel_chunks)}")
```

**分割策略說明**：
- **有頁面信息**：使用基於頁面的分割，確保 100% 頁碼覆蓋
- **無頁面信息**：使用基本分割模式，直接處理完整內容

### 批量處理

```python
files = ["file1.pdf", "file2.pdf", "file3.pdf"]
all_chunks = []

for file_path in files:
    result = converter.convert_file(file_path)
    chunks = splitter.split_markdown(input_data=result)
    all_chunks.extend(chunks)

print(f"批量處理完成: {len(all_chunks)} 個 chunks")
```

### 自定義分析

```python
# 按頁碼分組
page_groups = {}
for chunk in chunks:
    page_num = chunk.metadata.get('page_number')
    if page_num not in page_groups:
        page_groups[page_num] = []
    page_groups[page_num].append(chunk)

# 按標題級數分組
header_groups = {}
for chunk in chunks:
    header_level = get_header_level(chunk.metadata)
    if header_level not in header_groups:
        header_groups[header_level] = []
    header_groups[header_level].append(chunk)
```

## 📊 輸出格式

### Excel 文件結構

| 欄位 | 描述 |
|------|------|
| A欄 | 原始內容 (頁面級) |
| B欄 | 正規化後內容 (頁面級) |
| C欄 | 分割後的 Chunk |
| D欄 | Chunk 編號 |
| E欄 | Chunk 長度 |
| F欄 | 包含標題 |
| G欄 | 是否為表格 |
| H欄 | 檔名 |
| I欄 | 檔案類型 |
| J欄 | 來源路徑 |
| K欄 | 轉換器 |
| L欄 | 總頁數 |
| M欄 | 總表格數 |
| N欄 | 頁碼 |
| O欄 | 頁面標題 |
| P欄 | 標題級數 |
| Q欄 | 表格合併數 |
| R欄 | 完整元數據 |

### Chunk Metadata

每個 chunk 包含豐富的 metadata：

```python
{
    'page_number': 1,                    # 頁碼
    'page_title': '封面頁',              # 頁面標題
    'file_name': 'document.pdf',         # 檔名
    'file_type': '.pdf',                 # 檔案類型
    'source': 'path/to/document.pdf',    # 來源路徑
    'converter_used': 'marker',          # 轉換器
    'total_pages': 12,                   # 總頁數
    'total_tables': 4,                   # 總表格數
    'Header 1': '主標題',                # 一級標題
    'Header 2': '二級標題',              # 二級標題
    'Header 3': '三級標題',              # 三級標題
    'Header 4': '四級標題',              # 四級標題
    'is_table': False,                   # 是否為表格
    'table_chunks_merged': 0             # 表格合併數
}
```

## 🔧 配置選項

### ChunkSplitter 參數

| 參數 | 類型 | 預設值 | 描述 |
|------|------|--------|------|
| `chunk_size` | int | 1000 | 每個 chunk 的最大字符數 |
| `chunk_overlap` | int | 200 | chunk 之間的重疊字符數 |
| `normalize_output` | bool | True | 是否啟用內容正規化 |
| `keep_tables_together` | bool | True | 是否保持表格完整性 |
| `output_base_dir` | str | "service/output" | 輸出基礎目錄 |

### 內容正規化功能

- 清理多餘的空格和換行
- 簡化表格分隔符
- 移除 HTML 標籤（如 `<br>`）
- 統一標題格式

## 📁 目錄結構

```
service/chunk/
├── __init__.py              # 模組初始化
├── chunk_splitter.py        # 主要分割器
├── excel_exporter.py        # Excel 導出器
├── markdown_normalizer.py   # 內容正規化器
├── table_handler.py         # 表格處理器
├── README.md               # 詳細文檔
├── QUICK_START.md          # 快速開始指南
├── test/                   # 測試文件
│   ├── test_chunk_splitter.py
│   ├── test_normalizer.py
│   └── test_table_fix.py
├── examples/               # 使用範例
│   ├── basic_usage.py
│   └── advanced_usage.py
└── docs/                   # 詳細文檔
    └── (未來擴展)
```

## 🚨 常見問題

### Q: 為什麼有些 chunks 很短？
A: 系統會自動合併長度小於 30 字符的 chunks（通常是標題），但如果標題與內容不在同一頁面，則不會合併。

### Q: 如何調整 chunk 大小？
A: 修改 `chunk_size` 參數，建議值為 500-2000 字符。

### Q: 表格被分割了怎麼辦？
A: 確保 `keep_tables_together=True`，系統會自動檢測並保持表格完整性。

### Q: Excel 文件沒有頁碼怎麼辦？
A: 這是正常的！Excel 文件通常沒有頁面結構，系統會自動使用基本分割模式，chunks 不會有頁碼信息。

### Q: 如何處理大量文件？
A: 使用批量處理功能，或考慮並行處理以提高效率。

### Q: 如何知道使用了哪種分割模式？
A: 檢查 chunks 的 `page_number` metadata：有頁碼表示使用頁面分割，無頁碼表示使用基本分割。

## 📚 更多資源

- [基本使用範例](examples/basic_usage.py)
- [進階使用範例](examples/advanced_usage.py)
- [測試文件](test/)
- [詳細文檔](README.md)

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改進這個工具！

---

**快速開始完成！** 🎉 現在您可以開始使用 Chunk 分割器來處理您的文檔了。
