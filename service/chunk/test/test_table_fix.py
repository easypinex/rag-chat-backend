"""
測試表格欄位數量修正

驗證正規化器能正確保持表格的欄位數量。
"""

import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk import MarkdownNormalizer
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_table_column_count():
    """測試表格欄位數量保持"""
    logger.info("=== 測試表格欄位數量保持 ===")
    
    # 測試表格（8個欄位）
    test_table = """# 附表三:保單價值準備金比率表  

|保險年齡|30歲以下|31歲至40歲|41歲至50歲|51歲至60歲|61歲至70歲|71歲至90歲|91歲以上|
|---|---|---|---|---|---|---|---|
|比率|190%|160%|140%|120%|110%|102%|100%|"""
    
    logger.info("原始表格:")
    logger.info(test_table)
    
    # 計算原始欄位數量
    lines = test_table.strip().split('\n')
    header_line = [line for line in lines if line.startswith('|') and not line.startswith('|---')][0]
    original_columns = len([col for col in header_line.split('|') if col.strip()])
    logger.info(f"原始欄位數量: {original_columns}")
    
    # 正規化
    normalizer = MarkdownNormalizer()
    normalized_table = normalizer.normalize_text(test_table)
    
    logger.info("\n正規化後表格:")
    logger.info(normalized_table)
    
    # 計算正規化後欄位數量
    normalized_lines = normalized_table.strip().split('\n')
    normalized_header_line = [line for line in normalized_lines if line.startswith('|') and not line.startswith('|---')][0]
    normalized_columns = len([col for col in normalized_header_line.split('|') if col.strip()])
    logger.info(f"正規化後欄位數量: {normalized_columns}")
    
    # 驗證
    if original_columns == normalized_columns:
        logger.info("✅ 欄位數量保持一致")
    else:
        logger.error(f"❌ 欄位數量不一致: {original_columns} -> {normalized_columns}")
    
    # 檢查分隔符行
    separator_lines = [line for line in normalized_lines if line.startswith('|---')]
    if separator_lines:
        separator_line = separator_lines[0]
        separator_columns = len([col for col in separator_line.split('|') if col.strip()])
        logger.info(f"分隔符欄位數量: {separator_columns}")
        
        if separator_columns == normalized_columns:
            logger.info("✅ 分隔符欄位數量與標題一致")
        else:
            logger.error(f"❌ 分隔符欄位數量不一致: {separator_columns} vs {normalized_columns}")


def test_various_table_sizes():
    """測試不同大小的表格"""
    logger.info("=== 測試不同大小的表格 ===")
    
    test_cases = [
        {
            "name": "3欄位表格",
            "table": """|A|B|C|
|---|---|---|
|1|2|3|"""
        },
        {
            "name": "5欄位表格", 
            "table": """|A|B|C|D|E|
|---|---|---|---|---|
|1|2|3|4|5|"""
        },
        {
            "name": "8欄位表格",
            "table": """|A|B|C|D|E|F|G|H|
|---|---|---|---|---|---|---|---|
|1|2|3|4|5|6|7|8|"""
        }
    ]
    
    normalizer = MarkdownNormalizer()
    
    for test_case in test_cases:
        logger.info(f"\n測試 {test_case['name']}:")
        
        # 計算原始欄位數量
        lines = test_case['table'].strip().split('\n')
        header_line = [line for line in lines if line.startswith('|') and not line.startswith('|---')][0]
        original_columns = len([col for col in header_line.split('|') if col.strip()])
        
        # 正規化
        normalized = normalizer.normalize_text(test_case['table'])
        
        # 計算正規化後欄位數量
        normalized_lines = normalized.strip().split('\n')
        normalized_header_line = [line for line in normalized_lines if line.startswith('|') and not line.startswith('|---')][0]
        normalized_columns = len([col for col in normalized_header_line.split('|') if col.strip()])
        
        logger.info(f"原始: {original_columns} 欄位")
        logger.info(f"正規化後: {normalized_columns} 欄位")
        
        if original_columns == normalized_columns:
            logger.info("✅ 通過")
        else:
            logger.error("❌ 失敗")


if __name__ == "__main__":
    test_table_column_count()
    test_various_table_sizes()
    logger.info("=== 測試完成 ===")
