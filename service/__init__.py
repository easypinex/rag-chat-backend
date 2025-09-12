"""
Service Package

提供各種服務功能的套件
"""

# Import converters that exist
try:
    from .markdown_markitdown import MarkitdownConverter
except ImportError:
    MarkitdownConverter = None

try:
    from .markdown_marker import MarkerConverter
except ImportError:
    MarkerConverter = None

try:
    from .markdown_langchain import LangChainConverter
except ImportError:
    LangChainConverter = None

# Build __all__ list with available converters
__all__ = []
if MarkitdownConverter:
    __all__.append('MarkitdownConverter')
if MarkerConverter:
    __all__.append('MarkerConverter')
if LangChainConverter:
    __all__.append('LangChainConverter')

