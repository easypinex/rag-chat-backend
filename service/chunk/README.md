# Chunk 分割模組

基於 LangChain 的智能 Markdown 分割服務，專門為 RAG 系統設計，提供兩種分割器以滿足不同使用場景的需求。

## 🔧 兩種分割器

### 1. **ChunkSplitter** (傳統分割器)
- **適用場景**: 一般文檔處理、簡單 RAG 系統
- **特點**: 單層分割，直接輸出最終 chunks
- **優勢**: 簡單易用，處理速度快

### 2. **HierarchicalChunkSplitter** (分層分割器) ⭐ **推薦**
- **適用場景**: 複雜文檔、高精度 RAG 系統、表格密集文檔
- **特點**: 雙層分割架構 (Parent + Child chunks)
- **優勢**: 精準控制 chunk 大小，特別優化表格處理

## 🚀 功能特色

- ✅ **智能分割策略**: 自動檢測文件類型，支援基於頁面分割和基本分割兩種模式
- ✅ **基於頁面分割**: 使用 PDF 原始頁面結構進行分割，確保 100% 頁碼覆蓋
- ✅ **基本分割模式**: 支援沒有頁面結構的文件（如 Excel、Word），直接使用內容分割
- ✅ **智能合併**: 自動合併過短的標題 chunks，保持內容完整性
- ✅ **表格處理**: 自動檢測並保持表格完整性，避免表格被分割
- ✅ **內容正規化**: 清理多餘符號、空格和 HTML 標籤，優化 LLM 輸入
- ✅ **豐富 metadata**: 包含檔名、頁碼、標題級數、轉換器等信息
- ✅ **Excel 分析**: 支援詳細的 Excel 分析報告，包含頁面級原始內容
- ✅ **多種輸入**: 支援文件路徑和 ConversionResult 對象輸入
- ✅ **分層分析**: 分層分割器提供詳細的分組效率和大小分布分析

## 📁 目錄結構

```
service/chunk/
├── __init__.py                    # 模組初始化
├── chunk_splitter.py              # 傳統分割器
├── hierarchical_splitter.py       # 分層分割器 ⭐ 推薦
├── hierarchical_models.py          # 分層分割資料模型
├── excel_exporter.py              # Excel 導出器
├── markdown_normalizer.py         # 內容正規化器
├── table_handler.py               # 表格處理器
├── README.md                      # 詳細文檔
├── QUICK_START.md                 # 快速開始指南
├── HIERARCHICAL_README.md         # 分層分割詳細文檔
├── test/                          # 測試文件
│   ├── test_chunk_splitter.py     # 傳統分割器測試
│   ├── test_hierarchical.py       # 分層分割器測試
│   ├── test_excel_output.py       # Excel 輸出測試
│   ├── test_new_excel_format.py   # 新 Excel 格式測試
│   ├── test_parent_overlap.py     # 父層重疊測試
│   ├── test_retriever_integration.py # 檢索器整合測試
│   ├── test_normalizer.py         # 正規化器測試
│   └── test_table_fix.py          # 表格修復測試
├── examples/                      # 使用範例
│   ├── basic_usage.py             # 基本使用範例
│   ├── advanced_usage.py          # 進階使用範例
│   ├── hierarchical_example.py   # 分層分割範例 ⭐ 推薦
│   ├── excel_output_example.py   # Excel 輸出範例
│   └── retriever_integration_example.py # 檢索器整合範例
├── analysis/                      # 分析工具
│   ├── analysis.py                # 文檔分析器
│   ├── example_usage.py           # 分析器使用範例
│   └── output/                    # 分析結果輸出
└── docs/                          # 詳細文檔
    └── (未來擴展)
```

## 🚀 快速開始

> 📖 詳細的使用指南請參考 [QUICK_START.md](QUICK_START.md)

### 1. 傳統分割器 (ChunkSplitter)

