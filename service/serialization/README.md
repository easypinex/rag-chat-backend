# Serialization 模組

這個模組提供 `ConversionResult` 對象的序列化和反序列化功能，支援將轉換結果保存為 JSON 格式，並可以從 JSON 文件恢復完整的 `ConversionResult` 對象。

## 功能特色

- **完整序列化**: 支援 `ConversionResult`、`ConversionMetadata`、`PageInfo`、`TableInfo` 的完整序列化
- **JSON 格式**: 使用 JSON 格式儲存，便於查看和調試
- **元數據保存**: 保存所有轉換元數據，包括文件信息、頁面信息、表格信息等
- **版本控制**: 支援序列化版本標記，便於未來擴展
- **文件管理**: 提供文件列表、驗證、信息查詢等功能
- **ChunkSplitter 整合**: 直接支援從序列化文件進行 chunk 分割

## 模組結構

```
service/serialization/
├── __init__.py                    # 模組初始化
├── conversion_serializer.py       # 序列化器
├── conversion_deserializer.py    # 反序列化器
├── example_usage.py              # 使用範例
└── README.md                     # 說明文件
```

## 快速開始

### 1. 序列化 ConversionResult

```python
from service.serialization import ConversionSerializer
from service.markdown_integrate.data_models import ConversionResult

# 創建序列化器
serializer = ConversionSerializer()

# 序列化 ConversionResult
json_path = serializer.serialize(conversion_result, "my_conversion.json")
print(f"序列化完成: {json_path}")
```

### 2. 反序列化 ConversionResult

```python
from service.serialization import ConversionDeserializer

# 創建反序列化器
deserializer = ConversionDeserializer()

# 從 JSON 文件反序列化
conversion_result = deserializer.deserialize("my_conversion.json")
print(f"文件名: {conversion_result.metadata.file_name}")
```

### 3. 使用序列化文件進行 Chunk 分割

```python
from service.chunk.chunk_splitter import ChunkSplitter

# 創建 ChunkSplitter
splitter = ChunkSplitter()

# 從序列化文件分割
chunks = splitter.split_markdown(
    input_data="my_conversion.json",
    from_serialization=True,
    output_excel=True
)
```

## API 參考

### ConversionSerializer

#### `__init__(output_dir: str = "service/serialization/markdown")`
初始化序列化器，指定 JSON 文件輸出目錄。

#### `serialize(conversion_result: ConversionResult, filename: Optional[str] = None) -> str`
序列化 `ConversionResult` 為 JSON 文件。

**參數:**
- `conversion_result`: 要序列化的 ConversionResult 對象
- `filename`: 自定義文件名，如果為 None 則自動生成

**返回:**
- `str`: JSON 文件路徑

#### `get_available_files() -> list[str]`
獲取可用的序列化文件列表。

#### `get_file_info(file_path: str) -> Dict[str, Any]`
獲取序列化文件的基本信息。

### ConversionDeserializer

#### `__init__(input_dir: str = "service/serialization/markdown")`
初始化反序列化器，指定 JSON 文件輸入目錄。

#### `deserialize(file_path: str) -> ConversionResult`
從 JSON 文件反序列化 `ConversionResult`。

**參數:**
- `file_path`: JSON 文件路徑

**返回:**
- `ConversionResult`: 反序列化後的對象

#### `deserialize_from_latest() -> Optional[ConversionResult]`
從最新的序列化文件反序列化。

#### `deserialize_by_filename(filename: str) -> ConversionResult`
根據文件名反序列化。

#### `list_available_files() -> List[Dict[str, Any]]`
列出可用的序列化文件及其信息。

#### `validate_file(file_path: str) -> bool`
驗證序列化文件是否有效。

## 使用場景

### 1. 長時間轉換的結果保存

當文件轉換需要很長時間時，可以將 `ConversionResult` 序列化保存，避免重複轉換：

```python
# 轉換完成後立即序列化
conversion_result = unified_converter.convert_file("large_document.pdf")
serializer = ConversionSerializer()
json_path = serializer.serialize(conversion_result)

# 後續使用時直接反序列化
deserializer = ConversionDeserializer()
conversion_result = deserializer.deserialize(json_path)
```

### 2. 批次處理多個文件

```python
# 轉換多個文件並序列化
for file_path in file_list:
    conversion_result = unified_converter.convert_file(file_path)
    serializer.serialize(conversion_result)

# 後續批次處理
deserializer = ConversionDeserializer()
for json_file in deserializer.list_available_files():
    conversion_result = deserializer.deserialize(json_file["file_path"])
    chunks = splitter.split_markdown(conversion_result)
```

### 3. 開發和調試

序列化文件便於查看轉換結果的詳細信息，支援調試和驗證：

```python
# 查看序列化文件信息
deserializer = ConversionDeserializer()
files = deserializer.list_available_files()
for file_info in files:
    print(f"文件: {file_info['original_file_name']}")
    print(f"頁數: {file_info['total_pages']}")
    print(f"轉換器: {file_info['converter_used']}")
```

## 文件格式

序列化的 JSON 文件包含以下結構：

```json
{
  "content": "完整的 markdown 內容",
  "metadata": {
    "file_name": "文件名",
    "file_path": "文件路徑",
    "file_type": "文件類型",
    "file_size": 文件大小,
    "total_pages": 總頁數,
    "total_tables": 總表格數,
    "total_content_length": 總內容長度,
    "conversion_timestamp": 轉換時間戳,
    "converter_used": "使用的轉換器",
    "additional_info": {}
  },
  "pages": [
    {
      "page_number": 頁碼,
      "title": "頁面標題",
      "content": "頁面內容",
      "content_length": 內容長度,
      "block_count": 區塊數量,
      "block_types": {"區塊類型": 數量},
      "table_count": 表格數量,
      "tables": [
        {
          "table_id": "表格ID",
          "title": "表格標題",
          "content": "表格內容",
          "row_count": 行數,
          "column_count": 列數,
          "start_line": 開始行,
          "end_line": 結束行
        }
      ]
    }
  ],
  "output_path": "輸出路徑",
  "serialization_timestamp": "序列化時間戳",
  "serialization_version": "序列化版本"
}
```

## 注意事項

1. **文件大小**: 大型文件的序列化文件可能很大，請確保有足夠的磁盤空間
2. **編碼**: 所有文件使用 UTF-8 編碼
3. **路徑**: 序列化文件中的路徑為字符串格式
4. **版本兼容**: 不同版本的序列化格式可能不兼容，請注意版本標記
5. **文件清理**: 定期清理不需要的序列化文件以節省空間

## 範例執行

運行完整的使用範例：

```bash
cd service/serialization
python example_usage.py
```

這將執行所有序列化和反序列化範例，展示完整的使用流程。
