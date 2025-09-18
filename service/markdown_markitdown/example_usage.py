"""
MarkitdownConverter 的使用範例。
"""

import sys
import os
sys.path.append('..')

from markitdown_converter import MarkitdownConverter


def example_single_file_conversion():
    """範例：轉換單一檔案。"""
    print("=== 單一檔案轉換範例 ===")
    
    converter = MarkitdownConverter()
    
    # 轉換特定的 PDF 檔案
    # pdf_path = "raw_docs/old_version/台灣人壽e樂活一年定期住院日額健康保險.pdf"
    pdf_path = "raw_docs/個人保險保單服務暨契約變更手冊(114年9月版)_Unlock.pdf"
    
    try:
        result = converter.convert_file_to_markdown(pdf_path)
        print(f"Successfully converted: {result}")
    except FileNotFoundError:
        print(f"File not found: {pdf_path}")
    except Exception as e:
        print(f"Error converting file: {e}")


def example_directory_conversion():
    """範例：轉換 old_version 目錄中的所有支援檔案。"""
    print("\n=== 目錄轉換範例 ===")
    
    converter = MarkitdownConverter()
    
    try:
        # 轉換 old_version 目錄中的所有支援檔案
        results = converter.convert_old_version_docs()
        
        print(f"Converted {len(results)} files:")
        for result in results:
            print(f"  - {result}")
            
    except Exception as e:
        print(f"Error converting directory: {e}")


def example_custom_directories():
    """範例：使用自訂輸入和輸出目錄進行轉換。"""
    print("\n=== 自訂目錄範例 ===")
    
    converter = MarkitdownConverter(
        input_dir="raw_docs",
        output_dir="markdown/converted"
    )
    
    try:
        # 轉換輸入目錄中的所有支援檔案
        results = converter.convert_directory()
        
        print(f"Converted {len(results)} files:")
        for result in results:
            print(f"  - {result}")
            
    except Exception as e:
        print(f"Error converting directory: {e}")


def example_conversion_stats():
    """範例：取得轉換統計資訊。"""
    print("\n=== 轉換統計資訊範例 ===")
    
    converter = MarkitdownConverter()
    
    stats = converter.get_conversion_stats()
    
    print("轉換統計資訊：")
    print(f"  Input files: {stats['input_files_count']}")
    print(f"  Output MDs: {stats['output_mds_count']}")
    print(f"  Input Directory: {stats['input_directory']}")
    print(f"  Output Directory: {stats['output_directory']}")
    print(f"  Supported extensions: {', '.join(stats['supported_extensions'])}")


def example_xlsx_conversion():
    """範例：轉換 XLSX 檔案。"""
    print("\n=== XLSX 檔案轉換範例 ===")
    
    converter = MarkitdownConverter()
    
    try:
        # 轉換 XLSX 檔案
        xlsx_path = "raw_docs/理賠審核原則.xlsx"
        result = converter.convert_file_to_markdown(xlsx_path)
        print(f"Successfully converted XLSX: {result}")
    except FileNotFoundError:
        print(f"XLSX file not found: {xlsx_path}")
    except Exception as e:
        print(f"Error converting XLSX: {e}")


def example_extension_conversion():
    """範例：轉換特定副檔名的所有檔案。"""
    print("\n=== 特定副檔名轉換範例 ===")
    
    converter = MarkitdownConverter()
    
    try:
        # 轉換所有 XLSX 檔案
        results = converter.convert_by_extension('.xlsx')
        
        print(f"Converted {len(results)} XLSX files:")
        for result in results:
            print(f"  - {result}")
            
    except Exception as e:
        print(f"Error converting XLSX files: {e}")


def example_multi_format_conversion():
    """範例：轉換多種格式的檔案。"""
    print("\n=== 多格式檔案轉換範例 ===")
    
    converter = MarkitdownConverter()
    
    # 測試不同格式的檔案
    test_files = [
        "raw_docs/理賠審核原則.xlsx",  # Excel
        "raw_docs/個人保險保單服務暨契約變更手冊(114年9月版)_Unlock.pdf",  # PDF
        # 可以添加更多格式的測試檔案
    ]
    
    for file_path in test_files:
        try:
            if os.path.exists(file_path):
                result = converter.convert_file_to_markdown(file_path)
                print(f"Successfully converted {file_path}: {result}")
            else:
                print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error converting {file_path}: {e}")


