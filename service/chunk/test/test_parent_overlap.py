"""
測試 parent_chunk_overlap 參數

驗證新添加的 parent_chunk_overlap 參數是否正常工作。
"""

import sys
import logging
from pathlib import Path

# 添加路徑到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk.hierarchical_splitter import HierarchicalChunkSplitter

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_parent_overlap_parameter():
    """測試 parent_chunk_overlap 參數"""
    logger.info("=== 測試 parent_chunk_overlap 參數 ===")
    
    try:
        # 創建分層分割器，使用新的 parent_chunk_overlap 參數
        splitter = HierarchicalChunkSplitter(
            parent_chunk_size=1000,      # 較小的父chunk用於測試
            parent_chunk_overlap=200,     # 父層重疊
            child_chunk_size=300,         # 較小的子chunk用於測試
            child_chunk_overlap=50,       # 子層重疊
            keep_tables_together=True,
            normalize_output=True
        )
        
        logger.info("✓ HierarchicalChunkSplitter 創建成功")
        logger.info(f"  - parent_chunk_size: {splitter.parent_chunk_size}")
        logger.info(f"  - parent_chunk_overlap: {splitter.parent_chunk_overlap}")
        logger.info(f"  - child_chunk_size: {splitter.child_chunk_size}")
        logger.info(f"  - child_chunk_overlap: {splitter.child_chunk_overlap}")
        
        # 檢查 parent_text_splitter 是否正確初始化
        if hasattr(splitter, 'parent_text_splitter'):
            logger.info("✓ parent_text_splitter 已初始化")
            logger.info(f"  - parent_text_splitter.chunk_size: {splitter.parent_text_splitter.chunk_size}")
            logger.info(f"  - parent_text_splitter.chunk_overlap: {splitter.parent_text_splitter.chunk_overlap}")
        else:
            logger.error("✗ parent_text_splitter 未初始化")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ parent_chunk_overlap 參數測試失敗: {e}")
        return False


def test_parent_overlap_functionality():
    """測試 parent_chunk_overlap 功能"""
    logger.info("=== 測試 parent_chunk_overlap 功能 ===")
    
    try:
        # 創建分層分割器
        splitter = HierarchicalChunkSplitter(
            parent_chunk_size=1500,      # 中等大小的父chunk
            parent_chunk_overlap=200,    # 父層重疊
            child_chunk_size=400,        # 中等大小的子chunk
            child_chunk_overlap=50,      # 子層重疊
            keep_tables_together=True,
            normalize_output=True
        )
        
        # 測試文件
        test_file = project_root / "raw_docs" / "理賠審核原則.xlsx"
        
        if not test_file.exists():
            logger.warning(f"測試文件不存在: {test_file}")
            return False
        
        # 進行分層分割
        result = splitter.split_hierarchically(str(test_file))
        
        logger.info(f"✓ 分層分割完成:")
        logger.info(f"  - 父chunks: {len(result.parent_chunks)}")
        logger.info(f"  - 子chunks: {len(result.child_chunks)}")
        logger.info(f"  - 分組效率: {result.grouping_analysis.grouping_efficiency:.2%}")
        
        # 檢查父chunk大小分佈
        parent_sizes = [chunk.size for chunk in result.parent_chunks]
        if parent_sizes:
            avg_parent_size = sum(parent_sizes) / len(parent_sizes)
            max_parent_size = max(parent_sizes)
            min_parent_size = min(parent_sizes)
            
            logger.info(f"  - 父chunk大小統計:")
            logger.info(f"    - 平均: {avg_parent_size:.2f} 字")
            logger.info(f"    - 最大: {max_parent_size} 字")
            logger.info(f"    - 最小: {min_parent_size} 字")
            
            # 檢查是否有父chunk使用了重疊分割
            large_parents = [size for size in parent_sizes if size > splitter.parent_chunk_size]
            if large_parents:
                logger.info(f"  - 超過父chunk大小的chunks: {len(large_parents)} 個")
                logger.info("    (這些chunks應該被進一步分割)")
            else:
                logger.info("  - 所有父chunks都在預期大小範圍內")
        
        # 檢查子chunk大小分佈
        child_sizes = [chunk.size for chunk in result.child_chunks]
        if child_sizes:
            avg_child_size = sum(child_sizes) / len(child_sizes)
            max_child_size = max(child_sizes)
            min_child_size = min(child_sizes)
            
            logger.info(f"  - 子chunk大小統計:")
            logger.info(f"    - 平均: {avg_child_size:.2f} 字")
            logger.info(f"    - 最大: {max_child_size} 字")
            logger.info(f"    - 最小: {min_child_size} 字")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ parent_chunk_overlap 功能測試失敗: {e}")
        return False


def test_parameter_validation():
    """測試參數驗證"""
    logger.info("=== 測試參數驗證 ===")
    
    try:
        # 測試不同的參數組合
        test_configs = [
            {
                "name": "標準配置",
                "parent_chunk_size": 2000,
                "parent_chunk_overlap": 200,
                "child_chunk_size": 350,
                "child_chunk_overlap": 50
            },
            {
                "name": "小配置",
                "parent_chunk_size": 1000,
                "parent_chunk_overlap": 100,
                "child_chunk_size": 200,
                "child_chunk_overlap": 25
            },
            {
                "name": "大配置",
                "parent_chunk_size": 3000,
                "parent_chunk_overlap": 300,
                "child_chunk_size": 500,
                "child_chunk_overlap": 75
            }
        ]
        
        for config in test_configs:
            logger.info(f"測試 {config['name']}...")
            
            splitter = HierarchicalChunkSplitter(
                parent_chunk_size=config["parent_chunk_size"],
                parent_chunk_overlap=config["parent_chunk_overlap"],
                child_chunk_size=config["child_chunk_size"],
                child_chunk_overlap=config["child_chunk_overlap"]
            )
            
            # 驗證參數是否正確設置
            assert splitter.parent_chunk_size == config["parent_chunk_size"]
            assert splitter.parent_chunk_overlap == config["parent_chunk_overlap"]
            assert splitter.child_chunk_size == config["child_chunk_size"]
            assert splitter.child_chunk_overlap == config["child_chunk_overlap"]
            
            # 驗證分割器是否正確初始化
            assert splitter.parent_text_splitter.chunk_size == config["parent_chunk_size"]
            assert splitter.parent_text_splitter.chunk_overlap == config["parent_chunk_overlap"]
            assert splitter.child_splitter.chunk_size == config["child_chunk_size"]
            assert splitter.child_splitter.chunk_overlap == config["child_chunk_overlap"]
            
            logger.info(f"  ✓ {config['name']} 配置正確")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 參數驗證測試失敗: {e}")
        return False


def main():
    """主測試程式"""
    logger.info("開始 parent_chunk_overlap 參數測試...")
    
    tests = [
        ("參數測試", test_parent_overlap_parameter),
        ("功能測試", test_parent_overlap_functionality),
        ("參數驗證", test_parameter_validation)
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
        logger.info("🎉 所有測試通過！parent_chunk_overlap 參數已準備就緒。")
    else:
        logger.warning("⚠ 部分測試失敗，請檢查相關功能。")


if __name__ == "__main__":
    main()
