"""
Service Package

提供各種服務功能的套件
"""

# Import converters that exist
try:
    from .markdown_integrate.markitdown import MarkitdownConverter
except ImportError:
    MarkitdownConverter = None

try:
    from .markdown_integrate.marker import MarkerConverter
except ImportError:
    MarkerConverter = None

try:
    from .markdown_langchain import LangChainConverter
except ImportError:
    LangChainConverter = None

try:
    from .chunk import ChunkSplitter, ExcelExporter, TableHandler, MarkdownNormalizer
except ImportError:
    ChunkSplitter = None
    ExcelExporter = None
    TableHandler = None
    MarkdownNormalizer = None

# Build __all__ list with available converters and chunk tools
__all__ = []
if MarkitdownConverter:
    __all__.append('MarkitdownConverter')
if MarkerConverter:
    __all__.append('MarkerConverter')
if LangChainConverter:
    __all__.append('LangChainConverter')
if ChunkSplitter:
    __all__.append('ChunkSplitter')
if ExcelExporter:
    __all__.append('ExcelExporter')
if TableHandler:
    __all__.append('TableHandler')
if MarkdownNormalizer:
    __all__.append('MarkdownNormalizer')

