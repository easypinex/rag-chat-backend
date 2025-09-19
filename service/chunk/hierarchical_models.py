"""
分層分割資料模型

定義分層分割過程中使用的資料結構，以清楚表達中間傳遞的資料物件。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from langchain_core.documents import Document
from datetime import datetime


@dataclass
class ParentChunk:
    """父層Chunk資料模型"""
    document: Document
    chunk_id: str
    parent_index: int
    size: int
    has_tables: bool = False
    table_count: int = 0
    header_level: Optional[str] = None
    header_text: Optional[str] = None
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化後處理"""
        self.size = len(self.document.page_content)
        self.metadata = self.document.metadata.copy()
        
        # 檢查是否包含表格
        self.has_tables = self._detect_tables()
        if self.has_tables:
            self.table_count = self._count_tables()
        
        # 提取標題信息
        self._extract_header_info()
    
    def _detect_tables(self) -> bool:
        """檢測是否包含表格"""
        content = self.document.page_content
        return "<!-- TABLE_START -->" in content or "|" in content
    
    def _count_tables(self) -> int:
        """計算表格數量"""
        content = self.document.page_content
        return content.count("<!-- TABLE_START -->")
    
    def _extract_header_info(self):
        """提取標題信息"""
        metadata = self.document.metadata
        
        # 按優先級查找標題
        for level in ['Header 1', 'Header 2', 'Header 3', 'Header 4']:
            if level in metadata and metadata[level]:
                self.header_level = level
                self.header_text = metadata[level]
                break
        
        # 提取頁碼
        self.page_number = metadata.get('page_number')


