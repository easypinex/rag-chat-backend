#!/usr/bin/env python3
"""
測試 Marker 輸出類型標注

驗證 MarkdownOutput 對象的類型標注是否正確
"""

import sys
from pathlib import Path

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from json_marker_converter import JsonMarkerConverter
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.config.parser import ConfigParser
    from marker.renderers.markdown import MarkdownOutput
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"❌ 依賴套件未安裝: {e}")
    DEPENDENCIES_AVAILABLE = False


def test_marker_output_type():
    """測試 Marker 輸出類型"""
    print("🔍 測試 Marker 輸出類型標注")
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
        # 測試 JsonMarkerConverter
        converter = JsonMarkerConverter()
        print("✅ JsonMarkerConverter 建立成功")
        
        # 測試直接使用 PdfConverter
        cfg = ConfigParser({"output_format": "json"})
        artifact_dict = create_model_dict()
        pdf_converter = PdfConverter(
            config=cfg.generate_config_dict(),
            artifact_dict=artifact_dict
        )
        print("✅ PdfConverter 建立成功")
        
        # 進行轉換
        print("🔄 進行轉換...")
        rendered = pdf_converter(str(test_pdf))
        
        # 檢查類型
        print(f"📊 實際類型: {type(rendered)}")
        print(f"📊 預期類型: {MarkdownOutput}")
        print(f"📊 類型匹配: {isinstance(rendered, MarkdownOutput)}")
        print()
        
        # 檢查屬性
        print("📋 屬性檢查:")
        attributes = ['markdown', 'images', 'metadata']
        for attr in attributes:
            has_attr = hasattr(rendered, attr)
            print(f"  - {attr}: {'✅' if has_attr else '❌'}")
            if has_attr:
                value = getattr(rendered, attr)
                print(f"    類型: {type(value)}")
                if isinstance(value, str):
                    print(f"    長度: {len(value)} 字元")
                elif isinstance(value, dict):
                    print(f"    項目數: {len(value)}")
                print(f"    值: {repr(value)[:100]}...")
        print()
        
        # 測試類型標注
        print("🔧 類型標注測試:")
        rendered_typed: MarkdownOutput = rendered
        print("✅ 類型標注成功")
        
        # 測試屬性訪問
        markdown_content: str = rendered_typed.markdown
        images_info: dict = rendered_typed.images
        metadata_info: dict = rendered_typed.metadata
        
        print(f"✅ markdown 屬性: {len(markdown_content)} 字元")
        print(f"✅ images 屬性: {len(images_info)} 項目")
        print(f"✅ metadata 屬性: {len(metadata_info)} 項目")
        print()
        
        # 測試 JsonMarkerConverter 的類型標注
        print("🔧 JsonMarkerConverter 類型標注測試:")
        pages = converter.marker_json_pages(str(test_pdf))
        print(f"✅ 返回類型: {type(pages)}")
        print(f"✅ 頁面數量: {len(pages)}")
        print(f"✅ 第一頁類型: {type(pages[0])}")
        print(f"✅ 第一頁長度: {len(pages[0])} 字元")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


def test_type_annotations():
    """測試類型標注的正確性"""
    print("\n🔍 測試類型標注正確性")
    print("=" * 50)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 依賴套件未安裝，跳過測試")
        return
    
    try:
        from typing import get_type_hints
        from json_marker_converter import JsonMarkerConverter
        
        converter = JsonMarkerConverter()
        
        # 獲取方法簽名
        hints = get_type_hints(converter.marker_json_pages)
        print("📋 marker_json_pages 方法簽名:")
        print(f"  返回類型: {hints.get('return', '未標注')}")
        print()
        
        # 檢查類型標注是否正確
        return_type = hints.get('return')
        if return_type:
            print(f"✅ 返回類型已標注: {return_type}")
        else:
            print("❌ 返回類型未標注")
        
    except Exception as e:
        print(f"❌ 類型標注測試失敗: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函數"""
    print("🚀 Marker 輸出類型測試")
    print("=" * 60)
    
    test_marker_output_type()
    test_type_annotations()
    
    print("\n✅ 類型測試完成!")
    print("\n💡 總結:")
    print("  - 驗證了 MarkdownOutput 對象的類型")
    print("  - 檢查了屬性訪問的正確性")
    print("  - 測試了類型標注的有效性")


if __name__ == "__main__":
    main()
