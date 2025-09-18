"""
Marker Converter 使用範例

展示如何使用 Marker 轉換器進行 PDF 到 Markdown 的轉換
採用 QUICK_START.md 推薦的方法
"""

import os
import sys
import logging
from pathlib import Path

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from marker_converter import MarkerConverter, PagesResult

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_single_pdf_conversion():
    """單一 PDF 檔案轉換範例 - 使用 Marker 轉換器"""
    print("=== 單一 PDF 檔案轉換範例 (Marker 轉換器) ===")
    
    # 建立轉換器
    try:
        converter = MarkerConverter()
        print("✓ Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ Marker 套件未安裝: {e}")
        return
    
    # 指定測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent.parent / "raw_docs"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("✗ 未找到測試 PDF 檔案")
        return
    
    test_pdf = pdf_files[0]
    print(f"使用測試檔案: {test_pdf.name}")
    
    # 方法 1: 完整轉換 (marker_to_markdown)
    try:
        print("\n--- 方法 1: 完整轉換 ---")
        markdown_content = converter.marker_to_markdown(str(test_pdf))
        
        # 保存到檔案
        output_path = test_pdf.parent / f"{test_pdf.stem}_marker.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✓ 完整轉換成功!")
        print(f"  - 輸出檔案: {output_path}")
        print(f"  - 內容長度: {len(markdown_content)} 字元")
        print(f"  - 內容預覽: {markdown_content[:200]}...")
        
    except Exception as e:
        print(f"✗ 完整轉換失敗: {e}")
    
    # 方法 2: 頁面列表和資訊 (marker_pages)
    try:
        print("\n--- 方法 2: 頁面列表和資訊 ---")
        result: PagesResult = converter.marker_pages(str(test_pdf))
        
        print(f"✓ 頁面分析成功!")
        print(f"  - 檔案名: {result['file_name']}")
        print(f"  - 總頁數: {result['total_pages']}")
        
        # 顯示前幾頁的資訊
        for i, page in enumerate(result['pages'][:3]):  # 只顯示前3頁
            print(f"  - 第 {page['page_number']} 頁:")
            print(f"    * 內容長度: {page['content_length']} 字元")
            print(f"    * 區塊數量: {page['block_count']}")
            print(f"    * 區塊類型: {page['block_types']}")
            print(f"    * 表格數量: {page['table_count']}")
            if page['table_count'] > 0:
                for table in page['tables']:
                    print(f"      - 表格 {table['table_id']}: {table['title']} ({table['row_count']}行×{table['column_count']}列)")
        
        if len(result['pages']) > 3:
            print(f"  - ... 還有 {len(result['pages']) - 3} 頁")
        
        # 顯示所有表格的統計
        total_tables = sum(page['table_count'] for page in result['pages'])
        if total_tables > 0:
            print(f"\n📊 表格統計:")
            print(f"  - 總表格數: {total_tables}")
            for page in result['pages']:
                if page['table_count'] > 0:
                    print(f"  - 第 {page['page_number']} 頁: {page['table_count']} 個表格")
        
    except Exception as e:
        print(f"✗ 頁面分析失敗: {e}")


def example_batch_conversion():
    """批量轉換範例 - 使用 Marker 轉換器"""
    print("\n=== 批量轉換範例 (Marker 轉換器) ===")
    
    try:
        converter = MarkerConverter()
        print("✓ Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ Marker 套件未安裝: {e}")
        return
    
    # 指定測試目錄
    raw_docs_dir = Path(__file__).parent.parent.parent.parent / "raw_docs"
    
    if not raw_docs_dir.exists():
        print("✗ 測試目錄不存在")
        return
    
    # 建立輸出目錄
    output_dir = Path(__file__).parent.parent / "converted"
    output_dir.mkdir(exist_ok=True)
    
    # 獲取 PDF 檔案列表
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    if not pdf_files:
        print("✗ 未找到 PDF 檔案")
        return
    
    print(f"找到 {len(pdf_files)} 個 PDF 檔案")
    
    # 批量轉換 - 使用完整轉換方法
    success_count = 0
    error_count = 0
    
    for pdf_file in pdf_files:
        try:
            print(f"\n處理檔案: {pdf_file.name}")
            
            # 使用完整轉換方法
            markdown_content = converter.marker_to_markdown(str(pdf_file))
            
            # 保存到輸出目錄
            output_file = output_dir / f"{pdf_file.stem}_marker.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"  ✓ 轉換成功: {len(markdown_content)} 字元")
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ 轉換失敗: {e}")
            error_count += 1
    
    print(f"\n批量轉換完成!")
    print(f"  - 成功: {success_count} 個檔案")
    print(f"  - 失敗: {error_count} 個檔案")
    print(f"  - 輸出目錄: {output_dir}")


