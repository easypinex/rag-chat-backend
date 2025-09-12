"""
MarkitdownConverter 的使用範例。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from service.markdown.markitdown_converter import MarkitdownConverter


def example_single_file_conversion():
    """範例：轉換單一 PDF 檔案。"""
    print("=== 單一檔案轉換範例 ===")
    
    converter = MarkitdownConverter()
    
    # 轉換特定的 PDF 檔案
    pdf_path = "raw_docs/old_version/台灣人壽e樂活一年定期住院日額健康保險.pdf"
    
    try:
        result = converter.convert_pdf_to_markdown(pdf_path)
        print(f"Successfully converted: {result}")
    except FileNotFoundError:
        print(f"PDF file not found: {pdf_path}")
    except Exception as e:
        print(f"Error converting PDF: {e}")


def example_directory_conversion():
    """範例：轉換 old_version 目錄中的所有 PDF 檔案。"""
    print("\n=== 目錄轉換範例 ===")
    
    converter = MarkitdownConverter()
    
    try:
        # 轉換 old_version 目錄中的所有 PDF
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
        input_dir="raw_docs/old_version",
        output_dir="markdown/converted"
    )
    
    try:
        # 轉換輸入目錄中的所有 PDF
        results = converter.convert_directory()
        
        print(f"Converted {len(results)} files:")
        for result in results:
            print(f"  - {result}")
            
    except Exception as e:
        print(f"Error converting directory: {e}")


def example_subdirectory_conversion():
    """範例：轉換特定子目錄中的 PDF。"""
    print("\n=== 子目錄轉換範例 ===")
    
    converter = MarkitdownConverter()
    
    try:
        # 轉換 dm 子目錄中的 PDF
        results = converter.convert_directory("old_version/dm")
        
        print(f"從 dm 子目錄轉換了 {len(results)} 個檔案：")
        for result in results:
            print(f"  - {result}")
            
    except Exception as e:
        print(f"Error converting subdirectory: {e}")


def example_conversion_stats():
    """範例：取得轉換統計資訊。"""
    print("\n=== 轉換統計資訊範例 ===")
    
    converter = MarkitdownConverter()
    
    stats = converter.get_conversion_stats()
    
    print("轉換統計資訊：")
    print(f"  Input PDFs: {stats['input_pdfs_count']}")
    print(f"  Output MDs: {stats['output_mds_count']}")
    print(f"  Input Directory: {stats['input_directory']}")
    print(f"  Output Directory: {stats['output_directory']}")


def main():
    """執行所有範例。"""
    print("MarkitdownConverter 使用範例")
    print("=" * 50)
    
    # 執行範例
    example_single_file_conversion()
    example_directory_conversion()
    example_custom_directories()
    example_subdirectory_conversion()
    example_conversion_stats()
    
    print("\n" + "=" * 50)
    print("範例執行完成！")


if __name__ == "__main__":
    main()
