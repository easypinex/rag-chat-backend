"""
統一 Markdown 轉換器

整合 Marker 和 Markitdown 轉換器，提供統一的接口和數據格式。
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import time

from .data_models import ConversionResult, PageInfo, ConversionMetadata, TableInfo
from .format_router import FormatRouter

# 嘗試導入轉換器
try:
    from .marker.marker_converter import MarkerConverter, create_marker_converter
    MARKER_AVAILABLE = True
except ImportError:
    MARKER_AVAILABLE = False
    logging.warning("Marker converter not available")

try:
    from .markitdown.markitdown_converter import MarkitdownConverter
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False
    logging.warning("Markitdown converter not available")

logger = logging.getLogger(__name__)


class UnifiedMarkdownConverter:
    """統一的 Markdown 轉換器"""
    
    def __init__(self, 
                 marker_model_locations: Optional[Dict[str, str]] = None,
                 markitdown_input_dir: str = "raw_docs",
                 markitdown_output_dir: str = "service/markdown_integrate/markitdown/converted"):
        """
        初始化統一轉換器
        
        Args:
            marker_model_locations: Marker 模型位置配置
            markitdown_input_dir: Markitdown 輸入目錄
            markitdown_output_dir: Markitdown 輸出目錄
        """
        self.marker_converter: Optional[MarkerConverter] = None
        self.markitdown_converter: Optional[MarkitdownConverter] = None
        self._initialize_converters(marker_model_locations, markitdown_input_dir, markitdown_output_dir)
    
    def _initialize_converters(self, marker_model_locations, markitdown_input_dir, markitdown_output_dir):
        """初始化兩個轉換器"""
        # 初始化 Marker 轉換器
        if MARKER_AVAILABLE:
            try:
                self.marker_converter = create_marker_converter(marker_model_locations)
                logger.info("Marker converter initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Marker converter: {e}")
        else:
            logger.warning("Marker converter not available")
        
        # 初始化 Markitdown 轉換器
        if MARKITDOWN_AVAILABLE:
            try:
                self.markitdown_converter = MarkitdownConverter(markitdown_input_dir, markitdown_output_dir)
                logger.info("Markitdown converter initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Markitdown converter: {e}")
        else:
            logger.warning("Markitdown converter not available")
    
    def convert_file(self, 
                    file_path: str, 
                    output_path: Optional[str] = None,
                    save_to_file: bool = False) -> ConversionResult:
        """
        統一轉換接口
        
        Args:
            file_path: 輸入檔案路徑
            output_path: 輸出檔案路徑（僅當 save_to_file=True 時使用）
            save_to_file: 是否保存到檔案
            
        Returns:
            ConversionResult: 統一格式的轉換結果
            
        Raises:
            FileNotFoundError: 如果檔案不存在
            ValueError: 如果檔案格式不支援
            RuntimeError: 如果對應的轉換器不可用
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 決定使用哪個轉換器
        converter_name, file_type = FormatRouter.get_converter_info(str(file_path))
        
        logger.info(f"Converting {file_path.name} using {converter_name}")
        
        # 根據轉換器類型進行轉換
        if converter_name == 'marker':
            return self._convert_with_marker(file_path, output_path, save_to_file)
        elif converter_name == 'markitdown':
            return self._convert_with_markitdown(file_path, output_path, save_to_file)
        else:
            raise ValueError(f"Unknown converter: {converter_name}")
    
    def _convert_with_marker(self, file_path: Path, output_path: Optional[str], save_to_file: bool) -> ConversionResult:
        """使用 Marker 轉換"""
        if not self.marker_converter:
            raise RuntimeError("Marker converter not available")
        
        # 使用 Marker 的 marker_pages 方法獲取結構化數據
        marker_result = self.marker_converter.marker_pages(str(file_path))
        
        # 轉換為統一格式
        pages: List[PageInfo] = []
        total_tables: int = 0
        
        for page_data in marker_result['pages']:
            # 轉換 TableInfo
            tables: List[TableInfo] = []
            for table_data in page_data.get('tables', []):
                table = TableInfo(
                    table_id=table_data['table_id'],
                    title=table_data['title'],
                    content=table_data['content'],
                    row_count=table_data['row_count'],
                    column_count=table_data['column_count'],
                    start_line=table_data['start_line'],
                    end_line=table_data['end_line']
                )
                tables.append(table)
            
            page = PageInfo(
                page_number=page_data['page_number'],
                content=page_data['content'],
                content_length=page_data['content_length'],
                block_count=page_data['block_count'],
                block_types=page_data['block_types'],
                tables=tables,
                table_count=page_data['table_count']
            )
            pages.append(page)
            total_tables += len(tables)
        
        # 合併所有頁面內容
        full_content = '\n\n'.join([page.content for page in pages])
        
        # 創建元數據
        metadata = ConversionMetadata(
            file_name=file_path.name,
            file_path=str(file_path),
            file_type=file_path.suffix.lower(),
            file_size=file_path.stat().st_size,
            total_pages=len(pages),
            total_tables=total_tables,
            total_content_length=len(full_content),
            conversion_timestamp=time.time(),
            converter_used='marker'
        )
        
        result = ConversionResult(
            content=full_content,
            pages=pages,
            metadata=metadata
        )
        
        # 如果需要保存到檔案
        if save_to_file:
            output_file = self._save_to_file(result, output_path, file_path)
            result.output_path = str(output_file)
        
        return result
    
    def _convert_with_markitdown(self, file_path: Path, output_path: Optional[str], save_to_file: bool) -> ConversionResult:
        """使用 Markitdown 轉換"""
        if not self.markitdown_converter:
            raise RuntimeError("Markitdown converter not available")
        
        # 使用 Markitdown 的 convert_file_with_metadata 方法
        markitdown_result = self.markitdown_converter.convert_file_with_metadata(str(file_path))
        
        # 轉換為統一格式
        pages: List[PageInfo] = []
        total_tables: int = 0
        
        # 特殊處理 Excel 檔案 - 使用工作表信息
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            # Excel 檔案：使用工作表信息創建頁面
            sheets: Optional[List[Dict[str, str]]] = markitdown_result.get('sheets')
            if sheets:
                for i, sheet in enumerate(sheets, 1):
                    page = PageInfo(
                        page_number=i,
                        title=sheet.get('title'),  # 可能是 None
                        content=sheet.get('content', ''),
                        content_length=len(sheet.get('content', '')),
                        block_count=0,  # Markitdown 不提供此信息
                        block_types=None,  # Markitdown 不提供此信息
                        tables=None,  # Markitdown 不提供表格信息
                        table_count=0
                    )
                    pages.append(page)
            else:
                # 如果沒有工作表信息，使用頁面信息
                page_contents: Optional[List[str]] = markitdown_result.get('pages')
                if page_contents:
                    for i, page_content in enumerate(page_contents, 1):
                        page = PageInfo(
                            page_number=i,
                            title=None,  # 非 Excel 頁面可能沒有標題
                            content=page_content,
                            content_length=len(page_content),
                            block_count=0,  # Markitdown 不提供此信息
                            block_types=None,  # Markitdown 不提供此信息
                            tables=None,  # Markitdown 不提供表格信息
                            table_count=0
                        )
                        pages.append(page)
        else:
            # 非 Excel 檔案：使用頁面信息
            page_contents: Optional[List[str]] = markitdown_result.get('pages')
            if page_contents:
                for i, page_content in enumerate(page_contents, 1):
                    page = PageInfo(
                        page_number=i,
                        title=None,  # 非 Excel 頁面可能沒有標題
                        content=page_content,
                        content_length=len(page_content),
                        block_count=0,  # Markitdown 不提供此信息
                        block_types=None,  # Markitdown 不提供此信息
                        tables=None,  # Markitdown 不提供表格信息
                        table_count=0
                    )
                    pages.append(page)
        
        # 如果沒有頁面，創建一個包含全部內容的頁面
        if not pages:
            full_content: str = markitdown_result.get('full_text', '')
            page = PageInfo(
                page_number=1,
                title=None,  # 可能沒有標題
                content=full_content,
                content_length=len(full_content),
                block_count=0,
                block_types=None,
                tables=None,
                table_count=0
            )
            pages = [page]
        
        full_content: str = markitdown_result.get('full_text', '')
        
        # 創建元數據
        metadata = ConversionMetadata(
            file_name=file_path.name,
            file_path=str(file_path),
            file_type=file_path.suffix.lower(),
            file_size=file_path.stat().st_size,
            total_pages=len(pages) if pages else 0,
            total_tables=total_tables,
            total_content_length=len(full_content),
            conversion_timestamp=time.time(),
            converter_used='markitdown',
            additional_info={
                'title': markitdown_result.get('title'),  # 可能是 None
                'sheets': markitdown_result.get('sheets', [])  # Excel 工作表信息
            }
        )
        
        result = ConversionResult(
            content=full_content,
            pages=pages,  # 可能是 None 或空列表
            metadata=metadata
        )
        
        # 如果需要保存到檔案
        if save_to_file:
            output_file = self._save_to_file(result, output_path, file_path)
            result.output_path = str(output_file)
        
        return result
    
    def _save_to_file(self, result: ConversionResult, output_path: Optional[str], file_path: Path) -> Path:
        """保存轉換結果到檔案"""
        if output_path:
            output_file = Path(output_path)
        else:
            output_file = file_path.with_suffix('.md')
        
        # 確保輸出目錄存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 寫入檔案
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.content)
        
        logger.info(f"Conversion result saved to: {output_file}")
        return output_file
    
    def is_supported(self, file_path: str) -> bool:
        """
        檢查檔案格式是否支援
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            bool: 是否支援該格式
        """
        return FormatRouter.is_supported(file_path)
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        獲取支援的格式列表
        
        Returns:
            dict: 包含 marker 和 markitdown 支援的格式
        """
        return FormatRouter.get_supported_formats()
    
    def get_converter_status(self) -> Dict[str, bool]:
        """
        獲取轉換器可用狀態
        
        Returns:
            dict: 各轉換器的可用狀態
        """
        return {
            'marker': self.marker_converter is not None,
            'markitdown': self.markitdown_converter is not None
        }
