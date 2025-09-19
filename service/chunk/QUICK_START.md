# Chunk 分割器快速開始指南

## 🚀 快速開始

Chunk 分割器是一個強大的文檔分割工具，專門為處理 PDF 文件而設計。它能夠智能地將文檔分割成適合 RAG 系統的 chunks，同時保持內容的完整性和語義連貫性。

## 🔧 兩種分割器選擇

本系統提供兩種分割器，針對不同的使用場景：

### 1. **ChunkSplitter** (傳統分割器)
- **適用場景**: 一般文檔處理、簡單 RAG 系統
- **特點**: 單層分割，直接輸出最終 chunks
- **優勢**: 簡單易用，處理速度快
- **推薦使用**: 文檔結構簡單、對 chunk 大小要求不嚴格

### 2. **HierarchicalChunkSplitter** (分層分割器) ⭐ **推薦**
- **適用場景**: 複雜文檔、高精度 RAG 系統、表格密集文檔
- **特點**: 雙層分割架構 (Parent + Child chunks)
- **優勢**: 精準控制 chunk 大小，特別優化表格處理
- **推薦使用**: 需要精確控制 chunk 大小、處理大型表格、高質量 RAG 系統

## 📊 分割器對比

| 特性 | ChunkSplitter | HierarchicalChunkSplitter |
|------|---------------|---------------------------|
| **分割層級** | 單層 | 雙層 (Parent + Child) |
| **Chunk 大小控制** | 基礎 | 精準 (250-400字) |
| **表格處理** | 一般 | 優化 |
| **處理速度** | 快 | 中等 |
| **記憶體使用** | 低 | 中等 |
| **適用複雜度** | 簡單-中等 | 中等-複雜 |
| **RAG 效果** | 良好 | 優秀 |

## 🎯 使用場景推薦

### 使用 ChunkSplitter 當：
- ✅ 處理簡單文檔（如純文字 PDF）
- ✅ 對 chunk 大小要求不嚴格
- ✅ 需要快速處理大量文件
- ✅ 系統資源有限
- ✅ 初次使用或原型開發

### 使用 HierarchicalChunkSplitter 當：
- ✅ 處理複雜文檔（如包含大量表格的保險手冊）
- ✅ 需要精確控制 chunk 大小（250-400字）
- ✅ 高質量 RAG 系統
- ✅ 表格密集文檔
- ✅ 需要詳細分析功能
- ✅ 生產環境部署

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

### 1. 傳統分割器 (ChunkSplitter)

```python
from service.chunk import ChunkSplitter
from service.markdown_integrate import UnifiedMarkdownConverter

# 轉換 PDF 到 Markdown
converter = UnifiedMarkdownConverter()
result = converter.convert_file("your_file.pdf")

# 使用傳統分割器
splitter = ChunkSplitter()
chunks = splitter.split_markdown(input_data=result)

print(f"分割完成: {len(chunks)} 個 chunks")
```

### 2. 分層分割器 (HierarchicalChunkSplitter) ⭐ **推薦**

```python
from service.chunk.hierarchical_splitter import HierarchicalChunkSplitter
from service.markdown_integrate import UnifiedMarkdownConverter

# 轉換 PDF 到 Markdown
converter = UnifiedMarkdownConverter()
result = converter.convert_file("your_file.pdf")

# 使用分層分割器（中文優化參數）
splitter = HierarchicalChunkSplitter(
    parent_chunk_size=2000,      # 父chunk大小（適合中文32k embedding）
    child_chunk_size=350,         # 子chunk大小（約100-150 tokens，適合中文rerank 512）
    child_chunk_overlap=50,       # 子chunk重疊（保持中文語義連貫性）
    keep_tables_together=True,    # 保持表格完整性
    normalize_output=True         # 正規化輸出
)

# 進行分層分割
result = splitter.split_hierarchically(
    input_data=result,
    output_excel=True,
    output_path="output/hierarchical_chunks.xlsx"
)

print(f"父chunks: {len(result.parent_chunks)}")
print(f"子chunks: {len(result.child_chunks)}")
print(f"分組效率: {result.grouping_analysis.grouping_efficiency:.2%}")
```

