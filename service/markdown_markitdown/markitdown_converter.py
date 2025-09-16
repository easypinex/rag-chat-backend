"""
使用微軟 markitdown 函式庫的 PDF 到 Markdown 轉換器。
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from markitdown import DocumentConverterResult, MarkItDown

# 設定日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarkitdownConverter:
    """使用微軟 markitdown 的 PDF 到 Markdown 轉換器類別。"""
    
    def __init__(self, input_dir: str = "raw_docs", output_dir: str = "service/markdown_markitdown/converted"):
        """
        初始化轉換器。
        
        Args:
            input_dir: 包含要轉換的 PDF 檔案的目錄
            output_dir: 儲存轉換後 markdown 檔案的目錄
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.converter = MarkItDown()
        
        # 如果輸出目錄不存在則建立
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"MarkitdownConverter initialized")
        logger.info(f"Input directory: {self.input_dir.absolute()}")
        logger.info(f"Output directory: {self.output_dir.absolute()}")
    
    def convert_pdf_to_markdown(self, pdf_path: str, output_filename: Optional[str] = None) -> str:
        """
        將單一 PDF 檔案轉換為 markdown。
        
        Args:
            pdf_path: PDF 檔案的路徑
            output_filename: 可選的自訂輸出檔案名稱（不含副檔名）
            
        Returns:
            轉換後的 markdown 檔案路徑
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path}")
        
        # 如果未提供則產生輸出檔案名稱
        if output_filename is None:
            output_filename = pdf_path.stem
        
        output_path = self.output_dir / f"{output_filename}.md"
        
        try:
            logger.info(f"Converting PDF: {pdf_path.name}")
            
            # 將 PDF 轉換為 markdown
            result: DocumentConverterResult = self.converter.convert(str(pdf_path))
            
            # 儲存 markdown 內容
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
            
            logger.info(f"Successfully converted: {pdf_path.name} -> {output_path.name}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error converting {pdf_path.name}: {str(e)}")
            raise
    
    def convert_directory(self, subdirectory: Optional[str] = None) -> List[str]:
        """
        轉換輸入目錄中的所有 PDF 檔案（可選擇性包含子目錄）。
        
        Args:
            subdirectory: 要處理的 input_dir 內可選子目錄
            
        Returns:
            轉換後的 markdown 檔案路徑清單
        """
        search_dir = self.input_dir
        if subdirectory:
            search_dir = self.input_dir / subdirectory
        
        if not search_dir.exists():
            raise FileNotFoundError(f"Directory not found: {search_dir}")
        
        # 尋找所有 PDF 檔案
        pdf_files = list(search_dir.glob("**/*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {search_dir}")
            return []
        
        logger.info(f"Found {len(pdf_files)} PDF files to convert")
        
        converted_files = []
        failed_files = []
        
        for pdf_file in pdf_files:
            try:
                # 為輸出檔案名稱建立相對路徑以保持目錄結構
                relative_path = pdf_file.relative_to(search_dir)
                output_filename = str(relative_path.with_suffix(''))
                
                # 確保輸出子目錄存在
                output_subdir = self.output_dir / relative_path.parent
                output_subdir.mkdir(parents=True, exist_ok=True)
                
                converted_path = self.convert_pdf_to_markdown(pdf_file, output_filename)
                converted_files.append(converted_path)
                
            except Exception as e:
                logger.error(f"Failed to convert {pdf_file.name}: {str(e)}")
                failed_files.append(pdf_file.name)
        
        logger.info(f"Conversion completed: {len(converted_files)} successful, {len(failed_files)} failed")
        
        if failed_files:
            logger.warning(f"Failed files: {failed_files}")
        
        return converted_files
    
    def convert_old_version_docs(self) -> List[str]:
        """
        轉換 old_version 目錄中的所有 PDF 檔案。
        
        Returns:
            轉換後的 markdown 檔案路徑清單
        """
        return self.convert_directory()
    
    def get_conversion_stats(self) -> dict:
        """
        取得轉換過程的統計資訊。
        
        Returns:
            包含轉換統計資訊的字典
        """
        input_pdfs = list(self.input_dir.glob("**/*.pdf"))
        output_mds = list(self.output_dir.glob("**/*.md"))
        
        return {
            "input_pdfs_count": len(input_pdfs),
            "output_mds_count": len(output_mds),
            "input_directory": str(self.input_dir.absolute()),
            "output_directory": str(self.output_dir.absolute())
        }


def main():
    """命令列使用的主要函式。"""
    import argparse
    
    parser = argparse.ArgumentParser(description="使用 markitdown 將 PDF 檔案轉換為 Markdown")
    parser.add_argument("--input-dir", default="raw_docs", help="包含 PDF 檔案的輸入目錄")
    parser.add_argument("--output-dir", default="markdown/converted", help="markdown 檔案的輸出目錄")
    parser.add_argument("--subdir", help="要處理的輸入目錄內子目錄")
    parser.add_argument("--file", help="要轉換的特定 PDF 檔案")
    
    args = parser.parse_args()
    
    converter = MarkitdownConverter(args.input_dir, args.output_dir)
    
    if args.file:
        # 轉換單一檔案
        result = converter.convert_pdf_to_markdown(args.file)
        print(f"Converted: {result}")
    else:
        # 轉換目錄
        if args.subdir:
            results = converter.convert_directory(args.subdir)
        else:
            results = converter.convert_old_version_docs()
        
        print(f"Converted {len(results)} files")
        for result in results:
            print(f"  - {result}")
        
        # 列印統計資訊
        stats = converter.get_conversion_stats()
        print(f"\nStatistics:")
        print(f"  Input PDFs: {stats['input_pdfs_count']}")
        print(f"  Output MDs: {stats['output_mds_count']}")


if __name__ == "__main__":
    main()
