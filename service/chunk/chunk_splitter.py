"""
Chunk 分割器

基於 LangChain 的 MarkdownHeaderTextSplitter 和 RecursiveCharacterTextSplitter
實現智能的 Markdown 分割功能。
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Union, Optional, Dict, Any
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from ..markdown_integrate.data_models import ConversionResult
from .table_handler import TableHandler
from .markdown_normalizer import MarkdownNormalizer
from .excel_exporter import ExcelExporter

logger = logging.getLogger(__name__)


class ChunkSplitter:
    """智能 Markdown 分割器"""
    
    def __init__(self, 
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 headers_to_split_on: Optional[List[tuple]] = None,
                 keep_tables_together: bool = True,
                 normalize_output: bool = True,
                 output_base_dir: str = "service/output"):
        """
        初始化分割器
        
        Args:
            chunk_size: 每個 chunk 的最大字符數
            chunk_overlap: chunk 之間的重疊字符數
            headers_to_split_on: 要分割的標題層級
            keep_tables_together: 是否保持表格完整性
            normalize_output: 是否正規化輸出內容
            output_base_dir: 輸出基礎目錄
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.keep_tables_together = keep_tables_together
        self.normalize_output = normalize_output
        self.output_base_dir = output_base_dir
        
        # 預設的標題分割層級
        if headers_to_split_on is None:
            self.headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
                ("####", "Header 4"),
            ]
        else:
            self.headers_to_split_on = headers_to_split_on
        
        # 初始化分割器
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False  # 保留標題用於上下文
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # 初始化表格處理器
        self.table_handler = TableHandler()
        
        # 初始化正規化器
        if self.normalize_output:
            self.normalizer = MarkdownNormalizer()
        else:
            self.normalizer = None
        
        logger.info(f"ChunkSplitter initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, normalize_output={normalize_output}")
    
    def split_markdown(self, 
                      input_data: Union[str, Path, ConversionResult],
                      output_excel: bool = False,
                      output_path: Optional[str] = None,
                      md_output_path: Optional[str] = None) -> List[Document]:
        """
        分割 Markdown 內容
        
        Args:
            input_data: 輸入數據（MD文件 路徑或 ConversionResult 對象）
            output_excel: 是否輸出報告 Excel 文件
            output_path: Excel 輸出路徑
            md_output_path: Markdown 輸出路徑
            
        Returns:
            List[Document]: 分割後的文檔列表
        """
        # 如果是 ConversionResult，檢查是否有頁面信息
        if isinstance(input_data, ConversionResult):
            # 檢查是否有頁面信息
            if input_data.pages and len(input_data.pages) > 0:
                # 有頁面信息，使用頁面分割
                return self._split_by_pages(input_data, output_excel, output_path, md_output_path)
            else:
                # 沒有頁面信息（如 Excel 文件），使用基本分割
                return self._split_without_pages(input_data, output_excel, output_path, md_output_path)
        
        # 獲取 Markdown 內容
        markdown_content, metadata = self._extract_content(input_data)
        
        # 保存原始內容用於 Excel 導出
        original_content = markdown_content
        
        # 正規化內容（在分割之前）
        normalized_content = None
        if self.normalize_output and self.normalizer:
            normalized_content = self.normalizer.normalize_text(markdown_content)
            markdown_content = normalized_content
            logger.info("Content normalized before splitting")
        
        # 如果啟用表格保持完整性，先處理表格
        if self.keep_tables_together:
            markdown_content = self.table_handler.mark_tables(markdown_content)
        
        # 使用 MarkdownHeaderTextSplitter 進行初步分割
        header_splits = self.markdown_splitter.split_text(markdown_content)
        
        # 對每個分割後的文檔進行進一步分割
        final_chunks = []
        for doc in header_splits:
            # 如果文檔太大，使用 RecursiveCharacterTextSplitter 進一步分割
            if len(doc.page_content) > self.chunk_size:
                sub_chunks = self.text_splitter.split_documents([doc])
                # 為每個子 chunk 添加檔名和頁碼信息
                enhanced_sub_chunks = self._enhance_chunks_with_metadata(sub_chunks, metadata)
                final_chunks.extend(enhanced_sub_chunks)
            else:
                # 為單個 chunk 添加檔名和頁碼信息
                enhanced_chunk = self._enhance_chunk_with_metadata(doc, metadata)
                final_chunks.append(enhanced_chunk)
        
        # 後處理：確保表格完整性
        if self.keep_tables_together:
            final_chunks = self._postprocess_tables(final_chunks)
        
        logger.info(f"Split markdown into {len(final_chunks)} chunks")
        
        # 輸出處理
        if output_excel:
            self._export_to_excel(final_chunks, original_content, output_path, normalized_content)
        
        if md_output_path:
            self._export_to_markdown(final_chunks, md_output_path)
        
        return final_chunks
    
    def _split_by_pages(self, 
                       conversion_result: ConversionResult,
                       output_excel: bool = False,
                       output_path: Optional[str] = None,
                       md_output_path: Optional[str] = None) -> List[Document]:
        """
        基於頁面分割 Markdown 內容
        
        Args:
            conversion_result: ConversionResult 對象
            output_excel: 是否輸出 Excel 文件
            output_path: Excel 輸出路徑
            md_output_path: Markdown 輸出路徑
            
        Returns:
            List[Document]: 分割後的文檔列表
        """
        all_chunks = []
        page_chunks_info = []  # 儲存每頁的 chunks 信息
        
        # 為每個頁面分割內容
        for page in conversion_result.pages:
            page_content = page.content
            original_page_content = page_content  # 保存原始頁面內容
            
            # 正規化頁面內容
            normalized_page_content = None
            if self.normalize_output and self.normalizer:
                normalized_page_content = self.normalizer.normalize_text(page_content)
                page_content = normalized_page_content
            
            # 標記表格
            if self.keep_tables_together:
                page_content = self.table_handler.mark_tables(page_content)
            
            # 使用 MarkdownHeaderTextSplitter 分割頁面
            page_splits = self.markdown_splitter.split_text(page_content)
            
            # 對頁面分割結果進行進一步處理
            page_chunks = []
            for doc in page_splits:
                if len(doc.page_content) > self.chunk_size:
                    # 如果太大，進一步分割
                    sub_chunks = self.text_splitter.split_documents([doc])
                    for sub_chunk in sub_chunks:
                        # 為每個子 chunk 添加頁碼信息
                        enhanced_chunk = self._enhance_chunk_with_page_info(sub_chunk, page, conversion_result)
                        all_chunks.append(enhanced_chunk)
                        page_chunks.append(enhanced_chunk)
                else:
                    # 直接添加頁碼信息
                    enhanced_chunk = self._enhance_chunk_with_page_info(doc, page, conversion_result)
                    all_chunks.append(enhanced_chunk)
                    page_chunks.append(enhanced_chunk)
            
            # 儲存頁面 chunks 信息
            page_chunks_info.append({
                'page_number': page.page_number,
                'original_content': original_page_content,
                'normalized_content': normalized_page_content,
                'chunks': page_chunks
            })
        
        # 後處理：確保表格完整性
        if self.keep_tables_together:
            all_chunks = self._postprocess_tables(all_chunks)
        
        # 合併過短的 chunks（通常是標題）
        all_chunks = self._merge_short_chunks(all_chunks)
        
        logger.info(f"Split {len(conversion_result.pages)} pages into {len(all_chunks)} chunks")
        
        # 輸出處理
        if output_excel:
            self._export_to_excel_with_page_info(all_chunks, page_chunks_info, output_path)
        
        if md_output_path:
            self._export_to_markdown(all_chunks, md_output_path)
        
        return all_chunks
    
    def _merge_short_chunks(self, chunks: List[Document], min_length: int = 30) -> List[Document]:
        """
        合併過短的 chunks（通常是標題）
        
        Args:
            chunks: 分割後的文檔列表
            min_length: 最小長度閾值
            
        Returns:
            List[Document]: 合併後的文檔列表
        """
        if not chunks:
            return chunks
        
        merged_chunks = []
        i = 0
        
        while i < len(chunks):
            current_chunk = chunks[i]
            
            # 如果當前 chunk 太短，嘗試與下一個 chunk 合併
            if len(current_chunk.page_content.strip()) < min_length and i + 1 < len(chunks):
                next_chunk = chunks[i + 1]
                
                # 檢查是否為同一頁面
                if (current_chunk.metadata.get('page_number') == next_chunk.metadata.get('page_number')):
                    # 合併內容
                    merged_content = current_chunk.page_content + '\n\n' + next_chunk.page_content
                    
                    # 合併 metadata（保留更完整的標題信息）
                    merged_metadata = current_chunk.metadata.copy()
                    for key, value in next_chunk.metadata.items():
                        if key not in merged_metadata or not merged_metadata[key]:
                            merged_metadata[key] = value
                        elif key.startswith('Header') and value and not merged_metadata[key]:
                            merged_metadata[key] = value
                    
                    # 創建合併後的 chunk
                    merged_chunk = Document(
                        page_content=merged_content,
                        metadata=merged_metadata
                    )
                    merged_chunks.append(merged_chunk)
                    i += 2  # 跳過下一個 chunk
                else:
                    # 不同頁面，保留當前 chunk
                    merged_chunks.append(current_chunk)
                    i += 1
            else:
                # 長度足夠或沒有下一個 chunk，保留當前 chunk
                merged_chunks.append(current_chunk)
                i += 1
        
        logger.info(f"Merged short chunks: {len(chunks)} -> {len(merged_chunks)}")
        return merged_chunks
    
    def _enhance_chunk_with_page_info(self, chunk: Document, page: 'PageInfo', conversion_result: ConversionResult) -> Document:
        """為 chunk 添加頁碼、頁面標題和文件信息"""
        enhanced_metadata = chunk.metadata.copy()
        
        # 添加頁碼信息
        enhanced_metadata['page_number'] = page.page_number
        
        # 添加頁面標題信息
        enhanced_metadata['page_title'] = page.title if page.title else None
        
        # 添加文件信息
        enhanced_metadata.update({
            'file_name': conversion_result.metadata.file_name,
            'file_type': conversion_result.metadata.file_type,
            'source': conversion_result.metadata.file_path,
            'converter_used': conversion_result.metadata.converter_used,
            'total_pages': conversion_result.metadata.total_pages,
            'total_tables': conversion_result.metadata.total_tables,
            'file_size': conversion_result.metadata.file_size,
            'conversion_timestamp': conversion_result.metadata.conversion_timestamp
        })
        
        return Document(page_content=chunk.page_content, metadata=enhanced_metadata)
    
    def _export_to_excel_with_page_info(self, chunks: List[Document], page_chunks_info: List[Dict], output_path: Optional[str]):
        """導出到 Excel，使用按頁面分割的原始和正規化內容"""
        from .excel_exporter import ExcelExporter
        
        if output_path is None:
            output_path = f"{self.output_base_dir}/chunk/chunks.xlsx"
        
        # 創建 Excel 導出器
        exporter = ExcelExporter()
        
        # 直接使用修改後的 Excel 導出器，傳遞頁面信息
        exporter.export_chunks_to_excel_with_page_content(chunks, page_chunks_info, output_path)
        logger.info(f"Chunks exported to Excel: {output_path}")
    
    def _extract_content(self, input_data: Union[str, Path, ConversionResult]) -> tuple[str, Dict[str, Any]]:
        """提取 Markdown 內容和元數據"""
        if isinstance(input_data, (str, Path)):
            # 文件路徑輸入
            file_path = Path(input_data)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {
                'source': str(file_path),
                'file_name': file_path.name,
                'file_type': file_path.suffix
            }
            
        elif isinstance(input_data, ConversionResult):
            # ConversionResult 對象輸入
            content = input_data.content
            metadata = {
                'source': input_data.metadata.file_path,
                'file_name': input_data.metadata.file_name,
                'file_type': input_data.metadata.file_type,
                'converter_used': input_data.metadata.converter_used,
                'total_pages': input_data.metadata.total_pages,
                'total_tables': input_data.metadata.total_tables,
                'file_size': input_data.metadata.file_size,
                'conversion_timestamp': input_data.metadata.conversion_timestamp
            }
            
            # 保存 ConversionResult 對象以便後續使用
            self._conversion_result = input_data
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}")
        
        return content, metadata
    
    def _enhance_chunk_with_metadata(self, chunk: Document, base_metadata: Dict[str, Any]) -> Document:
        """為單個 chunk 添加檔名和頁碼信息"""
        enhanced_metadata = chunk.metadata.copy()
        
        # 添加檔名和基本信息
        enhanced_metadata.update({
            'file_name': base_metadata.get('file_name', ''),
            'file_type': base_metadata.get('file_type', ''),
            'source': base_metadata.get('source', ''),
            'converter_used': base_metadata.get('converter_used', ''),
            'total_pages': base_metadata.get('total_pages', 0),
            'total_tables': base_metadata.get('total_tables', 0)
        })
        
        # 如果有 ConversionResult，嘗試推斷頁碼
        if hasattr(self, '_conversion_result') and self._conversion_result:
            page_number = self._estimate_page_number(chunk.page_content)
            if page_number:
                enhanced_metadata['page_number'] = page_number
        
        return Document(page_content=chunk.page_content, metadata=enhanced_metadata)
    
    def _enhance_chunks_with_metadata(self, chunks: List[Document], base_metadata: Dict[str, Any]) -> List[Document]:
        """為多個 chunks 添加檔名和頁碼信息"""
        enhanced_chunks = []
        for chunk in chunks:
            enhanced_chunk = self._enhance_chunk_with_metadata(chunk, base_metadata)
            enhanced_chunks.append(enhanced_chunk)
        return enhanced_chunks
    
    def _estimate_page_number(self, content: str) -> Optional[int]:
        """根據內容推斷頁碼"""
        if not hasattr(self, '_conversion_result') or not self._conversion_result:
            return None
        
        # 如果有頁面信息，嘗試匹配內容
        if self._conversion_result.pages:
            best_match = None
            best_score = 0
            
            for page in self._conversion_result.pages:
                # 計算內容相似度
                score = self._calculate_content_similarity(content, page.content)
                if score > best_score and score > 0.3:  # 閾值設為30%
                    best_score = score
                    best_match = page.page_number
            
            return best_match
        
        return None
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """計算兩個內容的相似度"""
        if not content1 or not content2:
            return 0.0
        
        # 提取關鍵詞進行匹配
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # 計算交集和聯集
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        # Jaccard 相似度
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _postprocess_tables(self, chunks: List[Document]) -> List[Document]:
        """後處理表格，確保表格完整性"""
        # 分離表格和一般 chunks
        table_chunks, regular_chunks = self.table_handler.extract_table_chunks(chunks)
        
        # 合併表格 chunks
        merged_table_chunks = self.table_handler.merge_table_chunks(table_chunks)
        
        # 清理一般 chunks 中的表格標記
        cleaned_regular_chunks = []
        for chunk in regular_chunks:
            cleaned_content = self.table_handler.clean_table_markers(chunk.page_content)
            cleaned_regular_chunks.append(Document(
                page_content=cleaned_content,
                metadata=chunk.metadata
            ))
        
        # 合併所有 chunks
        all_chunks = cleaned_regular_chunks + merged_table_chunks
        
        # 按原始順序排序（如果需要）
        return all_chunks
    
    
    def _export_to_excel(self, chunks: List[Document], original_content: str, output_path: Optional[str], normalized_content: Optional[str] = None):
        """導出到 Excel 文件"""
        from .excel_exporter import ExcelExporter
        
        if output_path is None:
            output_path = f"{self.output_base_dir}/chunk/chunks.xlsx"
        
        exporter = ExcelExporter()
        exporter.export_chunks_to_excel(chunks, original_content, output_path, normalized_content)
        logger.info(f"Chunks exported to Excel: {output_path}")
    
    def _export_to_markdown(self, chunks: List[Document], output_path: str):
        """導出到 Markdown 文件"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, chunk in enumerate(chunks, 1):
                f.write(f"## Chunk {i}\n\n")
                f.write(f"**Metadata:** {chunk.metadata}\n\n")
                f.write(f"{chunk.page_content}\n\n")
                f.write("---\n\n")
        
        logger.info(f"Chunks exported to Markdown: {output_path}")
    
    def get_chunk_statistics(self, chunks: List[Document]) -> Dict[str, Any]:
        """獲取分割統計信息"""
        total_chunks = len(chunks)
        total_length = sum(len(chunk.page_content) for chunk in chunks)
        avg_length = total_length / total_chunks if total_chunks > 0 else 0
        
        # 統計包含表格的 chunks
        table_chunks = sum(1 for chunk in chunks if chunk.metadata.get('is_table', False))
        
        return {
            'total_chunks': total_chunks,
            'total_length': total_length,
            'average_length': avg_length,
            'table_chunks': table_chunks,
            'regular_chunks': total_chunks - table_chunks
        }
    
    def _split_without_pages(self, 
                           conversion_result: ConversionResult,
                           output_excel: bool = False,
                           output_path: Optional[str] = None,
                           md_output_path: Optional[str] = None) -> List[Document]:
        """
        處理沒有頁面結構的 ConversionResult（如 Excel 文件）
        
        Args:
            conversion_result: ConversionResult 對象（沒有頁面信息）
            output_excel: 是否輸出 Excel 文件
            output_path: Excel 輸出路徑
            md_output_path: Markdown 輸出路徑
            
        Returns:
            List[Document]: 分割後的文檔列表
        """
        logger.info("Processing ConversionResult without page structure")
        
        # 獲取完整內容
        markdown_content = conversion_result.content
        original_content = markdown_content
        
        # 正規化內容（在分割之前）
        normalized_content = None
        if self.normalize_output and self.normalizer:
            normalized_content = self.normalizer.normalize_text(markdown_content)
            markdown_content = normalized_content
            logger.info("Content normalized before splitting")
        
        # 如果啟用表格保持完整性，先處理表格
        if self.keep_tables_together:
            markdown_content = self.table_handler.mark_tables(markdown_content)
        
        # 使用 MarkdownHeaderTextSplitter 進行初步分割
        header_splits = self.markdown_splitter.split_text(markdown_content)
        
        # 對每個分割後的文檔進行進一步分割
        final_chunks = []
        for doc in header_splits:
            # 如果文檔太大，使用 RecursiveCharacterTextSplitter 進一步分割
            if len(doc.page_content) > self.chunk_size:
                sub_chunks = self.text_splitter.split_documents([doc])
                # 為每個子 chunk 添加基本 metadata（無頁碼）
                enhanced_sub_chunks = self._enhance_chunks_without_pages(sub_chunks, conversion_result)
                final_chunks.extend(enhanced_sub_chunks)
            else:
                # 為單個 chunk 添加基本 metadata（無頁碼）
                enhanced_chunk = self._enhance_chunk_without_pages(doc, conversion_result)
                final_chunks.append(enhanced_chunk)
        
        # 後處理：確保表格完整性
        if self.keep_tables_together:
            final_chunks = self._postprocess_tables(final_chunks)
        
        # 合併過短的 chunks（通常是標題）
        final_chunks = self._merge_short_chunks(final_chunks)
        
        logger.info(f"Split content without pages into {len(final_chunks)} chunks")
        
        # 輸出處理
        if output_excel:
            self._export_to_excel_without_pages(final_chunks, original_content, normalized_content, output_path)
        
        if md_output_path:
            self._export_to_markdown(final_chunks, md_output_path)
        
        return final_chunks
    
    def _enhance_chunk_without_pages(self, chunk: Document, conversion_result: ConversionResult) -> Document:
        """
        為沒有頁面結構的 chunk 添加基本 metadata
        
        Args:
            chunk: 要增強的 chunk
            conversion_result: 轉換結果對象
            
        Returns:
            Document: 增強後的 chunk
        """
        # 基本文件信息
        chunk.metadata.update({
            'file_name': conversion_result.metadata.file_name,
            'file_type': conversion_result.metadata.file_type,
            'source': conversion_result.metadata.file_path,
            'converter_used': conversion_result.metadata.converter_used,
            'total_pages': conversion_result.metadata.total_pages,
            'total_tables': conversion_result.metadata.total_tables,
            # 注意：沒有 page_number，因為沒有頁面結構
        })
        
        return chunk
    
    def _enhance_chunks_without_pages(self, chunks: List[Document], conversion_result: ConversionResult) -> List[Document]:
        """
        為沒有頁面結構的多個 chunks 添加基本 metadata
        
        Args:
            chunks: 要增強的 chunks 列表
            conversion_result: 轉換結果對象
            
        Returns:
            List[Document]: 增強後的 chunks 列表
        """
        return [self._enhance_chunk_without_pages(chunk, conversion_result) for chunk in chunks]
    
    def _export_to_excel_without_pages(self, 
                                     chunks: List[Document], 
                                     original_content: str,
                                     normalized_content: Optional[str],
                                     output_path: str):
        """
        導出沒有頁面結構的 chunks 到 Excel
        
        Args:
            chunks: 要導出的 chunks
            original_content: 原始內容
            normalized_content: 正規化內容
            output_path: 輸出路徑
        """
        # 創建 Excel 導出器
        exporter = ExcelExporter()
        
        # 準備頁面信息（模擬單一頁面）
        page_chunks_info = [{
            'page_number': None,  # 沒有頁碼
            'original_content': original_content,
            'normalized_content': normalized_content or original_content,
            'chunks': chunks
        }]
        
        # 導出到 Excel
        exporter.export_chunks_to_excel_with_page_content(chunks, page_chunks_info, output_path)
        logger.info(f"Chunks exported to Excel: {output_path}")
