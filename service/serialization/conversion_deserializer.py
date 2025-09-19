"""
ConversionResult 反序列化器

從 JSON 文件反序列化 ConversionResult 對象，支援完整的元數據和頁面信息恢復。
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..markdown_integrate.data_models import ConversionResult, ConversionMetadata, PageInfo, TableInfo


class ConversionDeserializer:
    """ConversionResult 反序列化器"""
    
    def __init__(self, input_dir: str = "service/serialization/markdown"):
        """
        初始化反序列化器
        
        Args:
            input_dir: JSON 文件輸入目錄
        """
        self.input_dir = Path(input_dir)
    
    def deserialize(self, file_path: str) -> ConversionResult:
        """
        從 JSON 文件反序列化 ConversionResult
        
        Args:
            file_path: JSON 文件路徑
            
        Returns:
            ConversionResult: 反序列化後的 ConversionResult 對象
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Serialization file not found: {file_path}")
        
        # 讀取 JSON 文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 反序列化各個組件
        metadata = self._deserialize_metadata(data["metadata"])
        pages = self._deserialize_pages(data.get("pages")) if data.get("pages") else None
        
        # 創建 ConversionResult 對象
        conversion_result = ConversionResult(
            content=data["content"],
            metadata=metadata,
            pages=pages,
            output_path=data.get("output_path")
        )
        
        return conversion_result
    
    def _deserialize_metadata(self, metadata_dict: Dict[str, Any]) -> ConversionMetadata:
        """
        反序列化 ConversionMetadata
        
        Args:
            metadata_dict: 元數據字典
            
        Returns:
            ConversionMetadata: 反序列化後的元數據對象
        """
        return ConversionMetadata(
            file_name=metadata_dict["file_name"],
            file_path=metadata_dict["file_path"],
            file_type=metadata_dict["file_type"],
            file_size=metadata_dict["file_size"],
            total_pages=metadata_dict["total_pages"],
            total_tables=metadata_dict["total_tables"],
            total_content_length=metadata_dict["total_content_length"],
            conversion_timestamp=metadata_dict["conversion_timestamp"],
            converter_used=metadata_dict["converter_used"],
            additional_info=metadata_dict.get("additional_info", {})
        )
    
    def _deserialize_pages(self, pages_list: List[Dict[str, Any]]) -> List[PageInfo]:
        """
        反序列化頁面信息列表
        
        Args:
            pages_list: 頁面信息字典列表
            
        Returns:
            List[PageInfo]: 反序列化後的頁面信息列表
        """
        pages = []
        
        for page_dict in pages_list:
            page = PageInfo(
                page_number=page_dict["page_number"],
                title=page_dict.get("title"),
                content=page_dict["content"],
                content_length=page_dict.get("content_length", 0),
                block_count=page_dict.get("block_count", 0),
                block_types=page_dict.get("block_types", {}),
                table_count=page_dict.get("table_count", 0),
                tables=self._deserialize_tables(page_dict.get("tables", []))
            )
            pages.append(page)
        
        return pages
    
    def _deserialize_tables(self, tables_list: List[Dict[str, Any]]) -> List[TableInfo]:
        """
        反序列化表格信息列表
        
        Args:
            tables_list: 表格信息字典列表
            
        Returns:
            List[TableInfo]: 反序列化後的表格信息列表
        """
        tables = []
        
        for table_dict in tables_list:
            table = TableInfo(
                table_id=table_dict["table_id"],
                title=table_dict["title"],
                content=table_dict["content"],
                row_count=table_dict["row_count"],
                column_count=table_dict["column_count"],
                start_line=table_dict["start_line"],
                end_line=table_dict["end_line"]
            )
            tables.append(table)
        
        return tables
    
    def deserialize_from_latest(self) -> Optional[ConversionResult]:
        """
        從最新的序列化文件反序列化
        
        Returns:
            Optional[ConversionResult]: 反序列化後的 ConversionResult，如果沒有文件則返回 None
        """
        json_files = list(self.input_dir.glob("*.json"))
        if not json_files:
            return None
        
        # 按修改時間排序，獲取最新的文件
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
        return self.deserialize(str(latest_file))
    
    def deserialize_by_filename(self, filename: str) -> ConversionResult:
        """
        根據文件名反序列化
        
        Args:
            filename: 文件名（不包含路徑）
            
        Returns:
            ConversionResult: 反序列化後的 ConversionResult 對象
        """
        file_path = self.input_dir / filename
        return self.deserialize(str(file_path))
    
    def list_available_files(self) -> List[Dict[str, Any]]:
        """
        列出可用的序列化文件
        
        Returns:
            List[Dict[str, Any]]: 文件信息列表
        """
        json_files = list(self.input_dir.glob("*.json"))
        file_info_list = []
        
        for file_path in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                file_info = {
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size,
                    "serialization_timestamp": data.get("serialization_timestamp"),
                    "original_file_name": data.get("metadata", {}).get("file_name"),
                    "converter_used": data.get("metadata", {}).get("converter_used"),
                    "total_pages": data.get("metadata", {}).get("total_pages"),
                    "has_pages": data.get("pages") is not None
                }
                file_info_list.append(file_info)
            except Exception as e:
                # 如果文件損壞，跳過
                continue
        
        return file_info_list
    
    def validate_file(self, file_path: str) -> bool:
        """
        驗證序列化文件是否有效
        
        Args:
            file_path: JSON 文件路徑
            
        Returns:
            bool: 文件是否有效
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 檢查必要的字段
            required_fields = ["content", "metadata"]
            for field in required_fields:
                if field not in data:
                    return False
            
            # 檢查元數據字段
            metadata = data["metadata"]
            required_metadata_fields = [
                "file_name", "file_path", "file_type", "file_size",
                "total_pages", "total_tables", "total_content_length",
                "conversion_timestamp", "converter_used"
            ]
            for field in required_metadata_fields:
                if field not in metadata:
                    return False
            
            return True
            
        except Exception:
            return False
