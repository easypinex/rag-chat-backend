"""
ConversionResult 序列化器

將 ConversionResult 對象序列化為 JSON 格式，支援完整的元數據和頁面信息保存。
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ..markdown_integrate.data_models import ConversionResult, ConversionMetadata, PageInfo, TableInfo


class ConversionSerializer:
    """ConversionResult 序列化器"""
    
    def __init__(self, output_dir: str = "service/serialization/markdown"):
        """
        初始化序列化器
        
        Args:
            output_dir: JSON 文件輸出目錄
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def serialize(self, conversion_result: ConversionResult, filename: Optional[str] = None) -> str:
        """
        序列化 ConversionResult 為 JSON
        
        Args:
            conversion_result: 要序列化的 ConversionResult 對象
            filename: 自定義文件名，如果為 None 則自動生成
            
        Returns:
            str: JSON 文件路徑
        """
        if filename is None:
            # 自動生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(conversion_result.metadata.file_name).stem
            filename = f"{base_name}_{timestamp}.json"
        
        # 確保文件名以 .json 結尾
        if not filename.endswith('.json'):
            filename += '.json'
        
        # 構建完整路徑
        output_path = self.output_dir / filename
        
        # 序列化數據
        serialized_data = self._convert_to_dict(conversion_result)
        
        # 寫入 JSON 文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serialized_data, f, ensure_ascii=False, indent=2)
        
        return str(output_path)
    
    def _convert_to_dict(self, conversion_result: ConversionResult) -> Dict[str, Any]:
        """
        將 ConversionResult 轉換為字典格式
        
        Args:
            conversion_result: ConversionResult 對象
            
        Returns:
            Dict[str, Any]: 序列化後的字典
        """
        return {
            "content": conversion_result.content,
            "metadata": self._serialize_metadata(conversion_result.metadata),
            "pages": self._serialize_pages(conversion_result.pages) if conversion_result.pages else None,
            "output_path": conversion_result.output_path,
            "serialization_timestamp": datetime.now().isoformat(),
            "serialization_version": "1.0"
        }
    
    def _serialize_metadata(self, metadata: ConversionMetadata) -> Dict[str, Any]:
        """
        序列化 ConversionMetadata
        
        Args:
            metadata: ConversionMetadata 對象
            
        Returns:
            Dict[str, Any]: 序列化後的元數據字典
        """
        return {
            "file_name": metadata.file_name,
            "file_path": metadata.file_path,
            "file_type": metadata.file_type,
            "file_size": metadata.file_size,
            "total_pages": metadata.total_pages,
            "total_tables": metadata.total_tables,
            "total_content_length": metadata.total_content_length,
            "conversion_timestamp": metadata.conversion_timestamp,
            "converter_used": metadata.converter_used,
            "additional_info": metadata.additional_info or {}
        }
    
    def _serialize_pages(self, pages: list[PageInfo]) -> list[Dict[str, Any]]:
        """
        序列化頁面信息列表
        
        Args:
            pages: PageInfo 對象列表
            
        Returns:
            list[Dict[str, Any]]: 序列化後的頁面信息列表
        """
        serialized_pages = []
        
        for page in pages:
            page_dict = {
                "page_number": page.page_number,
                "title": page.title,
                "content": page.content,
                "content_length": page.content_length,
                "block_count": page.block_count,
                "block_types": page.block_types or {},
                "table_count": page.table_count,
                "tables": self._serialize_tables(page.tables) if page.tables else []
            }
            serialized_pages.append(page_dict)
        
        return serialized_pages
    
    def _serialize_tables(self, tables: list[TableInfo]) -> list[Dict[str, Any]]:
        """
        序列化表格信息列表
        
        Args:
            tables: TableInfo 對象列表
            
        Returns:
            list[Dict[str, Any]]: 序列化後的表格信息列表
        """
        serialized_tables = []
        
        for table in tables:
            table_dict = {
                "table_id": table.table_id,
                "title": table.title,
                "content": table.content,
                "row_count": table.row_count,
                "column_count": table.column_count,
                "start_line": table.start_line,
                "end_line": table.end_line
            }
            serialized_tables.append(table_dict)
        
        return serialized_tables
    
    def get_available_files(self) -> list[str]:
        """
        獲取可用的序列化文件列表
        
        Returns:
            list[str]: JSON 文件路徑列表
        """
        json_files = list(self.output_dir.glob("*.json"))
        return [str(f) for f in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)]
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        獲取序列化文件的基本信息
        
        Args:
            file_path: JSON 文件路徑
            
        Returns:
            Dict[str, Any]: 文件信息
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "serialization_timestamp": data.get("serialization_timestamp"),
            "serialization_version": data.get("serialization_version"),
            "original_file_name": data.get("metadata", {}).get("file_name"),
            "converter_used": data.get("metadata", {}).get("converter_used"),
            "total_pages": data.get("metadata", {}).get("total_pages"),
            "has_pages": data.get("pages") is not None
        }
