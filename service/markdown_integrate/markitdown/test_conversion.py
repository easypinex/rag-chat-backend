#!/usr/bin/env python3
"""
MarkItDown 轉換器測試腳本
"""

import os
import sys
from pathlib import Path

# 添加當前目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from markitdown_converter import MarkitdownConverter


def test_supported_formats():
    """測試支援的格式列表"""
    print("=== 測試支援的格式 ===")
    converter = MarkitdownConverter()
    
    print(f"支援的格式數量: {len(converter.SUPPORTED_EXTENSIONS)}")
    print("支援的格式:")
    for ext in sorted(converter.SUPPORTED_EXTENSIONS):
        print(f"  - {ext}")


def test_file_detection():
    """測試檔案格式檢測"""
    print("\n=== 測試檔案格式檢測 ===")
    converter = MarkitdownConverter()
    
    test_files = [
        "test.pdf",
        "test.xlsx", 
        "test.pptx",
        "test.docx",
        "test.txt",
        "test.unknown"
    ]
    
    for file_path in test_files:
        is_supported = converter.is_supported_file(Path(file_path))
        print(f"{file_path}: {'支援' if is_supported else '不支援'}")


def test_conversion_stats():
    """測試轉換統計"""
    print("\n=== 測試轉換統計 ===")
    converter = MarkitdownConverter()
    
    stats = converter.get_conversion_stats()
    print("轉換統計:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def test_single_file_conversion():
    """測試單一檔案轉換"""
    print("\n=== 測試單一檔案轉換 ===")
    converter = MarkitdownConverter()
    
    # 測試 XLSX 檔案
    xlsx_file = "raw_docs/理賠審核原則.xlsx"
    if os.path.exists(xlsx_file):
        try:
            result = converter.convert_file_to_markdown(xlsx_file, "test_xlsx")
            print(f"XLSX 轉換成功: {result}")
        except Exception as e:
            print(f"XLSX 轉換失敗: {e}")
    else:
        print(f"測試檔案不存在: {xlsx_file}")
    
    # 測試 PDF 檔案
    pdf_file = "raw_docs/個人保險保單服務暨契約變更手冊(114年9月版)_Unlock.pdf"
    if os.path.exists(pdf_file):
        try:
            result = converter.convert_file_to_markdown(pdf_file, "test_pdf")
            print(f"PDF 轉換成功: {result}")
        except Exception as e:
            print(f"PDF 轉換失敗: {e}")
    else:
        print(f"測試檔案不存在: {pdf_file}")


def test_extension_conversion():
    """測試特定副檔名轉換"""
    print("\n=== 測試特定副檔名轉換 ===")
    converter = MarkitdownConverter()
    
    # 測試 XLSX 轉換
    try:
        results = converter.convert_by_extension('.xlsx')
        print(f"XLSX 檔案轉換結果: {len(results)} 個檔案")
        for result in results:
            print(f"  - {result}")
    except Exception as e:
        print(f"XLSX 轉換失敗: {e}")
    
    # 測試 PPTX 轉換
    try:
        results = converter.convert_by_extension('.pptx')
        print(f"PPTX 檔案轉換結果: {len(results)} 個檔案")
        for result in results[:3]:  # 只顯示前3個
            print(f"  - {result}")
        if len(results) > 3:
            print(f"  ... 還有 {len(results) - 3} 個檔案")
    except Exception as e:
        print(f"PPTX 轉換失敗: {e}")


def main():
    """執行所有測試"""
    print("MarkItDown 轉換器測試")
    print("=" * 50)
    
    test_supported_formats()
    test_file_detection()
    test_conversion_stats()
    test_single_file_conversion()
    test_extension_conversion()
    
    print("\n" + "=" * 50)
    print("測試完成！")


if __name__ == "__main__":
    main()
