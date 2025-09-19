"""
分析工具使用範例

展示如何使用 DocumentAnalyzer 進行文件分析
"""

import sys
from pathlib import Path

# 添加路徑到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk.analysis.analysis import DocumentAnalyzer


def example_analyze_single_file():
    """範例：分析單個文件"""
    print("=== 分析單個文件範例 ===")
    
    # 創建分析器
    analyzer = DocumentAnalyzer()
    
    # 分析特定文件
    result = analyzer.analyze_single_file("檔案優化.txt")
    
    if result['status'] == 'success':
        print(f"✓ 成功處理文件: {result['file_name']}")
        print(f"  - 分割成 {result['chunks_count']} 個 chunks")
        print(f"  - 統計信息: {result['statistics']}")
        print(f"  - 輸出路徑: {result['output_paths']['directory']}")
    else:
        print(f"✗ 處理失敗: {result.get('error', '未知錯誤')}")


def example_analyze_all_files():
    """範例：分析所有文件"""
    print("\n=== 分析所有文件範例 ===")
    
    # 創建分析器
    analyzer = DocumentAnalyzer()
    
    # 分析所有文件
    summary = analyzer.analyze_all_files()
    
    print(f"總文件數: {summary['total_files']}")
    print(f"成功處理: {summary['successful']}")
    print(f"處理失敗: {summary['failed']}")
    print(f"成功率: {summary['success_rate']:.1f}%")
    
    # 顯示每個文件的處理結果
    for result in summary['results']:
        status_icon = "✓" if result['status'] == 'success' else "✗"
        print(f"{status_icon} {result['file_name']}: {result['status']}")
        if result['status'] == 'success':
            print(f"    - Chunks: {result['chunks_count']}")
            print(f"    - 平均長度: {result['statistics']['average_length']:.0f}")


def example_custom_settings():
    """範例：自訂設定"""
    print("\n=== 自訂設定範例 ===")
    
    # 創建自訂設定的分析器
    analyzer = DocumentAnalyzer(
        chunk_size=500,      # 較小的 chunk 大小
        chunk_overlap=100,   # 較小的重疊
        output_base_dir="custom_output"  # 自訂輸出目錄
    )
    
    print("自訂分析器已創建")
    print(f"Chunk 大小: {analyzer.chunk_size}")
    print(f"Chunk 重疊: {analyzer.chunk_overlap}")
    print(f"輸出目錄: {analyzer.output_base_dir}")


if __name__ == "__main__":
    print("文件分析工具使用範例")
    print("=" * 50)
    
    # 執行範例
    example_analyze_single_file()
    example_analyze_all_files()
    example_custom_settings()
    
    print("\n" + "=" * 50)
    print("範例執行完成！")