```python
from service.chunk import ChunkSplitter
from service.markdown_integrate import UnifiedMarkdownConverter

# 轉換文件到 Markdown
converter = UnifiedMarkdownConverter()
result = converter.convert_file("document.pdf")  # 或 "document.xlsx"

# 創建傳統分割器
splitter = ChunkSplitter(
    chunk_size=1000,           # 每個 chunk 的最大字符數
    chunk_overlap=200,         # chunk 之間的重疊字符數
    normalize_output=True,     # 啟用內容正規化
    keep_tables_together=True  # 保持表格完整性
)

# 分割內容（自動檢測分割模式）
chunks = splitter.split_markdown(
    input_data=result,
    output_excel=True,
    output_path="output/chunks.xlsx"
)

print(f"分割完成: {len(chunks)} 個 chunks")
```

### 2. 分層分割器 (HierarchicalChunkSplitter) ⭐ **推薦**

```python
from service.chunk.hierarchical_splitter import HierarchicalChunkSplitter
from service.markdown_integrate import UnifiedMarkdownConverter

# 轉換文件到 Markdown
converter = UnifiedMarkdownConverter()
result = converter.convert_file("document.pdf")  # 或 "document.xlsx"

# 創建分層分割器（中文優化參數）
splitter = HierarchicalChunkSplitter(
    parent_chunk_size=2000,      # 父chunk大小（適合中文32k embedding）
    child_chunk_size=350,        # 子chunk大小（約100-150 tokens，適合中文rerank 512）
    child_chunk_overlap=50,      # 子chunk重疊（保持中文語義連貫性）
    keep_tables_together=True,  # 保持表格完整性
    normalize_output=True       # 正規化輸出
)

# 進行分層分割
hierarchical_result = splitter.split_hierarchically(
    input_data=result,
    output_excel=True,
    output_path="output/hierarchical_chunks.xlsx"
)

print(f"父chunks: {len(hierarchical_result.parent_chunks)}")
print(f"子chunks: {len(hierarchical_result.child_chunks)}")
print(f"分組效率: {hierarchical_result.grouping_analysis.grouping_efficiency:.2%}")
```

### 3. 分析結果

#### 傳統分割器分析
```python
# 基本統計
total_chunks = len(chunks)
total_length = sum(len(chunk.page_content) for chunk in chunks)
avg_length = total_length / total_chunks

# 頁碼覆蓋
page_numbers = [chunk.metadata.get('page_number') for chunk in chunks]
unique_pages = len(set(page_numbers))

# 表格 chunks
table_chunks = [chunk for chunk in chunks if chunk.metadata.get('is_table', False)]

print(f"總 chunks: {total_chunks}")
print(f"平均長度: {avg_length:.1f}")
print(f"頁碼覆蓋: {unique_pages} 頁")
print(f"表格 chunks: {len(table_chunks)}")
```

#### 分層分割器分析
```python
# 分層統計
print(f"父chunks: {len(hierarchical_result.parent_chunks)}")
print(f"子chunks: {len(hierarchical_result.child_chunks)}")
print(f"分組效率: {hierarchical_result.grouping_analysis.grouping_efficiency:.2%}")

# 大小分布分析
size_dist = hierarchical_result.size_distribution
print(f"平均子chunk大小: {size_dist.avg_child_size:.1f}")
print(f"大小變異係數: {size_dist.size_variance:.2f}")

# 表格處理統計
table_stats = hierarchical_result.table_handling_stats
print(f"表格chunks: {table_stats.table_chunks_count}")
print(f"表格合併數: {table_stats.tables_merged}")

# 分組分析
grouping = hierarchical_result.grouping_analysis
print(f"有效分組: {grouping.valid_groups}")
print(f"空分組: {grouping.empty_groups}")
print(f"單一子chunk分組: {grouping.single_child_groups}")
```

## 🔧 主要組件

### ChunkSplitter (傳統分割器)

傳統分割器類，提供以下功能：

