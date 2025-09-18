"""
表格處理器

專門處理 Markdown 表格的檢測、分割和重組功能。
"""

import re
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)


class TableHandler:
    """表格處理器"""
    
    def __init__(self):
        """初始化表格處理器"""
        self.table_pattern = r'(\|.*\|(?:\n\|.*\|)*)'
        self.table_start_marker = "<!-- TABLE_START -->"
        self.table_end_marker = "<!-- TABLE_END -->"
    
    def detect_tables(self, content: str) -> List[Dict[str, Any]]:
        """
        檢測內容中的表格
        
        Args:
            content: Markdown 內容
            
        Returns:
            List[Dict]: 表格信息列表
        """
        tables = []
        matches = re.finditer(self.table_pattern, content, re.MULTILINE)
        
        for i, match in enumerate(matches):
            table_content = match.group(1)
            start_pos = match.start()
            end_pos = match.end()
            
            # 分析表格結構
            table_info = self._analyze_table_structure(table_content)
            
            tables.append({
                'index': i,
                'content': table_content,
                'start_pos': start_pos,
                'end_pos': end_pos,
                'rows': table_info['rows'],
                'columns': table_info['columns'],
                'has_header': table_info['has_header']
            })
        
        logger.info(f"Detected {len(tables)} tables in content")
        return tables
    
    def _analyze_table_structure(self, table_content: str) -> Dict[str, Any]:
        """分析表格結構"""
        lines = table_content.strip().split('\n')
        rows = len(lines)
        
        # 計算列數（基於第一行）
        if rows > 0:
            first_line = lines[0]
            columns = len([cell for cell in first_line.split('|') if cell.strip()])
        else:
            columns = 0
        
        # 檢查是否有表頭（第二行通常是分隔符行）
        has_header = rows > 1 and '---' in lines[1] if rows > 1 else False
        
        return {
            'rows': rows,
            'columns': columns,
            'has_header': has_header
        }
    
    def mark_tables(self, content: str) -> str:
        """
        標記表格邊界
        
        Args:
            content: 原始 Markdown 內容
            
        Returns:
            str: 標記後的內容
        """
        def replace_table(match):
            table_content = match.group(1)
            return f"\n\n{self.table_start_marker}\n{table_content}\n{self.table_end_marker}\n\n"
        
        marked_content = re.sub(self.table_pattern, replace_table, content, flags=re.MULTILINE)
        logger.info("Tables marked in content")
        return marked_content
    
    def extract_table_chunks(self, chunks: List[Document]) -> Tuple[List[Document], List[Document]]:
        """
        從 chunks 中分離表格和一般內容
        
        Args:
            chunks: 文檔 chunks 列表
            
        Returns:
            Tuple[List[Document], List[Document]]: (表格 chunks, 一般 chunks)
        """
        table_chunks = []
        regular_chunks = []
        
        for chunk in chunks:
            if self._is_table_chunk(chunk):
                table_chunks.append(chunk)
            else:
                regular_chunks.append(chunk)
        
        logger.info(f"Separated {len(table_chunks)} table chunks and {len(regular_chunks)} regular chunks")
        return table_chunks, regular_chunks
    
    def _is_table_chunk(self, chunk: Document) -> bool:
        """檢查 chunk 是否包含表格"""
        content = chunk.page_content
        
        # 檢查是否包含表格標記
        if self.table_start_marker in content or self.table_end_marker in content:
            return True
        
        # 檢查是否包含表格模式
        if re.search(self.table_pattern, content, re.MULTILINE):
            return True
        
        # 檢查元數據
        if chunk.metadata.get('is_table', False):
            return True
        
        return False
    
    def merge_table_chunks(self, table_chunks: List[Document]) -> List[Document]:
        """
        合併相關的表格 chunks
        
        Args:
            table_chunks: 表格 chunks 列表
            
        Returns:
            List[Document]: 合併後的表格 chunks
        """
        if not table_chunks:
            return []
        
        merged_chunks = []
        current_table_group = []
        
        for chunk in table_chunks:
            if self.table_start_marker in chunk.page_content:
                # 開始新的表格組
                if current_table_group:
                    merged_chunks.append(self._merge_table_group(current_table_group))
                current_table_group = [chunk]
            elif self.table_end_marker in chunk.page_content:
                # 結束當前表格組
                current_table_group.append(chunk)
                merged_chunks.append(self._merge_table_group(current_table_group))
                current_table_group = []
            else:
                # 表格中間內容
                current_table_group.append(chunk)
        
        # 處理最後一組
        if current_table_group:
            merged_chunks.append(self._merge_table_group(current_table_group))
        
        logger.info(f"Merged {len(table_chunks)} table chunks into {len(merged_chunks)} merged chunks")
        return merged_chunks
    
    def _merge_table_group(self, table_group: List[Document]) -> Document:
        """合併表格組"""
        if not table_group:
            return Document(page_content="", metadata={})
        
        # 合併內容
        contents = []
        metadata = {}
        
        for chunk in table_group:
            # 清理表格標記
            clean_content = chunk.page_content.replace(self.table_start_marker, "").replace(self.table_end_marker, "")
            contents.append(clean_content.strip())
            
            # 合併元數據
            metadata.update(chunk.metadata)
        
        merged_content = "\n".join(contents)
        metadata['is_table'] = True
        metadata['table_chunks_merged'] = len(table_group)
        
        return Document(page_content=merged_content, metadata=metadata)
    
    def clean_table_markers(self, content: str) -> str:
        """清理表格標記"""
        content = content.replace(self.table_start_marker, "")
        content = content.replace(self.table_end_marker, "")
        return content.strip()
    
    def get_table_statistics(self, chunks: List[Document]) -> Dict[str, Any]:
        """獲取表格統計信息"""
        table_chunks = [chunk for chunk in chunks if self._is_table_chunk(chunk)]
        regular_chunks = [chunk for chunk in chunks if not self._is_table_chunk(chunk)]
        
        total_tables = len(table_chunks)
        total_regular = len(regular_chunks)
        
        # 計算表格相關統計
        table_lengths = [len(chunk.page_content) for chunk in table_chunks]
        avg_table_length = sum(table_lengths) / len(table_lengths) if table_lengths else 0
        
        return {
            'total_chunks': len(chunks),
            'table_chunks': total_tables,
            'regular_chunks': total_regular,
            'table_ratio': total_tables / len(chunks) if chunks else 0,
            'avg_table_length': round(avg_table_length, 2),
            'max_table_length': max(table_lengths) if table_lengths else 0,
            'min_table_length': min(table_lengths) if table_lengths else 0
        }
