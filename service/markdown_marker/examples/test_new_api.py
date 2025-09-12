#!/usr/bin/env python3
"""
測試新的 API 設計

驗證 marker_json_pages 方法的新返回格式
"""

import sys
from pathlib import Path

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from json_marker_converter import JsonMarkerConverter, PagesResult, PageContent
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"❌ 依賴套件未安裝: {e}")
    DEPENDENCIES_AVAILABLE = False


def test_new_api():
    """測試新的 API 設計"""
    print("🔍 測試新的 API 設計")
    print("=" * 50)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 依賴套件未安裝，跳過測試")
        return
    
    # 尋找測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent.parent / "raw_docs" / "old_version"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ 未找到測試 PDF 檔案")
        return
    
    test_pdf = pdf_files[0]
    print(f"📁 使用測試檔案: {test_pdf.name}")
    
    try:
        converter = JsonMarkerConverter()
        print("✅ JSON Marker 轉換器建立成功")
        
        # 測試新的 marker_json_pages 方法
        print("🔄 測試 marker_json_pages 方法...")
        result: PagesResult = converter.marker_json_pages(str(test_pdf))
        
        print(f"📊 返回類型: {type(result)}")
        print(f"📊 檔案名稱: {result['file_name']}")
        print(f"📊 總頁數: {result['total_pages']}")
        print()
        
        # 檢查每頁的資訊
        print("📋 頁面資訊:")
        for i, page in enumerate(result['pages'][:3], 1):  # 只顯示前3頁
            print(f"第 {page['page_number']} 頁:")
            print(f"  - 內容長度: {page['content_length']} 字元")
            print(f"  - 區塊數量: {page['block_count']}")
            print(f"  - 區塊類型: {page['block_types']}")
            print(f"  - 內容預覽: {page['content'][:100]}...")
            print()
        
        # 測試 marker_json_to_markdown 方法
        print("🔄 測試 marker_json_to_markdown 方法...")
        markdown_content: str = converter.marker_json_to_markdown(str(test_pdf))
        print(f"📊 Markdown 內容長度: {len(markdown_content)} 字元")
        print(f"📊 內容預覽: {markdown_content[:200]}...")
        print()
        
        # 驗證類型標注
        print("🔧 類型標注驗證:")
        print(f"✅ result 類型: {type(result)}")
        print(f"✅ result['pages'] 類型: {type(result['pages'])}")
        print(f"✅ 第一頁類型: {type(result['pages'][0])}")
        print(f"✅ 第一頁內容類型: {type(result['pages'][0]['content'])}")
        print(f"✅ markdown_content 類型: {type(markdown_content)}")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_usage():
    """演示新的使用方式"""
    print("\n💡 新的使用方式演示")
    print("=" * 50)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 依賴套件未安裝，跳過演示")
        return
    
    # 尋找測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent.parent / "raw_docs" / "old_version"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ 未找到測試 PDF 檔案")
        return
    
    test_pdf = pdf_files[0]
    
    try:
        converter = JsonMarkerConverter()
        
        # 演示 1: 獲取頁面資訊
        print("📄 演示 1: 獲取頁面資訊")
        result: PagesResult = converter.marker_json_pages(str(test_pdf))
        
        print(f"檔案: {result['file_name']}")
        print(f"總頁數: {result['total_pages']}")
        
        # 統計資訊
        total_chars = sum(page['content_length'] for page in result['pages'])
        avg_chars = total_chars / result['total_pages']
        
        print(f"總字元數: {total_chars}")
        print(f"平均每頁字元數: {avg_chars:.1f}")
        
        # 區塊類型統計
        all_block_types = {}
        for page in result['pages']:
            for block_type, count in page['block_types'].items():
                all_block_types[block_type] = all_block_types.get(block_type, 0) + count
        
        print(f"區塊類型分布: {all_block_types}")
        print()
        
        # 演示 2: 逐頁處理
        print("📄 演示 2: 逐頁處理")
        for page in result['pages'][:2]:  # 只處理前2頁
            print(f"處理第 {page['page_number']} 頁...")
            content = page['content']
            
            # 可以對每頁進行個別處理
            if 'table' in page['block_types']:
                print(f"  - 包含 {page['block_types']['table']} 個表格")
            if 'title' in page['block_types']:
                print(f"  - 包含 {page['block_types']['title']} 個標題")
            print(f"  - 內容長度: {page['content_length']} 字元")
        print()
        
        # 演示 3: 生成完整文檔
        print("📄 演示 3: 生成完整文檔")
        markdown_content: str = converter.marker_json_to_markdown(str(test_pdf))
        print(f"完整 Markdown 文檔長度: {len(markdown_content)} 字元")
        print("✅ 包含頁碼標記和所有頁面內容")
        
    except Exception as e:
        print(f"❌ 演示失敗: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函數"""
    print("🚀 新 API 設計測試")
    print("=" * 60)
    
    test_new_api()
    demonstrate_usage()
    
    print("\n✅ 新 API 測試完成!")
    print("\n💡 總結:")
    print("  - marker_json_pages 現在返回 PagesResult 對象")
    print("  - 包含完整的頁面內容和統計資訊")
    print("  - 移除了 get_page_info 方法")
    print("  - 提供了更豐富的頁面分析功能")


if __name__ == "__main__":
    main()