- **基於頁面分割**: 使用 PDF 原始頁面結構進行分割，確保 100% 頁碼覆蓋
- **智能合併**: 自動合併過短的標題 chunks（<30字符）
- **表格處理**: 自動檢測和保持表格完整性
- **內容正規化**: 清理多餘符號、空格和 HTML 標籤
- **豐富 metadata**: 包含檔名、頁碼、標題級數等信息

### HierarchicalChunkSplitter (分層分割器) ⭐ **推薦**

分層分割器類，提供以下功能：

- **雙層分割架構**: Parent + Child chunks 設計，精準控制大小
- **中文優化**: 針對中文文檔優化的參數設置
- **表格友好**: 特別優化大型表格的處理
- **分組分析**: 提供詳細的分組效率和大小分布分析
- **RAG 優化**: 適合高質量 RAG 系統的 chunk 大小控制
- **豐富分析**: 包含分組統計、表格處理統計、大小分布等詳細信息

### ExcelExporter

Excel 導出器，提供以下功能：

- **頁面級內容**: A欄和B欄顯示完整的頁面原始和正規化內容
- **按頁碼合併**: 同一頁面的多個 chunks 會合併原始內容欄位
- **詳細信息**: 包含檔名、頁碼、標題級數、轉換器等信息
- **格式設置**: 自動設置列寬、邊框、對齊方式
- **17個欄位**: 完整的 metadata 展開到獨立欄位

### MarkdownNormalizer

內容正規化器，提供以下功能：

- **空格清理**: 移除多餘的空格和換行
- **表格簡化**: 簡化表格分隔符，統一格式
- **HTML 清理**: 移除 `<br>` 等 HTML 標籤
- **格式統一**: 統一標題和列表格式

### TableHandler

表格處理器，提供以下功能：

- **表格檢測**: 使用正則表達式檢測 Markdown 表格
- **結構分析**: 分析表格的行數、列數、表頭信息
- **邊界標記**: 標記表格邊界以保持完整性
- **合併處理**: 合併相關的表格 chunks

## 配置選項

### ChunkSplitter 參數 (傳統分割器)

```python
ChunkSplitter(
    chunk_size=1000,                    # 每個 chunk 的最大字符數
    chunk_overlap=200,                  # chunk 之間的重疊字符數
    headers_to_split_on=[               # 要分割的標題層級
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ],
    keep_tables_together=True,          # 是否保持表格完整性
    normalize_output=True,              # 是否正規化輸出
    output_base_dir="service/output"    # 輸出基礎目錄
)
```

### HierarchicalChunkSplitter 參數 (分層分割器) ⭐ **推薦**

```python
HierarchicalChunkSplitter(
    parent_chunk_size=2000,             # 父層chunk大小（適合中文32k embedding）
    parent_chunk_overlap=200,           # 父層chunk重疊大小（保持中文語義連貫性）
    child_chunk_size=350,               # 子層chunk大小（約100-150 tokens，適合中文rerank 512）
    child_chunk_overlap=50,             # 子層chunk重疊大小（保持中文語義連貫性）
    headers_to_split_on=[               # 要分割的標題層級
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ],
    keep_tables_together=True,          # 是否保持表格完整性
    normalize_output=True,              # 是否正規化輸出
    output_base_dir="service/output"    # 輸出基礎目錄
)
```

### 輸出選項

#### 傳統分割器輸出
```python
chunks = splitter.split_markdown(
    input_data=input_data,
    output_excel=True,                  # 是否輸出 Excel 文件
    output_path="output/chunks.xlsx",  # Excel 輸出路徑
    md_output_path="output/chunks.md"  # Markdown 輸出路徑
)
```

#### 分層分割器輸出
```python
hierarchical_result = splitter.split_hierarchically(
    input_data=input_data,
    output_excel=True,                  # 是否輸出 Excel 文件
    output_path="output/hierarchical_chunks.xlsx",  # Excel 輸出路徑
    md_output_path="output/hierarchical_chunks.md"  # Markdown 輸出路徑
)

# 分層分割器返回 HierarchicalSplitResult 對象
# 包含 parent_chunks, child_chunks, grouping_analysis 等
```

## 統計信息

