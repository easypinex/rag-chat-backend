"""
Markdown 正規化器測試腳本

測試 MarkdownNormalizer 的功能，包括表格清理、HTML 標籤移除等。
"""

import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk import MarkdownNormalizer, ChunkSplitter
from langchain_core.documents import Document
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_normalizer_basic():
    """測試基本正規化功能"""
    logger.info("=== 測試基本正規化功能 ===")
    
    # 創建測試內容
    test_content = """
# 測試標題

這是一個測試段落，包含多餘的空格   和   換行。

## 表格測試

| 欄位1 | 欄位2 | 欄位3 |
|-------|-------|-------|
| 值1   | 值2   | 值3   |
| 值4   | 值5   | 值6   |

### HTML 標籤測試

這是一個包含 <br> 標籤的段落。<br><br>還有 <strong>粗體</strong> 和 <em>斜體</em> 文字。

#### 多餘符號測試

| 欄位1    | 欄位2    | 欄位3    |
|----------|----------|----------|
| 值1      | 值2      | 值3      |
| 值4      | 值5      | 值6      |
"""
    
    # 創建文檔
    doc = Document(page_content=test_content, metadata={'test': True})
    
    # 創建正規化器
    normalizer = MarkdownNormalizer()
    
    # 正規化文檔
    normalized_doc = normalizer.normalize_document(doc)
    
    logger.info("原始內容:")
    logger.info(f"長度: {len(doc.page_content)}")
    logger.info(f"行數: {len(doc.page_content.split(chr(10)))}")
    
    logger.info("\n正規化後內容:")
    logger.info(f"長度: {len(normalized_doc.page_content)}")
    logger.info(f"行數: {len(normalized_doc.page_content.split(chr(10)))}")
    
    logger.info("\n正規化後內容預覽:")
    logger.info(normalized_doc.page_content)
    
    # 獲取統計信息
    stats = normalizer.get_normalization_stats(doc.page_content, normalized_doc.page_content)
    logger.info(f"\n正規化統計: {stats}")


def test_normalizer_with_chunks():
    """測試使用現有的 chunks 進行正規化"""
    logger.info("=== 測試使用現有 chunks 進行正規化 ===")
    
    # 讀取現有的 chunks 文件
    chunks_file = Path("service/chunk/output/md/chunks.md")
    if not chunks_file.exists():
        logger.warning("沒有找到現有的 chunks 文件，跳過此測試")
        return
    
    # 創建 ChunkSplitter 並啟用正規化
    splitter = ChunkSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        keep_tables_together=True,
        normalize_output=True  # 啟用正規化
    )
    
    # 讀取原始內容
    with open(chunks_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # 創建文檔
    doc = Document(page_content=original_content, metadata={'source': 'chunks.md'})
    
    # 使用正規化器
    normalizer = MarkdownNormalizer()
    normalized_doc = normalizer.normalize_document(doc)
    
    # 保存正規化後的內容
    output_file = Path("service/chunk/output/md/normalized_chunks.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(normalized_doc.page_content)
    
    # 統計信息
    stats = normalizer.get_normalization_stats(doc.page_content, normalized_doc.page_content)
    logger.info(f"正規化統計: {stats}")
    logger.info(f"正規化後文件保存至: {output_file}")


def test_table_cleaning():
    """測試表格清理功能"""
    logger.info("=== 測試表格清理功能 ===")
    
    # 包含多餘符號的表格
    messy_table = """
| 欄位1    | 欄位2    | 欄位3    |
|----------|----------|----------|
| 值1      | 值2      | 值3      |
| 值4      | 值5      | 值6      |
| 值7      | 值8      | 值9      |
"""
    
    normalizer = MarkdownNormalizer()
    cleaned_table = normalizer.normalize_text(messy_table)
    
    logger.info("原始表格:")
    logger.info(repr(messy_table))
    
    logger.info("\n清理後表格:")
    logger.info(repr(cleaned_table))
    
    logger.info("\n清理後表格顯示:")
    logger.info(cleaned_table)


def test_html_removal():
    """測試 HTML 標籤移除功能"""
    logger.info("=== 測試 HTML 標籤移除功能 ===")
    
    html_content = """
# 測試 HTML 內容

這是一個包含 <br> 標籤的段落。<br><br>

還有 <strong>粗體</strong> 和 <em>斜體</em> 文字。

<div class="container">
    <p>這是一個段落</p>
    <span>這是 span 標籤</span>
</div>

最後是 <a href="http://example.com">連結</a>。
"""
    
    normalizer = MarkdownNormalizer()
    cleaned_content = normalizer.normalize_text(html_content)
    
    logger.info("原始內容:")
    logger.info(html_content)
    
    logger.info("\n清理後內容:")
    logger.info(cleaned_content)


if __name__ == "__main__":
    # 運行所有測試
    test_normalizer_basic()
    test_table_cleaning()
    test_html_removal()
    test_normalizer_with_chunks()
    
    logger.info("=== 所有測試完成 ===")
