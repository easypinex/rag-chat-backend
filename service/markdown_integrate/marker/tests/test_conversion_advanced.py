"""
JSON Marker Converter 轉換測試

實際測試 JSON Marker 轉換器的轉換功能
"""

import os
import sys
import logging
from pathlib import Path

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from marker_converter import MarkerConverter

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_single_pdf_conversion():
    """測試單一 PDF 檔案轉換"""
    print("=== 測試單一 PDF 檔案轉換 ===")
    
    try:
        converter = MarkerConverter()
        print("✓ JSON Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ 依賴套件未安裝: {e}")
        return False
    
    # 指定測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent / "raw_docs" / "old_version"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("✗ 未找到測試 PDF 檔案")
        return False
    
    test_pdf = pdf_files[0]
    print(f"使用測試檔案: {test_pdf.name}")
    
    try:
        # 獲取頁面資訊
        page_info = converter.get_page_info(str(test_pdf))
        print(f"頁面資訊:")
        print(f"  - 檔案名: {page_info['file_name']}")
        print(f"  - 總頁數: {page_info['total_pages']}")
        
        # 進行轉換
        output_path = test_pdf.parent / f"{test_pdf.stem}_json_test.md"
        markdown_content = converter.convert_pdf_to_markdown(
            str(test_pdf), 
            str(output_path)
        )
        
        print(f"✓ 轉換成功!")
        print(f"  - 輸出檔案: {output_path}")
        print(f"  - 內容長度: {len(markdown_content)} 字元")
        
        # 檢查輸出檔案是否存在
        if output_path.exists():
            print(f"  - 檔案大小: {output_path.stat().st_size} bytes")
        
        # 檢查內容是否包含頁碼
        if "## Page" in markdown_content:
            print("  - ✓ 包含頁碼標記")
        else:
            print("  - ✗ 缺少頁碼標記")
        
        # 檢查內容是否包含表格
        if "|" in markdown_content and "---" in markdown_content:
            print("  - ✓ 包含表格內容")
        else:
            print("  - - 無表格內容")
        
        return True
        
    except Exception as e:
        print(f"✗ 轉換失敗: {e}")
        return False


def test_batch_conversion():
    """測試批量轉換"""
    print("\n=== 測試批量轉換 ===")
    
    try:
        converter = MarkerConverter()
        print("✓ JSON Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ 依賴套件未安裝: {e}")
        return False
    
    # 指定測試目錄
    raw_docs_dir = Path(__file__).parent.parent.parent / "raw_docs" / "old_version"
    
    if not raw_docs_dir.exists():
        print("✗ 測試目錄不存在")
        return False
    
    # 建立輸出目錄
    output_dir = Path(__file__).parent / "json_converted"
    output_dir.mkdir(exist_ok=True)
    
    try:
        results = converter.convert_multiple_pdfs(
            str(raw_docs_dir), 
            str(output_dir)
        )
        
        print(f"✓ 批量轉換完成!")
        print(f"  - 處理檔案數: {len(results)}")
        print(f"  - 輸出目錄: {output_dir}")
        
        success_count = 0
        for filename, content in results.items():
            if content.startswith("Error:"):
                print(f"  ✗ {filename}: {content}")
            else:
                print(f"  ✓ {filename}: {len(content)} 字元")
                success_count += 1
        
        print(f"  - 成功轉換: {success_count}/{len(results)} 個檔案")
        return success_count > 0
        
    except Exception as e:
        print(f"✗ 批量轉換失敗: {e}")
        return False


def test_page_structure_analysis():
    """測試頁面結構分析"""
    print("\n=== 測試頁面結構分析 ===")
    
    try:
        converter = MarkerConverter()
        print("✓ JSON Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ 依賴套件未安裝: {e}")
        return False
    
    # 指定測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent / "raw_docs" / "old_version"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("✗ 未找到測試 PDF 檔案")
        return False
    
    test_pdf = pdf_files[0]
    print(f"分析檔案: {test_pdf.name}")
    
    try:
        # 獲取頁面結構
        pages = converter.marker_pages(str(test_pdf))
        
        print(f"總頁數: {len(pages)}")
        
        # 分析前幾頁
        for i, page in enumerate(pages[:3], start=1):
            children = getattr(page, "children", []) or []
            print(f"\n第 {i} 頁結構:")
            print(f"  - 區塊數量: {len(children)}")
            
            # 統計區塊類型
            block_types = {}
            for child in children:
                bt = getattr(child, "block_type", "unknown")
                block_types[bt] = block_types.get(bt, 0) + 1
            
            print(f"  - 區塊類型分布:")
            for bt, count in block_types.items():
                print(f"    - {bt}: {count} 個")
        
        return True
        
    except Exception as e:
        print(f"✗ 頁面結構分析失敗: {e}")
        return False


