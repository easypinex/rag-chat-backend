"""
Marker Converter 使用範例

展示如何使用 Marker 轉換器進行 PDF 到 Markdown 的轉換
"""

import os
import sys
import logging
from pathlib import Path

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from marker_converter import MarkerConverter, create_marker_converter

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_single_pdf_conversion():
    """單一 PDF 檔案轉換範例"""
    print("=== 單一 PDF 檔案轉換範例 ===")
    
    # 建立轉換器
    try:
        converter = MarkerConverter()
        print("✓ Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ Marker 套件未安裝: {e}")
        return
    
    # 指定測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent / "raw_docs" / "old_version"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("✗ 未找到測試 PDF 檔案")
        return
    
    test_pdf = pdf_files[0]
    print(f"使用測試檔案: {test_pdf.name}")
    
    # 獲取檔案資訊
    try:
        info = converter.get_conversion_info(str(test_pdf))
        print(f"檔案資訊:")
        print(f"  - 檔案名: {info['file_name']}")
        print(f"  - 檔案大小: {info['file_size_mb']} MB")
        print(f"  - 副檔名: {info['extension']}")
    except Exception as e:
        print(f"✗ 獲取檔案資訊失敗: {e}")
        return
    
    # 進行轉換
    try:
        output_path = test_pdf.parent / f"{test_pdf.stem}_marker.md"
        markdown_content = converter.convert_pdf_to_markdown(
            str(test_pdf), 
            str(output_path)
        )
        
        print(f"✓ 轉換成功!")
        print(f"  - 輸出檔案: {output_path}")
        print(f"  - 內容長度: {len(markdown_content)} 字元")
        print(f"  - 內容預覽: {markdown_content[:200]}...")
        
    except Exception as e:
        print(f"✗ 轉換失敗: {e}")


def example_batch_conversion():
    """批量轉換範例"""
    print("\n=== 批量轉換範例 ===")
    
    try:
        converter = MarkerConverter()
        print("✓ Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ Marker 套件未安裝: {e}")
        return
    
    # 指定測試目錄
    raw_docs_dir = Path(__file__).parent.parent.parent / "raw_docs" / "old_version"
    
    if not raw_docs_dir.exists():
        print("✗ 測試目錄不存在")
        return
    
    # 建立輸出目錄
    output_dir = Path(__file__).parent / "marker_converted"
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
        converter = create_marker_converter(model_locations)
        print("✓ 使用自定義模型位置的轉換器建立成功")
        
        # 注意：實際使用時需要確保模型檔案存在於指定位置
        
    except ImportError as e:
        print(f"✗ Marker 套件未安裝: {e}")
    except Exception as e:
        print(f"✗ 建立轉換器失敗: {e}")


def example_error_handling():
    """錯誤處理範例"""
    print("\n=== 錯誤處理範例 ===")
    
    try:
        converter = MarkerConverter()
    except ImportError as e:
        print(f"✗ Marker 套件未安裝: {e}")
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
    print("Marker Converter 使用範例")
    print("=" * 50)
    
    # 檢查 Marker 套件是否可用
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered
        print("✓ Marker 套件已安裝")
    except ImportError:
        print("✗ Marker 套件未安裝，請執行: pip install marker-pdf[full]")
        return
    
    # 執行範例
    example_single_pdf_conversion()
    example_batch_conversion()
    example_custom_model_locations()
    example_error_handling()
    
    print("\n範例執行完成!")


if __name__ == "__main__":
    main()