### 3. 自定義參數

#### 傳統分割器自定義
```python
# 創建自定義傳統分割器
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

#### 分層分割器自定義
```python
# 創建自定義分層分割器
splitter = HierarchicalChunkSplitter(
    parent_chunk_size=2000,      # 父chunk大小
    parent_chunk_overlap=200,     # 父chunk重疊
    child_chunk_size=350,         # 子chunk大小（目標250-400字）
    child_chunk_overlap=50,       # 子chunk重疊
    keep_tables_together=True,    # 保持表格完整性
    normalize_output=True         # 正規化輸出
)

result = splitter.split_hierarchically(
    input_data=result,
    output_excel=True,
    output_path="output/hierarchical_chunks.xlsx"
)
```

### 4. 分析結果

#### 傳統分割器分析
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

#### 分層分割器分析
```python
# 分層統計
print(f"父chunks: {len(result.parent_chunks)}")
print(f"子chunks: {len(result.child_chunks)}")
print(f"分組效率: {result.grouping_analysis.grouping_efficiency:.2%}")

# 大小分布分析
size_dist = result.size_distribution
print(f"平均子chunk大小: {size_dist.avg_child_size:.1f}")
print(f"大小變異係數: {size_dist.size_variance:.2f}")

# 表格處理統計
table_stats = result.table_handling_stats
print(f"表格chunks: {table_stats.table_chunks_count}")
print(f"表格合併數: {table_stats.tables_merged}")

# 分組分析
grouping = result.grouping_analysis
print(f"有效分組: {grouping.valid_groups}")
print(f"空分組: {grouping.empty_groups}")
print(f"單一子chunk分組: {grouping.single_child_groups}")
```

## 🎯 進階功能

### 處理不同文件類型

兩種分割器都會自動檢測文件類型並選擇最適合的分割策略：

#### 傳統分割器處理
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

#### 分層分割器處理
```python
# PDF 文件（有頁面結構）
pdf_result = converter.convert_file("document.pdf")
pdf_hierarchical = splitter.split_hierarchically(input_data=pdf_result)

# Excel 文件（可能有或沒有頁面結構）
excel_result = converter.convert_file("data.xlsx")
excel_hierarchical = splitter.split_hierarchically(input_data=excel_result)

# 檢查分層分割效果
print(f"PDF 分組效率: {pdf_hierarchical.grouping_analysis.grouping_efficiency:.2%}")
print(f"Excel 分組效率: {excel_hierarchical.grouping_analysis.grouping_efficiency:.2%}")
```

**分割策略說明**：
- **有頁面信息**：使用基於頁面的分割，確保 100% 頁碼覆蓋
- **無頁面信息**：使用基本分割模式，直接處理完整內容
- **分層分割**：特別優化表格處理，提供更精準的 chunk 大小控制

### 批量處理

#### 傳統分割器批量處理
```python
files = ["file1.pdf", "file2.pdf", "file3.pdf"]
all_chunks = []

for file_path in files:
    result = converter.convert_file(file_path)
    chunks = splitter.split_markdown(input_data=result)
    all_chunks.extend(chunks)

print(f"批量處理完成: {len(all_chunks)} 個 chunks")
```

#### 分層分割器批量處理
```python
files = ["file1.pdf", "file2.pdf", "file3.pdf"]
all_parent_chunks = []
all_child_chunks = []

for file_path in files:
    result = converter.convert_file(file_path)
    hierarchical_result = splitter.split_hierarchically(input_data=result)
    all_parent_chunks.extend(hierarchical_result.parent_chunks)
    all_child_chunks.extend(hierarchical_result.child_chunks)

print(f"批量處理完成:")
print(f"  父chunks: {len(all_parent_chunks)}")
print(f"  子chunks: {len(all_child_chunks)}")
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

