"""
分層分割範例使用

展示如何使用 HierarchicalChunkSplitter 進行分層分割，
並分析分組情況。
"""

import sys
import logging
from pathlib import Path

# 添加路徑到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk.hierarchical_splitter import HierarchicalChunkSplitter
from service.chunk.analysis.analysis import DocumentAnalyzer

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_hierarchical_splitting():
    """範例：分層分割單個文件"""
    logger.info("=== 分層分割範例 ===")
    
    # 創建分層分割器
    splitter = HierarchicalChunkSplitter(
        parent_chunk_size=2000,      # 父chunk大小
        child_chunk_size=350,         # 子chunk大小 (目標250-400字)
        child_chunk_overlap=50,      # 子chunk重疊
        keep_tables_together=True,   # 保持表格完整性
        normalize_output=True        # 正規化輸出
    )
    
    # 假設有一個測試文件
    test_file = project_root / "raw_docs" / "理賠審核原則.xlsx"
    
    if not test_file.exists():
        logger.warning(f"測試文件不存在: {test_file}")
        return
    
    try:
        # 進行分層分割
        result = splitter.split_hierarchically(
            input_data=str(test_file),
            output_excel=True,
            output_path=str(project_root / "service" / "output" / "hierarchical_test.xlsx")
        )
        
        # 顯示結果
        logger.info(f"分割完成:")
        logger.info(f"- 父chunks數量: {len(result.parent_chunks)}")
        logger.info(f"- 子chunks數量: {len(result.child_chunks)}")
        logger.info(f"- 平均每父chunk的子chunks數: {result.grouping_analysis.avg_children_per_parent:.2f}")
        logger.info(f"- 分組效率: {result.grouping_analysis.grouping_efficiency:.2%}")
        
        # 顯示大小統計
        child_sizes = [chunk.size for chunk in result.child_chunks]
        logger.info(f"子chunk大小統計:")
        logger.info(f"- 最小: {min(child_sizes)}")
        logger.info(f"- 最大: {max(child_sizes)}")
        logger.info(f"- 平均: {sum(child_sizes) / len(child_sizes):.2f}")
        
        # 顯示表格處理統計
        table_stats = result.grouping_analysis.table_handling_stats
        logger.info(f"表格處理統計:")
        logger.info(f"- 表格chunks: {table_stats['total_table_chunks']}")
        logger.info(f"- 一般chunks: {table_stats['total_regular_chunks']}")
        logger.info(f"- 表格比例: {table_stats['table_chunk_ratio']:.2%}")
        
        return result
        
    except Exception as e:
        logger.error(f"分層分割失敗: {e}")
        return None


def example_analysis_comparison():
    """範例：比較傳統分割與分層分割"""
    logger.info("=== 分割方式比較範例 ===")
    
    # 創建分析器 - 傳統分割
    traditional_analyzer = DocumentAnalyzer(
        use_hierarchical=False,
        chunk_size=1000,
        chunk_overlap=200
    )
    
    # 創建分析器 - 分層分割
    hierarchical_analyzer = DocumentAnalyzer(
        use_hierarchical=True,
        chunk_size=2000,        # 父chunk大小
        chunk_overlap=200,      # 父chunk重疊
        child_chunk_size=350,   # 子chunk大小
        child_chunk_overlap=50  # 子chunk重疊
    )
    
    # 測試文件
    test_file = "理賠審核原則.xlsx"
    
    try:
        # 傳統分割
        logger.info("執行傳統分割...")
        traditional_result = traditional_analyzer.analyze_single_file(test_file)
        
        # 分層分割
        logger.info("執行分層分割...")
        hierarchical_result = hierarchical_analyzer.analyze_single_file(test_file)
        
        # 比較結果
        logger.info("=== 比較結果 ===")
        logger.info(f"傳統分割:")
        logger.info(f"- Chunks數量: {traditional_result['chunks_count']}")
        logger.info(f"- 平均大小: {traditional_result['statistics']['average_length']:.2f}")
        
        if hierarchical_result['hierarchical_info']:
            hierarchical_info = hierarchical_result['hierarchical_info']
            logger.info(f"分層分割:")
            logger.info(f"- 父chunks: {hierarchical_info['parent_chunks_count']}")
            logger.info(f"- 子chunks: {hierarchical_info['child_chunks_count']}")
            logger.info(f"- 子chunk平均大小: {hierarchical_info['grouping_analysis']['child_size_stats']['avg']:.2f}")
            logger.info(f"- 分組效率: {hierarchical_info['grouping_analysis']['grouping_efficiency']:.2%}")
        
        return {
            'traditional': traditional_result,
            'hierarchical': hierarchical_result
        }
        
    except Exception as e:
        logger.error(f"比較分析失敗: {e}")
        return None


