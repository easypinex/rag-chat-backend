"""
文件分析程式

針對 raw_docs/ 目錄下的文件進行分析，使用 ChunkSplitter 進行分割，
並產生結構化的分析結果。
"""

import os
import sys
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# 添加路徑到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

# 直接導入模組
from service.chunk.chunk_splitter import ChunkSplitter
from service.markdown_integrate.unified_converter import UnifiedMarkdownConverter
from service.serialization import ConversionSerializer, ConversionDeserializer

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentAnalyzer:
    """文件分析器"""
    
    def __init__(self, 
                 raw_docs_dir: str = None,
                 output_base_dir: str = "service/chunk/analysis/output",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        """
        初始化分析器
        
        Args:
            raw_docs_dir: 原始文件目錄
            output_base_dir: 輸出基礎目錄
            chunk_size: chunk 大小
            chunk_overlap: chunk 重疊大小
        """
        # 設定預設的 raw_docs 目錄
        if raw_docs_dir is None:
            # 從當前目錄向上找到專案根目錄
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent
            raw_docs_dir = project_root / "raw_docs"
        
        self.raw_docs_dir = Path(raw_docs_dir)
        # 確保輸出路徑是絕對路徑
        if not Path(output_base_dir).is_absolute():
            # 如果是相對路徑，從專案根目錄開始
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent
            self.output_base_dir = project_root / output_base_dir
        else:
            self.output_base_dir = Path(output_base_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 初始化轉換器和分割器
        self.converter = UnifiedMarkdownConverter()
        self.splitter = ChunkSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            normalize_output=True
        )
        
        # 初始化序列化器
        self.serializer = ConversionSerializer()
        self.deserializer = ConversionDeserializer()
        
        # 確保輸出目錄存在
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DocumentAnalyzer initialized")
        logger.info(f"Raw docs directory: {self.raw_docs_dir}")
        logger.info(f"Output directory: {self.output_base_dir}")
    
    def get_files_to_process(self) -> List[Path]:
        """
        獲取需要處理的文件列表（不包含子資料夾）
        
        Returns:
            List[Path]: 文件路徑列表
        """
        if not self.raw_docs_dir.exists():
            logger.error(f"Raw docs directory not found: {self.raw_docs_dir}")
            return []
        
        # 只獲取根目錄下的文件，不包含子資料夾
        files = []
        for item in self.raw_docs_dir.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                # 支援的文件格式
                if item.suffix.lower() in ['.pdf', '.docx', '.xlsx', '.xls', '.txt', '.md']:
                    files.append(item)
                else:
                    logger.info(f"Skipping unsupported file: {item.name}")
        
        logger.info(f"Found {len(files)} files to process")
        return files
    
    def create_output_structure(self, file_path: Path) -> Dict[str, Path]:
        """
        為單個文件創建輸出目錄結構
        
        Args:
            file_path: 原始文件路徑
            
        Returns:
            Dict[str, Path]: 輸出路徑字典
        """
        # 獲取文件名（不含副檔名）
        file_stem = file_path.stem
        
        # 創建文件專用目錄
        file_output_dir = self.output_base_dir / file_stem
        file_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 定義輸出文件路徑
        output_paths = {
            'directory': file_output_dir,
            'original': file_output_dir / f"{file_stem}{file_path.suffix}",
            'markdown': file_output_dir / f"{file_stem}_Markdown.md",
            'excel': file_output_dir / f"{file_stem}_Chunk.xlsx",
            'serialization': file_output_dir / f"{file_stem}_ConversionResult.json"
        }
        
        return output_paths
    
    def get_serialization_path(self, file_path: Path) -> Path:
        """
        獲取序列化 JSON 文件路徑
        
        Args:
            file_path: 原始文件路徑
            
        Returns:
            Path: 序列化文件路徑
        """
        output_paths = self.create_output_structure(file_path)
        return output_paths['serialization']
    
    def check_serialization_exists(self, file_path: Path) -> bool:
        """
        檢查序列化文件是否存在且有效
        
        Args:
            file_path: 原始文件路徑
            
        Returns:
            bool: 序列化文件是否存在且有效
        """
        serialization_path = self.get_serialization_path(file_path)
        
        if not serialization_path.exists():
            logger.info(f"Serialization file not found: {serialization_path}")
            return False
        
        # 驗證序列化文件是否有效
        try:
            is_valid = self.deserializer.validate_file(str(serialization_path))
            if is_valid:
                logger.info(f"Found valid serialization file: {serialization_path}")
                return True
            else:
                logger.warning(f"Invalid serialization file: {serialization_path}")
                return False
        except Exception as e:
            logger.warning(f"Error validating serialization file {serialization_path}: {e}")
            return False
    
    def load_from_serialization(self, file_path: Path):
        """
        從序列化文件載入 ConversionResult
        
        Args:
            file_path: 原始文件路徑
            
        Returns:
            ConversionResult: 反序列化後的 ConversionResult 對象
        """
        serialization_path = self.get_serialization_path(file_path)
        logger.info(f"Loading ConversionResult from serialization: {serialization_path}")
        return self.deserializer.deserialize(str(serialization_path))
    
    def save_to_serialization(self, conversion_result, file_path: Path):
        """
        保存 ConversionResult 到序列化文件
        
        Args:
            conversion_result: ConversionResult 對象
            file_path: 原始文件路徑
        """
        serialization_path = self.get_serialization_path(file_path)
        # 確保目錄存在
        serialization_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving ConversionResult to serialization: {serialization_path}")
        # 使用自定義路徑進行序列化
        self.serializer.serialize(conversion_result, str(serialization_path))
    
    def copy_original_file(self, source_path: Path, dest_path: Path) -> bool:
        """
        複製原始文件到輸出目錄
        
        Args:
            source_path: 源文件路徑
            dest_path: 目標文件路徑
            
        Returns:
            bool: 是否成功
        """
        try:
            shutil.copy2(source_path, dest_path)
            logger.info(f"Copied original file: {source_path.name} -> {dest_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to copy original file {source_path.name}: {e}")
            return False
    
    def process_single_file(self, file_path: Path) -> Dict[str, Any]:
        """
        處理單個文件
        
        Args:
            file_path: 文件路徑
            
        Returns:
            Dict[str, Any]: 處理結果
        """
        logger.info(f"Processing file: {file_path.name}")
        
        try:
            # 創建輸出目錄結構
            output_paths = self.create_output_structure(file_path)
            
            # 複製原始文件
            copy_success = self.copy_original_file(file_path, output_paths['original'])
            
            # 檢查是否存在序列化文件
            conversion_result = None
            used_serialization = False
            
            if self.check_serialization_exists(file_path):
                # 從序列化文件載入
                logger.info(f"Using existing serialization for {file_path.name}")
                conversion_result = self.load_from_serialization(file_path)
                used_serialization = True
            else:
                # 轉換文件為 Markdown
                logger.info(f"Converting {file_path.name} to Markdown...")
                conversion_result = self.converter.convert_file(str(file_path))
                
                if not conversion_result or not conversion_result.content:
                    logger.error(f"Failed to convert {file_path.name}")
                    return {
                        'file_name': file_path.name,
                        'status': 'failed',
                        'error': 'Conversion failed',
                        'output_paths': output_paths
                    }
                
                # 保存序列化文件
                logger.info(f"Saving ConversionResult to serialization for {file_path.name}")
                self.save_to_serialization(conversion_result, file_path)
            
            # 保存 Markdown 文件
            with open(output_paths['markdown'], 'w', encoding='utf-8') as f:
                f.write(conversion_result.content)
            logger.info(f"Saved Markdown: {output_paths['markdown']}")
            
            # 使用 ChunkSplitter 進行分割
            logger.info(f"Splitting {file_path.name} into chunks...")
            chunks = self.splitter.split_markdown(
                input_data=conversion_result,
                output_excel=True,
                output_path=str(output_paths['excel'])
            )
            
            # 獲取統計信息
            stats = self.splitter.get_chunk_statistics(chunks)
            
            # 將 Path 對象轉換為字符串以便 JSON 序列化
            output_paths_str = {
                key: str(value) if isinstance(value, Path) else value
                for key, value in output_paths.items()
            }
            
            result = {
                'file_name': file_path.name,
                'status': 'success',
                'output_paths': output_paths_str,
                'chunks_count': len(chunks),
                'statistics': stats,
                'used_serialization': used_serialization,
                'serialization_path': str(self.get_serialization_path(file_path)) if used_serialization else None,
                'conversion_metadata': {
                    'file_type': conversion_result.metadata.file_type,
                    'total_pages': conversion_result.metadata.total_pages,
                    'total_tables': conversion_result.metadata.total_tables,
                    'converter_used': conversion_result.metadata.converter_used
                }
            }
            
            logger.info(f"Successfully processed {file_path.name}: {len(chunks)} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            # 處理 output_paths 的 Path 對象轉換
            output_paths_str = None
            if 'output_paths' in locals():
                output_paths_str = {
                    key: str(value) if isinstance(value, Path) else value
                    for key, value in output_paths.items()
                }
            
            return {
                'file_name': file_path.name,
                'status': 'error',
                'error': str(e),
                'output_paths': output_paths_str
            }
    
    def analyze_all_files(self) -> Dict[str, Any]:
        """
        分析所有文件
        
        Returns:
            Dict[str, Any]: 分析結果摘要
        """
        logger.info("Starting analysis of all files...")
        
        # 獲取所有需要處理的文件
        files_to_process = self.get_files_to_process()
        
        if not files_to_process:
            logger.warning("No files found to process")
            return {
                'total_files': 0,
                'successful': 0,
                'failed': 0,
                'results': []
            }
        
        # 處理每個文件
        results = []
        successful_count = 0
        failed_count = 0
        
        for file_path in files_to_process:
            result = self.process_single_file(file_path)
            results.append(result)
            
            if result['status'] == 'success':
                successful_count += 1
            else:
                failed_count += 1
        
        # 生成摘要報告
        summary = {
            'total_files': len(files_to_process),
            'successful': successful_count,
            'failed': failed_count,
            'success_rate': successful_count / len(files_to_process) * 100 if files_to_process else 0,
            'results': results,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # 保存摘要報告
        summary_path = self.output_base_dir / "analysis_summary.json"
        import json
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Analysis completed: {successful_count}/{len(files_to_process)} files processed successfully")
        logger.info(f"Summary saved to: {summary_path}")
        
        return summary
    
    def analyze_single_file(self, file_name: str) -> Dict[str, Any]:
        """
        分析單個指定文件
        
        Args:
            file_name: 文件名
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        file_path = self.raw_docs_dir / file_name
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {
                'file_name': file_name,
                'status': 'error',
                'error': 'File not found'
            }
        
        return self.process_single_file(file_path)


def main():
    """主程式入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Document Analysis Tool')
    parser.add_argument('--file', type=str, help='Analyze specific file by name')
    parser.add_argument('--raw-docs', type=str, default='raw_docs', help='Raw documents directory')
    parser.add_argument('--output', type=str, default='service/chunk/analysis/output', help='Output directory')
    parser.add_argument('--chunk-size', type=int, default=1000, help='Chunk size')
    parser.add_argument('--chunk-overlap', type=int, default=200, help='Chunk overlap')
    
    args = parser.parse_args()
    
    # 創建分析器
    analyzer = DocumentAnalyzer(
        raw_docs_dir=args.raw_docs,
        output_base_dir=args.output,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    if args.file:
        # 分析單個文件
        logger.info(f"Analyzing single file: {args.file}")
        result = analyzer.analyze_single_file(args.file)
        print(f"Analysis result: {result}")
    else:
        # 分析所有文件
        logger.info("Analyzing all files...")
        summary = analyzer.analyze_all_files()
        print(f"Analysis summary: {summary}")


if __name__ == "__main__":
    main()
