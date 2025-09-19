# 文件分析工具

這個工具用於分析 `raw_docs/` 目錄下的文件，使用 ChunkSplitter 進行智能分割，並產生結構化的分析結果。

## 功能特色

- 自動處理 `raw_docs/` 目錄下的所有支援文件格式
- 使用 UnifiedConverter 將文件轉換為 Markdown
- 使用 ChunkSplitter 進行智能分割
- **序列化支援**: 自動保存和重用 ConversionResult JSON 文件
- 為每個文件創建專用的輸出目錄
- 產生詳細的分析報告

## 支援的文件格式

- PDF (.pdf)
- Word 文件 (.docx)
- Excel 文件 (.xlsx, .xls)
- 文字文件 (.txt)
- Markdown 文件 (.md)

## 輸出結構

每個分析的文件會產生以下結構：

```
chunk/analysis/output/
├── {文件名}/
│   ├── {文件名}.{副檔名}                    # 原始文件
│   ├── {文件名}_Markdown.md                # 轉換後的 Markdown
│   ├── {文件名}_Chunk.xlsx                 # 分析報告 Excel
│   └── {文件名}_ConversionResult.json       # 序列化的 ConversionResult
└── analysis_summary.json                   # 整體分析摘要
```

## 使用方法

### 1. 分析所有文件

```bash
cd service/chunk/analysis
python analysis.py
```

### 2. 分析特定文件

```bash
python analysis.py --file "文件名.pdf"
```

### 3. 自訂參數

```bash
python analysis.py \
  --raw-docs "raw_docs" \
  --output "service/chunk/analysis/output" \
  --chunk-size 1000 \
  --chunk-overlap 200
```

## 參數說明

- `--file`: 指定要分析的文件名
- `--raw-docs`: 原始文件目錄（預設：raw_docs）
- `--output`: 輸出目錄（預設：service/chunk/analysis/output）
- `--chunk-size`: Chunk 大小（預設：1000）
- `--chunk-overlap`: Chunk 重疊大小（預設：200）

## 程式化使用

```python
from analysis import DocumentAnalyzer

# 創建分析器
analyzer = DocumentAnalyzer(
    raw_docs_dir="raw_docs",
    output_base_dir="service/chunk/analysis/output",
    chunk_size=1000,
    chunk_overlap=200
)

# 分析所有文件
summary = analyzer.analyze_all_files()

# 分析特定文件
result = analyzer.analyze_single_file("文件名.pdf")
```

## 測試

執行測試腳本：

```bash
python test_analysis.py
```

## 輸出說明

### Excel 報告內容

- **Chunks 工作表**: 包含所有分割後的 chunks 詳細信息
- **原始內容工作表**: 完整的原始 Markdown 內容
- **正規化內容工作表**: 正規化後的內容
- **統計信息工作表**: 分析統計數據

### 分析摘要 (analysis_summary.json)

```json
{
  "total_files": 5,
  "successful": 4,
  "failed": 1,
  "success_rate": 80.0,
  "analysis_timestamp": "2024-01-01T12:00:00",
  "results": [
    {
      "file_name": "文件.pdf",
      "status": "success",
      "chunks_count": 15,
      "statistics": {
        "total_chunks": 15,
        "average_length": 850,
        "table_chunks": 3
      }
    }
  ]
}
```

## 序列化功能

### 自動序列化
- 每次轉換文件後，會自動保存 `ConversionResult` 為 JSON 文件
- 文件路徑：`{輸出目錄}/{文件名}/{文件名}_ConversionResult.json`

### 智能重用
- 如果發現已存在的序列化文件，會優先使用
- 避免重複的長時間轉換過程
- 大幅提升開發效率

### 序列化文件內容
```json
{
  "content": "完整的 markdown 內容",
  "metadata": {
    "file_name": "文件名",
    "file_type": "文件類型",
    "total_pages": 總頁數,
    "converter_used": "使用的轉換器"
  },
  "pages": [
    {
      "page_number": 頁碼,
      "title": "頁面標題",
      "content": "頁面內容",
      "tables": [...]
    }
  ],
  "serialization_timestamp": "序列化時間戳"
}
```

## 注意事項

1. 確保 `raw_docs/` 目錄存在且包含要分析的文件
2. 輸出目錄會自動創建
3. 如果文件已存在，會被覆蓋
4. 大型文件處理可能需要較長時間
5. 確保有足夠的磁碟空間存儲輸出文件
6. **序列化文件會自動重用，避免重複轉換**

## 錯誤處理

程式會記錄所有處理過程和錯誤信息到日誌中。如果某個文件處理失敗，會繼續處理其他文件，並在最終摘要中報告失敗的文件。
