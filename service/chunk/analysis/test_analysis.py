"""
測試分析程式

用於測試 DocumentAnalyzer 的功能
"""

import sys
from pathlib import Path

# 添加路徑到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk.analysis.analysis import DocumentAnalyzer


def test_analyzer_initialization():
    """測試分析器初始化"""
    print("Testing analyzer initialization...")
    
    try:
        analyzer = DocumentAnalyzer()
        print("✓ Analyzer initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize analyzer: {e}")
        return False


def test_get_files():
    """測試獲取文件列表"""
    print("Testing file discovery...")
    
    try:
        analyzer = DocumentAnalyzer()
        files = analyzer.get_files_to_process()
        print(f"✓ Found {len(files)} files to process")
        
        for file in files:
            print(f"  - {file.name}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to get files: {e}")
        return False


def test_single_file_processing():
    """測試單個文件處理"""
    print("Testing single file processing...")
    
    try:
        analyzer = DocumentAnalyzer()
        files = analyzer.get_files_to_process()
        
        if not files:
            print("No files found to test")
            return True
        
        # 選擇第一個文件進行測試
        test_file = files[0]
        print(f"Testing with file: {test_file.name}")
        
        result = analyzer.process_single_file(test_file)
        
        if result['status'] == 'success':
            print("✓ File processed successfully")
            print(f"  - Chunks: {result['chunks_count']}")
            print(f"  - Statistics: {result['statistics']}")
            return True
        else:
            print(f"✗ File processing failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Error in single file processing: {e}")
        return False


def main():
    """主測試函數"""
    print("=== Document Analyzer Test ===")
    print()
    
    tests = [
        ("Initialization", test_analyzer_initialization),
        ("File Discovery", test_get_files),
        ("Single File Processing", test_single_file_processing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        print()
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")


if __name__ == "__main__":
    main()
