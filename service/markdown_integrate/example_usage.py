"""
統一 Markdown 轉換器使用示例

展示如何使用 UnifiedMarkdownConverter 進行各種格式的轉換。
"""

import logging
from pathlib import Path
from service.markdown_integrate import UnifiedMarkdownConverter

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def basic_usage_example():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 初始化轉換器
    converter = UnifiedMarkdownConverter()
    
    # 檢查轉換器狀態
    status = converter.get_converter_status()
    print(f"轉換器狀態: {status}")
    
    # 獲取支援的格式
    formats = converter.get_supported_formats()
    print(f"支援的格式:")
    print(f"  Marker: {formats['marker']}")
    print(f"  Markitdown: {formats['markitdown']}")


def convert_pdf_example():
    """PDF 轉換示例 (使用 Marker)"""
    print("\n=== PDF 轉換示例 ===")
    
    converter = UnifiedMarkdownConverter()
    
    # 假設有一個 PDF 檔案
    pdf_file = "raw_docs/example.pdf"
    
    if Path(pdf_file).exists():
        try:
            result = converter.convert_file(pdf_file)
            
            print(f"檔案: {result.metadata.file_name}")
            print(f"總頁數: {result.metadata.total_pages}")
            print(f"總表格數: {result.metadata.total_tables}")
            print(f"使用轉換器: {result.metadata.converter_used}")
            print(f"內容長度: {len(result.content)}")
            
            # 處理頁面信息
            if result.pages:
                for page in result.pages:
                    print(f"第 {page.page_number} 頁:")
                    print(f"  內容長度: {page.content_length}")
                    print(f"  區塊數量: {page.block_count}")
                    print(f"  表格數量: {page.table_count}")
                    
                    # 處理表格
                    if page.tables:
                        for table in page.tables:
                            print(f"    表格: {table.title}")
                            print(f"    行數: {table.row_count}, 列數: {table.column_count}")
            
        except Exception as e:
            print(f"轉換失敗: {e}")
    else:
        print(f"檔案不存在: {pdf_file}")


def convert_excel_example():
    """Excel 轉換示例 (使用 Markitdown)"""
    print("\n=== Excel 轉換示例 ===")
    
    converter = UnifiedMarkdownConverter()
    
    # 假設有一個 Excel 檔案
    excel_file = "raw_docs/example.xlsx"
    
    if Path(excel_file).exists():
        try:
            result = converter.convert_file(excel_file, save_to_file=True)
            
            print(f"檔案: {result.metadata.file_name}")
            print(f"總頁數: {result.metadata.total_pages}")
            print(f"使用轉換器: {result.metadata.converter_used}")
            print(f"輸出檔案: {result.output_path}")
            
            # 處理工作表信息
            if result.pages:
                for page in result.pages:
                    print(f"工作表 {page.page_number}: {page.title}")
                    print(f"  內容長度: {page.content_length}")
            
            # 處理額外信息
            if result.metadata.additional_info:
                sheets_info = result.metadata.additional_info.get('sheets', [])
                print(f"工作表信息: {len(sheets_info)} 個工作表")
                
        except Exception as e:
            print(f"轉換失敗: {e}")
    else:
        print(f"檔案不存在: {excel_file}")


def convert_with_error_handling():
    """錯誤處理示例"""
    print("\n=== 錯誤處理示例 ===")
    
    converter = UnifiedMarkdownConverter()
    
    test_files = [
        "nonexistent.pdf",  # 檔案不存在
        "unsupported.xyz",  # 不支援的格式
        "document.pdf"      # 正常檔案
    ]
    
    for file_path in test_files:
        print(f"\n處理檔案: {file_path}")
        
        try:
            # 檢查格式支援
            if not converter.is_supported(file_path):
                print(f"  格式不支援: {file_path}")
                continue
            
            # 檢查檔案存在
            if not Path(file_path).exists():
                print(f"  檔案不存在: {file_path}")
                continue
            
            # 進行轉換
            result = converter.convert_file(file_path)
            print(f"  轉換成功: {result.metadata.file_name}")
            
        except FileNotFoundError:
            print(f"  錯誤: 檔案不存在")
        except ValueError as e:
            print(f"  錯誤: {e}")
        except RuntimeError as e:
            print(f"  錯誤: {e}")
        except Exception as e:
            print(f"  未知錯誤: {e}")


def batch_conversion_example():
    """批量轉換示例"""
    print("\n=== 批量轉換示例 ===")
    
    converter = UnifiedMarkdownConverter()
    
    # 假設有多個檔案
    test_files = [
        "raw_docs/document.pdf",
        "raw_docs/spreadsheet.xlsx",
        "raw_docs/presentation.pptx"
    ]
    
    results = []
    
    for file_path in test_files:
        if Path(file_path).exists() and converter.is_supported(file_path):
            try:
                result = converter.convert_file(file_path)
                results.append(result)
                print(f"✓ 轉換成功: {result.metadata.file_name}")
            except Exception as e:
                print(f"✗ 轉換失敗: {file_path} - {e}")
        else:
            print(f"- 跳過: {file_path}")
    
    # 統計結果
    print(f"\n批量轉換完成:")
    print(f"  成功: {len(results)} 個檔案")
    print(f"  總頁數: {sum(r.metadata.total_pages for r in results)}")
    print(f"  總表格數: {sum(r.metadata.total_tables for r in results)}")


def main():
    """主函數"""
    print("統一 Markdown 轉換器使用示例")
    print("=" * 50)
    
    # 基本使用
    basic_usage_example()
    
    # PDF 轉換
    convert_pdf_example()
    
    # Excel 轉換
    convert_excel_example()
    
    # 錯誤處理
    convert_with_error_handling()
    
    # 批量轉換
    batch_conversion_example()
    
    print("\n示例完成!")


if __name__ == "__main__":
    main()
