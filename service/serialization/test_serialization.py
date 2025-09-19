"""
Serialization 模組測試

簡單的測試腳本來驗證序列化和反序列化功能是否正常工作。
"""

import os
import tempfile
from pathlib import Path
from service.markdown_integrate.data_models import ConversionResult, ConversionMetadata, PageInfo, TableInfo
from service.serialization import ConversionSerializer, ConversionDeserializer


def test_basic_serialization():
    """測試基本序列化和反序列化功能"""
    print("測試基本序列化和反序列化...")
    
    # 創建測試數據
    metadata = ConversionMetadata(
        file_name="test_document.pdf",
        file_path="/test/path/test_document.pdf",
        file_type=".pdf",
        file_size=1024,
        total_pages=2,
        total_tables=1,
        total_content_length=500,
        conversion_timestamp=1234567890.0,
        converter_used="marker"
    )
    
    # 創建測試頁面
    page1 = PageInfo(
        page_number=1,
        title="Test Page 1",
        content="# Test Page 1\n\nThis is test content.",
        content_length=50,
        block_count=2,
        block_types={"header": 1, "paragraph": 1},
        table_count=1,
        tables=[
            TableInfo(
                table_id="table_1",
                title="Test Table",
                content="| A | B |\n|---|---|\n| 1 | 2 |",
                row_count=2,
                column_count=2,
                start_line=5,
                end_line=7
            )
        ]
    )
    
    page2 = PageInfo(
        page_number=2,
        title="Test Page 2",
        content="# Test Page 2\n\nMore test content.",
        content_length=40,
        block_count=2,
        block_types={"header": 1, "paragraph": 1},
        table_count=0,
        tables=[]
    )
    
    # 創建 ConversionResult
    conversion_result = ConversionResult(
        content="# Test Page 1\n\nThis is test content.\n\n# Test Page 2\n\nMore test content.",
        metadata=metadata,
        pages=[page1, page2],
        output_path="/test/output.md"
    )
    
    # 使用臨時目錄進行測試
    with tempfile.TemporaryDirectory() as temp_dir:
        # 序列化
        serializer = ConversionSerializer(output_dir=temp_dir)
        json_path = serializer.serialize(conversion_result, "test_conversion.json")
        
        print(f"✓ 序列化完成: {json_path}")
        
        # 驗證文件存在
        assert os.path.exists(json_path), "序列化文件不存在"
        print("✓ 序列化文件存在")
        
        # 反序列化
        deserializer = ConversionDeserializer(input_dir=temp_dir)
        restored_result = deserializer.deserialize(json_path)
        
        print("✓ 反序列化完成")
        
        # 驗證基本屬性
        assert restored_result.content == conversion_result.content, "內容不匹配"
        assert restored_result.metadata.file_name == conversion_result.metadata.file_name, "文件名不匹配"
        assert restored_result.metadata.total_pages == conversion_result.metadata.total_pages, "總頁數不匹配"
        assert len(restored_result.pages) == len(conversion_result.pages), "頁面數量不匹配"
        
        print("✓ 基本屬性驗證通過")
        
        # 驗證頁面信息
        for i, (original_page, restored_page) in enumerate(zip(conversion_result.pages, restored_result.pages)):
            assert original_page.page_number == restored_page.page_number, f"頁面 {i} 頁碼不匹配"
            assert original_page.title == restored_page.title, f"頁面 {i} 標題不匹配"
            assert original_page.content == restored_page.content, f"頁面 {i} 內容不匹配"
            assert len(original_page.tables) == len(restored_page.tables), f"頁面 {i} 表格數量不匹配"
        
        print("✓ 頁面信息驗證通過")
        
        # 驗證表格信息
        for i, (original_table, restored_table) in enumerate(zip(conversion_result.pages[0].tables, restored_result.pages[0].tables)):
            assert original_table.table_id == restored_table.table_id, f"表格 {i} ID 不匹配"
            assert original_table.title == restored_table.title, f"表格 {i} 標題不匹配"
            assert original_table.content == restored_table.content, f"表格 {i} 內容不匹配"
        
        print("✓ 表格信息驗證通過")
        
        # 測試文件驗證
        is_valid = deserializer.validate_file(json_path)
        assert is_valid, "文件驗證失敗"
        print("✓ 文件驗證通過")
        
        # 測試文件信息獲取
        file_info = deserializer.get_file_info(json_path)
        assert file_info['original_file_name'] == "test_document.pdf", "文件信息不正確"
        print("✓ 文件信息獲取成功")
        
        print("🎉 所有測試通過！")


def test_chunk_splitter_integration():
    """測試與 ChunkSplitter 的整合"""
    print("\n測試與 ChunkSplitter 的整合...")
    
    try:
        from service.chunk.chunk_splitter import ChunkSplitter
        
        # 創建測試數據
        metadata = ConversionMetadata(
            file_name="integration_test.pdf",
            file_path="/test/integration_test.pdf",
            file_type=".pdf",
            file_size=2048,
            total_pages=1,
            total_tables=0,
            total_content_length=200,
            conversion_timestamp=1234567890.0,
            converter_used="marker"
        )
        
        page = PageInfo(
            page_number=1,
            title="Integration Test",
            content="# Integration Test\n\nThis is a test for chunk splitting integration.\n\n## Section 1\n\nContent for section 1.\n\n## Section 2\n\nContent for section 2.",
            content_length=150,
            block_count=5,
            block_types={"header": 3, "paragraph": 2},
            table_count=0,
            tables=[]
        )
        
        conversion_result = ConversionResult(
            content="# Integration Test\n\nThis is a test for chunk splitting integration.\n\n## Section 1\n\nContent for section 1.\n\n## Section 2\n\nContent for section 2.",
            metadata=metadata,
            pages=[page],
            output_path="/test/integration_output.md"
        )
        
        # 使用臨時目錄進行測試
        with tempfile.TemporaryDirectory() as temp_dir:
            # 序列化
            serializer = ConversionSerializer(output_dir=temp_dir)
            json_path = serializer.serialize(conversion_result, "integration_test.json")
            
            print(f"✓ 序列化完成: {json_path}")
            
            # 使用 ChunkSplitter 從序列化文件分割
            splitter = ChunkSplitter(chunk_size=100, chunk_overlap=20)
            chunks = splitter.split_markdown(
                input_data=json_path,
                from_serialization=True
            )
            
            print(f"✓ 分割完成，產生 {len(chunks)} 個 chunks")
            
            # 驗證 chunks
            assert len(chunks) > 0, "沒有產生任何 chunks"
            
            # 檢查第一個 chunk 的 metadata
            first_chunk = chunks[0]
            assert first_chunk.metadata.get('file_name') == "integration_test.pdf", "文件名不正確"
            assert first_chunk.metadata.get('page_number') == 1, "頁碼不正確"
            assert first_chunk.metadata.get('page_title') == "Integration Test", "頁面標題不正確"
            
            print("✓ Chunk metadata 驗證通過")
            print("🎉 ChunkSplitter 整合測試通過！")
            
    except ImportError as e:
        print(f"⚠️ 無法導入 ChunkSplitter: {e}")
        print("跳過 ChunkSplitter 整合測試")


def main():
    """執行所有測試"""
    print("Serialization 模組測試")
    print("=" * 40)
    
    try:
        test_basic_serialization()
        test_chunk_splitter_integration()
        print("\n🎉 所有測試完成！")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
