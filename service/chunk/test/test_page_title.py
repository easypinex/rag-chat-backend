#!/usr/bin/env python3
"""
測試 page_title 功能

創建模擬的 PageInfo 來測試 page_title 功能是否正常工作。
"""

import sys
from pathlib import Path
import logging

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk import ChunkSplitter
from service.markdown_integrate.data_models import ConversionResult, ConversionMetadata, PageInfo
from langchain_core.documents import Document

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_mock_conversion_result_with_page_titles():
    """創建一個有頁面標題的模擬 ConversionResult"""
    
    # 模擬的 Markdown 內容
    mock_content = """# 測試文檔

這是一個測試文檔，用於驗證頁面標題功能。

## 第一節

這是第一節的內容。

## 第二節

這是第二節的內容。
"""
    
    # 創建有標題的頁面
    pages = [
        PageInfo(
            page_number=1,
            title="封面頁",
            content="# 測試文檔\n\n這是一個測試文檔，用於驗證頁面標題功能。",
            content_length=50
        ),
        PageInfo(
            page_number=2,
            title="內容頁面",
            content="## 第一節\n\n這是第一節的內容。\n\n## 第二節\n\n這是第二節的內容。",
            content_length=100
        )
    ]
    
    # 創建 metadata
    metadata = ConversionMetadata(
        file_name="test_with_titles.pdf",
        file_path="test_with_titles.pdf",
        file_type=".pdf",
        file_size=len(mock_content),
        total_pages=2,
        total_tables=0,
        total_content_length=len(mock_content),
        conversion_timestamp=1234567890.0,
        converter_used="test_converter"
    )
    
    # 創建 ConversionResult
    result = ConversionResult(
        content=mock_content,
        metadata=metadata,
        pages=pages
    )
    
    return result

def test_page_title_functionality():
    """測試頁面標題功能"""
    print("=== 測試 Page Title 功能 ===\n")
    
    # 1. 創建模擬的 ConversionResult
    print("🔄 步驟 1: 創建模擬的 ConversionResult（有頁面標題）")
    conversion_result = create_mock_conversion_result_with_page_titles()
    
    print(f"✅ 模擬 ConversionResult 創建完成")
    print(f"   - 檔名: {conversion_result.metadata.file_name}")
    print(f"   - 總頁數: {conversion_result.metadata.total_pages}")
    print(f"   - 頁面信息: {'有' if conversion_result.pages and len(conversion_result.pages) > 0 else '無'}")
    
    # 檢查頁面標題
    if conversion_result.pages:
        print(f"   - 頁面標題:")
        for page in conversion_result.pages:
            print(f"     頁面 {page.page_number}: {page.title}")
    
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
        output_path="service/output/chunk/page_title_test.xlsx",
        md_output_path="service/output/md/page_title_test.md"
    )
    
    print(f"✅ 分割完成: 共 {len(chunks)} 個 chunks")
    
    # 3. 分析結果
    print("\n📊 步驟 3: 分析結果")
    
    # 檢查頁面標題
    page_titles = [chunk.metadata.get('page_title') for chunk in chunks]
    has_page_titles = any(pt is not None for pt in page_titles)
    
    print(f"   - 總 chunks: {len(chunks)}")
    print(f"   - 頁面標題情況: {'有頁面標題' if has_page_titles else '無頁面標題'}")
    
    # 4. 檢查每個 chunk 的頁面標題
    print("\n📝 步驟 4: Chunk 頁面標題檢查")
    for i, chunk in enumerate(chunks, 1):
        page_number = chunk.metadata.get('page_number')
        page_title = chunk.metadata.get('page_title')
        print(f"   - Chunk {i}: 頁碼={page_number}, 頁面標題={page_title}")
    
    # 5. 檢查 Excel 輸出
    print("\n📊 步驟 5: Excel 輸出檢查")
    try:
        import pandas as pd
        df = pd.read_excel("service/output/chunk/page_title_test.xlsx")
        
        print(f"   - Excel 總行數: {len(df)}")
        print(f"   - 頁面標題欄位: {'頁面標題' in df.columns}")
        
        if '頁面標題' in df.columns:
            page_title_values = df['頁面標題'].tolist()
            print(f"   - 頁面標題值: {page_title_values}")
            print(f"   - 有效頁面標題數量: {sum(1 for v in page_title_values if pd.notna(v) and v != '')}")
        
    except Exception as e:
        print(f"   - Excel 檢查失敗: {e}")
    
    print(f"\n🎉 Page Title 功能測試完成！")
    print(f"📁 Excel 文件: service/output/chunk/page_title_test.xlsx")
    print(f"📁 Markdown 文件: service/output/md/page_title_test.md")
    
    return chunks

def main():
    """主測試函數"""
    print("=== Page Title 功能測試 ===\n")
    
    try:
        # 測試頁面標題功能
        chunks = test_page_title_functionality()
        
        if chunks:
            print(f"\n🎉 測試完成！")
        else:
            print(f"\n❌ 測試失敗")
            
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
