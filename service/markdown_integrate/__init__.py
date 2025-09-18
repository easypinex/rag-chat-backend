"""
統一 Markdown 轉換器模組

整合 Marker 和 Markitdown 轉換器，提供統一的接口和數據格式。

主要組件：
- UnifiedMarkdownConverter: 統一轉換器主類
- ConversionResult: 統一轉換結果
- PageInfo: 頁面信息
- TableInfo: 表格信息
- FormatRouter: 格式路由器
"""

from .unified_converter import UnifiedMarkdownConverter
from .data_models import ConversionResult, PageInfo, TableInfo, ConversionMetadata
from .format_router import FormatRouter

__version__ = "1.0.0"
__author__ = "RAG Chat Backend Team"

# 主要導出
__all__ = [
    'UnifiedMarkdownConverter',
    'ConversionResult', 
    'PageInfo',
    'TableInfo',
    'ConversionMetadata',
    'FormatRouter'
]
