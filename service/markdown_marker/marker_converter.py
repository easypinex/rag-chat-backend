"""
Marker-based Markdown Converter

使用 Marker 進行 PDF 到 Markdown 的轉換
支援每頁結構化輸出和表格轉換
"""

import os
import re
import logging
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from marker.renderers.markdown import MarkdownOutput
import tempfile
import shutil

try:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.config.parser import ConfigParser
    MARKER_AVAILABLE = True
except ImportError:
    MARKER_AVAILABLE = False
    logging.warning("Marker package not available. Please install marker-pdf[full].")

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    logging.warning("BeautifulSoup not available. Please install beautifulsoup4.")

logger = logging.getLogger(__name__)



class TableInfo(TypedDict):
    """表格資訊"""
    table_id: str              # 表格 UUID
    title: str                 # 表格標題
    content: str               # 表格 Markdown 內容
    row_count: int             # 行數
    column_count: int          # 列數
    start_line: int            # 在頁面中的起始行號
    end_line: int              # 在頁面中的結束行號


class PageContent(TypedDict):
    """頁面內容和資訊"""
    page_number: int           # 頁碼
    content: str               # 頁面 Markdown 內容
    content_length: int        # 內容長度
    block_count: int           # 區塊數量
    block_types: Dict[str, int]  # 區塊類型分布，如 {'paragraph': 5, 'title': 2}
    tables: List[TableInfo]    # 頁面中的表格列表
    table_count: int           # 表格數量


class PagesResult(TypedDict):
    """頁面列表結果"""
    file_name: str             # 檔案名稱
    total_pages: int           # 總頁數
    pages: List[PageContent]   # 每頁內容和資訊列表


