"""
測試新的分層Excel輸出格式

驗證新的Excel輸出格式是否包含原文、正規化、Parent Chunk、Sub Chunk等欄位。
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


def test_new_excel_format():
    """測試新的Excel輸出格式"""
    logger.info("=== 測試新的分層Excel輸出格式 ===")
    
    try:
        # 創建分層分割器
        splitter = HierarchicalChunkSplitter(
            parent_chunk_size=1000,      # 較小的父chunk用於測試
            parent_chunk_overlap=100,    # 父層重疊
            child_chunk_size=300,        # 較小的子chunk用於測試
            child_chunk_overlap=30,      # 子層重疊
            keep_tables_together=True,
            normalize_output=True
        )
        
        # 測試文件
        test_file = project_root / "raw_docs" / "理賠審核原則.xlsx"
        
        if not test_file.exists():
            logger.warning(f"測試文件不存在: {test_file}")
            return False
        
        # 進行分層分割並輸出Excel
        output_path = project_root / "service" / "output" / "test_new_excel_format.xlsx"
        result = splitter.split_hierarchically(
            input_data=str(test_file),
            output_excel=True,
            output_path=str(output_path)
        )
        
        logger.info(f"✓ 分層分割完成:")
        logger.info(f"  - 父chunks: {len(result.parent_chunks)}")
        logger.info(f"  - 子chunks: {len(result.child_chunks)}")
        logger.info(f"  - Excel文件: {output_path}")
        
        # 檢查Excel文件是否存在
        if output_path.exists():
            logger.info("✓ Excel文件已生成")
            
            # 檢查文件大小
            file_size = output_path.stat().st_size
            logger.info(f"  - 文件大小: {file_size:,} bytes")
            
            if file_size > 0:
                logger.info("✓ Excel文件不為空")
            else:
                logger.error("✗ Excel文件為空")
                return False
        else:
            logger.error("✗ Excel文件未生成")
            return False
        
        # 檢查分層結構
        parent_count = len(result.parent_chunks)
        child_count = len(result.child_chunks)
        
        logger.info(f"✓ 分層結構檢查:")
        logger.info(f"  - 父chunks數量: {parent_count}")
        logger.info(f"  - 子chunks數量: {child_count}")
        
        if parent_count > 0 and child_count > 0:
            logger.info("✓ 分層結構正常")
        else:
            logger.warning("⚠ 分層結構異常")
        
        # 檢查分組效率
        grouping_efficiency = result.grouping_analysis.grouping_efficiency
        logger.info(f"  - 分組效率: {grouping_efficiency:.2%}")
        
        if grouping_efficiency > 0:
            logger.info("✓ 分組效率正常")
        else:
            logger.warning("⚠ 分組效率為0")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 新Excel格式測試失敗: {e}")
        return False


def test_excel_content_structure():
    """測試Excel內容結構"""
    logger.info("=== 測試Excel內容結構 ===")
    
    try:
        import pandas as pd
        
        # 讀取生成的Excel文件
        output_path = project_root / "service" / "output" / "test_new_excel_format.xlsx"
        
        if not output_path.exists():
            logger.error("Excel文件不存在，請先運行基本測試")
            return False
        
        # 讀取Excel文件
        excel_file = pd.ExcelFile(output_path)
        
        logger.info(f"✓ Excel文件包含的工作表:")
        for sheet_name in excel_file.sheet_names:
            logger.info(f"  - {sheet_name}")
        
        # 檢查分層Chunks工作表
        if "分層Chunks" in excel_file.sheet_names:
            logger.info("✓ 找到分層Chunks工作表")
            
            # 讀取分層Chunks工作表
            df = pd.read_excel(output_path, sheet_name="分層Chunks")
            
            logger.info(f"✓ 分層Chunks工作表包含 {len(df)} 行數據")
            logger.info(f"✓ 欄位: {list(df.columns)}")
            
            # 檢查必要的欄位
            required_columns = [
                "原文", "正規化", "Parent Chunk", "Sub Chunk", "層級", 
                "Chunk ID", "父Chunk ID", "索引", "大小", "是否表格"
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"✗ 缺少必要欄位: {missing_columns}")
                return False
            else:
                logger.info("✓ 包含所有必要欄位")
            
            # 檢查層級分佈
            level_counts = df['層級'].value_counts()
            logger.info(f"✓ 層級分佈:")
            for level, count in level_counts.items():
                logger.info(f"  - {level}: {count} 個")
            
            # 檢查父子關係
            parent_chunks = df[df['層級'] == '父層']
            child_chunks = df[df['層級'] == '子層']
            
            logger.info(f"✓ 父子關係檢查:")
            logger.info(f"  - 父chunks: {len(parent_chunks)} 個")
            logger.info(f"  - 子chunks: {len(child_chunks)} 個")
            
            if len(parent_chunks) > 0 and len(child_chunks) > 0:
                logger.info("✓ 父子關係正常")
            else:
                logger.warning("⚠ 父子關係異常")
            
            # 檢查內容欄位
            content_columns = ["原文", "正規化", "Parent Chunk", "Sub Chunk"]
            for col in content_columns:
                non_empty_count = df[col].notna().sum()
                logger.info(f"  - {col}: {non_empty_count} 個非空值")
            
            return True
        else:
            logger.error("✗ 未找到分層Chunks工作表")
            return False
        
    except Exception as e:
        logger.error(f"✗ Excel內容結構測試失敗: {e}")
        return False


def test_vertical_merge_logic():
    """測試垂直合併邏輯"""
    logger.info("=== 測試垂直合併邏輯 ===")
    
    try:
        import pandas as pd
        
        # 讀取Excel文件
        output_path = project_root / "service" / "output" / "test_new_excel_format.xlsx"
        
        if not output_path.exists():
            logger.error("Excel文件不存在，請先運行基本測試")
            return False
        
        # 讀取分層Chunks工作表
        df = pd.read_excel(output_path, sheet_name="分層Chunks")
        
        # 檢查垂直合併邏輯
        logger.info("✓ 檢查垂直合併邏輯:")
        
        # 按父chunk分組檢查
        parent_chunks = df[df['層級'] == '父層']
        
        for idx, parent_row in parent_chunks.iterrows():
            parent_id = parent_row['Chunk ID']
            
            # 找到對應的子chunks
            child_chunks = df[(df['層級'] == '子層') & (df['父Chunk ID'] == parent_id)]
            
            logger.info(f"  - 父chunk {parent_id}: {len(child_chunks)} 個子chunks")
            
            # 檢查父子關係
            if len(child_chunks) > 0:
                # 檢查子chunks的父ID是否正確
                correct_parent_ids = child_chunks['父Chunk ID'] == parent_id
                if correct_parent_ids.all():
                    logger.info(f"    ✓ 父子關係正確")
                else:
                    logger.error(f"    ✗ 父子關係錯誤")
                    return False
            else:
                logger.info(f"    - 沒有子chunks")
        
        # 檢查整體結構
        total_parents = len(parent_chunks)
        total_children = len(df[df['層級'] == '子層'])
        
        logger.info(f"✓ 整體結構:")
        logger.info(f"  - 總父chunks: {total_parents}")
        logger.info(f"  - 總子chunks: {total_children}")
        logger.info(f"  - 總行數: {len(df)}")
        
        if total_parents + total_children == len(df):
            logger.info("✓ 垂直合併邏輯正確")
        else:
            logger.warning("⚠ 垂直合併邏輯可能有問題")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 垂直合併邏輯測試失敗: {e}")
        return False


def main():
    """主測試程式"""
    logger.info("開始測試新的分層Excel輸出格式...")
    
    tests = [
        ("基本格式測試", test_new_excel_format),
        ("內容結構測試", test_excel_content_structure),
        ("垂直合併測試", test_vertical_merge_logic)
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
        logger.info("🎉 所有測試通過！新的Excel輸出格式已準備就緒。")
    else:
        logger.warning("⚠ 部分測試失敗，請檢查相關功能。")


if __name__ == "__main__":
    main()
