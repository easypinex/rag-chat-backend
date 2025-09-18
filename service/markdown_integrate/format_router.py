"""
格式路由器

根據檔案格式決定使用哪個轉換器（Marker 或 Markitdown）
"""

from pathlib import Path
from typing import Tuple, Set


class FormatRouter:
    """格式路由器 - 決定使用哪個轉換器"""
    
    # Marker 支援的格式 (docx, pdf, pptx)
    MARKER_FORMATS: Set[str] = {'.docx', '.pdf', '.pptx'}
    
    # Markitdown 支援的格式 (excel 和其他)
    MARKITDOWN_FORMATS: Set[str] = {
        '.xlsx', '.xls', '.png', '.jpg', '.jpeg', '.gif', '.bmp', 
        '.tiff', '.webp', '.mp3', '.wav', '.flac', '.aac', '.ogg', 
        '.m4a', '.html', '.htm', '.csv', '.json', '.xml', '.txt',
        '.zip', '.epub', '.mobi'
    }
    
    @classmethod
    def get_converter_info(cls, file_path: str) -> Tuple[str, str]:
        """
        根據檔案格式決定使用哪個轉換器
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            Tuple[converter_name, file_type]: 轉換器名稱和檔案類型
            
        Raises:
            ValueError: 如果檔案格式不支援
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in cls.MARKER_FORMATS:
            return 'marker', file_ext
        elif file_ext in cls.MARKITDOWN_FORMATS:
            return 'markitdown', file_ext
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """
        檢查檔案格式是否支援
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            bool: 是否支援該格式
        """
        try:
            cls.get_converter_info(file_path)
            return True
        except ValueError:
            return False
    
    @classmethod
    def get_supported_formats(cls) -> dict:
        """
        獲取所有支援的格式列表
        
        Returns:
            dict: 包含 marker 和 markitdown 支援的格式
        """
        return {
            'marker': sorted(list(cls.MARKER_FORMATS)),
            'markitdown': sorted(list(cls.MARKITDOWN_FORMATS))
        }
    
    @classmethod
    def get_all_supported_formats(cls) -> Set[str]:
        """
        獲取所有支援的格式（合併 marker 和 markitdown）
        
        Returns:
            Set[str]: 所有支援的格式
        """
        return cls.MARKER_FORMATS.union(cls.MARKITDOWN_FORMATS)
