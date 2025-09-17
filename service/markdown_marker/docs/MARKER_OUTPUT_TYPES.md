# Marker 輸出類型說明

## 概述

本文檔詳細說明了 Marker 轉換器的輸出類型，特別是 `MarkdownOutput` 對象的結構和屬性。

## 主要輸出類型

### MarkdownOutput 對象

當使用 `PdfConverter` 進行 PDF 轉換時，返回的是 `MarkdownOutput` 對象：

```python
from marker.renderers.markdown import MarkdownOutput

# 轉換器返回類型
rendered: MarkdownOutput = self.converter(input_pdf)
```

### MarkdownOutput 主要屬性

根據實際測試，`MarkdownOutput` 對象包含以下主要屬性：

#### 1. markdown (str)
- **類型**: `str`
- **描述**: 完整的 Markdown 內容字符串
- **用途**: 這是我們主要使用的屬性，包含整個 PDF 轉換後的 Markdown 內容
- **範例**: 
  ```python
  markdown_content: str = rendered.markdown
  print(f"Markdown 長度: {len(markdown_content)} 字元")
  ```

#### 2. images (Dict)
- **類型**: `Dict`
- **描述**: 圖片信息字典
- **用途**: 包含 PDF 中提取的圖片相關信息
- **範例**:
  ```python
  images_info: Dict = rendered.images
  print(f"圖片數量: {len(images_info)}")
  ```

#### 3. metadata (Dict)
- **類型**: `Dict`
- **描述**: 元數據信息字典
- **用途**: 包含文檔的元數據，如目錄結構等
- **範例**:
  ```python
  metadata_info: Dict = rendered.metadata
  print(f"元數據: {metadata_info}")
  ```

## 實際使用範例

### 基本使用

```python
def marker_pages(self, input_pdf: str) -> List[str]:
    """獲取 PDF 的每頁內容"""
    try:
        # 明確標注返回類型
        rendered: 'MarkdownOutput' = self.converter(input_pdf)
        
        # 提取 Markdown 內容
        if hasattr(rendered, 'markdown'):
            markdown_content: str = rendered.markdown
            pages = self._split_markdown_by_pages(markdown_content)
        else:
            # 備用方案
            pages = [str(rendered)]
        
        return pages
    except Exception as e:
        logger.error(f"轉換失敗: {e}")
        raise
```

### 完整屬性訪問

```python
def get_full_marker_output(self, input_pdf: str) -> Dict[str, Any]:
    """獲取完整的 Marker 輸出信息"""
    try:
        rendered: 'MarkdownOutput' = self.converter(input_pdf)
        
        return {
            'markdown': rendered.markdown,
            'images': rendered.images,
            'metadata': rendered.metadata,
            'markdown_length': len(rendered.markdown),
            'image_count': len(rendered.images),
            'has_metadata': bool(rendered.metadata)
        }
    except Exception as e:
        logger.error(f"獲取輸出失敗: {e}")
        raise

def get_pages_with_analysis(self, input_pdf: str) -> PagesResult:
    """獲取頁面列表和詳細分析"""
    try:
        result = self.marker_pages(input_pdf)
        
        # 添加額外的統計資訊
        total_chars = sum(page['content_length'] for page in result['pages'])
        avg_chars = total_chars / result['total_pages'] if result['total_pages'] > 0 else 0
        
        # 統計所有區塊類型
        all_block_types = {}
        for page in result['pages']:
            for block_type, count in page['block_types'].items():
                all_block_types[block_type] = all_block_types.get(block_type, 0) + count
        
        return {
            **result,
            'total_characters': total_chars,
            'average_chars_per_page': avg_chars,
            'all_block_types': all_block_types
        }
    except Exception as e:
        logger.error(f"獲取頁面分析失敗: {e}")
        raise
```

## 類型安全檢查

### 使用 hasattr 檢查

```python
# 安全的屬性訪問
if hasattr(rendered, 'markdown'):
    markdown_content = rendered.markdown
else:
    # 處理沒有 markdown 屬性的情況
    markdown_content = str(rendered)
```

### 使用 isinstance 檢查

```python
from marker.renderers.markdown import MarkdownOutput

# 類型檢查
if isinstance(rendered, MarkdownOutput):
    # 安全訪問 MarkdownOutput 屬性
    markdown_content = rendered.markdown
    images_info = rendered.images
    metadata_info = rendered.metadata
else:
    # 處理其他類型
    markdown_content = str(rendered)
```

## 實際測試結果

根據我們的測試，`MarkdownOutput` 對象的實際結構如下：

```
📊 輸出對象類型: <class 'marker.renderers.markdown.MarkdownOutput'>
📊 輸出對象模組: marker.renderers.markdown

📋 輸出對象屬性:
  - markdown: str (長度: 15053)
  - images: dict = {}
  - metadata: dict = {'table_of_contents': [...]}
  - 其他 Pydantic 相關屬性...
```

## 最佳實踐

### 1. 明確類型標注

```python
# 推薦：明確標注類型
rendered: 'MarkdownOutput' = self.converter(input_pdf)
markdown_content: str = rendered.markdown
```

### 2. 安全屬性訪問

```python
# 推薦：使用 hasattr 檢查
if hasattr(rendered, 'markdown'):
    markdown_content = rendered.markdown
else:
    # 備用方案
    markdown_content = str(rendered)
```

### 3. 錯誤處理

```python
try:
    rendered: 'MarkdownOutput' = self.converter(input_pdf)
    markdown_content = rendered.markdown
except AttributeError as e:
    logger.warning(f"MarkdownOutput 缺少預期屬性: {e}")
    markdown_content = str(rendered)
except Exception as e:
    logger.error(f"轉換失敗: {e}")
    raise
```

## 總結

- **主要類型**: `MarkdownOutput` 對象
- **核心屬性**: `markdown` (str), `images` (Dict), `metadata` (Dict)
- **最佳實踐**: 明確類型標注 + 安全屬性訪問 + 適當錯誤處理
- **主要用途**: 提取 `markdown` 屬性進行後續處理
