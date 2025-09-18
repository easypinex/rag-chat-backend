"""
Chunk 模組

基於 LangChain 的 Markdown 分割服務，支援多種輸入格式和輸出選項。
"""

from .chunk_splitter import ChunkSplitter
from .excel_exporter import ExcelExporter
from .table_handler import TableHandler
from .markdown_normalizer import MarkdownNormalizer

__version__ = "1.0.0"
__author__ = "RAG Chat Backend Team"

__all__ = [
    'ChunkSplitter',
    'ExcelExporter', 
    'TableHandler',
    'MarkdownNormalizer'
]
