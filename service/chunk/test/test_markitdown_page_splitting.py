#!/usr/bin/env python3
"""
測試 ChunkSplitter 與 MarkitdownConverter 頁面分割功能的整合

測試在 MarkitdownConverter 頁面分割開啟和關閉情況下，
ChunkSplitter 是否能正常處理 Excel 文件並取得正確的 page_title。
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

def test_chunk_splitter_with_page_splitting_enabled():
    """測試啟用頁面分割時的 ChunkSplitter 表現"""
    print("=== 測試啟用頁面分割的 ChunkSplitter ===\n")
    
    # 創建啟用頁面分割的轉換器
    converter = UnifiedMarkdownConverter(enable_markitdown_page_splitting=True)
    
    # 轉換 Excel 文件
    print("🔄 步驟 1: 轉換 Excel 文件（啟用頁面分割）")
    result = converter.convert_file('raw_docs/理賠審核原則.xlsx')
    
    print(f"✅ 轉換完成")
    print(f"   - 檔名: {result.metadata.file_name}")
    print(f"   - 轉換器: {result.metadata.converter_used}")
    print(f"   - 總頁數: {result.metadata.total_pages}")
    print(f"   - 頁面信息: {'有' if result.pages and len(result.pages) > 0 else '無'}")
    
    if result.pages:
        print(f"   - 頁面標題範例: {[page.title for page in result.pages[:3]]}")
    
    # 使用 ChunkSplitter 分割
    print("\n✂️ 步驟 2: 使用 ChunkSplitter 分割")
    splitter = ChunkSplitter(
        chunk_size=500,
        chunk_overlap=100,
        normalize_output=True,
        keep_tables_together=True
    )
    
    chunks = splitter.split_markdown(
        input_data=result,
        output_excel=True,
        output_path="service/output/chunk/markitdown_enabled_test.xlsx",
        md_output_path="service/output/md/markitdown_enabled_test.md"
    )
    
    print(f"✅ 分割完成: 共 {len(chunks)} 個 chunks")
    
    # 分析結果
    print("\n📊 步驟 3: 分析結果")
    
    # 檢查 page_title 覆蓋率
    page_titles = [chunk.metadata.get('page_title') for chunk in chunks]
    has_page_titles = any(pt is not None for pt in page_titles)
    page_title_count = sum(1 for pt in page_titles if pt is not None)
    
    print(f"   - 總 chunks: {len(chunks)}")
    print(f"   - 有 page_title 的 chunks: {page_title_count}")
    print(f"   - page_title 覆蓋率: {page_title_count/len(chunks)*100:.1f}%")
    
    # 檢查前幾個 chunks 的 page_title
    print(f"\n📝 前 5 個 chunks 的 page_title:")
    for i, chunk in enumerate(chunks[:5], 1):
        page_number = chunk.metadata.get('page_number')
        page_title = chunk.metadata.get('page_title')
        print(f"   - Chunk {i}: 頁碼={page_number}, 頁面標題={page_title}")
    
    return chunks

def test_chunk_splitter_with_page_splitting_disabled():
    """測試禁用頁面分割時的 ChunkSplitter 表現"""
    print("\n=== 測試禁用頁面分割的 ChunkSplitter ===\n")
    
    # 創建禁用頁面分割的轉換器
    converter = UnifiedMarkdownConverter(enable_markitdown_page_splitting=False)
    
    # 轉換 Excel 文件
    print("🔄 步驟 1: 轉換 Excel 文件（禁用頁面分割）")
    result = converter.convert_file('raw_docs/理賠審核原則.xlsx')
    
    print(f"✅ 轉換完成")
    print(f"   - 檔名: {result.metadata.file_name}")
    print(f"   - 轉換器: {result.metadata.converter_used}")
    print(f"   - 總頁數: {result.metadata.total_pages}")
    print(f"   - 頁面信息: {'有' if result.pages and len(result.pages) > 0 else '無'}")
    
    # 使用 ChunkSplitter 分割
    print("\n✂️ 步驟 2: 使用 ChunkSplitter 分割")
    splitter = ChunkSplitter(
        chunk_size=500,
        chunk_overlap=100,
        normalize_output=True,
        keep_tables_together=True
    )
    
    chunks = splitter.split_markdown(
        input_data=result,
        output_excel=True,
        output_path="service/output/chunk/markitdown_disabled_test.xlsx",
        md_output_path="service/output/md/markitdown_disabled_test.md"
    )
    
    print(f"✅ 分割完成: 共 {len(chunks)} 個 chunks")
    
    # 分析結果
    print("\n📊 步驟 3: 分析結果")
    
    # 檢查 page_title 覆蓋率
    page_titles = [chunk.metadata.get('page_title') for chunk in chunks]
    has_page_titles = any(pt is not None for pt in page_titles)
    page_title_count = sum(1 for pt in page_titles if pt is not None)
    
    print(f"   - 總 chunks: {len(chunks)}")
    print(f"   - 有 page_title 的 chunks: {page_title_count}")
    print(f"   - page_title 覆蓋率: {page_title_count/len(chunks)*100:.1f}%")
    
    # 檢查前幾個 chunks 的 page_title
    print(f"\n📝 前 5 個 chunks 的 page_title:")
    for i, chunk in enumerate(chunks[:5], 1):
        page_number = chunk.metadata.get('page_number')
        page_title = chunk.metadata.get('page_title')
        print(f"   - Chunk {i}: 頁碼={page_number}, 頁面標題={page_title}")
    
    return chunks

def test_excel_output_comparison():
    """比較兩個 Excel 輸出的差異"""
    print("\n=== Excel 輸出比較 ===\n")
    
    try:
        import pandas as pd
        
        # 讀取兩個 Excel 文件
        enabled_file = "service/output/chunk/markitdown_enabled_test.xlsx"
        disabled_file = "service/output/chunk/markitdown_disabled_test.xlsx"
        
        if Path(enabled_file).exists() and Path(disabled_file).exists():
            df_enabled = pd.read_excel(enabled_file)
            df_disabled = pd.read_excel(disabled_file)
            
            print(f"📊 啟用頁面分割 Excel:")
            print(f"   - 總行數: {len(df_enabled)}")
            print(f"   - 頁面標題欄位: {'頁面標題' in df_enabled.columns}")
            if '頁面標題' in df_enabled.columns:
                page_title_values = df_enabled['頁面標題'].tolist()
                valid_titles = sum(1 for v in page_title_values if pd.notna(v) and v != '')
                print(f"   - 有效頁面標題數量: {valid_titles}")
                print(f"   - 頁面標題範例: {page_title_values[:3]}")
            
            print(f"\n📊 禁用頁面分割 Excel:")
            print(f"   - 總行數: {len(df_disabled)}")
            print(f"   - 頁面標題欄位: {'頁面標題' in df_disabled.columns}")
            if '頁面標題' in df_disabled.columns:
                page_title_values = df_disabled['頁面標題'].tolist()
                valid_titles = sum(1 for v in page_title_values if pd.notna(v) and v != '')
                print(f"   - 有效頁面標題數量: {valid_titles}")
                print(f"   - 頁面標題範例: {page_title_values[:3]}")
            
            print(f"\n📈 比較結果:")
            print(f"   - 啟用頁面分割: {len(df_enabled)} 行")
            print(f"   - 禁用頁面分割: {len(df_disabled)} 行")
            print(f"   - 差異: {len(df_enabled) - len(df_disabled)} 行")
            
        else:
            print("❌ Excel 文件不存在，無法比較")
            
    except Exception as e:
        print(f"❌ Excel 比較失敗: {e}")

def main():
    """主測試函數"""
    print("=== ChunkSplitter 與 MarkitdownConverter 頁面分割整合測試 ===\n")
    
    try:
        # 測試啟用頁面分割
        chunks_enabled = test_chunk_splitter_with_page_splitting_enabled()
        
        # 測試禁用頁面分割
        chunks_disabled = test_chunk_splitter_with_page_splitting_disabled()
        
        # 比較 Excel 輸出
        test_excel_output_comparison()
        
        # 總結
        print("\n=== 測試總結 ===")
        print(f"✅ 啟用頁面分割: {len(chunks_enabled)} 個 chunks")
        print(f"✅ 禁用頁面分割: {len(chunks_disabled)} 個 chunks")
        
        # 檢查 page_title 覆蓋率
        enabled_titles = sum(1 for chunk in chunks_enabled if chunk.metadata.get('page_title'))
        disabled_titles = sum(1 for chunk in chunks_disabled if chunk.metadata.get('page_title'))
        
        print(f"📊 頁面標題覆蓋率:")
        print(f"   - 啟用頁面分割: {enabled_titles}/{len(chunks_enabled)} ({enabled_titles/len(chunks_enabled)*100:.1f}%)")
        print(f"   - 禁用頁面分割: {disabled_titles}/{len(chunks_disabled)} ({disabled_titles/len(chunks_disabled)*100:.1f}%)")
        
        if enabled_titles > 0 and disabled_titles == 0:
            print("🎉 測試成功！頁面分割功能正常工作")
        else:
            print("❌ 測試可能異常，請檢查結果")
        
        print(f"\n🎉 測試完成！")
        print(f"📁 啟用頁面分割 Excel: service/output/chunk/markitdown_enabled_test.xlsx")
        print(f"📁 禁用頁面分割 Excel: service/output/chunk/markitdown_disabled_test.xlsx")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
