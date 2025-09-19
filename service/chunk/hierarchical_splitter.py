"""
分層Chunk分割器

實現基於LangChain ParentDocumentRetriever模式的分層分割功能，
使用物件清楚表達中間傳遞的資料。
"""

import os
import re
import logging
import uuid
from pathlib import Path
from typing import List, Union, Optional, Dict, Any, Tuple
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from ..markdown_integrate.data_models import ConversionResult
from ..serialization import ConversionDeserializer
from .table_handler import TableHandler
from .markdown_normalizer import MarkdownNormalizer
from .excel_exporter import ExcelExporter
from .hierarchical_models import (
    ParentChunk, ChildChunk, GroupingAnalysis, HierarchicalSplitResult,
    SizeDistribution, TableHandlingStats
)

logger = logging.getLogger(__name__)


class HierarchicalChunkSplitter:
    """分層Chunk分割器 - 實現ParentDocumentRetriever模式"""
    
    def __init__(self, 
                 parent_chunk_size: int = 2000,
                 parent_chunk_overlap: int = 200,
                 child_chunk_size: int = 350,
                 child_chunk_overlap: int = 50,
                 headers_to_split_on: Optional[List[tuple]] = None,
                 keep_tables_together: bool = True,
                 normalize_output: bool = True,
                 output_base_dir: str = "service/output"):
        """
        初始化分層分割器 - 針對中文優化
        
        Args:
            parent_chunk_size: 父層chunk大小 (預設2000字，適合中文32k embedding)
            parent_chunk_overlap: 父層chunk重疊大小 (預設200字，保持中文語義連貫性)
            child_chunk_size: 子層chunk大小 (預設350字，約100-150 tokens，適合中文rerank 512)
            child_chunk_overlap: 子層chunk重疊大小 (預設50字，保持中文語義連貫性)
            headers_to_split_on: 要分割的標題層級
            keep_tables_together: 是否保持表格完整性
            normalize_output: 是否正規化輸出內容
            output_base_dir: 輸出基礎目錄
        """
        self.parent_chunk_size = parent_chunk_size
        self.parent_chunk_overlap = parent_chunk_overlap
        self.child_chunk_size = child_chunk_size
        self.child_chunk_overlap = child_chunk_overlap
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
        self.parent_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False  # 保留標題用於上下文
        )
        
        # 父層進一步分割器（當父chunk太大時使用）
        self.parent_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=parent_chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=child_chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # 初始化表格處理器
        self.table_handler = TableHandler()
        
        # 初始化正規化器
        if self.normalize_output:
            self.normalizer = MarkdownNormalizer()
        else:
            self.normalizer = None
        
        logger.info(f"HierarchicalChunkSplitter initialized")
        logger.info(f"Parent chunk size: {parent_chunk_size}, Child chunk size: {child_chunk_size}")
        logger.info(f"Child chunk overlap: {child_chunk_overlap}, Normalize output: {normalize_output}")
    
    def split_hierarchically(self, 
                           input_data: Union[str, Path, ConversionResult],
                           output_excel: bool = False,
                           output_path: Optional[str] = None,
                           md_output_path: Optional[str] = None,
                           from_serialization: bool = False) -> HierarchicalSplitResult:
        """
        分層分割文檔
        
        Args:
            input_data: 輸入數據（MD文件路徑、ConversionResult對象或序列化文件路徑）
            output_excel: 是否輸出Excel文件
            output_path: Excel輸出路徑
            md_output_path: Markdown輸出路徑
            from_serialization: 是否從序列化文件載入ConversionResult
            
        Returns:
            HierarchicalSplitResult: 分層分割結果
        """
        logger.info("Starting hierarchical splitting...")
        
        # 處理序列化文件載入
        if from_serialization and isinstance(input_data, (str, Path)):
            input_data = self._load_from_serialization(input_data)
        
        # 如果是ConversionResult，檢查是否有頁面信息
        if isinstance(input_data, ConversionResult):
            if input_data.pages and len(input_data.pages) > 0:
                # 有頁面信息，使用頁面分割
                return self._split_by_pages_hierarchically(input_data, output_excel, output_path, md_output_path)
            else:
                # 沒有頁面信息，使用基本分割
                return self._split_without_pages_hierarchically(input_data, output_excel, output_path, md_output_path)
        
        # 獲取Markdown內容
        markdown_content, metadata = self._extract_content(input_data)
        
        print(f"DEBUG: Starting split_markdown with keep_tables_together={self.keep_tables_together}")
        
        # 正規化內容
        normalized_content = None
        if self.normalize_output and self.normalizer:
            normalized_content = self.normalizer.normalize_text(markdown_content)
            markdown_content = normalized_content
            logger.info("Content normalized before splitting")
        
        # 如果啟用表格保持完整性，先處理表格
        if self.keep_tables_together:
            print("DEBUG: Marking tables in content")
            markdown_content = self.table_handler.mark_tables(markdown_content)
        
        # 1. Parent層分割
        parent_documents = self.parent_splitter.split_text(markdown_content)
        parent_chunks = self._create_parent_chunks(parent_documents, metadata)
        
        # 2. Child層分割
        child_chunks = self._create_child_chunks(parent_chunks)
        
        # 3. 後處理：確保表格完整性
        if self.keep_tables_together:
            print(f"DEBUG: Cleaning table markers from {len(parent_chunks)} parent chunks")
            logger.info(f"Cleaning table markers from {len(parent_chunks)} parent chunks")
            # 清理父chunks中的表格標記
            parent_chunks = self._clean_parent_table_markers(parent_chunks)
            child_chunks = self._postprocess_tables(child_chunks)
        
        # 4. 分析分組情況
        grouping_analysis = self._analyze_grouping(parent_chunks, child_chunks)
        
        # 5. 創建結果物件
        result = HierarchicalSplitResult(
            parent_chunks=parent_chunks,
            child_chunks=child_chunks,
            grouping_analysis=grouping_analysis,
            processing_metadata={
                'input_type': type(input_data).__name__,
                'normalized': self.normalize_output,
                'tables_handled': self.keep_tables_together,
                'processing_timestamp': self._get_timestamp()
            }
        )
        
        # 6. 輸出處理
        if output_excel:
            self._export_to_excel(result, markdown_content, output_path, normalized_content)
        
        if md_output_path:
            self._export_to_markdown(result, md_output_path)
        
        logger.info(f"Hierarchical splitting completed: {len(parent_chunks)} parent chunks, {len(child_chunks)} child chunks")
        return result
    
    def _create_parent_chunks(self, parent_documents: List[Document], base_metadata: Dict[str, Any]) -> List[ParentChunk]:
        """創建父層chunks"""
        parent_chunks = []
        
        for i, doc in enumerate(parent_documents):
            # 如果父chunk太大，需要進一步分割
            if len(doc.page_content) > self.parent_chunk_size:
                # 使用parent_text_splitter分割
                sub_documents = self.parent_text_splitter.split_documents([doc])
                
                for j, sub_doc in enumerate(sub_documents):
                    # 生成唯一ID
                    chunk_id = f"parent_{uuid.uuid4().hex[:8]}"
                    
                    # 創建ParentChunk物件
                    parent_chunk = ParentChunk(
                        document=sub_doc,
                        chunk_id=chunk_id,
                        parent_index=i,
                        size=len(sub_doc.page_content),
                        metadata=base_metadata.copy()
                    )
                    
                    parent_chunks.append(parent_chunk)
            else:
                # 父chunk大小合適，直接使用
                chunk_id = f"parent_{uuid.uuid4().hex[:8]}"
                
                parent_chunk = ParentChunk(
                    document=doc,
                    chunk_id=chunk_id,
                    parent_index=i,
                    size=len(doc.page_content),
                    metadata=base_metadata.copy()
                )
                
                parent_chunks.append(parent_chunk)
        
        logger.info(f"Created {len(parent_chunks)} parent chunks")
        return parent_chunks
    
    def _create_child_chunks(self, parent_chunks: List[ParentChunk]) -> List[ChildChunk]:
        """創建子層chunks - 參考chunk_splitter.py的邏輯"""
        child_chunks = []
        
        for parent_chunk in parent_chunks:
            # 在切割子chunk前，先清理表格分隔符
            cleaned_content = self.table_handler.clean_table_separators(parent_chunk.document.page_content)
            
            # 如果內容被清理後變空或太短，跳過這個父chunk
            if not cleaned_content.strip() or len(cleaned_content.strip()) < 10:
                logger.warning(f"Skipping parent chunk {parent_chunk.chunk_id} after cleaning: content too short")
                continue
            
            # 創建清理後的Document
            cleaned_document = Document(
                page_content=cleaned_content,
                metadata=parent_chunk.document.metadata.copy()
            )
            
            # 對每個父chunk進行子分割，不管大小
            # 使用child_splitter分割
            sub_documents = self.child_splitter.split_documents([cleaned_document])
            
            for j, sub_doc in enumerate(sub_documents):
                # 再次清理子chunk中的表格分隔符
                final_content = self.table_handler.clean_table_separators(sub_doc.page_content)
                
                # 如果子chunk內容太短，跳過
                if not final_content.strip() or len(final_content.strip()) < 5:
                    logger.warning(f"Skipping child chunk {j} from parent {parent_chunk.chunk_id}: content too short after cleaning")
                    continue
                
                # 創建最終的Document
                final_document = Document(
                    page_content=final_content,
                    metadata=sub_doc.metadata.copy()
                )
                
                # 生成唯一ID
                child_id = f"child_{uuid.uuid4().hex[:8]}"
                
                # 創建ChildChunk物件
                child_chunk = ChildChunk(
                    document=final_document,
                    chunk_id=child_id,
                    parent_chunk_id=parent_chunk.chunk_id,
                    child_index=j,
                    size=len(final_content),
                    metadata=parent_chunk.metadata.copy()
                )
                
                child_chunks.append(child_chunk)
        
        logger.info(f"Created {len(child_chunks)} child chunks from {len(parent_chunks)} parent chunks")
        return child_chunks
    
    def _analyze_grouping(self, parent_chunks: List[ParentChunk], child_chunks: List[ChildChunk]) -> GroupingAnalysis:
        """分析分組情況"""
        logger.info("Analyzing grouping...")
        
        # 計算大小統計
        parent_sizes = [chunk.size for chunk in parent_chunks]
        child_sizes = [chunk.size for chunk in child_chunks]
        
        parent_size_stats = SizeDistribution.from_sizes(parent_sizes)
        child_size_stats = SizeDistribution.from_sizes(child_sizes)
        
        # 表格處理統計
        table_handling_stats = TableHandlingStats.from_chunks(child_chunks)
        
        # 計算分組效率
        grouping_efficiency = self._calculate_grouping_efficiency(parent_chunks, child_chunks)
        
        # 大小分佈
        size_distribution = self._calculate_size_distribution(child_sizes)
        
        analysis = GroupingAnalysis(
            total_parent_chunks=len(parent_chunks),
            total_child_chunks=len(child_chunks),
            avg_children_per_parent=len(child_chunks) / len(parent_chunks) if parent_chunks else 0,
            parent_size_stats={
                'min': parent_size_stats.min_size,
                'max': parent_size_stats.max_size,
                'avg': parent_size_stats.avg_size,
                'median': parent_size_stats.median_size
            },
            child_size_stats={
                'min': child_size_stats.min_size,
                'max': child_size_stats.max_size,
                'avg': child_size_stats.avg_size,
                'median': child_size_stats.median_size
            },
            table_handling_stats={
                'total_table_chunks': table_handling_stats.total_table_chunks,
                'total_regular_chunks': table_handling_stats.total_regular_chunks,
                'table_chunk_ratio': table_handling_stats.table_chunk_ratio,
                'avg_table_size': table_handling_stats.avg_table_size,
                'largest_table_size': table_handling_stats.largest_table_size,
                'table_fragmentation_count': table_handling_stats.table_fragmentation_count
            },
            grouping_efficiency=grouping_efficiency,
            size_distribution=size_distribution
        )
        
        logger.info(f"Grouping analysis completed: {analysis.avg_children_per_parent:.2f} children per parent")
        return analysis
    
    def _calculate_grouping_efficiency(self, parent_chunks: List[ParentChunk], child_chunks: List[ChildChunk]) -> float:
        """計算分組效率"""
        if not parent_chunks or not child_chunks:
            return 0.0
        
        # 計算理想分組效率（基於大小比例）
        total_parent_size = sum(chunk.size for chunk in parent_chunks)
        total_child_size = sum(chunk.size for chunk in child_chunks)
        
        # 避免重複計算，理想情況下child_size應該接近parent_size
        if total_parent_size == 0:
            return 0.0
        
        # 計算實際分組與理想分組的差異
        ideal_ratio = total_parent_size / len(parent_chunks)
        actual_avg_child = total_child_size / len(child_chunks)
        
        # 效率 = 1 - |實際 - 理想| / 理想
        efficiency = 1 - abs(actual_avg_child - ideal_ratio) / ideal_ratio
        return max(0.0, min(1.0, efficiency))
    
    def _calculate_size_distribution(self, sizes: List[int]) -> Dict[str, int]:
        """計算大小分佈"""
        ranges = [(0, 200), (200, 400), (400, 600), (600, 800), (800, 1000), (1000, float('inf'))]
        distribution = {}
        
        for range_min, range_max in ranges:
            range_key = f"{range_min}-{range_max if range_max != float('inf') else '∞'}"
            count = sum(1 for size in sizes if range_min <= size < range_max)
            distribution[range_key] = count
        
        return distribution
    
    def _postprocess_tables(self, child_chunks: List[ChildChunk]) -> List[ChildChunk]:
        """後處理表格，確保表格完整性 - 分層分割版本，保持更多子chunks"""
        # 分離表格和一般chunks
        table_chunks = [chunk for chunk in child_chunks if chunk.is_table_chunk]
        regular_chunks = [chunk for chunk in child_chunks if not chunk.is_table_chunk]
        
        # 對於分層分割，我們只合併非常小的表格chunks，保持大部分子chunks
        merged_table_chunks = self._merge_small_table_chunks_only(table_chunks)
        
        # 清理一般chunks中的表格標記和分隔符
        cleaned_regular_chunks = []
        for chunk in regular_chunks:
            # 先清理表格標記
            cleaned_content = self.table_handler.clean_table_markers(chunk.document.page_content)
            # 再清理表格分隔符
            cleaned_content = self.table_handler.clean_table_separators(cleaned_content)
            
            # 如果內容太短，跳過
            if not cleaned_content.strip() or len(cleaned_content.strip()) < 5:
                logger.warning(f"Skipping regular chunk {chunk.chunk_id}: content too short after cleaning")
                continue
                
            chunk.document = Document(page_content=cleaned_content, metadata=chunk.document.metadata)
            cleaned_regular_chunks.append(chunk)
        
        # 清理表格chunks中的表格標記和分隔符
        cleaned_table_chunks = []
        for chunk in merged_table_chunks:
            # 先清理表格標記
            cleaned_content = self.table_handler.clean_table_markers(chunk.document.page_content)
            # 再清理表格分隔符
            cleaned_content = self.table_handler.clean_table_separators(cleaned_content)
            
            # 如果內容太短，跳過
            if not cleaned_content.strip() or len(cleaned_content.strip()) < 5:
                logger.warning(f"Skipping table chunk {chunk.chunk_id}: content too short after cleaning")
                continue
                
            chunk.document = Document(page_content=cleaned_content, metadata=chunk.document.metadata)
            cleaned_table_chunks.append(chunk)
        
        # 合併所有chunks
        all_chunks = cleaned_regular_chunks + cleaned_table_chunks
        
        # 按父chunk和子chunk順序排序
        all_chunks = self._sort_child_chunks(all_chunks)
        
        logger.info(f"Table postprocessing completed: {len(all_chunks)} chunks")
        return all_chunks
    
    def _clean_parent_table_markers(self, parent_chunks: List[ParentChunk]) -> List[ParentChunk]:
        """清理父chunks中的表格標記"""
        logger.info(f"Starting to clean table markers from {len(parent_chunks)} parent chunks")
        cleaned_parent_chunks = []
        for i, parent_chunk in enumerate(parent_chunks):
            # 檢查原始內容是否包含表格標記
            original_content = parent_chunk.document.page_content
            has_markers = '<!-- TABLE_START -->' in original_content or '<!-- TABLE_END -->' in original_content
            logger.info(f"Parent chunk {i+1}: has_markers={has_markers}, content_length={len(original_content)}")
            
            # 清理表格標記
            cleaned_content = self.table_handler.clean_table_markers(original_content)
            
            # 檢查清理後的內容
            still_has_markers = '<!-- TABLE_START -->' in cleaned_content or '<!-- TABLE_END -->' in cleaned_content
            logger.info(f"Parent chunk {i+1} after cleaning: still_has_markers={still_has_markers}, cleaned_length={len(cleaned_content)}")
            
            # 創建新的Document物件
            cleaned_document = Document(page_content=cleaned_content, metadata=parent_chunk.document.metadata)
            # 創建新的ParentChunk物件
            cleaned_parent_chunk = ParentChunk(
                document=cleaned_document,
                chunk_id=parent_chunk.chunk_id,
                parent_index=parent_chunk.parent_index,
                size=len(cleaned_content),
                has_tables=parent_chunk.has_tables,
                table_count=parent_chunk.table_count,
                header_level=parent_chunk.header_level,
                header_text=parent_chunk.header_text,
                page_number=parent_chunk.page_number,
                metadata=parent_chunk.metadata
            )
            cleaned_parent_chunks.append(cleaned_parent_chunk)
        
        logger.info(f"Cleaned table markers from {len(parent_chunks)} parent chunks")
        return cleaned_parent_chunks
    
    def _merge_small_table_chunks_only(self, table_chunks: List[ChildChunk], min_size: int = 100) -> List[ChildChunk]:
        """只合併非常小的表格chunks，保持大部分子chunks"""
        if not table_chunks:
            return []
        
        # 分離大小chunks
        small_chunks = [chunk for chunk in table_chunks if chunk.size < min_size]
        large_chunks = [chunk for chunk in table_chunks if chunk.size >= min_size]
        
        # 只合併小chunks（按父chunk分組）
        merged_small_chunks = self._merge_table_chunks_by_parent(small_chunks)
        
        # 合併結果
        all_chunks = large_chunks + merged_small_chunks
        
        logger.info(f"Merged small table chunks: {len(table_chunks)} -> {len(all_chunks)}")
        return all_chunks
    
    def _merge_table_chunks_by_parent(self, table_chunks: List[ChildChunk]) -> List[ChildChunk]:
        """按父chunk合併表格chunks"""
        if not table_chunks:
            return []
        
        # 按父chunk分組
        parent_groups = {}
        for chunk in table_chunks:
            parent_id = chunk.parent_chunk_id
            if parent_id not in parent_groups:
                parent_groups[parent_id] = []
            parent_groups[parent_id].append(chunk)
        
        merged_chunks = []
        for parent_id, chunks in parent_groups.items():
            if len(chunks) == 1:
                # 只有一個chunk，直接添加
                merged_chunks.append(chunks[0])
            else:
                # 多個chunks，需要合併
                merged_chunk = self._merge_table_group(chunks)
                merged_chunks.append(merged_chunk)
        
        return merged_chunks
    
    def _merge_table_group(self, chunks: List[ChildChunk]) -> ChildChunk:
        """合併表格組"""
        if not chunks:
            return None
        
        # 合併內容
        contents = []
        metadata = chunks[0].metadata.copy()
        
        for chunk in chunks:
            clean_content = self.table_handler.clean_table_markers(chunk.document.page_content)
            contents.append(clean_content.strip())
        
        merged_content = "\n".join(contents)
        
        # 創建合併後的Document
        merged_document = Document(page_content=merged_content, metadata=metadata)
        
        # 創建合併後的ChildChunk
        merged_chunk = ChildChunk(
            document=merged_document,
            chunk_id=f"merged_{uuid.uuid4().hex[:8]}",
            parent_chunk_id=chunks[0].parent_chunk_id,
            child_index=0,
            size=len(merged_content),
            is_table_chunk=True,
            metadata=metadata
        )
        
        return merged_chunk
    
    def _sort_child_chunks(self, child_chunks: List[ChildChunk]) -> List[ChildChunk]:
        """排序子chunks"""
        def sort_key(chunk):
            # 按父chunk ID和子chunk索引排序
            return (chunk.parent_chunk_id, chunk.child_index)
        
        sorted_chunks = sorted(child_chunks, key=sort_key)
        
        # 為每個chunk添加全局編號
        for i, chunk in enumerate(sorted_chunks, 1):
            chunk.metadata['global_chunk_number'] = i
        
        return sorted_chunks
    
    def _extract_content(self, input_data: Union[str, Path, ConversionResult]) -> Tuple[str, Dict[str, Any]]:
        """提取Markdown內容和元數據"""
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
            # ConversionResult對象輸入
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
            
            # 保存ConversionResult對象以便後續使用
            self._conversion_result = input_data
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}")
        
        return content, metadata
    
    def _split_by_pages_hierarchically(self, 
                                     conversion_result: ConversionResult,
                                     output_excel: bool = False,
                                     output_path: Optional[str] = None,
                                     md_output_path: Optional[str] = None) -> HierarchicalSplitResult:
        """基於頁面的分層分割"""
        logger.info("Starting hierarchical splitting by pages...")
        
        all_parent_chunks = []
        all_child_chunks = []
        
        # 為每個頁面進行分層分割
        for page in conversion_result.pages:
            page_content = page.content
            
            # 正規化頁面內容
            if self.normalize_output and self.normalizer:
                page_content = self.normalizer.normalize_text(page_content)
            
            # 標記表格
            if self.keep_tables_together:
                page_content = self.table_handler.mark_tables(page_content)
            
            # 使用MarkdownHeaderTextSplitter分割頁面
            page_splits = self.parent_splitter.split_text(page_content)
            
            # 創建父chunks
            page_parent_chunks = []
            for i, doc in enumerate(page_splits):
                chunk_id = f"parent_{page.page_number}_{i}_{uuid.uuid4().hex[:8]}"
                
                # 添加頁面信息到metadata
                enhanced_metadata = doc.metadata.copy()
                enhanced_metadata.update({
                    'page_number': page.page_number,
                    'page_title': page.title,
                    'file_name': conversion_result.metadata.file_name,
                    'file_type': conversion_result.metadata.file_type,
                    'source': conversion_result.metadata.file_path
                })
                
                enhanced_doc = Document(page_content=doc.page_content, metadata=enhanced_metadata)
                
                parent_chunk = ParentChunk(
                    document=enhanced_doc,
                    chunk_id=chunk_id,
                    parent_index=i,
                    size=len(doc.page_content),
                    page_number=page.page_number,
                    metadata=enhanced_metadata
                )
                
                page_parent_chunks.append(parent_chunk)
            
            # 創建子chunks
            page_child_chunks = self._create_child_chunks(page_parent_chunks)
            
            all_parent_chunks.extend(page_parent_chunks)
            all_child_chunks.extend(page_child_chunks)
        
        # 後處理表格
        if self.keep_tables_together:
            # 清理父chunks中的表格標記
            all_parent_chunks = self._clean_parent_table_markers(all_parent_chunks)
            all_child_chunks = self._postprocess_tables(all_child_chunks)
        
        # 分析分組情況
        grouping_analysis = self._analyze_grouping(all_parent_chunks, all_child_chunks)
        
        # 創建結果
        result = HierarchicalSplitResult(
            parent_chunks=all_parent_chunks,
            child_chunks=all_child_chunks,
            grouping_analysis=grouping_analysis,
            processing_metadata={
                'input_type': 'ConversionResult',
                'pages_processed': len(conversion_result.pages),
                'normalized': self.normalize_output,
                'tables_handled': self.keep_tables_together,
                'processing_timestamp': self._get_timestamp()
            }
        )
        
        # 輸出處理
        if output_excel:
            # 獲取正規化內容
            normalized_content = None
            if self.normalize_output and self.normalizer:
                normalized_content = self.normalizer.normalize_text(conversion_result.content)
            self._export_to_excel(result, conversion_result.content, output_path, normalized_content)
        
        if md_output_path:
            self._export_to_markdown(result, md_output_path)
        
        logger.info(f"Hierarchical page splitting completed: {len(all_parent_chunks)} parent chunks, {len(all_child_chunks)} child chunks")
        return result
    
    def _split_without_pages_hierarchically(self, 
                                         conversion_result: ConversionResult,
                                         output_excel: bool = False,
                                         output_path: Optional[str] = None,
                                         md_output_path: Optional[str] = None) -> HierarchicalSplitResult:
        """處理沒有頁面結構的分層分割"""
        logger.info("Starting hierarchical splitting without pages...")
        
        # 獲取完整內容
        markdown_content = conversion_result.content
        
        # 正規化內容
        if self.normalize_output and self.normalizer:
            markdown_content = self.normalizer.normalize_text(markdown_content)
        
        # 標記表格
        if self.keep_tables_together:
            markdown_content = self.table_handler.mark_tables(markdown_content)
        
        # 使用MarkdownHeaderTextSplitter進行初步分割
        header_splits = self.parent_splitter.split_text(markdown_content)
        
        # 創建父chunks
        parent_chunks = []
        for i, doc in enumerate(header_splits):
            chunk_id = f"parent_{i}_{uuid.uuid4().hex[:8]}"
            
            # 添加基本metadata
            enhanced_metadata = doc.metadata.copy()
            enhanced_metadata.update({
                'file_name': conversion_result.metadata.file_name,
                'file_type': conversion_result.metadata.file_type,
                'source': conversion_result.metadata.file_path,
                'converter_used': conversion_result.metadata.converter_used,
                'total_pages': conversion_result.metadata.total_pages,
                'total_tables': conversion_result.metadata.total_tables
            })
            
            enhanced_doc = Document(page_content=doc.page_content, metadata=enhanced_metadata)
            
            parent_chunk = ParentChunk(
                document=enhanced_doc,
                chunk_id=chunk_id,
                parent_index=i,
                size=len(doc.page_content),
                metadata=enhanced_metadata
            )
            
            parent_chunks.append(parent_chunk)
        
        # 創建子chunks
        child_chunks = self._create_child_chunks(parent_chunks)
        
        # 後處理表格
        if self.keep_tables_together:
            # 清理父chunks中的表格標記
            parent_chunks = self._clean_parent_table_markers(parent_chunks)
            child_chunks = self._postprocess_tables(child_chunks)
        
        # 分析分組情況
        grouping_analysis = self._analyze_grouping(parent_chunks, child_chunks)
        
        # 創建結果
        result = HierarchicalSplitResult(
            parent_chunks=parent_chunks,
            child_chunks=child_chunks,
            grouping_analysis=grouping_analysis,
            processing_metadata={
                'input_type': 'ConversionResult',
                'normalized': self.normalize_output,
                'tables_handled': self.keep_tables_together,
                'processing_timestamp': self._get_timestamp()
            }
        )
        
        # 輸出處理
        if output_excel:
            # 獲取正規化內容
            normalized_content = None
            if self.normalize_output and self.normalizer:
                normalized_content = self.normalizer.normalize_text(conversion_result.content)
            self._export_to_excel(result, conversion_result.content, output_path, normalized_content)
        
        if md_output_path:
            self._export_to_markdown(result, md_output_path)
        
        logger.info(f"Hierarchical splitting without pages completed: {len(parent_chunks)} parent chunks, {len(child_chunks)} child chunks")
        return result
    
    def _export_to_excel(self, result: HierarchicalSplitResult, original_content: str, output_path: Optional[str], normalized_content: Optional[str] = None):
        """導出到Excel文件"""
        if output_path is None:
            output_path = f"{self.output_base_dir}/hierarchical_chunks.xlsx"
        
        # 創建Excel導出器
        exporter = ExcelExporter()
        
        # 準備數據
        parent_data = []
        child_data = []
        
        for parent_chunk in result.parent_chunks:
            parent_data.append({
                'chunk_id': parent_chunk.chunk_id,
                'chunk_type': 'parent',
                'size': parent_chunk.size,
                'has_tables': parent_chunk.has_tables,
                'table_count': parent_chunk.table_count,
                'header_level': parent_chunk.header_level,
                'header_text': parent_chunk.header_text,
                'page_number': parent_chunk.page_number,
                'content': parent_chunk.document.page_content,
                'original_content': original_content,  # 添加原文
                'normalized_content': normalized_content if normalized_content else original_content,  # 添加正規化內容
                'file_name': parent_chunk.metadata.get('file_name', ''),
                'file_type': parent_chunk.metadata.get('file_type', ''),
                'index': parent_chunk.parent_index
            })
        
        for child_chunk in result.child_chunks:
            child_data.append({
                'chunk_id': child_chunk.chunk_id,
                'parent_chunk_id': child_chunk.parent_chunk_id,
                'chunk_type': 'child',
                'size': child_chunk.size,
                'is_table_chunk': child_chunk.is_table_chunk,
                'parent_header': child_chunk.parent_header,
                'page_number': child_chunk.page_number,
                'content': child_chunk.document.page_content,
                'original_content': original_content,  # 添加原文
                'normalized_content': normalized_content if normalized_content else original_content,  # 添加正規化內容
                'file_name': child_chunk.metadata.get('file_name', ''),
                'file_type': child_chunk.metadata.get('file_type', ''),
                'child_index': child_chunk.child_index
            })
        
        # 導出到Excel
        exporter.export_hierarchical_chunks_to_excel(
            parent_data, child_data, result.grouping_analysis, output_path
        )
        
        logger.info(f"Hierarchical chunks exported to Excel: {output_path}")
    
    def _export_to_markdown(self, result: HierarchicalSplitResult, output_path: str):
        """導出到Markdown文件"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Hierarchical Chunk Analysis\n\n")
            f.write(f"**Analysis Summary:**\n")
            f.write(f"- Parent Chunks: {result.grouping_analysis.total_parent_chunks}\n")
            f.write(f"- Child Chunks: {result.grouping_analysis.total_child_chunks}\n")
            f.write(f"- Avg Children per Parent: {result.grouping_analysis.avg_children_per_parent:.2f}\n\n")
            
            # 輸出父chunks
            f.write("## Parent Chunks\n\n")
            for i, parent_chunk in enumerate(result.parent_chunks, 1):
                f.write(f"### Parent Chunk {i} (ID: {parent_chunk.chunk_id})\n\n")
                f.write(f"**Size:** {parent_chunk.size} characters\n")
                f.write(f"**Has Tables:** {parent_chunk.has_tables}\n")
                f.write(f"**Header:** {parent_chunk.header_text or 'None'}\n\n")
                f.write(f"{parent_chunk.document.page_content}\n\n")
                f.write("---\n\n")
            
            # 輸出子chunks
            f.write("## Child Chunks\n\n")
            for i, child_chunk in enumerate(result.child_chunks, 1):
                f.write(f"### Child Chunk {i} (ID: {child_chunk.chunk_id})\n\n")
                f.write(f"**Parent:** {child_chunk.parent_chunk_id}\n")
                f.write(f"**Size:** {child_chunk.size} characters\n")
                f.write(f"**Is Table:** {child_chunk.is_table_chunk}\n\n")
                f.write(f"{child_chunk.document.page_content}\n\n")
                f.write("---\n\n")
        
        logger.info(f"Hierarchical chunks exported to Markdown: {output_path}")
    
    def _load_from_serialization(self, file_path: Union[str, Path]) -> ConversionResult:
        """從序列化文件載入ConversionResult"""
        deserializer = ConversionDeserializer()
        conversion_result = deserializer.deserialize(str(file_path))
        logger.info(f"Loaded ConversionResult from serialization: {file_path}")
        return conversion_result
    
    def _get_timestamp(self) -> str:
        """獲取當前時間戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_chunk_statistics(self, result: HierarchicalSplitResult) -> Dict[str, Any]:
        """獲取分割統計信息"""
        return {
            'parent_chunks': len(result.parent_chunks),
            'child_chunks': len(result.child_chunks),
            'avg_children_per_parent': result.grouping_analysis.avg_children_per_parent,
            'parent_size_stats': result.grouping_analysis.parent_size_stats,
            'child_size_stats': result.grouping_analysis.child_size_stats,
            'table_handling_stats': result.grouping_analysis.table_handling_stats,
            'grouping_efficiency': result.grouping_analysis.grouping_efficiency
        }
