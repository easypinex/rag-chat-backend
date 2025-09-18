"""
統一 Markdown 轉換器的數據模型

定義所有轉換器使用的統一數據結構，確保不同轉換器的結果格式一致。
"""

from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TableInfo:
    """表格資訊 - 與 marker 的 TableInfo 兼容"""
    table_id: str
    title: str
    content: str
    row_count: int
    column_count: int
    start_line: int
    end_line: int


@dataclass
class PageInfo:
    """頁面資訊 - 統一格式"""
    page_number: int
    title: Optional[str] = None  # 可能沒有標題
    content: str = ""
    content_length: int = 0
    block_count: int = 0
    block_types: Optional[Dict[str, int]] = None  # 可能沒有區塊類型信息
    tables: Optional[List[TableInfo]] = None  # 可能沒有表格
    table_count: int = 0
    
    def __post_init__(self):
        if self.block_types is None:
            self.block_types = {}
        if self.tables is None:
            self.tables = []
        if self.content_length == 0:
            self.content_length = len(self.content)


@dataclass
class ConversionMetadata:
    """轉換元數據"""
    file_name: str
    file_path: str
    file_type: str
    file_size: int
    total_pages: int
    total_tables: int
    total_content_length: int
    conversion_timestamp: float
    converter_used: str  # 'marker' 或 'markitdown'
    additional_info: Optional[Dict[str, Any]] = None  # 可能沒有額外信息
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}


@dataclass
class ConversionResult:
    """統一轉換結果"""
    content: str                    # 完整的 markdown 內容
    metadata: ConversionMetadata   # 元數據
    pages: Optional[List[PageInfo]] = None  # 可能沒有頁面信息
    output_path: Optional[str] = None  # 如果保存到檔案，記錄路徑
    
    def __post_init__(self):
        if self.pages is None:
            self.pages = []
