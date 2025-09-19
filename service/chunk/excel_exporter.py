"""
Excel 導出器

將分割後的 chunks 導出到 Excel 文件，支援合併單元格功能。
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class ExcelExporter:
    """Excel 導出器"""
    
    def __init__(self):
        """初始化導出器"""
        self.workbook = None
        self.worksheet = None
    
    def export_chunks_to_excel(self, 
                              chunks: List[Document], 
                              original_content: str,
                              output_path: str,
                              normalized_content: Optional[str] = None):
        """
        將 chunks 導出到 Excel 文件
        
        Args:
            chunks: 分割後的文檔列表
            original_content: 原始 Markdown 內容
            output_path: 輸出文件路徑
            normalized_content: 正規化後的內容（可選）
        """
        # 確保輸出目錄存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 創建工作簿
        self.workbook = Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.title = "Markdown Chunks"
        
        # 設置標題行
        self._setup_headers()
        
        # 填充數據
        self._fill_data(chunks, original_content, normalized_content)
        
        # 設置格式
        self._format_worksheet()
        
        # 保存文件
        self.workbook.save(output_path)
        logger.info(f"Excel file saved to: {output_path}")
    
    def export_chunks_to_excel_with_page_content(self, chunks: List[Document], page_chunks_info: List[Dict], output_path: str):
        """
        將 chunks 導出到 Excel 文件，使用按頁面分割的原始和正規化內容
        
        Args:
            chunks: 分割後的文檔列表
            page_chunks_info: 頁面 chunks 信息列表
            output_path: 輸出文件路徑
        """
        # 確保輸出目錄存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 創建工作簿
        self.workbook = Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.title = "Markdown Chunks"
        
        # 設置標題行
        self._setup_headers()
        
        # 填充數據
        self._fill_data_with_page_content(chunks, page_chunks_info)
        
        # 設置格式
        self._format_worksheet()
        
        # 保存文件
        self.workbook.save(output_path)
        logger.info(f"Excel file saved to: {output_path}")
    
    def _setup_headers(self):
        """設置標題行"""
        headers = [
            "原始內容 (A欄)",
            "正規化後內容 (B欄)",
            "分割後的 Chunk (C欄)", 
            "Chunk 編號",
            "Chunk 長度",
            "包含標題",
            "是否為表格",
            # 展開的 metadata 欄位
            "檔名",
            "檔案類型",
            "來源路徑",
            "轉換器",
            "總頁數",
            "總表格數",
            "頁碼",
            "頁面標題",
            "標題級數",
            "表格合併數",
            "完整元數據"
        ]
        
        for col, header in enumerate(headers, 1):
            cell = self.worksheet.cell(row=1, column=col, value=header)
            cell.font = cell.font.copy(bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')
    
    def _fill_data(self, chunks: List[Document], original_content: str, normalized_content: Optional[str] = None):
        """填充數據到工作表"""
        current_row = 2
        
        # 如果沒有提供正規化內容，使用原始內容
        if normalized_content is None:
            normalized_content = original_content
        
        for i, chunk in enumerate(chunks, 1):
            # A欄：原始內容（會根據 chunks 數量進行合併）
            self.worksheet.cell(row=current_row, column=1, value=original_content)
            
            # B欄：正規化後內容（會根據 chunks 數量進行合併）
            self.worksheet.cell(row=current_row, column=2, value=normalized_content)
            
            # C欄：分割後的 Chunk
            self.worksheet.cell(row=current_row, column=3, value=chunk.page_content)
            
            # D欄：Chunk 編號（使用全局編號）
            global_chunk_number = chunk.metadata.get('global_chunk_number', i)
            self.worksheet.cell(row=current_row, column=4, value=global_chunk_number)
            
            # E欄：Chunk 長度
            self.worksheet.cell(row=current_row, column=5, value=len(chunk.page_content))
            
            # F欄：包含標題
            has_headers = any(header in chunk.page_content for header in ['#', '##', '###', '####'])
            self.worksheet.cell(row=current_row, column=6, value="是" if has_headers else "否")
            
            # G欄：是否為表格
            is_table = chunk.metadata.get('is_table', False)
            self.worksheet.cell(row=current_row, column=7, value="是" if is_table else "否")
            
            # 展開的 metadata 欄位 (H欄開始)
            # H欄：檔名
            self.worksheet.cell(row=current_row, column=8, value=chunk.metadata.get('file_name', ''))
            
            # I欄：檔案類型
            self.worksheet.cell(row=current_row, column=9, value=chunk.metadata.get('file_type', ''))
            
            # J欄：來源路徑
            self.worksheet.cell(row=current_row, column=10, value=chunk.metadata.get('source', ''))
            
            # K欄：轉換器
            self.worksheet.cell(row=current_row, column=11, value=chunk.metadata.get('converter_used', ''))
            
            # L欄：總頁數
            self.worksheet.cell(row=current_row, column=12, value=chunk.metadata.get('total_pages', ''))
            
            # M欄：總表格數
            self.worksheet.cell(row=current_row, column=13, value=chunk.metadata.get('total_tables', ''))
            
            # N欄：頁碼
            self.worksheet.cell(row=current_row, column=14, value=chunk.metadata.get('page_number', ''))
            
            # O欄：頁面標題
            self.worksheet.cell(row=current_row, column=15, value=chunk.metadata.get('page_title', ''))
            
            # P欄：標題級數（合併四個標題欄位）
            header_level = self._get_header_level(chunk.metadata)
            self.worksheet.cell(row=current_row, column=16, value=header_level)
            
            # Q欄：表格合併數
            self.worksheet.cell(row=current_row, column=17, value=chunk.metadata.get('table_chunks_merged', ''))
            
            # R欄：完整元數據
            metadata_str = self._format_metadata(chunk.metadata)
            self.worksheet.cell(row=current_row, column=18, value=metadata_str)
            
            current_row += 1
        
        # 合併 A欄 和 B欄 的單元格（因為原始內容和正規化內容相同）
        if len(chunks) > 1:
            self.worksheet.merge_cells(f'A2:A{current_row - 1}')
            self.worksheet.merge_cells(f'B2:B{current_row - 1}')
    
    def _fill_data_with_page_content(self, chunks: List[Document], page_chunks_info: List[Dict]):
        """填充數據到工作表，使用按頁面分割的內容"""
        current_row = 2
        
        for i, chunk in enumerate(chunks, 1):
            # 獲取頁面級別的原始和正規化內容
            page_number = chunk.metadata.get('page_number')
            
            # 找到對應的頁面信息
            page_info = None
            for page_data in page_chunks_info:
                if page_data['page_number'] == page_number:
                    page_info = page_data
                    break
            
            # 使用頁面內容或 chunk 內容作為備用
            if page_info:
                page_original_content = page_info['original_content']
                page_normalized_content = page_info['normalized_content']
            else:
                page_original_content = chunk.page_content
                page_normalized_content = chunk.page_content
            
            # A欄：頁面原始內容
            self.worksheet.cell(row=current_row, column=1, value=page_original_content)
            
            # B欄：頁面正規化內容
            self.worksheet.cell(row=current_row, column=2, value=page_normalized_content)
            
            # C欄：分割後的 Chunk
            self.worksheet.cell(row=current_row, column=3, value=chunk.page_content)
            
            # D欄：Chunk 編號（使用全局編號）
            global_chunk_number = chunk.metadata.get('global_chunk_number', i)
            self.worksheet.cell(row=current_row, column=4, value=global_chunk_number)
            
            # E欄：Chunk 長度
            self.worksheet.cell(row=current_row, column=5, value=len(chunk.page_content))
            
            # F欄：包含標題
            has_headers = any(header in chunk.page_content for header in ['#', '##', '###', '####'])
            self.worksheet.cell(row=current_row, column=6, value="是" if has_headers else "否")
            
            # G欄：是否為表格
            is_table = chunk.metadata.get('is_table', False)
            self.worksheet.cell(row=current_row, column=7, value="是" if is_table else "否")
            
            # 展開的 metadata 欄位 (H欄開始)
            # H欄：檔名
            self.worksheet.cell(row=current_row, column=8, value=chunk.metadata.get('file_name', ''))
            
            # I欄：檔案類型
            self.worksheet.cell(row=current_row, column=9, value=chunk.metadata.get('file_type', ''))
            
            # J欄：來源路徑
            self.worksheet.cell(row=current_row, column=10, value=chunk.metadata.get('source', ''))
            
            # K欄：轉換器
            self.worksheet.cell(row=current_row, column=11, value=chunk.metadata.get('converter_used', ''))
            
            # L欄：總頁數
            self.worksheet.cell(row=current_row, column=12, value=chunk.metadata.get('total_pages', ''))
            
            # M欄：總表格數
            self.worksheet.cell(row=current_row, column=13, value=chunk.metadata.get('total_tables', ''))
            
            # N欄：頁碼
            self.worksheet.cell(row=current_row, column=14, value=chunk.metadata.get('page_number', ''))
            
            # O欄：頁面標題
            self.worksheet.cell(row=current_row, column=15, value=chunk.metadata.get('page_title', ''))
            
            # P欄：標題級數（合併四個標題欄位）
            header_level = self._get_header_level(chunk.metadata)
            self.worksheet.cell(row=current_row, column=16, value=header_level)
            
            # Q欄：表格合併數
            self.worksheet.cell(row=current_row, column=17, value=chunk.metadata.get('table_chunks_merged', ''))
            
            # R欄：完整元數據
            metadata_str = self._format_metadata(chunk.metadata)
            self.worksheet.cell(row=current_row, column=18, value=metadata_str)
            
            current_row += 1
        
        # 按頁碼分組合併 A欄 和 B欄 的單元格
        self._merge_cells_by_page(chunks)
    
    def _merge_cells_by_page(self, chunks: List[Document]):
        """按頁碼分組合併單元格"""
        # 按頁碼分組
        page_groups = {}
        for i, chunk in enumerate(chunks, 2):  # 從第2行開始
            page_number = chunk.metadata.get('page_number')
            # 如果沒有頁碼，使用 'no_page' 作為分組鍵
            if page_number is None:
                page_number = 'no_page'
            if page_number not in page_groups:
                page_groups[page_number] = []
            page_groups[page_number].append(i)
        
        # 為每個頁碼組合併單元格
        for page_number, rows in page_groups.items():
            if len(rows) > 1:
                start_row = min(rows)
                end_row = max(rows)
                self.worksheet.merge_cells(f'A{start_row}:A{end_row}')
                self.worksheet.merge_cells(f'B{start_row}:B{end_row}')
    
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """格式化元數據為字符串"""
        if not metadata:
            return "無"
        
        # 優先顯示重要信息
        important_keys = ['file_name', 'page_number', 'Header 1', 'Header 2', 'Header 3', 'Header 4', 'is_table']
        formatted_items = []
        
        # 先添加重要信息
        for key in important_keys:
            if key in metadata:
                value = metadata[key]
                if isinstance(value, (str, int, float, bool)):
                    formatted_items.append(f"{key}: {value}")
                else:
                    formatted_items.append(f"{key}: {str(value)[:30]}...")
        
        # 再添加其他信息
        for key, value in metadata.items():
            if key not in important_keys:
                if isinstance(value, (str, int, float, bool)):
                    formatted_items.append(f"{key}: {value}")
                else:
                    formatted_items.append(f"{key}: {str(value)[:30]}...")
        
        return "; ".join(formatted_items)
    
    def _get_header_level(self, metadata: Dict[str, Any]) -> str:
        """獲取標題級數（一、二、三、四）"""
        if 'Header 4' in metadata and metadata['Header 4']:
            return '四'
        elif 'Header 3' in metadata and metadata['Header 3']:
            return '三'
        elif 'Header 2' in metadata and metadata['Header 2']:
            return '二'
        elif 'Header 1' in metadata and metadata['Header 1']:
            return '一'
        else:
            return ''
    
    def _format_worksheet(self):
        """設置工作表格式"""
        # 設置列寬
        column_widths = {
            'A': 30,  # 原始內容
            'B': 30,  # 正規化後內容
            'C': 50,  # Chunk 內容
            'D': 10,  # 編號
            'E': 12,  # 長度
            'F': 12,  # 包含標題
            'G': 12,  # 是否表格
            'H': 25,  # 檔名
            'I': 12,  # 檔案類型
            'J': 30,  # 來源路徑
            'K': 12,  # 轉換器
            'L': 10,  # 總頁數
            'M': 12,  # 總表格數
            'N': 10,  # 頁碼
            'O': 20,  # 頁面標題
            'P': 12,  # 標題級數
            'Q': 12,  # 表格合併數
            'R': 30   # 完整元數據
        }
        
        for col, width in column_widths.items():
            self.worksheet.column_dimensions[col].width = width
        
        # 設置邊框
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # 為所有數據單元格設置邊框
        for row in self.worksheet.iter_rows(min_row=1, max_row=self.worksheet.max_row):
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(vertical='top', wrap_text=True)
        
        # 設置 A欄 和 B欄 的對齊方式（合併的單元格）
        for row in range(2, self.worksheet.max_row + 1):
            # A欄：原始內容
            cell_a = self.worksheet.cell(row=row, column=1)
            cell_a.alignment = Alignment(vertical='top', horizontal='left', wrap_text=True)
            
            # B欄：正規化後內容
            cell_b = self.worksheet.cell(row=row, column=2)
            cell_b.alignment = Alignment(vertical='top', horizontal='left', wrap_text=True)
    
    def create_summary_sheet(self, chunks: List[Document], output_path: str):
        """創建統計摘要工作表"""
        if not self.workbook:
            self.workbook = Workbook()
        
        # 創建摘要工作表
        summary_sheet = self.workbook.create_sheet("統計摘要")
        
        # 統計信息
        total_chunks = len(chunks)
        total_length = sum(len(chunk.page_content) for chunk in chunks)
        avg_length = total_length / total_chunks if total_chunks > 0 else 0
        table_chunks = sum(1 for chunk in chunks if chunk.metadata.get('is_table', False))
        
        # 填充統計信息
        stats = [
            ("總 Chunk 數量", total_chunks),
            ("總字符數", total_length),
            ("平均 Chunk 長度", round(avg_length, 2)),
            ("表格 Chunk 數量", table_chunks),
            ("一般 Chunk 數量", total_chunks - table_chunks),
            ("表格比例", f"{round(table_chunks / total_chunks * 100, 2)}%" if total_chunks > 0 else "0%")
        ]
        
        for i, (label, value) in enumerate(stats, 1):
            summary_sheet.cell(row=i, column=1, value=label).font = summary_sheet.cell(row=i, column=1).font.copy(bold=True)
            summary_sheet.cell(row=i, column=2, value=value)
        
        # 保存文件
        self.workbook.save(output_path)
        logger.info(f"Summary sheet added to: {output_path}")
