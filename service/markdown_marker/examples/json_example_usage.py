"""
JSON Marker Converter 使用範例

展示如何使用 JSON Marker 轉換器進行 PDF 到 Markdown 的轉換
支援每頁結構化輸出和表格轉換
"""

import os
import sys
import logging
from pathlib import Path

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from json_marker_converter import JsonMarkerConverter, create_json_marker_converter

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_single_pdf_conversion():
    """單一 PDF 檔案轉換範例（使用 JSON API）"""
    print("=== 單一 PDF 檔案轉換範例（JSON API） ===")
    
    # 建立轉換器
    try:
        converter = JsonMarkerConverter()
        print("✓ JSON Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ 依賴套件未安裝: {e}")
        return
    
    # 指定測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent / "raw_docs" / "old_version"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("✗ 未找到測試 PDF 檔案")
        return
    
    test_pdf = pdf_files[0]
    print(f"使用測試檔案: {test_pdf.name}")
    
    # 獲取頁面資訊
    try:
        page_info = converter.get_page_info(str(test_pdf))
        print(f"頁面資訊:")
        print(f"  - 檔案名: {page_info['file_name']}")
        print(f"  - 總頁數: {page_info['total_pages']}")
        for page in page_info['pages'][:3]:  # 只顯示前3頁
            print(f"  - 第 {page['page_number']} 頁: {page['block_count']} 個區塊")
    except Exception as e:
        print(f"✗ 獲取頁面資訊失敗: {e}")
        return
    
    # 進行轉換
    try:
        output_path = test_pdf.parent / f"{test_pdf.stem}_json_marker.md"
        markdown_content = converter.convert_pdf_to_markdown(
            str(test_pdf), 
            str(output_path)
        )
        
        print(f"✓ 轉換成功!")
        print(f"  - 輸出檔案: {output_path}")
        print(f"  - 內容長度: {len(markdown_content)} 字元")
        print(f"  - 內容預覽:")
        print("    " + "\n    ".join(markdown_content[:500].split("\n")[:10]))
        
    except Exception as e:
        print(f"✗ 轉換失敗: {e}")


def example_batch_conversion():
    """批量轉換範例（使用 JSON API）"""
    print("\n=== 批量轉換範例（JSON API） ===")
    
    try:
        converter = JsonMarkerConverter()
        print("✓ JSON Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ 依賴套件未安裝: {e}")
        return
    
    # 指定測試目錄
    raw_docs_dir = Path(__file__).parent.parent.parent / "raw_docs" / "old_version"
    
    if not raw_docs_dir.exists():
        print("✗ 測試目錄不存在")
        return
    
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
        
        for filename, content in results.items():
            if content.startswith("Error:"):
                print(f"  ✗ {filename}: {content}")
            else:
                print(f"  ✓ {filename}: {len(content)} 字元")
        
    except Exception as e:
        print(f"✗ 批量轉換失敗: {e}")


def example_page_structure_analysis():
    """頁面結構分析範例"""
    print("\n=== 頁面結構分析範例 ===")
    
    try:
        converter = JsonMarkerConverter()
        print("✓ JSON Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ 依賴套件未安裝: {e}")
        return
    
    # 指定測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent / "raw_docs" / "old_version"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("✗ 未找到測試 PDF 檔案")
        return
    
    test_pdf = pdf_files[0]
    print(f"分析檔案: {test_pdf.name}")
    
    try:
        # 獲取頁面結構
        pages = converter.marker_json_pages(str(test_pdf))
        
        print(f"總頁數: {len(pages)}")
        
        for i, page in enumerate(pages[:3], start=1):  # 只分析前3頁
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
            
            # 顯示前幾個區塊的內容預覽
            print(f"  - 內容預覽:")
            for j, child in enumerate(children[:3]):
                text = getattr(child, "text", None) or getattr(child, "markdown", None) or ""
                preview = text[:100].replace("\n", " ") if text else "[無文字內容]"
                bt = getattr(child, "block_type", "unknown")
                print(f"    {j+1}. [{bt}] {preview}...")
        
    except Exception as e:
        print(f"✗ 頁面結構分析失敗: {e}")


def example_table_conversion():
    """表格轉換範例"""
    print("\n=== 表格轉換範例 ===")
    
    try:
        converter = JsonMarkerConverter()
        print("✓ JSON Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ 依賴套件未安裝: {e}")
        return
    
    # 測試 HTML 表格轉換
    test_html_tables = [
        # 簡單表格
        """
        <table>
            <tr><th>姓名</th><th>年齡</th><th>城市</th></tr>
            <tr><td>張三</td><td>25</td><td>台北</td></tr>
            <tr><td>李四</td><td>30</td><td>高雄</td></tr>
        </table>
        """,
        # 複雜表格（有 rowspan）
        """
        <table>
            <tr><th rowspan="2">項目</th><th>Q1</th><th>Q2</th></tr>
            <tr><td>100</td><td>200</td></tr>
        </table>
        """
    ]
    
    for i, html in enumerate(test_html_tables, 1):
        print(f"\n測試表格 {i}:")
        print("原始 HTML:")
        print(html.strip())
        print("\n轉換結果:")
        result = converter._table_html_to_md(html)
        print(result)


def example_custom_model_locations():
    """自定義模型位置範例"""
    print("\n=== 自定義模型位置範例 ===")
    
    # 自定義模型位置（範例）
    model_locations = {
        "layout_model": "/path/to/layout/model",
        "ocr_model": "/path/to/ocr/model",
        "edit_model": "/path/to/edit/model"
    }
    
    try:
        # 使用便利函數建立轉換器
        converter = create_json_marker_converter(model_locations)
        print("✓ 使用自定義模型位置的轉換器建立成功")
        
        # 注意：實際使用時需要確保模型檔案存在於指定位置
        
    except ImportError as e:
        print(f"✗ 依賴套件未安裝: {e}")
    except Exception as e:
        print(f"✗ 建立轉換器失敗: {e}")


def example_error_handling():
    """錯誤處理範例"""
    print("\n=== 錯誤處理範例 ===")
    
    try:
        converter = JsonMarkerConverter()
    except ImportError as e:
        print(f"✗ 依賴套件未安裝: {e}")
        return
    
    # 測試不存在的檔案
    try:
        converter.convert_pdf_to_markdown("nonexistent.pdf")
    except FileNotFoundError as e:
        print(f"✓ 正確捕獲檔案不存在錯誤: {e}")
    
    # 測試不存在的目錄
    try:
        converter.convert_multiple_pdfs("nonexistent_directory")
    except FileNotFoundError as e:
        print(f"✓ 正確捕獲目錄不存在錯誤: {e}")


def main():
    """主函數"""
    print("JSON Marker Converter 使用範例")
    print("=" * 50)
    
    # 檢查依賴套件是否可用
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.config.parser import ConfigParser
        print("✓ Marker 套件已安裝")
    except ImportError:
        print("✗ Marker 套件未安裝，請執行: pip install marker-pdf[full]")
        return
    
    try:
        from bs4 import BeautifulSoup
        print("✓ BeautifulSoup 套件已安裝")
    except ImportError:
        print("✗ BeautifulSoup 套件未安裝，請執行: pip install beautifulsoup4")
        return
    
    # 執行範例
    example_single_pdf_conversion()
    example_batch_conversion()
    example_page_structure_analysis()
    example_table_conversion()
    example_custom_model_locations()
    example_error_handling()
    
    print("\n範例執行完成!")


if __name__ == "__main__":
    main()
