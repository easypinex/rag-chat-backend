#!/usr/bin/env python3
"""
MarkItDown 轉換器進階功能範例
展示頁面分割、工作表轉換和元資料提取功能
"""

import os
import sys
from pathlib import Path

# 添加當前目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from markitdown_converter import MarkitdownConverter


def demo_pages_conversion():
    """展示頁面轉換功能"""
    print("=" * 60)
    print("📄 頁面轉換功能展示")
    print("=" * 60)
    
    converter = MarkitdownConverter()
    
    # 測試不同格式的頁面轉換
    test_files = [
        ("PDF", "raw_docs/個人保險保單服務暨契約變更手冊(114年9月版)_Unlock.pdf"),
        ("PowerPoint", "raw_docs/old_version/dm/中信_吉美世美元利率變動型終身壽險_理說會簡報_Final1.pptx"),
        ("Excel", "raw_docs/理賠審核原則.xlsx")
    ]
    
    for file_type, file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n🔍 轉換 {file_type} 檔案: {Path(file_path).name}")
            try:
                pages = converter.convert_file_to_pages(file_path)
                print(f"   ✅ 成功轉換為 {len(pages)} 頁")
                
                # 顯示每頁的資訊
                for i, page in enumerate(pages[:3]):  # 只顯示前3頁
                    print(f"   📄 第 {i+1} 頁: {len(page)} 字元")
                    if len(page) > 0:
                        preview = page[:100].replace('\n', ' ')
                        print(f"     預覽: {preview}...")
                
                if len(pages) > 3:
                    print(f"   ... 還有 {len(pages) - 3} 頁")
                    
            except Exception as e:
                print(f"   ❌ 轉換失敗: {e}")
        else:
            print(f"   ⚠️  檔案不存在: {file_path}")


def demo_excel_sheets():
    """展示 Excel 工作表轉換功能"""
    print("\n" + "=" * 60)
    print("📊 Excel 工作表轉換功能展示")
    print("=" * 60)
    
    converter = MarkitdownConverter()
    
    xlsx_file = "raw_docs/理賠審核原則.xlsx"
    if os.path.exists(xlsx_file):
        print(f"🔍 轉換 Excel 檔案: {Path(xlsx_file).name}")
        try:
            sheets = converter.convert_excel_to_sheets(xlsx_file)
            print(f"   ✅ 成功轉換為 {len(sheets)} 個工作表")
            
            # 顯示前5個工作表的詳細資訊
            for i, sheet in enumerate(sheets[:5]):
                print(f"   📋 工作表 {i+1}: '{sheet['title']}'")
                print(f"      內容長度: {len(sheet['content'])} 字元")
                
                # 顯示內容預覽
                content_preview = sheet['content'][:150].replace('\n', ' ')
                print(f"      內容預覽: {content_preview}...")
            
            if len(sheets) > 5:
                print(f"   ... 還有 {len(sheets) - 5} 個工作表")
                print(f"   📊 工作表總覽:")
                for i, sheet in enumerate(sheets):
                    print(f"      {i+1:2d}. {sheet['title']} ({len(sheet['content'])} 字元)")
                
        except Exception as e:
            print(f"   ❌ 轉換失敗: {e}")
    else:
        print(f"   ⚠️  檔案不存在: {xlsx_file}")


def demo_metadata_extraction():
    """展示元資料提取功能"""
    print("\n" + "=" * 60)
    print("📋 元資料提取功能展示")
    print("=" * 60)
    
    converter = MarkitdownConverter()
    
    test_files = [
        ("Excel", "raw_docs/理賠審核原則.xlsx"),
        ("PDF", "raw_docs/個人保險保單服務暨契約變更手冊(114年9月版)_Unlock.pdf"),
        ("PowerPoint", "raw_docs/old_version/dm/中信_吉美世美元利率變動型終身壽險_理說會簡報_Final1.pptx")
    ]
    
    for file_type, file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n🔍 提取 {file_type} 元資料: {Path(file_path).name}")
            try:
                metadata = converter.convert_file_with_metadata(file_path)
                
                print(f"   📁 檔案資訊:")
                print(f"      檔案名稱: {metadata['file_name']}")
                print(f"      檔案類型: {metadata['file_type']}")
                print(f"      標題: {metadata['title']}")
                print(f"      完整文字長度: {len(metadata['full_text'])} 字元")
                print(f"      頁面數: {len(metadata['pages'])}")
                
                if 'sheets' in metadata:
                    print(f"      工作表數: {len(metadata['sheets'])}")
                    for sheet in metadata['sheets']:
                        print(f"        - {sheet['title']}")
                
                print(f"   📊 元資料:")
                for key, value in metadata['metadata'].items():
                    if key == 'conversion_timestamp':
                        import time
                        value = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))
                    elif key == 'file_modified':
                        import time
                        value = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))
                    print(f"        {key}: {value}")
                    
            except Exception as e:
                print(f"   ❌ 提取失敗: {e}")
        else:
            print(f"   ⚠️  檔案不存在: {file_path}")


def demo_practical_usage():
    """展示實際使用場景"""
    print("\n" + "=" * 60)
    print("🚀 實際使用場景展示")
    print("=" * 60)
    
    converter = MarkitdownConverter()
    
    # 場景1: 處理 PowerPoint 簡報，獲取每頁內容
    print("\n📊 場景1: 分析 PowerPoint 簡報內容")
    pptx_file = "raw_docs/old_version/dm/中信_吉美世美元利率變動型終身壽險_理說會簡報_Final1.pptx"
    if os.path.exists(pptx_file):
        try:
            pages = converter.convert_file_to_pages(pptx_file)
            print(f"   簡報總共 {len(pages)} 頁")
            
            # 分析每頁的關鍵詞
            keywords = ["保險", "利率", "美元", "終身", "壽險"]
            for i, page in enumerate(pages):
                if len(page) > 0:
                    found_keywords = [kw for kw in keywords if kw in page]
                    if found_keywords:
                        print(f"   第 {i+1} 頁包含關鍵詞: {', '.join(found_keywords)}")
        except Exception as e:
            print(f"   ❌ 分析失敗: {e}")
    
    # 場景2: 處理 Excel 表格，獲取結構化資料
    print("\n📋 場景2: 處理 Excel 表格資料")
    xlsx_file = "raw_docs/理賠審核原則.xlsx"
    if os.path.exists(xlsx_file):
        try:
            sheets = converter.convert_excel_to_sheets(xlsx_file)
            for sheet in sheets:
                print(f"   工作表: {sheet['title']}")
                # 計算表格行數（簡單估算）
                lines = sheet['content'].split('\n')
                table_lines = [line for line in lines if '|' in line]
                print(f"   表格行數: {len(table_lines)}")
        except Exception as e:
            print(f"   ❌ 處理失敗: {e}")
    
    # 場景3: 批量處理並獲取統計資訊
    print("\n📈 場景3: 批量處理統計")
    try:
        stats = converter.get_conversion_stats()
        print(f"   輸入檔案總數: {stats['input_files_count']}")
        print(f"   已轉換檔案數: {stats['output_mds_count']}")
        print(f"   支援格式數: {len(stats['supported_extensions'])}")
    except Exception as e:
        print(f"   ❌ 統計失敗: {e}")


def main():
    """執行所有展示"""
    print("🎯 MarkItDown 轉換器進階功能展示")
    print("展示頁面分割、工作表轉換和元資料提取功能")
    
    demo_pages_conversion()
    demo_excel_sheets()
    demo_metadata_extraction()
    demo_practical_usage()
    
    print("\n" + "=" * 60)
    print("✅ 展示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