def test_table_conversion():
    """測試表格轉換功能"""
    print("\n=== 測試表格轉換功能 ===")
    
    try:
        converter = MarkerConverter()
        print("✓ JSON Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ 依賴套件未安裝: {e}")
        return False
    
    # 測試 HTML 表格轉換
    test_cases = [
        {
            "name": "簡單表格",
            "html": """
            <table>
                <tr><th>姓名</th><th>年齡</th><th>城市</th></tr>
                <tr><td>張三</td><td>25</td><td>台北</td></tr>
                <tr><td>李四</td><td>30</td><td>高雄</td></tr>
            </table>
            """,
            "expected": ["| 姓名 | 年齡 | 城市 |", "| 張三 | 25 | 台北 |"]
        },
        {
            "name": "複雜表格（rowspan）",
            "html": """
            <table>
                <tr><th rowspan="2">項目</th><th>Q1</th><th>Q2</th></tr>
                <tr><td>100</td><td>200</td></tr>
            </table>
            """,
            "expected": ["complex table; keep HTML", "<table>"]
        }
    ]
    
    success_count = 0
    for test_case in test_cases:
        print(f"\n測試 {test_case['name']}:")
        result = converter._table_html_to_md(test_case['html'])
        
        # 檢查預期結果
        all_expected_found = True
        for expected in test_case['expected']:
            if expected in result:
                print(f"  ✓ 找到預期內容: {expected}")
            else:
                print(f"  ✗ 缺少預期內容: {expected}")
                all_expected_found = False
        
        if all_expected_found:
            success_count += 1
            print(f"  ✓ {test_case['name']} 測試通過")
        else:
            print(f"  ✗ {test_case['name']} 測試失敗")
    
    print(f"\n表格轉換測試結果: {success_count}/{len(test_cases)} 通過")
    return success_count == len(test_cases)


def test_error_handling():
    """測試錯誤處理"""
    print("\n=== 測試錯誤處理 ===")
    
    try:
        converter = MarkerConverter()
        print("✓ JSON Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ 依賴套件未安裝: {e}")
        return False
    
    # 測試檔案不存在錯誤
    try:
        converter.convert_pdf_to_markdown("nonexistent.pdf")
        print("✗ 應該拋出 FileNotFoundError")
        return False
    except FileNotFoundError:
        print("✓ 正確捕獲檔案不存在錯誤")
    except Exception as e:
        print(f"✗ 捕獲到錯誤但不是預期的 FileNotFoundError: {e}")
        return False
    
    # 測試目錄不存在錯誤
    try:
        converter.convert_multiple_pdfs("nonexistent_directory")
        print("✗ 應該拋出 FileNotFoundError")
        return False
    except FileNotFoundError:
        print("✓ 正確捕獲目錄不存在錯誤")
    except Exception as e:
        print(f"✗ 捕獲到錯誤但不是預期的 FileNotFoundError: {e}")
        return False
    
    return True


def main():
    """主測試函數"""
    print("JSON Marker Converter 轉換測試")
    print("=" * 50)
    
    # 檢查依賴套件
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.config.parser import ConfigParser
        from bs4 import BeautifulSoup
        print("✓ 所有依賴套件已安裝")
    except ImportError as e:
        print(f"✗ 依賴套件未安裝: {e}")
        print("請執行: pip install marker-pdf[full] beautifulsoup4")
        return
    
    # 執行測試
    tests = [
        test_single_pdf_conversion,
        test_batch_conversion,
        test_page_structure_analysis,
        test_table_conversion,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ 測試 {test_func.__name__} 執行失敗: {e}")
    
    print(f"\n測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過!")
    else:
        print("⚠️  部分測試失敗，請檢查上述錯誤訊息")


if __name__ == "__main__":
    main()
