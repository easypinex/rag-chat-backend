"""
Chunk 分割器測試腳本

使用 unified_converter 轉換 PDF 文件，然後測試 chunk 分割功能。
"""

import os
import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from service.markdown_integrate import UnifiedMarkdownConverter
from service.chunk import ChunkSplitter
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_chunk_splitter():
    """測試 chunk 分割器"""
    
    # 測試文件路徑
    test_pdf = "raw_docs/old_version/台灣人壽美年有鑫美元利率變動型還本終身保險.pdf"
    
    # 輸出目錄
    output_dir = Path("service/output")
    md_output_dir = output_dir / "md"
    excel_output_dir = output_dir / "chunk"
    
    # 確保輸出目錄存在
    md_output_dir.mkdir(parents=True, exist_ok=True)
    excel_output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=== 開始測試 Chunk 分割器 ===")
    
    try:
        # 1. 使用 UnifiedMarkdownConverter 轉換 PDF
        logger.info("步驟 1: 轉換 PDF 到 Markdown")
        converter = UnifiedMarkdownConverter()
        
        # 檢查轉換器狀態
        status = converter.get_converter_status()
        logger.info(f"轉換器狀態: {status}")
        
        if not status['marker'] and not status['markitdown']:
            logger.error("沒有可用的轉換器！")
            return
        
        # 轉換文件
        result = converter.convert_file(test_pdf, save_to_file=True)
        logger.info(f"轉換完成: {result.metadata.file_name}")
        logger.info(f"總頁數: {result.metadata.total_pages}")
        logger.info(f"總表格數: {result.metadata.total_tables}")
        
        # 2. 使用 ChunkSplitter 分割 Markdown
        logger.info("步驟 2: 分割 Markdown 內容")
        chunk_splitter = ChunkSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            keep_tables_together=True
        )
        
        # 使用 ConversionResult 對象進行分割
        chunks = chunk_splitter.split_markdown(
            input_data=result,
            output_excel=True,
            output_path=str(excel_output_dir / "chunks.xlsx"),
            md_output_path=str(md_output_dir / "chunks.md")
        )
        
        logger.info(f"分割完成: 共 {len(chunks)} 個 chunks")
        
        # 3. 獲取統計信息
        stats = chunk_splitter.get_chunk_statistics(chunks)
        logger.info("=== 分割統計 ===")
        for key, value in stats.items():
            logger.info(f"{key}: {value}")
        
        # 4. 表格統計
        table_stats = chunk_splitter.table_handler.get_table_statistics(chunks)
        logger.info("=== 表格統計 ===")
        for key, value in table_stats.items():
            logger.info(f"{key}: {value}")
        
        # 5. 顯示前幾個 chunks 的內容
        logger.info("=== 前 3 個 Chunks 預覽 ===")
        for i, chunk in enumerate(chunks[:3], 1):
            logger.info(f"--- Chunk {i} ---")
            logger.info(f"長度: {len(chunk.page_content)}")
            logger.info(f"元數據: {chunk.metadata}")
            logger.info(f"內容預覽: {chunk.page_content[:200]}...")
            logger.info("")
        
        logger.info("=== 測試完成 ===")
        logger.info(f"Excel 文件: {excel_output_dir / 'chunks.xlsx'}")
        logger.info(f"Markdown 文件: {md_output_dir / 'chunks.md'}")
        
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


def test_with_markdown_file():
    """測試使用 Markdown 文件作為輸入"""
    logger.info("=== 測試 Markdown 文件輸入 ===")
    
    # 查找現有的 Markdown 文件
    md_files = list(Path("service/markdown_integrate/marker/converted").glob("*.md"))
    if not md_files:
        logger.warning("沒有找到 Markdown 文件")
        return
    
    test_md = md_files[0]
    logger.info(f"使用文件: {test_md}")
    
    # 創建 ChunkSplitter
    chunk_splitter = ChunkSplitter(
        chunk_size=800,
        chunk_overlap=150,
        keep_tables_together=True
    )
    
    # 分割文件
    chunks = chunk_splitter.split_markdown(
        input_data=str(test_md),
        output_excel=True,
        output_path="service/output/chunk/markdown_test.xlsx",
        md_output_path="service/output/md/markdown_test.md"
    )
    
    logger.info(f"Markdown 文件分割完成: {len(chunks)} 個 chunks")
    
    # 統計信息
    stats = chunk_splitter.get_chunk_statistics(chunks)
    logger.info("統計信息:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")


if __name__ == "__main__":
    # 測試 PDF 轉換和分割
    test_chunk_splitter()
    
    # 測試 Markdown 文件分割
    test_with_markdown_file()
