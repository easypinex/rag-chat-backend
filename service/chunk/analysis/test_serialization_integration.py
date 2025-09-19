"""
測試 analysis.py 中的序列化整合功能

驗證 DocumentAnalyzer 能夠正確檢測、載入和保存序列化文件。
"""

import os
import tempfile
import shutil
from pathlib import Path
from service.chunk.analysis.analysis import DocumentAnalyzer
from service.markdown_integrate.data_models import ConversionResult, ConversionMetadata, PageInfo


def test_serialization_detection():
    """測試序列化文件檢測功能"""
    print("測試序列化文件檢測功能...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 創建測試分析器
        analyzer = DocumentAnalyzer(
            raw_docs_dir=temp_dir,
            output_base_dir=os.path.join(temp_dir, "output")
        )
        
        # 創建測試文件
        test_file = Path(temp_dir) / "test_document.pdf"
        test_file.write_text("Test PDF content")
        
        # 測試序列化文件不存在的情況
        exists = analyzer.check_serialization_exists(test_file)
        assert not exists, "序列化文件不應該存在"
        print("✓ 序列化文件不存在檢測通過")
        
        # 創建一個假的序列化文件
        serialization_path = analyzer.get_serialization_path(test_file)
        serialization_path.parent.mkdir(parents=True, exist_ok=True)
        serialization_path.write_text("{}")  # 空的 JSON
        
        # 測試無效序列化文件
        exists = analyzer.check_serialization_exists(test_file)
        assert not exists, "無效序列化文件不應該被認為存在"
        print("✓ 無效序列化文件檢測通過")


def test_serialization_workflow():
    """測試完整的序列化工作流程"""
    print("\n測試完整的序列化工作流程...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 創建測試分析器
        analyzer = DocumentAnalyzer(
            raw_docs_dir=temp_dir,
            output_base_dir=os.path.join(temp_dir, "output")
        )
        
        # 創建測試文件
        test_file = Path(temp_dir) / "test_document.pdf"
        test_file.write_text("Test PDF content")
        
        # 創建模擬的 ConversionResult
        metadata = ConversionMetadata(
            file_name="test_document.pdf",
            file_path=str(test_file),
            file_type=".pdf",
            file_size=1024,
            total_pages=1,
            total_tables=0,
            total_content_length=100,
            conversion_timestamp=1234567890.0,
            converter_used="test_converter"
        )
        
        page = PageInfo(
            page_number=1,
            title="Test Page",
            content="# Test Page\n\nTest content.",
            content_length=50,
            block_count=2,
            block_types={"header": 1, "paragraph": 1},
            table_count=0,
            tables=[]
        )
        
        conversion_result = ConversionResult(
            content="# Test Page\n\nTest content.",
            metadata=metadata,
            pages=[page],
            output_path="/test/output.md"
        )
        
        # 測試保存序列化文件
        analyzer.save_to_serialization(conversion_result, test_file)
        serialization_path = analyzer.get_serialization_path(test_file)
        assert serialization_path.exists(), "序列化文件應該被創建"
        print("✓ 序列化文件保存成功")
        
        # 測試載入序列化文件
        loaded_result = analyzer.load_from_serialization(test_file)
        assert loaded_result.content == conversion_result.content, "載入的內容不匹配"
        assert loaded_result.metadata.file_name == conversion_result.metadata.file_name, "載入的元數據不匹配"
        print("✓ 序列化文件載入成功")
        
        # 測試序列化文件存在檢測
        exists = analyzer.check_serialization_exists(test_file)
        assert exists, "序列化文件應該被檢測為存在"
        print("✓ 序列化文件存在檢測通過")


def test_output_structure():
    """測試輸出目錄結構包含序列化文件"""
    print("\n測試輸出目錄結構...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 創建測試分析器
        analyzer = DocumentAnalyzer(
            raw_docs_dir=temp_dir,
            output_base_dir=os.path.join(temp_dir, "output")
        )
        
        # 創建測試文件
        test_file = Path(temp_dir) / "test_document.pdf"
        test_file.write_text("Test PDF content")
        
        # 獲取輸出結構
        output_paths = analyzer.create_output_structure(test_file)
        
        # 檢查是否包含序列化文件路徑
        assert 'serialization' in output_paths, "輸出結構應該包含序列化文件路徑"
        assert output_paths['serialization'].name == "test_document_ConversionResult.json", "序列化文件名不正確"
        print("✓ 輸出目錄結構包含序列化文件路徑")


def test_serialization_path_consistency():
    """測試序列化文件路徑的一致性"""
    print("\n測試序列化文件路徑一致性...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 創建測試分析器
        analyzer = DocumentAnalyzer(
            raw_docs_dir=temp_dir,
            output_base_dir=os.path.join(temp_dir, "output")
        )
        
        # 創建測試文件
        test_file = Path(temp_dir) / "test_document.pdf"
        test_file.write_text("Test PDF content")
        
        # 獲取序列化文件路徑
        serialization_path1 = analyzer.get_serialization_path(test_file)
        output_paths = analyzer.create_output_structure(test_file)
        serialization_path2 = output_paths['serialization']
        
        # 檢查路徑一致性
        assert serialization_path1 == serialization_path2, "序列化文件路徑應該一致"
        print("✓ 序列化文件路徑一致性檢查通過")


def main():
    """執行所有測試"""
    print("Analysis.py 序列化整合測試")
    print("=" * 50)
    
    try:
        test_serialization_detection()
        test_serialization_workflow()
        test_output_structure()
        test_serialization_path_consistency()
        
        print("\n🎉 所有測試通過！")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
