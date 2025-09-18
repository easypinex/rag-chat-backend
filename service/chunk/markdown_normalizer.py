"""
Markdown 正規化器

清理和正規化 Markdown 內容，特別針對表格進行優化，
移除多餘的空格、符號和 HTML 標籤，使其更適合 LLM 處理。
"""

import re
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)


class MarkdownNormalizer:
    """Markdown 正規化器"""
    
    def __init__(self, 
                 clean_tables: bool = True,
                 remove_extra_spaces: bool = True,
                 remove_html_tags: bool = True,
                 normalize_line_breaks: bool = True):
        """
        初始化正規化器
        
        Args:
            clean_tables: 是否清理表格格式
            remove_extra_spaces: 是否移除多餘空格
            remove_html_tags: 是否移除 HTML 標籤
            normalize_line_breaks: 是否正規化換行符
        """
        self.clean_tables = clean_tables
        self.remove_extra_spaces = remove_extra_spaces
        self.remove_html_tags = remove_html_tags
        self.normalize_line_breaks = normalize_line_breaks
        
        # 編譯正則表達式以提高性能
        self._compile_patterns()
        
        logger.info("MarkdownNormalizer initialized")
    
    def _compile_patterns(self):
        """編譯正則表達式模式"""
        # HTML 標籤模式
        self.html_tag_pattern = re.compile(r'<[^>]+>')
        
        # 多餘空格模式
        self.extra_spaces_pattern = re.compile(r'[ \t]+')
        
        # 多餘換行模式
        self.extra_newlines_pattern = re.compile(r'\n{3,}')
        
        # 表格分隔符模式（多餘的 - 符號）
        self.table_separator_pattern = re.compile(r'\|[\s\-]+\|')
        
        # 表格行尾空格
        self.table_trailing_spaces_pattern = re.compile(r'[ \t]+\|')
        
        # 表格行首空格
        self.table_leading_spaces_pattern = re.compile(r'\|[ \t]+')
        
        # 連續的 | 符號
        self.consecutive_pipes_pattern = re.compile(r'\|{2,}')
    
    def normalize_document(self, document: Document) -> Document:
        """
        正規化單個文檔
        
        Args:
            document: LangChain Document 對象
            
        Returns:
            Document: 正規化後的文檔
        """
        original_content = document.page_content
        normalized_content = self.normalize_text(original_content)
        
        # 創建新的文檔對象
        normalized_doc = Document(
            page_content=normalized_content,
            metadata=document.metadata.copy()
        )
        
        # 添加正規化標記
        normalized_doc.metadata['normalized'] = True
        normalized_doc.metadata['original_length'] = len(original_content)
        normalized_doc.metadata['normalized_length'] = len(normalized_content)
        
        return normalized_doc
    
    def normalize_documents(self, documents: List[Document]) -> List[Document]:
        """
        正規化多個文檔
        
        Args:
            documents: 文檔列表
            
        Returns:
            List[Document]: 正規化後的文檔列表
        """
        normalized_docs = []
        
        for doc in documents:
            normalized_doc = self.normalize_document(doc)
            normalized_docs.append(normalized_doc)
        
        logger.info(f"Normalized {len(documents)} documents")
        return normalized_docs
    
    def normalize_text(self, text: str) -> str:
        """
        正規化文本內容
        
        Args:
            text: 原始文本
            
        Returns:
            str: 正規化後的文本
        """
        if not text:
            return text
        
        normalized = text
        
        # 1. 移除 HTML 標籤
        if self.remove_html_tags:
            normalized = self._remove_html_tags(normalized)
        
        # 2. 正規化換行符
        if self.normalize_line_breaks:
            normalized = self._normalize_line_breaks(normalized)
        
        # 3. 清理表格格式
        if self.clean_tables:
            normalized = self._clean_tables(normalized)
        
        # 4. 移除多餘空格
        if self.remove_extra_spaces:
            normalized = self._remove_extra_spaces(normalized)
        
        # 5. 最終清理
        normalized = self._final_cleanup(normalized)
        
        return normalized
    
    def _remove_html_tags(self, text: str) -> str:
        """移除 HTML 標籤"""
        # 移除常見的 HTML 標籤
        text = self.html_tag_pattern.sub('', text)
        
        # 特別處理 <br> 標籤
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        
        return text
    
    def _normalize_line_breaks(self, text: str) -> str:
        """正規化換行符"""
        # 統一換行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 移除多餘的換行符（保留最多兩個連續換行）
        text = self.extra_newlines_pattern.sub('\n\n', text)
        
        return text
    
    def _clean_tables(self, text: str) -> str:
        """清理表格格式"""
        lines = text.split('\n')
        cleaned_lines = []
        in_table = False
        
        for line in lines:
            # 檢查是否為表格行
            if '|' in line:
                in_table = True
                cleaned_line = self._clean_table_line(line)
                cleaned_lines.append(cleaned_line)
            else:
                if in_table:
                    # 表格結束，檢查是否需要添加空行
                    if line.strip() and not line.startswith('#'):
                        cleaned_lines.append('')
                    in_table = False
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _clean_table_line(self, line: str) -> str:
        """清理單個表格行"""
        # 移除行首行尾空格
        line = line.strip()
        
        # 移除多餘的空格
        line = self.extra_spaces_pattern.sub(' ', line)
        
        # 清理表格分隔符（移除多餘的 - 符號）
        if re.match(r'\|[\s\-]+\|', line):
            # 這是表格分隔符行，簡化為標準格式
            parts = line.split('|')
            if len(parts) >= 3:
                # 保持原有的欄位數量，只簡化分隔符
                simplified_parts = [''] + ['---'] * (len(parts) - 2) + ['']
                line = '|'.join(simplified_parts)
        
        # 清理表格單元格內容
        parts = line.split('|')
        cleaned_parts = []
        
        for part in parts:
            # 移除前後空格
            cleaned_part = part.strip()
            # 移除內部多餘空格
            cleaned_part = self.extra_spaces_pattern.sub(' ', cleaned_part)
            cleaned_parts.append(cleaned_part)
        
        return '|'.join(cleaned_parts)
    
    def _remove_extra_spaces(self, text: str) -> str:
        """移除多餘空格"""
        # 移除行尾空格
        lines = text.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        
        # 移除多餘的空白字符
        text = '\n'.join(cleaned_lines)
        text = self.extra_spaces_pattern.sub(' ', text)
        
        return text
    
    def _final_cleanup(self, text: str) -> str:
        """最終清理"""
        # 移除開頭和結尾的空白
        text = text.strip()
        
        # 移除多餘的空行
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # 確保以單個換行符結尾
        if text and not text.endswith('\n'):
            text += '\n'
        
        return text
    
    def get_normalization_stats(self, original_text: str, normalized_text: str) -> Dict[str, Any]:
        """獲取正規化統計信息"""
        return {
            'original_length': len(original_text),
            'normalized_length': len(normalized_text),
            'length_reduction': len(original_text) - len(normalized_text),
            'reduction_percentage': round((len(original_text) - len(normalized_text)) / len(original_text) * 100, 2) if original_text else 0,
            'original_lines': len(original_text.split('\n')),
            'normalized_lines': len(normalized_text.split('\n')),
            'line_reduction': len(original_text.split('\n')) - len(normalized_text.split('\n'))
        }
    
    def normalize_chunks_with_stats(self, chunks: List[Document]) -> tuple[List[Document], Dict[str, Any]]:
        """
        正規化 chunks 並返回統計信息
        
        Args:
            chunks: 原始 chunks 列表
            
        Returns:
            tuple: (正規化後的 chunks, 統計信息)
        """
        normalized_chunks = self.normalize_documents(chunks)
        
        # 計算統計信息
        total_original_length = sum(len(chunk.page_content) for chunk in chunks)
        total_normalized_length = sum(len(chunk.page_content) for chunk in normalized_chunks)
        
        stats = {
            'total_chunks': len(chunks),
            'total_original_length': total_original_length,
            'total_normalized_length': total_normalized_length,
            'total_reduction': total_original_length - total_normalized_length,
            'average_reduction_per_chunk': (total_original_length - total_normalized_length) / len(chunks) if chunks else 0,
            'reduction_percentage': round((total_original_length - total_normalized_length) / total_original_length * 100, 2) if total_original_length else 0
        }
        
        return normalized_chunks, stats
