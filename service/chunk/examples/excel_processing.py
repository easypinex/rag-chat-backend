#!/usr/bin/env python3
"""
Excel 文件處理範例

展示如何使用 ChunkSplitter 處理 Excel 文件，包括有頁面結構和無頁面結構的情況。
"""

import sys
from pathlib import Path
import logging

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk import ChunkSplitter
from service.markdown_integrate import UnifiedMarkdownConverter

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def process_excel_file():
    """處理 Excel 文件"""
    print("=== Excel 文件處理範例 ===\n")
    
    # 1. 準備輸入文件
    excel_file = "raw_docs/理賠審核原則.xlsx"
    
    if not Path(excel_file).exists():
        print(f"❌ 找不到文件: {excel_file}")
        print("請確保文件存在於指定路徑")
        return
    
    print(f"📄 輸入文件: {excel_file}")
    
    # 2. 轉換 Excel 到 Markdown
    print("\n🔄 步驟 1: 轉換 Excel 到 Markdown")
    converter = UnifiedMarkdownConverter()
    result = converter.convert_file(excel_file)
    
    print(f"✅ 轉換完成")
    print(f"   - 檔名: {result.metadata.file_name}")
    print(f"   - 檔案類型: {result.metadata.file_type}")
    print(f"   - 轉換器: {result.metadata.converter_used}")
    print(f"   - 總頁數: {result.metadata.total_pages}")
    print(f"   - 總表格數: {result.metadata.total_tables}")
    print(f"   - 頁面信息: {'有' if result.pages and len(result.pages) > 0 else '無'}")
    
    # 3. 分割 Markdown 內容
    print("\n✂️ 步驟 2: 分割 Markdown 內容")
    
    # 創建分割器
    splitter = ChunkSplitter(
        chunk_size=800,           # 較小的 chunk 大小
        chunk_overlap=150,        # 較小的重疊
        normalize_output=True,    # 啟用內容正規化
        keep_tables_together=True # 保持表格完整性
    )
    
    # 分割內容
    chunks = splitter.split_markdown(
        input_data=result,
        output_excel=True,         # 輸出 Excel 文件
        output_path="service/output/chunk/excel_processing.xlsx",
        md_output_path="service/output/md/excel_processing.md"
    )
    
    print(f"✅ 分割完成: 共 {len(chunks)} 個 chunks")
    
    # 4. 分析結果
    print("\n📊 步驟 3: 分析結果")
    
    # 基本統計
    total_length = sum(len(chunk.page_content) for chunk in chunks)
    avg_length = total_length / len(chunks) if chunks else 0
    
    # 檢查頁碼情況
    page_numbers = [chunk.metadata.get('page_number') for chunk in chunks]
    has_page_numbers = any(pn is not None for pn in page_numbers)
    unique_pages = len(set(pn for pn in page_numbers if pn is not None))
    
    # 表格 chunks
    table_chunks = [chunk for chunk in chunks if chunk.metadata.get('is_table', False)]
    
    print(f"   - 總 chunks: {len(chunks)}")
    print(f"   - 總字符數: {total_length}")
    print(f"   - 平均長度: {avg_length:.1f}")
    print(f"   - 表格 chunks: {len(table_chunks)}")
    print(f"   - 一般 chunks: {len(chunks) - len(table_chunks)}")
    print(f"   - 頁碼情況: {'有頁碼' if has_page_numbers else '無頁碼'}")
    if has_page_numbers:
        print(f"   - 頁碼覆蓋: {unique_pages} 頁")
    
    # 5. 檢查分割模式
    print("\n🔍 步驟 4: 分割模式分析")
    if has_page_numbers:
        print("✅ 使用基於頁面的分割模式")
        print("   - 每個 chunk 都有明確的頁碼")
        print("   - 原始內容按頁面分組")
    else:
        print("✅ 使用基本分割模式")
        print("   - 直接處理完整內容")
        print("   - 沒有頁碼信息")
    
    # 6. 顯示前幾個 chunks
    print("\n📝 步驟 5: 前 3 個 Chunks 預覽")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n--- Chunk {i} ---")
        print(f"長度: {len(chunk.page_content)}")
        print(f"頁碼: {chunk.metadata.get('page_number', 'N/A')}")
        print(f"標題級數: {chunk.metadata.get('Header 1', 'N/A')}")
        print(f"內容預覽: {chunk.page_content[:100]}...")
    
    print(f"\n🎉 Excel 文件處理完成！")
    print(f"📁 Excel 文件: service/output/chunk/excel_processing.xlsx")
    print(f"📁 Markdown 文件: service/output/md/excel_processing.md")
    
    return chunks

def analyze_chunk_metadata(chunks):
    """分析 chunk metadata"""
    print("\n=== Chunk Metadata 分析 ===\n")
    
    if not chunks:
        print("❌ 沒有 chunks 可分析")
        return
    
    # 統計 metadata 欄位
    all_metadata_keys = set()
    for chunk in chunks:
        all_metadata_keys.update(chunk.metadata.keys())
    
    print(f"📊 Metadata 欄位統計:")
    for key in sorted(all_metadata_keys):
        count = sum(1 for chunk in chunks if key in chunk.metadata)
        print(f"   - {key}: {count}/{len(chunks)} chunks")
    
    # 檢查頁碼分布
    page_numbers = [chunk.metadata.get('page_number') for chunk in chunks]
    page_distribution = {}
    for pn in page_numbers:
        if pn is not None:
            page_distribution[pn] = page_distribution.get(pn, 0) + 1
    
    if page_distribution:
        print(f"\n📄 頁碼分布:")
        for page_num in sorted(page_distribution.keys()):
            print(f"   - 頁面 {page_num}: {page_distribution[page_num]} 個 chunks")
    else:
        print(f"\n📄 頁碼分布: 無頁碼信息（基本分割模式）")
    
    # 檢查標題級數分布
    header_levels = {}
    for chunk in chunks:
        level = get_header_level(chunk.metadata)
        header_levels[level] = header_levels.get(level, 0) + 1
    
    print(f"\n📋 標題級數分布:")
    for level in sorted(header_levels.keys()):
        print(f"   - {level}級標題: {header_levels[level]} 個 chunks")

def get_header_level(metadata):
    """獲取標題級數"""
    if 'Header 4' in metadata and metadata['Header 4']:
        return '四'
    elif 'Header 3' in metadata and metadata['Header 3']:
        return '三'
    elif 'Header 2' in metadata and metadata['Header 2']:
        return '二'
    elif 'Header 1' in metadata and metadata['Header 1']:
        return '一'
    else:
        return '無'

def main():
    """主函數"""
    print("=== Excel 文件處理範例 ===\n")
    
    try:
        # 處理 Excel 文件
        chunks = process_excel_file()
        
        if chunks:
            # 分析 metadata
            analyze_chunk_metadata(chunks)
            
            print(f"\n🎉 範例完成！")
        else:
            print(f"\n❌ 處理失敗")
            
    except Exception as e:
        print(f"\n❌ 處理過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
