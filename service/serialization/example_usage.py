"""
Serialization 模組使用範例

展示如何使用序列化和反序列化功能來保存和載入 ConversionResult 對象。
"""

import os
from pathlib import Path
from service.markdown_integrate.data_models import ConversionResult, ConversionMetadata, PageInfo, TableInfo
from service.serialization import ConversionSerializer, ConversionDeserializer
from service.chunk.chunk_splitter import ChunkSplitter


def example_serialize_conversion_result():
    """範例：序列化 ConversionResult"""
    print("=== 序列化 ConversionResult 範例 ===")
    
    # 創建示例數據
    metadata = ConversionMetadata(
        file_name="example_document.pdf",
        file_path="/path/to/example_document.pdf",
        file_type=".pdf",
        file_size=1024000,
        total_pages=5,
        total_tables=3,
        total_content_length=50000,
        conversion_timestamp=1234567890.0,
        converter_used="marker"
    )
    
    # 創建示例頁面
    page1 = PageInfo(
        page_number=1,
        title="Introduction",
        content="# Introduction\n\nThis is the first page content.",
        content_length=100,
        block_count=5,
        block_types={"header": 1, "paragraph": 4},
        table_count=1,
        tables=[
            TableInfo(
                table_id="table_1",
                title="Sample Table",
                content="| Col1 | Col2 |\n|------|------|\n| A    | B    |",
                row_count=2,
                column_count=2,
                start_line=10,
                end_line=12
            )
        ]
    )
    
    page2 = PageInfo(
        page_number=2,
        title="Details",
        content="# Details\n\nThis is the second page content.",
        content_length=150,
        block_count=3,
        block_types={"header": 1, "paragraph": 2},
        table_count=0,
        tables=[]
    )
    
    # 創建 ConversionResult
    conversion_result = ConversionResult(
        content="# Introduction\n\nThis is the first page content.\n\n# Details\n\nThis is the second page content.",
        metadata=metadata,
        pages=[page1, page2],
        output_path="/path/to/output.md"
    )
    
    # 序列化
    serializer = ConversionSerializer()
    json_path = serializer.serialize(conversion_result, "example_conversion.json")
    print(f"序列化完成，文件保存至: {json_path}")
    
    return json_path


def example_deserialize_conversion_result(json_path: str):
    """範例：反序列化 ConversionResult"""
    print("\n=== 反序列化 ConversionResult 範例 ===")
    
    # 反序列化
    deserializer = ConversionDeserializer()
    conversion_result = deserializer.deserialize(json_path)
    
    print(f"反序列化完成:")
    print(f"  文件名: {conversion_result.metadata.file_name}")
    print(f"  總頁數: {conversion_result.metadata.total_pages}")
    print(f"  轉換器: {conversion_result.metadata.converter_used}")
    print(f"  頁面數量: {len(conversion_result.pages) if conversion_result.pages else 0}")
    
    if conversion_result.pages:
        for page in conversion_result.pages:
            print(f"    頁面 {page.page_number}: {page.title} ({page.content_length} 字符)")
    
    return conversion_result


def example_chunk_splitter_with_serialization(json_path: str):
    """範例：使用序列化文件進行 Chunk 分割"""
    print("\n=== 使用序列化文件進行 Chunk 分割範例 ===")
    
    # 創建 ChunkSplitter
    splitter = ChunkSplitter(
        chunk_size=500,
        chunk_overlap=100,
        normalize_output=True
    )
    
    # 從序列化文件分割
    chunks = splitter.split_markdown(
        input_data=json_path,
        from_serialization=True,
        output_excel=True,
        output_path="service/output/chunk/example_chunks.xlsx",
        md_output_path="service/output/chunk/example_chunks.md"
    )
    
    print(f"分割完成，共產生 {len(chunks)} 個 chunks")
    
    # 顯示前幾個 chunk 的信息
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"  Chunk {i}:")
        print(f"    頁碼: {chunk.metadata.get('page_number', 'N/A')}")
        print(f"    標題: {chunk.metadata.get('page_title', 'N/A')}")
        print(f"    內容長度: {len(chunk.page_content)}")
        print(f"    內容預覽: {chunk.page_content[:100]}...")
        print()
    
    return chunks


def example_list_serialized_files():
    """範例：列出可用的序列化文件"""
    print("\n=== 列出序列化文件範例 ===")
    
    deserializer = ConversionDeserializer()
    files = deserializer.list_available_files()
    
    if files:
        print(f"找到 {len(files)} 個序列化文件:")
        for file_info in files:
            print(f"  - {file_info['file_name']}")
            print(f"    原始文件: {file_info['original_file_name']}")
            print(f"    轉換器: {file_info['converter_used']}")
            print(f"    頁數: {file_info['total_pages']}")
            print(f"    有頁面信息: {file_info['has_pages']}")
            print()
    else:
        print("沒有找到序列化文件")


def example_validate_serialized_file(json_path: str):
    """範例：驗證序列化文件"""
    print("\n=== 驗證序列化文件範例 ===")
    
    deserializer = ConversionDeserializer()
    is_valid = deserializer.validate_file(json_path)
    
    if is_valid:
        print(f"文件 {json_path} 驗證通過")
        
        # 獲取文件信息
        file_info = deserializer.get_file_info(json_path)
        print(f"文件信息:")
        for key, value in file_info.items():
            print(f"  {key}: {value}")
    else:
        print(f"文件 {json_path} 驗證失敗")


def main():
    """主函數：執行所有範例"""
    print("Serialization 模組使用範例")
    print("=" * 50)
    
    try:
        # 1. 序列化範例
        json_path = example_serialize_conversion_result()
        
        # 2. 反序列化範例
        conversion_result = example_deserialize_conversion_result(json_path)
        
        # 3. 使用序列化文件進行 Chunk 分割
        chunks = example_chunk_splitter_with_serialization(json_path)
        
        # 4. 列出序列化文件
        example_list_serialized_files()
        
        # 5. 驗證序列化文件
        example_validate_serialized_file(json_path)
        
        print("\n所有範例執行完成！")
        
    except Exception as e:
        print(f"執行範例時發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
