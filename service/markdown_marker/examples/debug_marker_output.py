#!/usr/bin/env python3
"""
調試 Marker 輸出結構

檢查 Marker 的實際輸出格式
"""

import os
import sys
from pathlib import Path

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.config.parser import ConfigParser
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"❌ 依賴套件未安裝: {e}")
    DEPENDENCIES_AVAILABLE = False


def debug_marker_output():
    """調試 Marker 的輸出結構"""
    print("🔍 調試 Marker 輸出結構")
    print("-" * 40)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 依賴套件未安裝，跳過調試")
        return
    
    # 尋找測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent / "raw_docs" / "old_version"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ 未找到測試 PDF 檔案")
        return
    
    test_pdf = pdf_files[0]
    print(f"📁 使用測試檔案: {test_pdf.name}")
    
    try:
        # 建立轉換器
        cfg = ConfigParser({"output_format": "json"})
        artifact_dict = create_model_dict()
        converter = PdfConverter(
            config=cfg.generate_config_dict(),
            artifact_dict=artifact_dict
        )
        
        print("✅ Marker 轉換器建立成功")
        
        # 進行轉換
        print("🔄 開始轉換...")
        rendered = converter(str(test_pdf))
        
        print(f"✅ 轉換完成!")
        print(f"📊 輸出對象類型: {type(rendered)}")
        print(f"📊 輸出對象屬性: {dir(rendered)}")
        
        # 檢查主要屬性
        for attr in ['children', 'pages', 'content', 'data', 'markdown', 'text']:
            if hasattr(rendered, attr):
                value = getattr(rendered, attr)
                print(f"  - {attr}: {type(value)} = {str(value)[:100]}...")
            else:
                print(f"  - {attr}: 不存在")
        
        # 如果 rendered 有 markdown 屬性，顯示內容
        if hasattr(rendered, 'markdown'):
            markdown_content = rendered.markdown
            print(f"\n📖 Markdown 內容預覽 (前 500 字元):")
            print(markdown_content[:500])
        
        # 如果 rendered 有 text 屬性，顯示內容
        elif hasattr(rendered, 'text'):
            text_content = rendered.text
            print(f"\n📖 Text 內容預覽 (前 500 字元):")
            print(text_content[:500])
        
    except Exception as e:
        print(f"❌ 調試失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_marker_output()
