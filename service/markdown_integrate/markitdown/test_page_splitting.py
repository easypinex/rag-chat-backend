#!/usr/bin/env python3
"""
測試 MarkitdownConverter 的頁面分割功能

測試啟用和禁用頁面分割的不同行為。
"""

import sys
from pathlib import Path
import logging

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from service.markdown_integrate.markitdown.markitdown_converter import MarkitdownConverter

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_page_splitting_enabled():
    """測試啟用頁面分割的情況"""
    print("=== 測試啟用頁面分割 ===\n")
    
    # 創建啟用頁面分割的轉換器
    converter = MarkitdownConverter(
        input_dir="raw_docs",
        output_dir="service/output/markitdown_test",
        enable_page_splitting=True
    )
    
    # 測試 Excel 文件
    excel_file = "raw_docs/理賠審核原則.xlsx"
    if not Path(excel_file).exists():
        print(f"❌ 找不到文件: {excel_file}")
        return None
    
    print(f"📄 測試文件: {excel_file}")
    
    # 轉換文件並獲取元數據
    result = converter.convert_file_with_metadata(excel_file)
    
    print(f"✅ 轉換完成")
    print(f"   - 檔名: {result['file_name']}")
    print(f"   - 檔案類型: {result['file_type']}")
    print(f"   - 頁面數量: {len(result.get('pages', []))}")
    print(f"   - 頁面標題數量: {len(result.get('page_titles', []))}")
    
    # 顯示頁面信息
    if result.get('pages'):
        print(f"\n📄 頁面信息:")
        for i, (page, title) in enumerate(zip(result['pages'], result.get('page_titles', [])), 1):
            print(f"   - 頁面 {i}: {title}")
            print(f"     內容長度: {len(page)}")
            print(f"     內容預覽: {page[:100]}...")
            print()
    
    return result

def test_page_splitting_disabled():
    """測試禁用頁面分割的情況"""
    print("=== 測試禁用頁面分割 ===\n")
    
    # 創建禁用頁面分割的轉換器
    converter = MarkitdownConverter(
        input_dir="raw_docs",
        output_dir="service/output/markitdown_test",
        enable_page_splitting=False
    )
    
    # 測試 Excel 文件
    excel_file = "raw_docs/理賠審核原則.xlsx"
    if not Path(excel_file).exists():
        print(f"❌ 找不到文件: {excel_file}")
        return None
    
    print(f"📄 測試文件: {excel_file}")
    
    # 轉換文件並獲取元數據
    result = converter.convert_file_with_metadata(excel_file)
    
    print(f"✅ 轉換完成")
    print(f"   - 檔名: {result['file_name']}")
    print(f"   - 檔案類型: {result['file_type']}")
    print(f"   - 頁面數量: {len(result.get('pages', []))}")
    print(f"   - 頁面標題數量: {len(result.get('page_titles', []))}")
    
    # 檢查是否為空列表
    pages = result.get('pages', [])
    if not pages:
        print(f"✅ 頁面分割已禁用，返回空頁面列表（符合預期）")
    else:
        print(f"❌ 頁面分割已禁用，但仍有頁面內容（不符合預期）")
    
    return result

def test_header_splitting():
    """測試 ## 標題分割功能"""
    print("=== 測試 ## 標題分割功能 ===\n")
    
    # 創建轉換器
    converter = MarkitdownConverter(enable_page_splitting=True)
    
    # 模擬有 ## 標題的內容
    test_content = """# 主標題

這是主標題的內容。

## 第一節

這是第一節的內容。

## 第二節

這是第二節的內容。

## 第三節

這是第三節的內容。
"""
    
    print("📝 測試內容:")
    print(test_content)
    print()
    
    # 測試分割功能
    pages = converter._split_by_headers(test_content)
    
    print(f"✅ 分割結果: {len(pages)} 個頁面")
    for i, page in enumerate(pages, 1):
        print(f"\n--- 頁面 {i} ---")
        print(f"長度: {len(page)}")
        print(f"內容: {page[:200]}...")
    
    return pages

def test_title_extraction():
    """測試標題提取功能"""
    print("=== 測試標題提取功能 ===\n")
    
    # 創建轉換器
    converter = MarkitdownConverter(enable_page_splitting=True)
    
    # 測試不同的頁面內容
    test_cases = [
        ("## 第一節\n\n這是第一節的內容。", "第一節"),
        ("# 主標題\n\n這是主標題的內容。", "主標題"),
        ("**重要標題**\n\n這是重要標題的內容。", "重要標題"),
        ("普通內容\n\n沒有標題的內容。", "普通內容"),
        ("", "Page 1"),
    ]
    
    for i, (content, expected) in enumerate(test_cases, 1):
        title = converter._extract_page_title(content, i)
        print(f"測試 {i}:")
        print(f"  內容: {content[:50]}...")
        print(f"  預期標題: {expected}")
        print(f"  實際標題: {title}")
        print(f"  結果: {'✅' if title == expected else '❌'}")
        print()

def main():
    """主測試函數"""
    print("=== MarkitdownConverter 頁面分割功能測試 ===\n")
    
    try:
        # 測試標題提取
        test_title_extraction()
        
        # 測試標題分割
        test_header_splitting()
        
        # 測試啟用頁面分割
        result_enabled = test_page_splitting_enabled()
        
        # 測試禁用頁面分割
        result_disabled = test_page_splitting_disabled()
        
        # 比較結果
        print("=== 結果比較 ===")
        if result_enabled and result_disabled:
            pages_enabled = len(result_enabled.get('pages', []))
            pages_disabled = len(result_disabled.get('pages', []))
            
            print(f"啟用頁面分割: {pages_enabled} 個頁面")
            print(f"禁用頁面分割: {pages_disabled} 個頁面")
            print(f"差異: {pages_enabled - pages_disabled} 個頁面")
            
            if pages_enabled > 0 and pages_disabled == 0:
                print("✅ 頁面分割功能正常工作")
            else:
                print("❌ 頁面分割功能可能異常")
        
        print(f"\n🎉 測試完成！")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