def example_page_analysis():
    """頁面分析範例 - 展示頁面級別的分析功能"""
    print("\n=== 頁面分析範例 ===")
    
    try:
        converter = MarkerConverter()
        print("✓ Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ Marker 套件未安裝: {e}")
        return
    
    # 指定測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent.parent / "raw_docs"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("✗ 未找到測試 PDF 檔案")
        return
    
    test_pdf = pdf_files[0]
    print(f"分析檔案: {test_pdf.name}")
    
    try:
        # 獲取頁面分析結果
        result: PagesResult = converter.marker_pages(str(test_pdf))
        
        print(f"\n=== 檔案分析結果 ===")
        print(f"檔案名: {result['file_name']}")
        print(f"總頁數: {result['total_pages']}")
        
        # 統計資訊
        total_content_length = sum(page['content_length'] for page in result['pages'])
        avg_content_length = total_content_length / len(result['pages']) if result['pages'] else 0
        
        print(f"\n=== 統計資訊 ===")
        print(f"總內容長度: {total_content_length} 字元")
        print(f"平均每頁長度: {avg_content_length:.1f} 字元")
        
        # 區塊類型統計
        all_block_types = {}
        for page in result['pages']:
            for block_type, count in page['block_types'].items():
                all_block_types[block_type] = all_block_types.get(block_type, 0) + count
        
        print(f"\n=== 區塊類型統計 ===")
        for block_type, count in sorted(all_block_types.items()):
            print(f"  {block_type}: {count} 個")
        
        # 表格統計
        total_tables = sum(page['table_count'] for page in result['pages'])
        if total_tables > 0:
            print(f"\n=== 表格統計 ===")
            print(f"總表格數: {total_tables}")
            for page in result['pages']:
                if page['table_count'] > 0:
                    print(f"  第 {page['page_number']} 頁: {page['table_count']} 個表格")
                    for table in page['tables']:
                        print(f"    - 表格 {table['table_id']}: {table['title']} ({table['row_count']}行×{table['column_count']}列)")
        
        # 顯示每頁詳細資訊
        print(f"\n=== 每頁詳細資訊 ===")
        for page in result['pages']:
            print(f"第 {page['page_number']} 頁:")
            print(f"  - 內容長度: {page['content_length']} 字元")
            print(f"  - 區塊數量: {page['block_count']}")
            print(f"  - 區塊類型: {page['block_types']}")
            print(f"  - 表格數量: {page['table_count']}")
            if page['content_length'] > 0:
                preview = page['content'][:100].replace('\n', ' ')
                print(f"  - 內容預覽: {preview}...")
            print()
        
    except Exception as e:
        print(f"✗ 頁面分析失敗: {e}")


