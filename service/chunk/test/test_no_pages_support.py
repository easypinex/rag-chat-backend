#!/usr/bin/env python3
"""
測試沒有頁面結構的文件支援功能

模擬沒有頁面信息的 ConversionResult 來測試 _split_without_pages 方法。
"""

import sys
from pathlib import Path
import logging
from typing import List

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk import ChunkSplitter
from service.markdown_integrate.data_models import ConversionResult, ConversionMetadata, PageInfo
from langchain_core.documents import Document

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_mock_conversion_result_without_pages():
    """創建一個沒有頁面信息的模擬 ConversionResult"""
    
    # 模擬的 Markdown 內容
    mock_content = """# 測試文檔

這是一個測試文檔，用於驗證沒有頁面結構的文件處理。

## 第一節

這是第一節的內容，包含一些基本信息。

### 子標題 1.1

這是子標題的內容。

## 第二節

這是第二節的內容。

### 子標題 2.1

這是另一個子標題的內容。

## 表格範例

| 欄位1 | 欄位2 | 欄位3 |
|-------|-------|-------|
| 值1   | 值2   | 值3   |
| 值4   | 值5   | 值6   |

## 結論

這是文檔的結論部分。
"""
    
    # 創建 metadata
    metadata = ConversionMetadata(
        file_name="test_no_pages.md",
        file_path="test_no_pages.md",
        file_type=".md",
        file_size=len(mock_content),
        total_pages=0,  # 沒有頁面
        total_tables=1,
        total_content_length=len(mock_content),
        conversion_timestamp=1234567890.0,
        converter_used="test_converter"
    )
    
    # 創建 ConversionResult，不設置 pages（或設置為空列表）
    result = ConversionResult(
        content=mock_content,
        metadata=metadata,
        pages=None  # 沒有頁面信息
    )
    
    return result

def test_no_pages_splitting():
    """測試沒有頁面結構的分割功能"""
    print("=== 測試沒有頁面結構的文件分割 ===\n")
    
    # 1. 創建模擬的 ConversionResult
    print("🔄 步驟 1: 創建模擬的 ConversionResult（無頁面信息）")
    conversion_result = create_mock_conversion_result_without_pages()
    
    print(f"✅ 模擬 ConversionResult 創建完成")
    print(f"   - 檔名: {conversion_result.metadata.file_name}")
    print(f"   - 檔案類型: {conversion_result.metadata.file_type}")
    print(f"   - 轉換器: {conversion_result.metadata.converter_used}")
    print(f"   - 總頁數: {conversion_result.metadata.total_pages}")
    print(f"   - 總表格數: {conversion_result.metadata.total_tables}")
    print(f"   - 頁面信息: {'有' if conversion_result.pages and len(conversion_result.pages) > 0 else '無'}")
    print(f"   - 內容長度: {len(conversion_result.content)}")
    
    # 2. 分割內容
    print("\n✂️ 步驟 2: 分割 Markdown 內容")
    
    # 創建分割器
    splitter = ChunkSplitter(
        chunk_size=500,           # 較小的 chunk 大小
        chunk_overlap=100,        # 較小的重疊
        normalize_output=True,    # 啟用內容正規化
        keep_tables_together=True # 保持表格完整性
    )
    
    # 分割內容
    chunks = splitter.split_markdown(
        input_data=conversion_result,
        output_excel=True,         # 輸出 Excel 文件
        output_path="service/output/chunk/no_pages_test.xlsx",
        md_output_path="service/output/md/no_pages_test.md"
    )
    
    print(f"✅ 分割完成: 共 {len(chunks)} 個 chunks")
    
    # 3. 分析結果
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
    
    # 4. 檢查 metadata
    print("\n📝 步驟 4: 檢查 Metadata")
    if chunks:
        sample_chunk = chunks[0]
        print(f"範例 chunk metadata:")
        for key, value in sample_chunk.metadata.items():
            if key not in ['Header 1', 'Header 2', 'Header 3', 'Header 4']:
                print(f"   - {key}: {value}")
    
    # 5. 顯示所有 chunks
    print("\n📄 步驟 5: 所有 Chunks 預覽")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- Chunk {i} ---")
        print(f"長度: {len(chunk.page_content)}")
        print(f"頁碼: {chunk.metadata.get('page_number', 'N/A')}")
        print(f"標題級數: {chunk.metadata.get('Header 1', 'N/A')}")
        print(f"內容預覽: {chunk.page_content[:150]}...")
    
    print(f"\n🎉 沒有頁面結構的文件分割測試完成！")
    print(f"📁 Excel 文件: service/output/chunk/no_pages_test.xlsx")
    print(f"📁 Markdown 文件: service/output/md/no_pages_test.md")
    
    return chunks

def test_metadata_consistency_no_pages(chunks: List[Document]):
    """測試沒有頁面結構的 metadata 一致性"""
    print("\n=== 測試 Metadata 一致性（無頁面結構） ===\n")
    
    # 檢查所有 chunks 的 metadata 一致性
    required_fields = ['file_name', 'file_type', 'source', 'converter_used', 'total_pages', 'total_tables']
    
    print("檢查必要 metadata 欄位:")
    for field in required_fields:
        missing_count = sum(1 for chunk in chunks if field not in chunk.metadata)
        print(f"   - {field}: {len(chunks) - missing_count}/{len(chunks)} chunks 包含此欄位")
    
    # 檢查頁碼情況
    page_number_count = sum(1 for chunk in chunks if chunk.metadata.get('page_number') is not None)
    print(f"   - page_number: {page_number_count}/{len(chunks)} chunks 有頁碼（預期為 0）")
    
    # 檢查是否有其他不應該存在的頁面相關信息
    page_related_fields = ['page_number']
    for field in page_related_fields:
        present_count = sum(1 for chunk in chunks if chunk.metadata.get(field) is not None)
        print(f"   - {field}: {present_count}/{len(chunks)} chunks 有此欄位（預期為 0）")
    
    print("✅ Metadata 一致性檢查完成")

def main():
    """主測試函數"""
    print("=== 沒有頁面結構的文件支援功能測試 ===\n")
    
    try:
        # 測試沒有頁面結構的分割功能
        chunks = test_no_pages_splitting()
        
        if chunks:
            # 測試 metadata 一致性
            test_metadata_consistency_no_pages(chunks)
            
            print(f"\n🎉 所有測試完成！")
        else:
            print(f"\n❌ 測試失敗")
            
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