class MarkerConverter:
    """
    基於 Marker 的 PDF 到 Markdown 轉換器
    支援每頁結構化輸出和表格轉換
    """
    
    def __init__(self, model_locations: Optional[Dict[str, str]] = None):
        """
        初始化 Marker 轉換器
        
        Args:
            model_locations: 模型位置配置，如果為 None 則使用預設位置
        """
        if not MARKER_AVAILABLE:
            raise ImportError("Marker package is not available. Please install marker-pdf[full].")
        
        if not BEAUTIFULSOUP_AVAILABLE:
            raise ImportError("BeautifulSoup is not available. Please install beautifulsoup4.")
        
        self.model_locations = model_locations or {}
        self.converter: Optional[PdfConverter] = None
        self._initialize_converter()
    
    def _initialize_converter(self):
        """初始化 Marker 轉換器"""
        try:
            # 使用 Markdown 輸出格式並啟用分頁
            cfg = ConfigParser({
                "output_format": "markdown",
                "paginate_output": True
            })
            artifact_dict = create_model_dict()
            self.converter = PdfConverter(
                config=cfg.generate_config_dict(),
                artifact_dict=artifact_dict
            )
            logger.info("Marker converter initialized successfully with pagination enabled")
        except Exception as e:
            logger.error(f"Failed to initialize Marker converter: {e}")
            raise
    
    def _md_escape(self, text: str) -> str:
        """轉義 Markdown 特殊字符"""
        return text.replace("|", "\\|")
    
    def _table_html_to_md(self, html: str) -> str:
        """
        嘗試把 <table> 轉成 GFM 表格；若含 rowspan/colspan 就保留 HTML。
        
        Args:
            html: HTML 表格字符串
            
        Returns:
            轉換後的 Markdown 表格或原始 HTML
        """
        soup = BeautifulSoup(html or "", "html.parser")
        table = soup.find("table")
        if not table:
            return (html or "").strip()

        # 檢查是否有跨欄/跨列
        for cell in table.find_all(["td", "th"]):
            if cell.has_attr("rowspan") or cell.has_attr("colspan"):
                return f"\n<!-- complex table; keep HTML -->\n{str(table)}\n"

        # 提取表格行
        rows = []
        for tr in table.find_all("tr"):
            row = []
            for cell in tr.find_all(["td", "th"]):
                txt = " ".join(cell.stripped_strings)
                row.append(self._md_escape(txt))
            if row:
                rows.append(row)

        if not rows:
            return ""

        # 構建 Markdown 表格
        header = rows[0]
        sep = ["---"] * len(header)
        body = rows[1:]

        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(sep) + " |"
        ]
        for r in body:
            lines.append("| " + " | ".join(r) + " |")
        return "\n" + "\n".join(lines) + "\n"
    
    def _block_to_md(self, block) -> str:
        """
        將單一區塊轉換為 Markdown
        
        Args:
            block: Marker 區塊對象
            
        Returns:
            轉換後的 Markdown 字符串
        """
        # 調試：檢查 block 的屬性
        logger.debug(f"Block type: {type(block)}")
        logger.debug(f"Block attributes: {dir(block)}")
        
        # 嘗試不同的屬性名稱
        bt = ""
        text = ""
        
        # 檢查 block_type 屬性
        if hasattr(block, "block_type"):
            bt = (block.block_type or "").lower()
        elif hasattr(block, "type"):
            bt = (block.type or "").lower()
        
        # 檢查 text 屬性
        if hasattr(block, "text"):
            text = block.text or ""
        elif hasattr(block, "markdown"):
            text = block.markdown or ""
        elif hasattr(block, "content"):
            text = block.content or ""
        elif hasattr(block, "data"):
            text = str(block.data) if block.data else ""

        # 表格處理
        if "table" in bt:
            html = getattr(block, "html", None) or text
            return self._table_html_to_md(html)

        # 標題處理
        if "title" in bt or "header" in bt or getattr(block, "is_heading", False):
            return "\n## " + (text or "").strip() + "\n"

        # 方程式處理
        if "equation" in bt or "math" in bt:
            body = (text or "").strip()
            if "\n" in body:
                return "\n$$\n" + body + "\n$$\n"
            return "\n$" + body + "$\n"

        # 圖片/圖表處理
        if "figure" in bt or "image" in bt:
            cap = getattr(block, "caption", "") or ""
            return f'\n![figure]({"#"} "{self._md_escape(cap)}")\n'

        # 一般段落處理
        if text:
            # 清理軟換行
            t = re.sub(r"[ \t]+\n", "\n", text)
            t = re.sub(r"\n{3,}", "\n\n", t)
            return "\n" + t.strip() + "\n"

        return ""
    
    def marker_pages(self, input_pdf: str) -> PagesResult:
        """
        使用 Marker 獲取 PDF 的每頁內容結構和資訊
        
        Args:
            input_pdf (str): PDF 檔案路徑
            
        Returns:
            PagesResult: 包含頁面內容和資訊的結構化數據
                - file_name: 檔案名稱
                - total_pages: 總頁數
                - pages: 每頁的內容和資訊列表
                    - page_number: 頁碼
                    - content: 頁面 Markdown 內容
                    - content_length: 內容長度
                    - block_count: 區塊數量
                    - block_types: 區塊類型分布
        
        Example:
            >>> converter = MarkerConverter()
            >>> result = converter.marker_pages("document.pdf")
            >>> print(f"檔案: {result['file_name']}")
            >>> print(f"總共 {result['total_pages']} 頁")
            >>> for page in result['pages']:
            ...     print(f"第 {page['page_number']} 頁: {page['content_length']} 字元")
            ...     print(f"區塊數量: {page['block_count']}")
            ...     print(f"內容預覽: {page['content'][:100]}...")
        
        Note:
            - 返回的頁面列表是智能分割的結果，不是原始 PDF 的物理頁面
            - 分割策略：優先按標題分割，其次按段落分割
            - 每頁都包含完整的內容和統計資訊
        """
        try:
            # Marker 轉換器返回 MarkdownOutput 對象
            rendered: 'MarkdownOutput' = self.converter(input_pdf)
            
            # MarkdownOutput 對象包含以下主要屬性：
            # - markdown: str - 完整的 Markdown 內容
            # - images: Dict - 圖片信息
            # - metadata: Dict - 元數據信息
            if hasattr(rendered, 'markdown'):
                # 將 Markdown 內容按頁分割
                markdown_content: str = rendered.markdown
                page_contents = self._split_markdown_by_pages(markdown_content, rendered)
            else:
                # 如果沒有 markdown 屬性，將整個對象轉為字符串
                page_contents = [str(rendered)]
            
            # 構建頁面資訊
            pages_with_info = []
            
            for i, content in enumerate(page_contents, 1):
                # 分析頁面內容
                block_count, block_types, tables = self._analyze_page_content(content)
                
                page_info: PageContent = {
                    'page_number': i,
                    'content': content,
                    'content_length': len(content),
                    'block_count': block_count,
                    'block_types': block_types,
                    'tables': tables,
                    'table_count': len(tables)
                }
                pages_with_info.append(page_info)
            
            # 構建結果
            file_name = Path(input_pdf).name
            result: PagesResult = {
                'file_name': file_name,
                'total_pages': len(pages_with_info),
                'pages': pages_with_info
            }
            
            logger.info(f"Extracted {len(pages_with_info)} pages from PDF: {file_name}")
            return result
        except Exception as e:
            logger.error(f"Failed to extract pages from PDF: {e}")
            raise
    
    def _split_markdown_by_pages(self, markdown_content: str, rendered: 'MarkdownOutput' = None) -> List[str]:
        """
        將 Markdown 內容按照原始 PDF 的物理頁面分割
        
        Args:
            markdown_content (str): 完整的 Markdown 內容
            rendered (MarkdownOutput): Marker 轉換器返回的對象，包含頁面信息
            
        Returns:
            List[str]: 分割後的頁面列表，每個字符串是一頁的 Markdown 內容
            
        Algorithm:
            1. 如果有 rendered 對象，使用其 metadata 中的 page_id 信息
            2. 按照原始 PDF 的物理頁面分割
            3. 如果沒有頁面信息，則按標題分割作為備用方案
        
        Example:
            >>> content = "# Title\\n\\n## Section 1\\n\\nContent...\\n\\n## Section 2\\n\\nMore content..."
            >>> pages = converter._split_markdown_by_pages(content, rendered)
            >>> print(f"分割為 {len(pages)} 頁")
            >>> for i, page in enumerate(pages, 1):
            ...     print(f"第 {i} 頁: {len(page)} 字元")
        """
        # 如果有 rendered 對象且包含頁面信息，使用物理頁面分割
        if rendered and hasattr(rendered, 'metadata') and rendered.metadata:
            metadata = rendered.metadata
            if 'page_stats' in metadata:
                page_stats = metadata['page_stats']
                total_pages = len(page_stats)
                logger.info(f"使用物理頁面分割，共 {total_pages} 頁")
                
                # 按物理頁面分割內容
                pages = self._split_by_physical_pages(markdown_content, page_stats)
                if pages:
                    return pages
        
        # 備用方案：按標題分割（保持原有邏輯）
        logger.warning("使用備用方案：按標題分割")
        sections = re.split(r'\n(?=#{2,3}\s)', markdown_content)
        
        pages = []
        for section in sections:
            if section.strip():
                pages.append(section.strip())
        
        # 如果沒有頁面，至少返回一頁
        if not pages:
            pages = [markdown_content]
        
        return pages
    
    def _split_by_physical_pages(self, markdown_content: str, page_stats: List[Dict]) -> List[str]:
        """
        按照 Marker 的頁面分隔符分割 Markdown 內容
        
        Args:
            markdown_content (str): 完整的 Markdown 內容
            page_stats (List[Dict]): 頁面統計信息
            
        Returns:
            List[str]: 按物理頁面分割的內容列表
        """
        total_pages = len(page_stats)
        logger.info(f"使用 Marker 頁面分隔符分割 {total_pages} 個物理頁面")
        
        # Marker 的頁面分隔符格式：\n\n{page_id}------------------------------------------------\n\n
        # 其中 page_id 是頁面編號，後面跟著 48 個連字符
        page_separator_pattern = r'\n\n\{(\d+)\}' + r'-' * 48 + r'\n\n'
        
        # 使用正則表達式分割內容
        page_parts = re.split(page_separator_pattern, markdown_content)
        
        logger.info(f"找到 {len(page_parts)} 個部分")
        
        if len(page_parts) <= 1:
            logger.error("未找到 Marker 頁面分隔符，這不應該發生！")
            raise ValueError("Marker 頁面分隔符未找到，請檢查 paginate_output 是否正確啟用")
        
        # 第一個部分是第一頁的內容
        pages = []
        if page_parts[0].strip():
            pages.append(page_parts[0].strip())
        
        # 其餘部分每兩個元素一組：頁面編號和內容
        for i in range(1, len(page_parts), 2):
            if i + 1 < len(page_parts):
                page_id = page_parts[i]
                page_content = page_parts[i + 1].strip()
                if page_content:
                    pages.append(page_content)
        
        logger.info(f"成功分割為 {len(pages)} 頁")
        
        # 驗證頁數是否正確
        if len(pages) != total_pages:
            logger.warning(f"分割頁數 ({len(pages)}) 與預期頁數 ({total_pages}) 不符")
        
        return pages
    
    
    def _split_by_paragraphs(self, content: str) -> List[str]:
        """
        按段落分割內容為多頁
        
        Args:
            content (str): 要分割的 Markdown 內容
            
        Returns:
            List[str]: 分割後的頁面列表，每個字符串是一頁的內容
            
        Algorithm:
            1. 按雙換行符分割段落
            2. 每個段落作為一頁
            3. 至少返回一頁內容
        
        Example:
            >>> content = "段落1\\n\\n段落2\\n\\n段落3..."
            >>> pages = converter._split_by_paragraphs(content)
            >>> print(f"按段落分割為 {len(pages)} 頁")
        """
        paragraphs = content.split('\n\n')
        pages = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                pages.append(paragraph.strip())
        
        return pages if pages else [content]
    
    def _extract_tables_from_content(self, content: str) -> List[TableInfo]:
        """
        從頁面內容中提取表格信息
        
        Args:
            content (str): 頁面 Markdown 內容
            
        Returns:
            List[TableInfo]: 表格信息列表
        """
        tables = []
        lines = content.split('\n')
        
        # 查找表格行
        table_lines = []
        current_table_start = -1
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 檢查是否為表格行
            if '|' in line and line.count('|') >= 2:
                if current_table_start == -1:
                    current_table_start = i
                table_lines.append((i, line))
            else:
                # 如果不是表格行，檢查是否有完整的表格
                if table_lines and current_table_start != -1:
                    # 提取表格
                    table_info = self._parse_table_lines(table_lines, current_table_start)
                    if table_info:
                        tables.append(table_info)
                    table_lines = []
                    current_table_start = -1
        
        # 處理最後一個表格
        if table_lines and current_table_start != -1:
            table_info = self._parse_table_lines(table_lines, current_table_start)
            if table_info:
                tables.append(table_info)
        
        return tables
    
    def _parse_table_lines(self, table_lines: List[tuple], start_line: int) -> Optional[TableInfo]:
        """
        解析表格行，提取表格信息
        
        Args:
            table_lines (List[tuple]): 表格行列表，每個元素為 (行號, 內容)
            start_line (int): 表格起始行號
            
        Returns:
            Optional[TableInfo]: 表格信息，如果解析失敗則返回 None
        """
        if len(table_lines) < 2:  # 至少需要標題行和分隔行
            return None
        
        # 提取表格內容
        table_content_lines = [line for _, line in table_lines]
        table_content = '\n'.join(table_content_lines)
        
        # 計算行數和列數
        row_count = len(table_lines)
        
        # 跳過分隔行來計算列數
        data_lines = [line for _, line in table_lines if not line.startswith('|---')]
        if not data_lines:
            return None
            
        first_line = data_lines[0]
        column_count = first_line.count('|') - 1  # 減去首尾的 |
        
        # 嘗試提取表格標題（從表格前的內容中尋找）
        title = self._extract_table_title(table_content_lines[0])
        
        # 生成表格 UUID
        table_id = str(uuid.uuid4())
        
        return TableInfo(
            table_id=table_id,
            title=title,
            content=table_content,
            row_count=row_count,
            column_count=column_count,
            start_line=start_line,
            end_line=table_lines[-1][0]
        )
    
    def _extract_table_title(self, first_line: str) -> str:
        """
        從表格第一行提取標題
        
        Args:
            first_line (str): 表格第一行內容
            
        Returns:
            str: 表格標題
        """
        # 移除 Markdown 表格格式
        cells = [cell.strip() for cell in first_line.split('|') if cell.strip()]
        if cells:
            # 使用第一個非空單元格作為標題
            return cells[0]
        return "未命名表格"
    
    def _analyze_page_content(self, content: str) -> tuple[int, Dict[str, int], List[TableInfo]]:
        """
        分析頁面內容，統計區塊類型和數量，並提取表格信息
        
        Args:
            content (str): 頁面 Markdown 內容
            
        Returns:
            tuple[int, Dict[str, int], List[TableInfo]]: (區塊總數, 區塊類型分布, 表格列表)
        """
        block_types = {}
        block_count = 0
        
        # 按行分析內容
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            block_count += 1
            
            # 判斷區塊類型
            if line.startswith('#'):
                block_type = 'title'
            elif line.startswith('|') and '|' in line[1:]:
                block_type = 'table'
            elif line.startswith('- ') or line.startswith('* '):
                block_type = 'list'
            elif line.startswith('```'):
                block_type = 'code'
            elif line.startswith('>'):
                block_type = 'quote'
            elif line.startswith('<!--') and line.endswith('-->'):
                block_type = 'comment'
            else:
                block_type = 'paragraph'
            
            block_types[block_type] = block_types.get(block_type, 0) + 1
        
        # 提取表格信息
        tables = self._extract_tables_from_content(content)
        
        return block_count, block_types, tables
    
    def marker_to_markdown(self, input_pdf: str) -> str:
        """
        使用 Marker 結構生成 Markdown
        
        Args:
            input_pdf: PDF 檔案路徑
            
        Returns:
            轉換後的 Markdown 內容
        """
        result = self.marker_pages(input_pdf)
        parts = []
        
        for page_info in result['pages']:
            page_number = page_info['page_number']
            content = page_info['content']
            
            # 第一頁不加分隔線，其他頁面加分隔線
            if page_number == 1:
                parts.append(f"## Page {page_number}\n")
            else:
                parts.append(f"\n---\n\n## Page {page_number}\n")
            
            # 添加頁面內容
            parts.append(content)
        
        md = "\n".join(parts).strip() + "\n"
        # 清理多餘的換行
        md = re.sub(r"\n{4,}", "\n\n", md)
        return md
    
    def convert_pdf_to_markdown(
        self, 
        pdf_path: str, 
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        將 PDF 檔案轉換為 Markdown（使用 Marker API）
        
        Args:
            pdf_path: PDF 檔案路徑
            output_path: 輸出 Markdown 檔案路徑，如果為 None 則自動生成
            **kwargs: 其他轉換參數
            
        Returns:
            轉換後的 Markdown 內容
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # 如果沒有指定輸出路徑，則在相同目錄下生成 .md 檔案
        if output_path is None:
            output_path = pdf_path.with_suffix('.md')
        else:
            output_path = Path(output_path)
        
        try:
            logger.info(f"Converting PDF to Markdown using Marker API: {pdf_path}")
            
            # 使用 Marker API 進行轉換
            markdown_content = self.marker_to_markdown(str(pdf_path))
            
            # 將轉換結果寫入檔案
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Conversion completed. Output saved to: {output_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"Failed to convert PDF: {e}")
            raise
    
    def convert_multiple_pdfs(
        self, 
        pdf_directory: str, 
        output_directory: Optional[str] = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        批量轉換多個 PDF 檔案（使用 Marker API）
        
        Args:
            pdf_directory: PDF 檔案目錄
            output_directory: 輸出目錄，如果為 None 則在 PDF 目錄下建立 converted 子目錄
            **kwargs: 其他轉換參數
            
        Returns:
            轉換結果字典，key 為檔案名，value 為轉換後的 Markdown 內容
        """
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")
        
        if output_directory is None:
            output_dir = pdf_dir / "converted"
        else:
            output_dir = Path(output_directory)
        
        output_dir.mkdir(exist_ok=True)
        
        results = {}
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in directory: {pdf_dir}")
            return results
        
        logger.info(f"Found {len(pdf_files)} PDF files to convert using Marker API")
        
        for pdf_file in pdf_files:
            try:
                output_file = output_dir / f"{pdf_file.stem}.md"
                markdown_content = self.convert_pdf_to_markdown(
                    str(pdf_file), 
                    str(output_file),
                    **kwargs
                )
                results[pdf_file.name] = markdown_content
                logger.info(f"Successfully converted: {pdf_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to convert {pdf_file.name}: {e}")
                results[pdf_file.name] = f"Error: {str(e)}"
        
        return results
    


def create_marker_converter(model_locations: Optional[Dict[str, str]] = None) -> MarkerConverter:
    """
    建立 Marker 轉換器的便利函數
    
    Args:
        model_locations: 模型位置配置
        
    Returns:
        MarkerConverter 實例
    """
    return MarkerConverter(model_locations)
