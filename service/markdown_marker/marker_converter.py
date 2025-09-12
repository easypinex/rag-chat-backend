"""
Marker-based Markdown Converter

使用 Marker 套件進行 PDF 到 Markdown 的轉換
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import shutil

try:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    MARKER_AVAILABLE = True
except ImportError:
    MARKER_AVAILABLE = False
    logging.warning("Marker package not available. Please install marker-pdf[full].")

logger = logging.getLogger(__name__)


class MarkerConverter:
    """
    基於 Marker 套件的 PDF 到 Markdown 轉換器
    """
    
    def __init__(self, model_locations: Optional[Dict[str, str]] = None):
        """
        初始化 Marker 轉換器
        
        Args:
            model_locations: 模型位置配置，如果為 None 則使用預設位置
        """
        if not MARKER_AVAILABLE:
            raise ImportError("Marker package is not available. Please install marker-pdf[full].")
        
        self.model_locations = model_locations or {}
        self.converter = None
        self._initialize_converter()
    
    def _initialize_converter(self):
        """初始化 Marker 轉換器"""
        try:
            artifact_dict = create_model_dict()
            self.converter = PdfConverter(artifact_dict=artifact_dict)
            logger.info("Marker converter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Marker converter: {e}")
            raise
    
    def convert_pdf_to_markdown(
        self, 
        pdf_path: str, 
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        將 PDF 檔案轉換為 Markdown
        
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
            logger.info(f"Converting PDF to Markdown: {pdf_path}")
            
            # 使用 Marker 進行轉換
            rendered = self.converter(str(pdf_path))
            text, _, images = text_from_rendered(rendered)
            
            # 將轉換結果寫入檔案
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            logger.info(f"Conversion completed. Output saved to: {output_path}")
            
            # 如果有圖片，複製到輸出目錄
            if images:
                output_dir = output_path.parent
                images_dir = output_dir / f"{output_path.stem}_images"
                images_dir.mkdir(exist_ok=True)
                
                for img_path in images:
                    if os.path.exists(img_path):
                        shutil.copy2(img_path, images_dir)
                        logger.info(f"Copied image: {img_path} -> {images_dir}")
            
            return text
            
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
        批量轉換多個 PDF 檔案
        
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
        
        logger.info(f"Found {len(pdf_files)} PDF files to convert")
        
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
    
    def get_conversion_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        獲取 PDF 檔案的轉換資訊
        
        Args:
            pdf_path: PDF 檔案路徑
            
        Returns:
            包含檔案資訊的字典
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        stat = pdf_path.stat()
        return {
            "file_name": pdf_path.name,
            "file_size": stat.st_size,
            "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified_time": stat.st_mtime,
            "extension": pdf_path.suffix,
            "marker_available": MARKER_AVAILABLE
        }


def create_marker_converter(model_locations: Optional[Dict[str, str]] = None) -> MarkerConverter:
    """
    建立 Marker 轉換器的便利函數
    
    Args:
        model_locations: 模型位置配置
        
    Returns:
        MarkerConverter 實例
    """
    return MarkerConverter(model_locations)
