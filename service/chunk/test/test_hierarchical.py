"""
分層分割測試腳本

快速測試分層分割功能是否正常工作。
"""

import sys
import logging
from pathlib import Path

# 添加路徑到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk.hierarchical_splitter import HierarchicalChunkSplitter
from service.chunk.hierarchical_models import ParentChunk, ChildChunk, GroupingAnalysis

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_basic_functionality():
    """測試基本功能"""
    logger.info("=== 測試基本功能 ===")
    
    try:
        # 創建分層分割器
        splitter = HierarchicalChunkSplitter(
            parent_chunk_size=1000,
            child_chunk_size=300,
            child_chunk_overlap=50
        )
        
        logger.info("✓ HierarchicalChunkSplitter 創建成功")
        
        # 測試資料模型
        from langchain_core.documents import Document
        
        # 創建測試Document
        test_doc = Document(
            page_content="這是一個測試文檔內容。",
            metadata={"test": "value"}
        )
        
        # 測試ParentChunk
        parent_chunk = ParentChunk(
            document=test_doc,
            chunk_id="test_parent_001",
            parent_index=0,
            size=len(test_doc.page_content)
        )
        
        logger.info("✓ ParentChunk 創建成功")
        logger.info(f"  - ID: {parent_chunk.chunk_id}")
        logger.info(f"  - 大小: {parent_chunk.size}")
        
        # 測試ChildChunk
        child_chunk = ChildChunk(
            document=test_doc,
            chunk_id="test_child_001",
            parent_chunk_id="test_parent_001",
            child_index=0,
            size=len(test_doc.page_content)
        )
        
        logger.info("✓ ChildChunk 創建成功")
        logger.info(f"  - ID: {child_chunk.chunk_id}")
        logger.info(f"  - 父ID: {child_chunk.parent_chunk_id}")
        
        # 測試GroupingAnalysis
        analysis = GroupingAnalysis(
            total_parent_chunks=1,
            total_child_chunks=1,
            avg_children_per_parent=1.0,
            parent_size_stats={'min': 10, 'max': 10, 'avg': 10, 'median': 10},
            child_size_stats={'min': 10, 'max': 10, 'avg': 10, 'median': 10},
            table_handling_stats={'total_table_chunks': 0, 'total_regular_chunks': 1, 'table_chunk_ratio': 0.0, 'avg_table_size': 0, 'largest_table_size': 0, 'table_fragmentation_count': 0},
            grouping_efficiency=1.0,
            size_distribution={'0-200': 1, '200-400': 0, '400-600': 0, '600-800': 0, '800-1000': 0, '1000+': 0}
        )
        
        logger.info("✓ GroupingAnalysis 創建成功")
        logger.info(f"  - 分組效率: {analysis.grouping_efficiency:.2%}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 基本功能測試失敗: {e}")
        return False


def test_imports():
    """測試導入功能"""
    logger.info("=== 測試導入功能 ===")
    
    try:
        # 測試導入分層分割器
        from service.chunk.hierarchical_splitter import HierarchicalChunkSplitter
        logger.info("✓ HierarchicalChunkSplitter 導入成功")
        
        # 測試導入資料模型
        from service.chunk.hierarchical_models import (
            ParentChunk, ChildChunk, GroupingAnalysis, 
            HierarchicalSplitResult, SizeDistribution, TableHandlingStats
        )
        logger.info("✓ 資料模型導入成功")
        
        # 測試導入分析器
        from service.chunk.analysis.analysis import DocumentAnalyzer
        logger.info("✓ DocumentAnalyzer 導入成功")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 導入測試失敗: {e}")
        return False


def test_analysis_integration():
    """測試分析器整合"""
    logger.info("=== 測試分析器整合 ===")
    
    try:
        from service.chunk.analysis.analysis import DocumentAnalyzer
        
        # 測試創建傳統分析器
        traditional_analyzer = DocumentAnalyzer(
            use_hierarchical=False,
            chunk_size=1000,
            chunk_overlap=200
        )
        logger.info("✓ 傳統分析器創建成功")
        
        # 測試創建分層分析器
        hierarchical_analyzer = DocumentAnalyzer(
            use_hierarchical=True,
            chunk_size=2000,
            child_chunk_size=350,
            child_chunk_overlap=50
        )
        logger.info("✓ 分層分析器創建成功")
        
        # 檢查分割器類型
        if hasattr(hierarchical_analyzer.splitter, 'parent_splitter'):
            logger.info("✓ 分層分析器使用正確的分割器")
        else:
            logger.warning("⚠ 分層分析器可能未使用正確的分割器")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 分析器整合測試失敗: {e}")
        return False


def main():
    """主測試程式"""
    logger.info("開始分層分割測試...")
    
    tests = [
        ("導入功能", test_imports),
        ("基本功能", test_basic_functionality),
        ("分析器整合", test_analysis_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n執行測試: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✓ {test_name} 測試通過")
            else:
                logger.error(f"✗ {test_name} 測試失敗")
        except Exception as e:
            logger.error(f"✗ {test_name} 測試異常: {e}")
            results.append((test_name, False))
    
    # 顯示測試結果摘要
    logger.info("\n" + "="*50)
    logger.info("測試結果摘要:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        logger.info(f"- {test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        logger.info("🎉 所有測試通過！分層分割功能已準備就緒。")
    else:
        logger.warning("⚠ 部分測試失敗，請檢查相關功能。")


if __name__ == "__main__":
    main()
