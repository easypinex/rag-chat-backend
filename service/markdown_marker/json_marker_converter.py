"""
Marker JSON-based Markdown Converter

使用 Marker 的 JSON API 進行 PDF 到 Markdown 的轉換
支援每頁結構化輸出和表格轉換
"""

import os
import re
import logging
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



class PageContent(TypedDict):
    """頁面內容和資訊"""
    page_number: int           # 頁碼
    content: str               # 頁面 Markdown 內容
    content_length: int        # 內容長度
    block_count: int           # 區塊數量
    block_types: Dict[str, int]  # 區塊類型分布，如 {'paragraph': 5, 'title': 2}


class PagesResult(TypedDict):
    """頁面列表結果"""
    file_name: str             # 檔案名稱
    total_pages: int           # 總頁數
    pages: List[PageContent]   # 每頁內容和資訊列表


class JsonMarkerConverter:
    """
    基於 Marker JSON API 的 PDF 到 Markdown 轉換器
    支援每頁結構化輸出和表格轉換
    """
    
    def __init__(self, model_locations: Optional[Dict[str, str]] = None):
        """
        初始化 Marker JSON 轉換器
        
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
            # 使用 JSON 輸出格式
            cfg = ConfigParser({"output_format": "json"})
            artifact_dict = create_model_dict()
            self.converter = PdfConverter(
                config=cfg.generate_config_dict(),
                artifact_dict=artifact_dict
            )
            logger.info("Marker JSON converter initialized successfully")
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
    
    def marker_json_pages(self, input_pdf: str) -> PagesResult:
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
            >>> converter = JsonMarkerConverter()
            >>> result = converter.marker_json_pages("document.pdf")
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
                page_contents = self._split_markdown_by_pages(markdown_content)
            else:
                # 如果沒有 markdown 屬性，將整個對象轉為字符串
                page_contents = [str(rendered)]
            
            # 構建頁面資訊
            pages_with_info = []
            for i, content in enumerate(page_contents, 1):
                # 分析頁面內容
                block_count, block_types = self._analyze_page_content(content)
                
                page_info: PageContent = {
                    'page_number': i,
                    'content': content,
                    'content_length': len(content),
                    'block_count': block_count,
                    'block_types': block_types
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
    
    def _split_markdown_by_pages(self, markdown_content: str) -> List[str]:
        """
        將 Markdown 內容智能分割為多頁
        
        Args:
            markdown_content (str): 完整的 Markdown 內容
            
        Returns:
            List[str]: 分割後的頁面列表，每個字符串是一頁的 Markdown 內容
            
        Algorithm:
            1. 優先按標題分割（## 或 ### 開頭）
            2. 每個章節作為一頁
            3. 確保每頁內容完整且有意義
        
        Example:
            >>> content = "# Title\\n\\n## Section 1\\n\\nContent...\\n\\n## Section 2\\n\\nMore content..."
            >>> pages = converter._split_markdown_by_pages(content)
            >>> print(f"分割為 {len(pages)} 頁")
            >>> for i, page in enumerate(pages, 1):
            ...     print(f"第 {i} 頁: {len(page)} 字元")
        """
        # 智能分頁策略：
        # 1. 按標題分割（## 或 ### 開頭）
        # 2. 按段落分割
        # 3. 控制每頁的內容量
        
        # 首先按標題分割
        sections = re.split(r'\n(?=#{2,3}\s)', markdown_content)
        
        # 將每個章節作為一頁
        pages = []
        for section in sections:
            if section.strip():
                pages.append(section.strip())
        
        # 如果沒有頁面，至少返回一頁
        if not pages:
            pages = [markdown_content]
        
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
    
    def _analyze_page_content(self, content: str) -> tuple[int, Dict[str, int]]:
        """
        分析頁面內容，統計區塊類型和數量
        
        Args:
            content (str): 頁面 Markdown 內容
            
        Returns:
            tuple[int, Dict[str, int]]: (區塊總數, 區塊類型分布)
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
        
        return block_count, block_types
    
    def marker_json_to_markdown(self, input_pdf: str) -> str:
        """
        使用 Marker 的 JSON 結構生成 Markdown
        
        Args:
            input_pdf: PDF 檔案路徑
            
        Returns:
            轉換後的 Markdown 內容
        """
        result = self.marker_json_pages(input_pdf)
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
        將 PDF 檔案轉換為 Markdown（使用 JSON API）
        
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
            logger.info(f"Converting PDF to Markdown using JSON API: {pdf_path}")
            
            # 使用 JSON API 進行轉換
            markdown_content = self.marker_json_to_markdown(str(pdf_path))
            
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
        批量轉換多個 PDF 檔案（使用 JSON API）
        
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
            output_dir = pdf_dir / "json_converted"
        else:
            output_dir = Path(output_directory)
        
        output_dir.mkdir(exist_ok=True)
        
        results = {}
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in directory: {pdf_dir}")
            return results
        
        logger.info(f"Found {len(pdf_files)} PDF files to convert using JSON API")
        
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
    


def create_json_marker_converter(model_locations: Optional[Dict[str, str]] = None) -> JsonMarkerConverter:
    """
    建立 JSON Marker 轉換器的便利函數
    
    Args:
        model_locations: 模型位置配置
        
    Returns:
        JsonMarkerConverter 實例
    """
    return JsonMarkerConverter(model_locations)