### 基本統計

```python
stats = splitter.get_chunk_statistics(chunks)
print(f"總 chunks: {stats['total_chunks']}")
print(f"平均長度: {stats['average_length']}")
print(f"表格 chunks: {stats['table_chunks']}")
```

### 表格統計

```python
table_stats = splitter.table_handler.get_table_statistics(chunks)
print(f"表格比例: {table_stats['table_ratio']}")
print(f"平均表格長度: {table_stats['avg_table_length']}")
```

## 🧪 測試

### 運行測試

#### 傳統分割器測試
```bash
# 基本測試
python service/chunk/test/test_chunk_splitter.py

# 正規化器測試
python service/chunk/test/test_normalizer.py

# 表格修復測試
python service/chunk/test/test_table_fix.py
```

#### 分層分割器測試
```bash
# 分層分割器測試
python service/chunk/test/test_hierarchical.py

# Excel 輸出測試
python service/chunk/test/test_excel_output.py

# 新 Excel 格式測試
python service/chunk/test/test_new_excel_format.py

# 父層重疊測試
python service/chunk/test/test_parent_overlap.py

# 檢索器整合測試
python service/chunk/test/test_retriever_integration.py
```

### 使用範例

```bash
# 基本使用範例（傳統分割器）
python service/chunk/examples/basic_usage.py

# 進階使用範例（傳統分割器）
python service/chunk/examples/advanced_usage.py

# 分層分割範例（分層分割器）⭐ 推薦
python service/chunk/examples/hierarchical_example.py

# Excel 輸出範例
python service/chunk/examples/excel_output_example.py

# 檢索器整合範例
python service/chunk/examples/retriever_integration_example.py
```

測試腳本會：

1. 使用 UnifiedMarkdownConverter 轉換 PDF 文件
2. 使用相應的分割器分割 Markdown 內容
3. 導出到 Excel 和 Markdown 文件
4. 顯示詳細的統計信息
5. 驗證頁碼覆蓋和內容正規化
6. 分層分割器額外提供分組效率和大小分布分析

## 📊 輸出格式

### Excel 輸出結構

| 欄位 | 說明 |
|------|------|
| A欄 | 原始內容（頁面級，按頁碼合併） |
| B欄 | 正規化後內容（頁面級，按頁碼合併） |
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
| P欄 | 標題級數（一、二、三、四） |
| Q欄 | 表格合併數 |
| R欄 | 完整元數據 |

### Chunk Metadata 範例

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

## 依賴要求

- `langchain-text-splitters>=0.0.1`
- `openpyxl>=3.1.0`
- `pandas>=2.0.0`

## 注意事項

1. **表格處理**: 啟用 `keep_tables_together=True` 時，表格會被標記並保持完整性
2. **內存使用**: 大型文件可能消耗較多內存，建議適當調整 `chunk_size`
3. **輸出目錄**: 確保輸出目錄存在，否則會自動創建
4. **編碼**: 所有文件使用 UTF-8 編碼

## 範例輸出

### 傳統分割器輸出

測試成功後會生成：

- `service/chunk/output/chunk/chunks.xlsx` - Excel 輸出文件
- `service/chunk/output/md/chunks.md` - Markdown 輸出文件

### 分層分割器輸出

測試成功後會生成：

- `service/chunk/output/chunk/hierarchical_chunks.xlsx` - Excel 輸出文件
- `service/chunk/output/md/hierarchical_chunks.md` - Markdown 輸出文件

### 分析工具輸出

使用分析工具會生成：

- `service/chunk/analysis/output/` - 分析結果目錄
  - `analysis_summary.json` - 分析摘要
  - `[文件名]_Chunk.xlsx` - 分層分割 Excel 文件
  - `[文件名]_ConversionResult.json` - 轉換結果
  - `[文件名]_Markdown.md` - Markdown 文件

Excel 文件包含完整的原始內容和分割後的 chunks，便於人工檢核和分析。分層分割器額外提供詳細的分組效率和大小分布分析。