def example_table_analysis():
    """表格分析範例 - 專門展示表格提取和分析功能"""
    print("\n=== 表格分析範例 ===")
    
    try:
        converter = MarkerConverter()
        print("✓ Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ Marker 套件未安裝: {e}")
        return
    
    # 指定測試 PDF 檔案
    raw_docs_dir = Path(__file__).parent.parent.parent.parent / "raw_docs"
    pdf_files = list(raw_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("✗ 未找到測試 PDF 檔案")
        return
    
    test_pdf = pdf_files[0]
    print(f"分析檔案: {test_pdf.name}")
    
    try:
        # 獲取頁面分析結果
        result: PagesResult = converter.marker_pages(str(test_pdf))
        
        # 收集所有表格
        all_tables = []
        for page in result['pages']:
            for table in page['tables']:
                all_tables.append((page['page_number'], table))
        
        if not all_tables:
            print("✗ 未找到任何表格")
            return
        
        print(f"\n=== 表格分析結果 ===")
        print(f"檔案名: {result['file_name']}")
        print(f"總表格數: {len(all_tables)}")
        
        # 顯示每個表格的詳細信息
        for page_num, table in all_tables:
            print(f"\n📊 表格 {table['table_id']} (第 {page_num} 頁)")
            print(f"  標題: {table['title']}")
            print(f"  尺寸: {table['row_count']} 行 × {table['column_count']} 列")
            print(f"  位置: 第 {table['start_line']} 行到第 {table['end_line']} 行")
            print(f"  內容預覽:")
            
            # 顯示表格的前幾行
            lines = table['content'].split('\n')
            for i, line in enumerate(lines[:5]):
                print(f"    {i+1}: {line}")
            if len(lines) > 5:
                print(f"    ... 還有 {len(lines) - 5} 行")
        
        # 表格統計
        print(f"\n=== 表格統計 ===")
        total_rows = sum(table['row_count'] for _, table in all_tables)
        total_columns = sum(table['column_count'] for _, table in all_tables)
        avg_rows = total_rows / len(all_tables) if all_tables else 0
        avg_columns = total_columns / len(all_tables) if all_tables else 0
        
        print(f"總行數: {total_rows}")
        print(f"總列數: {total_columns}")
        print(f"平均行數: {avg_rows:.1f}")
        print(f"平均列數: {avg_columns:.1f}")
        
    except Exception as e:
        print(f"✗ 表格分析失敗: {e}")


def example_error_handling():
    """錯誤處理範例 - Marker 轉換器"""
    print("\n=== 錯誤處理範例 (Marker 轉換器) ===")
    
    try:
        converter = MarkerConverter()
        print("✓ Marker 轉換器建立成功")
    except ImportError as e:
        print(f"✗ Marker 套件未安裝: {e}")
        return
    
    # 測試不存在的檔案 - 完整轉換方法
    try:
        converter.marker_to_markdown("nonexistent.pdf")
    except FileNotFoundError as e:
        print(f"✓ 正確捕獲檔案不存在錯誤 (完整轉換): {e}")
    except Exception as e:
        print(f"✓ 正確捕獲其他錯誤 (完整轉換): {e}")
    
    # 測試不存在的檔案 - 頁面分析方法
    try:
        converter.marker_pages("nonexistent.pdf")
    except FileNotFoundError as e:
        print(f"✓ 正確捕獲檔案不存在錯誤 (頁面分析): {e}")
    except Exception as e:
        print(f"✓ 正確捕獲其他錯誤 (頁面分析): {e}")
    
    # 測試無效的 PDF 檔案
    try:
        # 創建一個臨時的無效 PDF 檔案
        invalid_pdf = Path("invalid.pdf")
        invalid_pdf.write_text("This is not a PDF file")
        
        converter.marker_to_markdown(str(invalid_pdf))
    except Exception as e:
        print(f"✓ 正確捕獲無效 PDF 錯誤: {e}")
    finally:
        # 清理臨時檔案
        if invalid_pdf.exists():
            invalid_pdf.unlink()


def main():
    """主函數"""
    print("Marker Converter 使用範例")
    print("採用 QUICK_START.md 推薦的方法")
    print("=" * 60)
    
    # 檢查 Marker 套件是否可用
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered
        print("✓ Marker 套件已安裝")
    except ImportError:
        print("✗ Marker 套件未安裝，請執行: pip install marker-pdf[full]")
        return
    
    # 執行範例
    example_single_pdf_conversion()
    example_batch_conversion()
    example_page_analysis()
    example_table_analysis()
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("範例執行完成!")
    print("\n主要特色:")
    print("✓ 頁碼標記 (## Page N)")
    print("✓ 智能表格轉換")
    print("✓ 複雜表格保留 HTML")
    print("✓ 完整錯誤處理")
    print("✓ 明確的類型標注")
    print("✓ 智能頁面分割")
    print("✓ 詳細的頁面分析")
    print("✓ 整合的頁面資訊")


if __name__ == "__main__":
    main()
