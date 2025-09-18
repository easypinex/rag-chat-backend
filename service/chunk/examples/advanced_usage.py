#!/usr/bin/env python3
"""
Chunk 分割器進階使用範例

這個範例展示進階功能，包括自定義參數、批量處理等。
"""

import sys
from pathlib import Path
import logging
from typing import List

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk import ChunkSplitter
from service.markdown_integrate import UnifiedMarkdownConverter
from langchain_core.documents import Document

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def process_multiple_files():
    """批量處理多個文件"""
    print("=== 批量處理多個文件 ===\n")
    
    # 文件列表
    files = [
        "raw_docs/old_version/台灣人壽美年有鑫美元利率變動型還本終身保險.pdf",
        # 可以添加更多文件
    ]
    
    converter = UnifiedMarkdownConverter()
    all_chunks = []
    
    for file_path in files:
        if not Path(file_path).exists():
            print(f"⚠️ 跳過不存在的文件: {file_path}")
            continue
        
        print(f"🔄 處理文件: {file_path}")
        
        # 轉換文件
        result = converter.convert_file(file_path)
        
        # 分割內容
        splitter = ChunkSplitter(
            chunk_size=800,           # 較小的 chunk 大小
            chunk_overlap=150,        # 較小的重疊
            normalize_output=True,
            keep_tables_together=True
        )
        
        chunks = splitter.split_markdown(input_data=result)
        all_chunks.extend(chunks)
        
        print(f"   ✅ 完成: {len(chunks)} 個 chunks")
    
    print(f"\n📊 批量處理結果:")
    print(f"   - 總文件數: {len(files)}")
    print(f"   - 總 chunks: {len(all_chunks)}")
    
    return all_chunks

def custom_chunk_analysis(chunks: List[Document]):
    """自定義 chunk 分析"""
    print("\n=== 自定義 Chunk 分析 ===\n")
    
    # 按頁碼分組
    page_groups = {}
    for chunk in chunks:
        page_num = chunk.metadata.get('page_number')
        if page_num not in page_groups:
            page_groups[page_num] = []
        page_groups[page_num].append(chunk)
    
    print("📄 按頁碼分組統計:")
    for page_num in sorted(page_groups.keys()):
        page_chunks = page_groups[page_num]
        total_length = sum(len(chunk.page_content) for chunk in page_chunks)
        avg_length = total_length / len(page_chunks)
        
        print(f"   頁面 {page_num}: {len(page_chunks)} 個 chunks, 平均長度: {avg_length:.1f}")
    
    # 按標題級數分組
    header_groups = {}
    for chunk in chunks:
        header_level = get_header_level(chunk.metadata)
        if header_level not in header_groups:
            header_groups[header_level] = []
        header_groups[header_level].append(chunk)
    
    print("\n📋 按標題級數分組統計:")
    for level in sorted(header_groups.keys()):
        chunks_count = len(header_groups[level])
        print(f"   {level}級標題: {chunks_count} 個 chunks")
    
    # 長度分布分析
    lengths = [len(chunk.page_content) for chunk in chunks]
    lengths.sort()
    
    print(f"\n📏 長度分布分析:")
    print(f"   最短: {min(lengths)} 字符")
    print(f"   最長: {max(lengths)} 字符")
    print(f"   中位數: {lengths[len(lengths)//2]} 字符")
    
    # 找出異常長的 chunks
    long_chunks = [chunk for chunk in chunks if len(chunk.page_content) > 2000]
    if long_chunks:
        print(f"\n⚠️ 異常長的 chunks ({len(long_chunks)} 個):")
        for i, chunk in enumerate(long_chunks[:3], 1):
            print(f"   {i}. 長度: {len(chunk.page_content)}, 頁碼: {chunk.metadata.get('page_number')}")

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

def export_custom_analysis(chunks: List[Document]):
    """導出自定義分析結果"""
    print("\n=== 導出自定義分析 ===\n")
    
    # 創建自定義分割器用於導出
    splitter = ChunkSplitter()
    
    # 導出到 Excel
    output_path = "service/output/chunk/advanced_analysis.xlsx"
    splitter._export_to_excel_with_page_info(
        chunks, 
        [],  # 空的頁面信息，使用備用邏輯
        output_path
    )
    
    print(f"📊 分析結果已導出到: {output_path}")

def main():
    """進階使用範例主函數"""
    print("=== Chunk 分割器進階使用範例 ===\n")
    
    # 1. 批量處理
    all_chunks = process_multiple_files()
    
    if not all_chunks:
        print("❌ 沒有處理到任何文件")
        return
    
    # 2. 自定義分析
    custom_chunk_analysis(all_chunks)
    
    # 3. 導出分析結果
    export_custom_analysis(all_chunks)
    
    print(f"\n🎉 進階範例完成！")

if __name__ == "__main__":
    main()