def example_detailed_analysis():
    """範例：詳細分析分層分割結果"""
    logger.info("=== 詳細分析範例 ===")
    
    # 創建分層分割器
    splitter = HierarchicalChunkSplitter(
        parent_chunk_size=2000,
        child_chunk_size=350,
        child_chunk_overlap=50
    )
    
    test_file = project_root / "raw_docs" / "理賠審核原則.xlsx"
    
    if not test_file.exists():
        logger.warning(f"測試文件不存在: {test_file}")
        return
    
    try:
        # 進行分層分割
        result = splitter.split_hierarchically(
            input_data=str(test_file),
            output_excel=True,
            output_path=str(project_root / "service" / "output" / "detailed_analysis.xlsx")
        )
        
        # 詳細分析每個父chunk
        logger.info("=== 父chunks詳細分析 ===")
        for i, parent_chunk in enumerate(result.parent_chunks[:3], 1):  # 只顯示前3個
            logger.info(f"父chunk {i}:")
            logger.info(f"- ID: {parent_chunk.chunk_id}")
            logger.info(f"- 大小: {parent_chunk.size}")
            logger.info(f"- 包含表格: {parent_chunk.has_tables}")
            logger.info(f"- 標題: {parent_chunk.header_text or '無'}")
            
            # 找到對應的子chunks
            children = result.get_children_of_parent(parent_chunk.chunk_id)
            logger.info(f"- 子chunks數量: {len(children)}")
            
            for j, child in enumerate(children[:2], 1):  # 只顯示前2個子chunk
                logger.info(f"  子chunk {j}:")
                logger.info(f"  - ID: {child.chunk_id}")
                logger.info(f"  - 大小: {child.size}")
                logger.info(f"  - 是否表格: {child.is_table_chunk}")
                logger.info(f"  - 內容預覽: {child.document.page_content[:100]}...")
        
        # 分析大小分佈
        logger.info("=== 大小分佈分析 ===")
        child_sizes = [chunk.size for chunk in result.child_chunks]
        size_ranges = {
            "0-200": 0, "200-400": 0, "400-600": 0, 
            "600-800": 0, "800-1000": 0, "1000+": 0
        }
        
        for size in child_sizes:
            if size < 200:
                size_ranges["0-200"] += 1
            elif size < 400:
                size_ranges["200-400"] += 1
            elif size < 600:
                size_ranges["400-600"] += 1
            elif size < 800:
                size_ranges["600-800"] += 1
            elif size < 1000:
                size_ranges["800-1000"] += 1
            else:
                size_ranges["1000+"] += 1
        
        for range_name, count in size_ranges.items():
            percentage = (count / len(child_sizes)) * 100 if child_sizes else 0
            logger.info(f"- {range_name}字: {count}個 ({percentage:.1f}%)")
        
        return result
        
    except Exception as e:
        logger.error(f"詳細分析失敗: {e}")
        return None


def main():
    """主程式"""
    logger.info("開始分層分割範例...")
    
    # 範例1: 基本分層分割
    logger.info("\n" + "="*50)
    result1 = example_hierarchical_splitting()
    
    # 範例2: 分割方式比較
    logger.info("\n" + "="*50)
    result2 = example_analysis_comparison()
    
    # 範例3: 詳細分析
    logger.info("\n" + "="*50)
    result3 = example_detailed_analysis()
    
    logger.info("\n所有範例執行完成！")


if __name__ == "__main__":
    main()