### ChunkSplitter 參數 (傳統分割器)

| 參數 | 類型 | 預設值 | 描述 |
|------|------|--------|------|
| `chunk_size` | int | 1000 | 每個 chunk 的最大字符數 |
| `chunk_overlap` | int | 200 | chunk 之間的重疊字符數 |
| `normalize_output` | bool | True | 是否啟用內容正規化 |
| `keep_tables_together` | bool | True | 是否保持表格完整性 |
| `output_base_dir` | str | "service/output" | 輸出基礎目錄 |

### HierarchicalChunkSplitter 參數 (分層分割器) ⭐ **推薦**

| 參數 | 類型 | 預設值 | 描述 |
|------|------|--------|------|
| `parent_chunk_size` | int | 2000 | 父層chunk大小（適合中文32k embedding） |
| `parent_chunk_overlap` | int | 200 | 父層chunk重疊大小（保持中文語義連貫性） |
| `child_chunk_size` | int | 350 | 子層chunk大小（約100-150 tokens，適合中文rerank 512） |
| `child_chunk_overlap` | int | 50 | 子層chunk重疊大小（保持中文語義連貫性） |
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

### Q: 應該選擇哪種分割器？
A: 
- **簡單文檔、快速處理** → 使用 `ChunkSplitter`
- **複雜文檔、高精度 RAG、表格密集** → 使用 `HierarchicalChunkSplitter` ⭐ **推薦**

### Q: 為什麼有些 chunks 很短？
A: 系統會自動合併長度小於 30 字符的 chunks（通常是標題），但如果標題與內容不在同一頁面，則不會合併。

### Q: 如何調整 chunk 大小？
A: 
- **傳統分割器**: 修改 `chunk_size` 參數，建議值為 500-2000 字符
- **分層分割器**: 調整 `child_chunk_size` 參數，建議值為 250-400 字符

### Q: 表格被分割了怎麼辦？
A: 確保 `keep_tables_together=True`，系統會自動檢測並保持表格完整性。分層分割器在表格處理方面表現更佳。

### Q: Excel 文件沒有頁碼怎麼辦？
A: 這是正常的！Excel 文件通常沒有頁面結構，系統會自動使用基本分割模式，chunks 不會有頁碼信息。

### Q: 如何處理大量文件？
A: 使用批量處理功能，或考慮並行處理以提高效率。分層分割器提供更詳細的分析功能。

### Q: 如何知道使用了哪種分割模式？
A: 檢查 chunks 的 `page_number` metadata：有頁碼表示使用頁面分割，無頁碼表示使用基本分割。

### Q: 分層分割器的分組效率是什麼？
A: 分組效率表示有效分組的比例，越高表示分割效果越好。建議保持在 80% 以上。

### Q: 什麼時候需要調整分層分割器參數？
A: 當分組效率低於 80% 或子chunk大小分布不均時，可以調整 `parent_chunk_size` 和 `child_chunk_size` 參數。

## 📚 更多資源

### 使用範例
- [基本使用範例](examples/basic_usage.py) - 傳統分割器
- [進階使用範例](examples/advanced_usage.py) - 傳統分割器進階功能
- [分層分割範例](examples/hierarchical_example.py) - 分層分割器 ⭐ **推薦**
- [Excel 輸出範例](examples/excel_output_example.py) - Excel 分析功能
- [檢索器整合範例](examples/retriever_integration_example.py) - RAG 系統整合

### 文檔資源
- [詳細文檔](README.md) - 完整 API 文檔
- [分層分割詳細文檔](HIERARCHICAL_README.md) - 分層分割器完整指南
- [測試文件](test/) - 所有測試案例

### 分析工具
- [文檔分析器](analysis/analysis.py) - 支援兩種分割器的分析工具
- [分析結果範例](analysis/output/) - 實際分析結果範例

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改進這個工具！

---

**快速開始完成！** 🎉 現在您可以開始使用 Chunk 分割器來處理您的文檔了。
