#!/usr/bin/env python3
"""
檢查頁面內容實際類型

驗證 marker_json_pages 方法實際返回的對象類型
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
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"❌ 依賴套件未安裝: {e}")
    DEPENDENCIES_AVAILABLE = False


def check_actual_page_types():
    """檢查實際的頁面類型"""
    print("🔍 檢查頁面內容實際類型")
    print("=" * 50)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 依賴套件未安裝，跳過檢查")
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
        
        # 獲取頁面列表
        print("🔄 獲取頁面列表...")
        pages = converter.marker_json_pages(str(test_pdf))
        
        print(f"📊 總共 {len(pages)} 頁")
        print()
        
        # 檢查每頁的類型
        type_counts = {}
        for i, page in enumerate(pages, 1):
            page_type = type(page)
            type_name = page_type.__name__
            type_module = page_type.__module__
            
            if type_name not in type_counts:
                type_counts[type_name] = {
                    'count': 0,
                    'module': type_module,
                    'examples': []
                }
            
            type_counts[type_name]['count'] += 1
            
            # 收集範例（最多3個）
            if len(type_counts[type_name]['examples']) < 3:
                if isinstance(page, str):
                    example = f"'{page[:50]}...'" if len(page) > 50 else f"'{page}'"
                else:
                    example = f"<{type_name} object>"
                type_counts[type_name]['examples'].append(example)
        
        # 顯示結果
        print("📋 頁面類型分析:")
        print("-" * 30)
        
        for type_name, info in type_counts.items():
            print(f"類型: {type_name}")
            print(f"  模組: {info['module']}")
            print(f"  數量: {info['count']} 頁")
            print(f"  範例: {', '.join(info['examples'])}")
            print()
        
        # 分析結果
        print("🔍 分析結果:")
        print("-" * 30)
        
        if len(type_counts) == 1:
            type_name = list(type_counts.keys())[0]
            print(f"✅ 所有頁面都是同一類型: {type_name}")
            print("💡 建議: 可以直接使用 List[str] 類型")
            
            if type_name == 'str':
                print("📝 建議的類型定義:")
                print("   直接使用 List[str]")
            else:
                print(f"📝 建議的類型定義:")
                print(f"   直接使用 List[{type_name}]")
        else:
            print(f"⚠️  發現 {len(type_counts)} 種不同的頁面類型:")
            for type_name in type_counts.keys():
                print(f"   - {type_name}")
            print("💡 建議: 保持 Union 類型定義")
            print("📝 建議的類型定義:")
            union_types = " | ".join(type_counts.keys())
            print(f"   直接使用 List[{union_types}]")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()


def check_marker_output_structure():
    """檢查 Marker 的實際輸出結構"""
    print("\n🔍 檢查 Marker 輸出結構")
    print("=" * 50)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 依賴套件未安裝，跳過檢查")
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
        # 直接使用 Marker 轉換器
        cfg = ConfigParser({"output_format": "json"})
        artifact_dict = create_model_dict()
        converter = PdfConverter(
            config=cfg.generate_config_dict(),
            artifact_dict=artifact_dict
        )
        
        print("✅ Marker 轉換器建立成功")
        
        # 進行轉換
        print("🔄 進行轉換...")
        rendered = converter(str(test_pdf))
        
        print(f"📊 輸出對象類型: {type(rendered)}")
        print(f"📊 輸出對象模組: {type(rendered).__module__}")
        print()
        
        # 檢查屬性
        print("📋 輸出對象屬性:")
        attrs = [attr for attr in dir(rendered) if not attr.startswith('_')]
        for attr in attrs:
            try:
                value = getattr(rendered, attr)
                if callable(value):
                    print(f"  - {attr}: <method>")
                else:
                    value_type = type(value).__name__
                    if isinstance(value, str) and len(value) > 100:
                        print(f"  - {attr}: {value_type} (長度: {len(value)})")
                    else:
                        print(f"  - {attr}: {value_type} = {repr(value)[:100]}")
            except Exception as e:
                print(f"  - {attr}: <無法訪問: {e}>")
        
        # 檢查是否有 markdown 屬性
        if hasattr(rendered, 'markdown'):
            markdown_content = rendered.markdown
            print(f"\n📄 Markdown 內容:")
            print(f"  - 類型: {type(markdown_content)}")
            print(f"  - 長度: {len(markdown_content)} 字元")
            print(f"  - 預覽: {markdown_content[:200]}...")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函數"""
    print("🚀 頁面內容類型檢查")
    print("=" * 60)
    
    check_actual_page_types()
    check_marker_output_structure()
    
    print("\n✅ 類型檢查完成!")
    print("\n💡 總結:")
    print("  - 檢查了 marker_json_pages 的實際返回類型")
    print("  - 分析了 Marker 的輸出結構")
    print("  - 提供了類型定義的優化建議")


if __name__ == "__main__":
    main()