def example_pages_conversion():
    """範例：轉換檔案為頁面列表。"""
    print("\n=== 頁面列表轉換範例 ===")
    
    converter = MarkitdownConverter()
    
    # 測試 PDF 檔案轉換為頁面
    pdf_path = "raw_docs/個人保險保單服務暨契約變更手冊(114年9月版)_Unlock.pdf"
    
    try:
        if os.path.exists(pdf_path):
            pages = converter.convert_file_to_pages(pdf_path)
            print(f"Successfully converted to {len(pages)} pages:")
            for i, page in enumerate(pages[:3]):  # 只顯示前3頁
                print(f"  Page {i+1}: {len(page)} characters")
                print(f"    Preview: {page[:100]}...")
            if len(pages) > 3:
                print(f"  ... and {len(pages) - 3} more pages")
        else:
            print(f"File not found: {pdf_path}")
    except Exception as e:
        print(f"Error converting to pages: {e}")


def example_excel_sheets_conversion():
    """範例：轉換 Excel 檔案為工作表列表。"""
    print("\n=== Excel 工作表轉換範例 ===")
    
    converter = MarkitdownConverter()
    
    # 測試 Excel 檔案轉換為工作表
    xlsx_path = "raw_docs/理賠審核原則.xlsx"
    
    try:
        if os.path.exists(xlsx_path):
            sheets = converter.convert_excel_to_sheets(xlsx_path)
            print(f"Successfully converted to {len(sheets)} sheets:")
            for sheet in sheets:
                print(f"  Sheet '{sheet['title']}': {len(sheet['content'])} characters")
                print(f"    Preview: {sheet['content'][:100]}...")
        else:
            print(f"File not found: {xlsx_path}")
    except Exception as e:
        print(f"Error converting Excel to sheets: {e}")


def example_metadata_conversion():
    """範例：轉換檔案並獲取完整元資料。"""
    print("\n=== 元資料轉換範例 ===")
    
    converter = MarkitdownConverter()
    
    # 測試 Excel 檔案轉換並獲取元資料
    xlsx_path = "raw_docs/理賠審核原則.xlsx"
    
    try:
        if os.path.exists(xlsx_path):
            result = converter.convert_file_with_metadata(xlsx_path)
            print(f"Successfully converted with metadata:")
            print(f"  File name: {result['file_name']}")
            print(f"  File type: {result['file_type']}")
            print(f"  Full text length: {len(result['full_text'])} characters")
            print(f"  Number of pages: {len(result['pages'])}")
            
            if 'sheets' in result:
                print(f"  Number of sheets: {len(result['sheets'])}")
                for sheet in result['sheets']:
                    print(f"    - {sheet['title']}")
            
            print(f"  Metadata keys: {list(result['metadata'].keys())}")
        else:
            print(f"File not found: {xlsx_path}")
    except Exception as e:
        print(f"Error converting with metadata: {e}")


def example_powerpoint_pages():
    """範例：轉換 PowerPoint 檔案為頁面列表。"""
    print("\n=== PowerPoint 頁面轉換範例 ===")
    
    converter = MarkitdownConverter()
    
    # 測試 PowerPoint 檔案轉換為頁面
    pptx_path = "raw_docs/old_version/dm/中信_吉美世美元利率變動型終身壽險_理說會簡報_Final1.pptx"
    
    try:
        if os.path.exists(pptx_path):
            pages = converter.convert_file_to_pages(pptx_path)
            print(f"Successfully converted to {len(pages)} slides:")
            for i, page in enumerate(pages[:3]):  # 只顯示前3頁
                print(f"  Slide {i+1}: {len(page)} characters")
                print(f"    Preview: {page[:100]}...")
            if len(pages) > 3:
                print(f"  ... and {len(pages) - 3} more slides")
        else:
            print(f"File not found: {pptx_path}")
    except Exception as e:
        print(f"Error converting PowerPoint to pages: {e}")


def main():
    """執行所有範例。"""
    print("MarkitdownConverter 使用範例")
    print("=" * 50)
    
    # 執行基本範例
    example_single_file_conversion()
    example_directory_conversion()
    example_custom_directories()
    example_conversion_stats()
    
    # 執行格式特定範例
    example_xlsx_conversion()
    example_extension_conversion()
    example_multi_format_conversion()
    
    # 執行新功能範例
    example_pages_conversion()
    example_excel_sheets_conversion()
    example_metadata_conversion()
    example_powerpoint_pages()
    
    print("\n" + "=" * 50)
    print("範例執行完成！")


if __name__ == "__main__":
    main()
