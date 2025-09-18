#!/usr/bin/env python3
"""
測試 Excel 文件支援功能

測試 ChunkSplitter 對沒有頁面結構的文件的處理能力。
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

def test_excel_file_conversion():
    """測試 Excel 文件轉換"""
    print("=== 測試 Excel 文件轉換功能 ===\n")
    
    # 1. 準備輸入文件
    excel_file = "raw_docs/理賠審核原則.xlsx"
    
    if not Path(excel_file).exists():
        print(f"❌ 找不到文件: {excel_file}")
        print("請確保文件存在於指定路徑")
        return False
    
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
        output_path="service/output/chunk/excel_test.xlsx",
        md_output_path="service/output/md/excel_test.md"
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
    
    # 表格 chunks
    table_chunks = [chunk for chunk in chunks if chunk.metadata.get('is_table', False)]
    
    print(f"   - 總 chunks: {len(chunks)}")
    print(f"   - 總字符數: {total_length}")
    print(f"   - 平均長度: {avg_length:.1f}")
    print(f"   - 表格 chunks: {len(table_chunks)}")
    print(f"   - 一般 chunks: {len(chunks) - len(table_chunks)}")
    print(f"   - 頁碼情況: {'有頁碼' if has_page_numbers else '無頁碼（符合預期）'}")
    
    # 5. 檢查 metadata
    print("\n📝 步驟 4: 檢查 Metadata")
    if chunks:
        sample_chunk = chunks[0]
        print(f"範例 chunk metadata:")
        for key, value in sample_chunk.metadata.items():
            if key not in ['Header 1', 'Header 2', 'Header 3', 'Header 4']:
                print(f"   - {key}: {value}")
    
    # 6. 顯示前幾個 chunks
    print("\n📄 步驟 5: 前 3 個 Chunks 預覽")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n--- Chunk {i} ---")
        print(f"長度: {len(chunk.page_content)}")
        print(f"頁碼: {chunk.metadata.get('page_number', 'N/A')}")
        print(f"標題級數: {chunk.metadata.get('Header 1', 'N/A')}")
        print(f"內容預覽: {chunk.page_content[:100]}...")
    
    print(f"\n🎉 Excel 文件轉換測試完成！")
    print(f"📁 Excel 文件: service/output/chunk/excel_test.xlsx")
    print(f"📁 Markdown 文件: service/output/md/excel_test.md")
    
    return True

def test_metadata_consistency():
    """測試 metadata 一致性"""
    print("\n=== 測試 Metadata 一致性 ===\n")
    
    excel_file = "raw_docs/理賠審核原則.xlsx"
    if not Path(excel_file).exists():
        print("❌ 測試文件不存在，跳過 metadata 測試")
        return
    
    # 轉換和分割
    converter = UnifiedMarkdownConverter()
    result = converter.convert_file(excel_file)
    
    splitter = ChunkSplitter(normalize_output=True)
    chunks = splitter.split_markdown(input_data=result)
    
    # 檢查所有 chunks 的 metadata 一致性
    required_fields = ['file_name', 'file_type', 'source', 'converter_used', 'total_pages', 'total_tables']
    
    print("檢查必要 metadata 欄位:")
    for field in required_fields:
        missing_count = sum(1 for chunk in chunks if field not in chunk.metadata)
        print(f"   - {field}: {len(chunks) - missing_count}/{len(chunks)} chunks 包含此欄位")
    
    # 檢查頁碼情況
    page_number_count = sum(1 for chunk in chunks if chunk.metadata.get('page_number') is not None)
    print(f"   - page_number: {page_number_count}/{len(chunks)} chunks 有頁碼（預期為 0）")
    
    print("✅ Metadata 一致性檢查完成")

def main():
    """主測試函數"""
    print("=== Excel 文件支援功能測試 ===\n")
    
    try:
        # 測試基本轉換功能
        success = test_excel_file_conversion()
        
        if success:
            # 測試 metadata 一致性
            test_metadata_consistency()
            
            print(f"\n🎉 所有測試完成！")
        else:
            print(f"\n❌ 測試失敗")
            
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