@dataclass
class ChildChunk:
    """子層Chunk資料模型"""
    document: Document
    chunk_id: str
    parent_chunk_id: str
    child_index: int
    size: int
    is_table_chunk: bool = False
    table_info: Optional[Dict[str, Any]] = None
    parent_header: Optional[str] = None
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化後處理"""
        self.size = len(self.document.page_content)
        self.metadata = self.document.metadata.copy()
        
        # 檢查是否為表格chunk
        self.is_table_chunk = self._detect_table_chunk()
        if self.is_table_chunk:
            self.table_info = self._analyze_table_info()
        
        # 提取父層標題
        self.parent_header = self._extract_parent_header()
        
        # 提取頁碼
        self.page_number = self.metadata.get('page_number')
    
    def _detect_table_chunk(self) -> bool:
        """檢測是否為表格chunk"""
        content = self.document.page_content
        return "<!-- TABLE_START -->" in content or "|" in content
    
    def _analyze_table_info(self) -> Dict[str, Any]:
        """分析表格信息"""
        content = self.document.page_content
        
        # 計算表格行數
        lines = content.split('\n')
        table_lines = [line for line in lines if '|' in line and line.strip()]
        
        return {
            'row_count': len(table_lines),
            'has_header': any('---' in line for line in lines),
            'table_markers': content.count("<!-- TABLE_START -->")
        }
    
    def _extract_parent_header(self) -> Optional[str]:
        """提取父層標題"""
        metadata = self.document.metadata
        
        # 按優先級查找標題
        for level in ['Header 1', 'Header 2', 'Header 3', 'Header 4']:
            if level in metadata and metadata[level]:
                return metadata[level]
        
        return None


@dataclass
class GroupingAnalysis:
    """分組分析資料模型"""
    total_parent_chunks: int
    total_child_chunks: int
    avg_children_per_parent: float
    parent_size_stats: Dict[str, float]
    child_size_stats: Dict[str, float]
    table_handling_stats: Dict[str, Any]
    grouping_efficiency: float
    size_distribution: Dict[str, int]
    analysis_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """計算統計數據"""
        self.avg_children_per_parent = (
            self.total_child_chunks / self.total_parent_chunks 
            if self.total_parent_chunks > 0 else 0
        )


@dataclass
class HierarchicalSplitResult:
    """分層分割結果資料模型"""
    parent_chunks: List[ParentChunk]
    child_chunks: List[ChildChunk]
    grouping_analysis: GroupingAnalysis
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_chunk_by_id(self, chunk_id: str, is_parent: bool = True) -> Optional[ParentChunk | ChildChunk]:
        """根據ID獲取chunk"""
        if is_parent:
            for chunk in self.parent_chunks:
                if chunk.chunk_id == chunk_id:
                    return chunk
        else:
            for chunk in self.child_chunks:
                if chunk.chunk_id == chunk_id:
                    return chunk
        return None
    
    def get_children_of_parent(self, parent_chunk_id: str) -> List[ChildChunk]:
        """獲取指定父chunk的所有子chunk"""
        return [child for child in self.child_chunks if child.parent_chunk_id == parent_chunk_id]
    
    def get_parent_of_child(self, child_chunk_id: str) -> Optional[ParentChunk]:
        """獲取指定子chunk的父chunk"""
        child_chunk = self.get_chunk_by_id(child_chunk_id, is_parent=False)
        if child_chunk:
            return self.get_chunk_by_id(child_chunk.parent_chunk_id, is_parent=True)
        return None


@dataclass
class SizeDistribution:
    """大小分佈統計"""
    min_size: int
    max_size: int
    avg_size: float
    median_size: float
    size_ranges: Dict[str, int]  # 例如: {"0-200": 5, "200-400": 10, "400-600": 3}
    
    @classmethod
    def from_sizes(cls, sizes: List[int], ranges: List[tuple] = None) -> 'SizeDistribution':
        """從大小列表創建分佈統計"""
        if not sizes:
            return cls(0, 0, 0, 0, {})
        
        sizes_sorted = sorted(sizes)
        min_size = min(sizes)
        max_size = max(sizes)
        avg_size = sum(sizes) / len(sizes)
        median_size = sizes_sorted[len(sizes_sorted) // 2]
        
        # 預設範圍
        if ranges is None:
            ranges = [(0, 200), (200, 400), (400, 600), (600, 800), (800, 1000), (1000, float('inf'))]
        
        size_ranges = {}
        for range_min, range_max in ranges:
            range_key = f"{range_min}-{range_max if range_max != float('inf') else '∞'}"
            count = sum(1 for size in sizes if range_min <= size < range_max)
            size_ranges[range_key] = count
        
        return cls(min_size, max_size, avg_size, median_size, size_ranges)


@dataclass
class TableHandlingStats:
    """表格處理統計"""
    total_table_chunks: int
    total_regular_chunks: int
    table_chunk_ratio: float
    avg_table_size: float
    largest_table_size: int
    table_fragmentation_count: int  # 被分割的表格數量
    
    @classmethod
    def from_chunks(cls, chunks: List[ChildChunk]) -> 'TableHandlingStats':
        """從chunk列表創建表格統計"""
        table_chunks = [chunk for chunk in chunks if chunk.is_table_chunk]
        regular_chunks = [chunk for chunk in chunks if not chunk.is_table_chunk]
        
        total_chunks = len(chunks)
        table_chunk_ratio = len(table_chunks) / total_chunks if total_chunks > 0 else 0
        
        table_sizes = [chunk.size for chunk in table_chunks]
        avg_table_size = sum(table_sizes) / len(table_sizes) if table_sizes else 0
        largest_table_size = max(table_sizes) if table_sizes else 0
        
        # 計算表格碎片化（同一父chunk中的表格被分割的次數）
        parent_table_counts = {}
        for chunk in table_chunks:
            if chunk.parent_chunk_id not in parent_table_counts:
                parent_table_counts[chunk.parent_chunk_id] = 0
            parent_table_counts[chunk.parent_chunk_id] += 1
        
        table_fragmentation_count = sum(1 for count in parent_table_counts.values() if count > 1)
        
        return cls(
            total_table_chunks=len(table_chunks),
            total_regular_chunks=len(regular_chunks),
            table_chunk_ratio=table_chunk_ratio,
            avg_table_size=avg_table_size,
            largest_table_size=largest_table_size,
            table_fragmentation_count=table_fragmentation_count
        )
