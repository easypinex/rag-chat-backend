"""
簡單的轉換測試腳本

用於快速測試 Advanced Marker 轉換功能
"""

import sys
import os
from pathlib import Path

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from marker_converter import MarkerConverter

# 設定專案根目錄
project_root = Path(__file__).parent.parent.parent


def test_basic_conversion():
    """基本轉換測試"""
    print("開始測試 Marker 轉換功能...")
    
    # 檢查 Marker 套件是否可用
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered
        print("✓ Marker 套件已安裝")
    except ImportError as e:
        print(f"✗ Marker 套件未安裝: {e}")
        print("請執行: pip install marker-pdf[full]")
        return False
    
    # 建立轉換器
    try:
        converter = MarkerConverter()
        print("✓ Advanced Marker 轉換器建立成功")
    except Exception as e:
        print(f"✗ 建立轉換器失敗: {e}")
        return False
    
    # 尋找測試 PDF 檔案
    raw_docs_dir = project_root / "raw_docs" / "old_version"
    if not raw_docs_dir.exists():
        print(f"✗ 測試目錄不存在: {raw_docs_dir}")
        return False
    
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    if not pdf_files:
        print("✗ 未找到測試 PDF 檔案")
        return False
    
    # 選擇第一個 PDF 檔案進行測試
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
        return False
    
    # 進行轉換測試
    try:
        output_path = test_pdf.parent / f"{test_pdf.stem}_marker_test.md"
        print(f"開始轉換...")
        
        markdown_content = converter.convert_pdf_to_markdown(
            str(test_pdf), 
            str(output_path)
        )
        
        print(f"✓ 轉換成功!")
        print(f"  - 輸出檔案: {output_path}")
        print(f"  - 內容長度: {len(markdown_content)} 字元")
        
        # 顯示內容預覽
        preview_length = 300
        if len(markdown_content) > preview_length:
            preview = markdown_content[:preview_length] + "..."
        else:
            preview = markdown_content
        
        print(f"  - 內容預覽:")
        print("    " + "\n    ".join(preview.split("\n")[:10]))
        
        return True
        
    except Exception as e:
        print(f"✗ 轉換失敗: {e}")
        return False


def test_batch_conversion():
    """批量轉換測試"""
    print("\n開始測試批量轉換功能...")
    
    try:
        converter = MarkerConverter()
    except Exception as e:
        print(f"✗ 建立轉換器失敗: {e}")
        return False
    
    raw_docs_dir = project_root / "raw_docs" / "old_version"
    if not raw_docs_dir.exists():
        print(f"✗ 測試目錄不存在: {raw_docs_dir}")
        return False
    
    # 建立輸出目錄
    output_dir = raw_docs_dir / "marker_test_output"
    output_dir.mkdir(exist_ok=True)
    
    try:
        print(f"開始批量轉換...")
        results = converter.convert_multiple_pdfs(
            str(raw_docs_dir), 
            str(output_dir)
        )
        
        print(f"✓ 批量轉換完成!")
        print(f"  - 處理檔案數: {len(results)}")
        print(f"  - 輸出目錄: {output_dir}")
        
        success_count = 0
        error_count = 0
        
        for filename, content in results.items():
            if content.startswith("Error:"):
                print(f"  ✗ {filename}: {content}")
                error_count += 1
            else:
                print(f"  ✓ {filename}: {len(content)} 字元")
                success_count += 1
        
        print(f"  - 成功: {success_count} 個檔案")
        print(f"  - 失敗: {error_count} 個檔案")
        
        return success_count > 0
        
    except Exception as e:
        print(f"✗ 批量轉換失敗: {e}")
        return False


def main():
    """主函數"""
        print("Marker 轉換功能測試")
    print("=" * 50)
    
    # 基本轉換測試
    basic_success = test_basic_conversion()
    
    # 批量轉換測試
    batch_success = test_batch_conversion()
    
    # 總結
    print("\n" + "=" * 50)
    print("測試結果總結:")
    print(f"  - 基本轉換: {'✓ 成功' if basic_success else '✗ 失敗'}")
    print(f"  - 批量轉換: {'✓ 成功' if batch_success else '✗ 失敗'}")
    
    if basic_success or batch_success:
        print("\n✓ Marker 轉換功能運作正常!")
    else:
        print("\n✗ Marker 轉換功能測試失敗!")
    
    return basic_success or batch_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
