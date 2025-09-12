#!/usr/bin/env python3
"""
JSON Marker Converter 演示腳本

展示 JSON Marker 轉換器的主要功能
"""

import os
import sys
from pathlib import Path

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from json_marker_converter import JsonMarkerConverter
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.config.parser import ConfigParser
    from bs4 import BeautifulSoup
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"❌ 依賴套件未安裝: {e}")
    print("請執行: pip install marker-pdf[full] beautifulsoup4")
    DEPENDENCIES_AVAILABLE = False


def demo_table_conversion():
    """演示表格轉換功能"""
    print("🔧 演示表格轉換功能")
    print("-" * 40)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 依賴套件未安裝，跳過演示")
        return
    
    try:
        converter = JsonMarkerConverter()
    except Exception as e:
        print(f"❌ 無法建立轉換器: {e}")
        return
    
    # 測試簡單表格
    print("📊 測試簡單表格轉換:")
    simple_table = """
    <table>
        <tr><th>產品</th><th>價格</th><th>庫存</th></tr>
        <tr><td>iPhone 15</td><td>NT$ 29,900</td><td>50</td></tr>
        <tr><td>Samsung S24</td><td>NT$ 28,900</td><td>30</td></tr>
        <tr><td>Google Pixel 8</td><td>NT$ 24,900</td><td>20</td></tr>
    </table>
    """
    
    result = converter._table_html_to_md(simple_table)
    print("轉換結果:")
    print(result)
    
    # 測試複雜表格
    print("\n📊 測試複雜表格轉換 (rowspan):")
    complex_table = """
    <table>
        <tr><th rowspan="2">季度</th><th>Q1</th><th>Q2</th></tr>
        <tr><td>100萬</td><td>150萬</td></tr>
    </table>
    """
    
    result = converter._table_html_to_md(complex_table)
    print("轉換結果:")
    print(result)
    
    print("✅ 表格轉換演示完成\n")


def demo_pdf_conversion():
    """演示 PDF 轉換功能"""
    print("📄 演示 PDF 轉換功能")
    print("-" * 40)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 依賴套件未安裝，跳過演示")
        return
    
    # 尋找測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent / "raw_docs" / "old_version"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ 未找到測試 PDF 檔案")
        print(f"請在 {raw_docs_dir} 目錄中放置 PDF 檔案")
        return
    
    test_pdf = pdf_files[0]
    print(f"📁 使用測試檔案: {test_pdf.name}")
    
    try:
        converter = JsonMarkerConverter()
        print("✅ JSON Marker 轉換器建立成功")
        
        # 獲取頁面資訊
        print("\n📊 獲取頁面資訊:")
        page_info = converter.get_page_info(str(test_pdf))
        print(f"  - 檔案名: {page_info['file_name']}")
        print(f"  - 總頁數: {page_info['total_pages']}")
        
        # 顯示前幾頁的結構
        for i, page in enumerate(page_info['pages'][:3], 1):
            print(f"  - 第 {i} 頁: {page['block_count']} 個區塊")
            if page['block_types']:
                types_str = ", ".join(f"{bt}({count})" for bt, count in 
                                    sorted(page['block_types'].items(), key=lambda x: x[1], reverse=True))
                print(f"    區塊類型: {types_str}")
        
        # 進行轉換
        print(f"\n🔄 開始轉換 PDF...")
        output_path = test_pdf.parent / f"{test_pdf.stem}_demo.md"
        markdown_content = converter.convert_pdf_to_markdown(
            str(test_pdf), 
            str(output_path)
        )
        
        print(f"✅ 轉換完成!")
        print(f"  - 輸出檔案: {output_path}")
        print(f"  - 內容長度: {len(markdown_content):,} 字元")
        
        # 檢查輸出內容
        if "## Page" in markdown_content:
            page_count = markdown_content.count("## Page")
            print(f"  - 包含 {page_count} 個頁碼標記")
        
        if "|" in markdown_content and "---" in markdown_content:
            table_count = markdown_content.count("|") // 3  # 粗略估算
            print(f"  - 包含約 {table_count} 個表格")
        
        # 顯示內容預覽
        print(f"\n📖 內容預覽 (前 500 字元):")
        preview = markdown_content[:500].replace("\n", "\n    ")
        print(f"    {preview}...")
        
    except Exception as e:
        print(f"❌ 轉換失敗: {e}")
        import traceback
        traceback.print_exc()


def demo_page_analysis():
    """演示頁面分析功能"""
    print("\n🔍 演示頁面分析功能")
    print("-" * 40)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 依賴套件未安裝，跳過演示")
        return
    
    # 尋找測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent / "raw_docs" / "old_version"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ 未找到測試 PDF 檔案")
        return
    
    test_pdf = pdf_files[0]
    print(f"📁 分析檔案: {test_pdf.name}")
    
    try:
        converter = JsonMarkerConverter()
        
        # 獲取頁面結構
        pages = converter.marker_json_pages(str(test_pdf))
        print(f"📊 總頁數: {len(pages)}")
        
        # 分析前幾頁
        for i, page in enumerate(pages[:3], 1):
            children = getattr(page, "children", []) or []
            print(f"\n📄 第 {i} 頁詳細分析:")
            print(f"  - 區塊數量: {len(children)}")
            
            # 統計區塊類型
            block_types = {}
            for child in children:
                bt = getattr(child, "block_type", "unknown")
                block_types[bt] = block_types.get(bt, 0) + 1
            
            print(f"  - 區塊類型分布:")
            for bt, count in sorted(block_types.items(), key=lambda x: x[1], reverse=True):
                print(f"    • {bt}: {count} 個")
            
            # 顯示前幾個區塊的內容預覽
            print(f"  - 內容預覽:")
            for j, child in enumerate(children[:3]):
                text = getattr(child, "text", None) or getattr(child, "markdown", None) or ""
                preview = text[:80].replace("\n", " ") if text else "[無文字內容]"
                bt = getattr(child, "block_type", "unknown")
                print(f"    {j+1}. [{bt}] {preview}...")
        
        print("✅ 頁面分析演示完成")
        
    except Exception as e:
        print(f"❌ 頁面分析失敗: {e}")


def main():
    """主函數"""
    print("🚀 JSON Marker Converter 演示")
    print("=" * 50)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 請先安裝依賴套件:")
        print("   pip install marker-pdf[full] beautifulsoup4")
        return
    
    # 執行演示
    demo_table_conversion()
    demo_pdf_conversion()
    demo_page_analysis()
    
    print("\n🎉 演示完成!")
    print("\n💡 提示:")
    print("  - 使用 JsonMarkerConverter 進行結構化轉換")
    print("  - 支援頁碼標記和智能表格轉換")
    print("  - 可以獲取詳細的頁面結構資訊")
    print("  - 適合需要精確控制轉換結果的場景")


if __name__ == "__main__":
    main()
