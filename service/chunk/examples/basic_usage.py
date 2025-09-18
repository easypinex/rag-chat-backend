#!/usr/bin/env python3
"""
Chunk 分割器基本使用範例

這個範例展示如何使用 ChunkSplitter 來分割 PDF 文件。
"""

import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk import ChunkSplitter
from service.markdown_integrate import UnifiedMarkdownConverter
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """基本使用範例"""
    print("=== Chunk 分割器基本使用範例 ===\n")
    
    # 1. 準備輸入文件
    pdf_file = "raw_docs/old_version/台灣人壽美年有鑫美元利率變動型還本終身保險.pdf"
    
    if not Path(pdf_file).exists():
        print(f"❌ 找不到文件: {pdf_file}")
        print("請確保文件存在於指定路徑")
        return
    
    print(f"📄 輸入文件: {pdf_file}")
    
    # 2. 轉換 PDF 到 Markdown
    print("\n🔄 步驟 1: 轉換 PDF 到 Markdown")
    converter = UnifiedMarkdownConverter()
    result = converter.convert_file(pdf_file)
    
    print(f"✅ 轉換完成")
    print(f"   - 總頁數: {result.metadata.total_pages}")
    print(f"   - 總表格數: {result.metadata.total_tables}")
    print(f"   - 轉換器: {result.metadata.converter_used}")
    
    # 3. 分割 Markdown 內容
    print("\n✂️ 步驟 2: 分割 Markdown 內容")
    
    # 創建分割器
    splitter = ChunkSplitter(
        chunk_size=1000,           # 每個 chunk 的最大字符數
        chunk_overlap=200,         # chunk 之間的重疊字符數
        normalize_output=True,     # 啟用內容正規化
        keep_tables_together=True  # 保持表格完整性
    )
    
    # 分割內容
    chunks = splitter.split_markdown(
        input_data=result,
        output_excel=True,         # 輸出 Excel 文件
        output_path="service/output/chunk/basic_example.xlsx",
        md_output_path="service/output/md/basic_example.md"
    )
    
    print(f"✅ 分割完成: 共 {len(chunks)} 個 chunks")
    
    # 4. 分析結果
    print("\n📊 步驟 3: 分析結果")
    
    # 統計信息
    total_length = sum(len(chunk.page_content) for chunk in chunks)
    avg_length = total_length / len(chunks) if chunks else 0
    
    table_chunks = [chunk for chunk in chunks if chunk.metadata.get('is_table', False)]
    
    print(f"   - 總 chunks: {len(chunks)}")
    print(f"   - 總字符數: {total_length}")
    print(f"   - 平均長度: {avg_length:.1f}")
    print(f"   - 表格 chunks: {len(table_chunks)}")
    print(f"   - 一般 chunks: {len(chunks) - len(table_chunks)}")
    
    # 頁碼分布
    page_numbers = [chunk.metadata.get('page_number') for chunk in chunks if chunk.metadata.get('page_number')]
    if page_numbers:
        unique_pages = len(set(page_numbers))
        print(f"   - 頁碼覆蓋: {unique_pages} 頁")
    
    # 5. 顯示前幾個 chunks
    print("\n📝 步驟 4: 前 3 個 Chunks 預覽")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n--- Chunk {i} ---")
        print(f"長度: {len(chunk.page_content)}")
        print(f"頁碼: {chunk.metadata.get('page_number', 'N/A')}")
        print(f"標題級數: {chunk.metadata.get('Header 1', 'N/A')}")
        print(f"內容預覽: {chunk.page_content[:100]}...")
    
    print(f"\n🎉 範例完成！")
    print(f"📁 Excel 文件: service/output/chunk/basic_example.xlsx")
    print(f"📁 Markdown 文件: service/output/md/basic_example.md")

if __name__ == "__main__":
    main()
