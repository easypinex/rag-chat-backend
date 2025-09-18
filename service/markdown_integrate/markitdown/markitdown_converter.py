"""
使用微軟 markitdown 函式庫的多格式檔案到 Markdown 轉換器。
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Set, Dict, Union
from markitdown import DocumentConverterResult, MarkItDown

# 設定日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarkitdownConverter:
    """使用微軟 markitdown 的多格式檔案到 Markdown 轉換器類別。"""
    
    # 支援的檔案格式
    SUPPORTED_EXTENSIONS = {
        '.pdf', '.pptx', '.ppt', '.docx', '.doc', '.xlsx', '.xls',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp',
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a',
        '.html', '.htm', '.csv', '.json', '.xml', '.txt',
        '.zip', '.epub', '.mobi'
    }
    
    def __init__(self, input_dir: str = "raw_docs", output_dir: str = "service/markdown_integrate/markitdown/converted", enable_page_splitting: bool = False):
        """
        初始化轉換器。
        
        Args:
            input_dir: 包含要轉換的檔案的目錄
            output_dir: 儲存轉換後 markdown 檔案的目錄
            enable_page_splitting: 是否啟用頁面分割功能（使用 ## 標題分割）
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.enable_page_splitting = enable_page_splitting
        self.converter = MarkItDown()
        
        # 如果輸出目錄不存在則建立
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"MarkitdownConverter initialized")
        logger.info(f"Input directory: {self.input_dir.absolute()}")
        logger.info(f"Output directory: {self.output_dir.absolute()}")
        logger.info(f"Page splitting enabled: {self.enable_page_splitting}")
        logger.info(f"Supported formats: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}")
    
    def is_supported_file(self, file_path: Path) -> bool:
        """
        檢查檔案是否為支援的格式。
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            是否為支援的格式
        """
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def convert_file_to_markdown(self, file_path: str, output_filename: Optional[str] = None) -> str:
        """
        將單一檔案轉換為 markdown。
        
        Args:
            file_path: 檔案的路徑
            output_filename: 可選的自訂輸出檔案名稱（不含副檔名）
            
        Returns:
            轉換後的 markdown 檔案路徑
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not self.is_supported_file(file_path):
            raise ValueError(f"Unsupported file format: {file_path.suffix}. Supported formats: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}")
        
        # 如果未提供則產生輸出檔案名稱
        if output_filename is None:
            output_filename = file_path.stem
        
        output_path = self.output_dir / f"{output_filename}.md"
        
        try:
            logger.info(f"Converting file: {file_path.name}")
            
            # 將檔案轉換為 markdown
            result: DocumentConverterResult = self.converter.convert(str(file_path))
            
            # 儲存 markdown 內容
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
            
            logger.info(f"Successfully converted: {file_path.name} -> {output_path.name}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error converting {file_path.name}: {str(e)}")
            raise
    
    def convert_pdf_to_markdown(self, pdf_path: str, output_filename: Optional[str] = None) -> str:
        """
        將單一 PDF 檔案轉換為 markdown（向後相容性）。
        
        Args:
            pdf_path: PDF 檔案的路徑
            output_filename: 可選的自訂輸出檔案名稱（不含副檔名）
            
        Returns:
            轉換後的 markdown 檔案路徑
        """
        return self.convert_file_to_markdown(pdf_path, output_filename)
    
    def convert_directory(self, subdirectory: Optional[str] = None) -> List[str]:
        """
        轉換輸入目錄中的所有支援檔案（可選擇性包含子目錄）。
        
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
        
        # 尋找所有支援的檔案
        supported_files = []
        for ext in self.SUPPORTED_EXTENSIONS:
            supported_files.extend(list(search_dir.glob(f"**/*{ext}")))
        
        if not supported_files:
            logger.warning(f"No supported files found in {search_dir}")
            return []
        
        logger.info(f"Found {len(supported_files)} supported files to convert")
        
        converted_files = []
        failed_files = []
        
        for file_path in supported_files:
            try:
                # 為輸出檔案名稱建立相對路徑以保持目錄結構
                relative_path = file_path.relative_to(search_dir)
                output_filename = str(relative_path.with_suffix(''))
                
                # 確保輸出子目錄存在
                output_subdir = self.output_dir / relative_path.parent
                output_subdir.mkdir(parents=True, exist_ok=True)
                
                converted_path = self.convert_file_to_markdown(file_path, output_filename)
                converted_files.append(converted_path)
                
            except Exception as e:
                logger.error(f"Failed to convert {file_path.name}: {str(e)}")
                failed_files.append(file_path.name)
        
        logger.info(f"Conversion completed: {len(converted_files)} successful, {len(failed_files)} failed")
        
        if failed_files:
            logger.warning(f"Failed files: {failed_files}")
        
        return converted_files
    
    def convert_old_version_docs(self) -> List[str]:
        """
        轉換 old_version 目錄中的所有支援檔案。
        
        Returns:
            轉換後的 markdown 檔案路徑清單
        """
        return self.convert_directory()
    
    def convert_by_extension(self, extension: str, subdirectory: Optional[str] = None) -> List[str]:
        """
        轉換特定副檔名的所有檔案。
        
        Args:
            extension: 要轉換的副檔名（例如 '.xlsx', '.pptx'）
            subdirectory: 要處理的 input_dir 內可選子目錄
            
        Returns:
            轉換後的 markdown 檔案路徑清單
        """
        search_dir = self.input_dir
        if subdirectory:
            search_dir = self.input_dir / subdirectory
        
        if not search_dir.exists():
            raise FileNotFoundError(f"Directory not found: {search_dir}")
        
        # 尋找特定副檔名的檔案
        files = list(search_dir.glob(f"**/*{extension}"))
        
        if not files:
            logger.warning(f"No {extension} files found in {search_dir}")
            return []
        
        logger.info(f"Found {len(files)} {extension} files to convert")
        
        converted_files = []
        failed_files = []
        
        for file_path in files:
            try:
                # 為輸出檔案名稱建立相對路徑以保持目錄結構
                relative_path = file_path.relative_to(search_dir)
                output_filename = str(relative_path.with_suffix(''))
                
                # 確保輸出子目錄存在
                output_subdir = self.output_dir / relative_path.parent
                output_subdir.mkdir(parents=True, exist_ok=True)
                
                converted_path = self.convert_file_to_markdown(file_path, output_filename)
                converted_files.append(converted_path)
                
            except Exception as e:
                logger.error(f"Failed to convert {file_path.name}: {str(e)}")
                failed_files.append(file_path.name)
        
        logger.info(f"Conversion completed: {len(converted_files)} successful, {len(failed_files)} failed")
        
        if failed_files:
            logger.warning(f"Failed files: {failed_files}")
        
        return converted_files
    
    def _split_by_headers(self, content: str) -> List[str]:
        """
        使用 ## 標題分割內容為頁面。
        
        Args:
            content: 要分割的 markdown 內容
            
        Returns:
            分割後的頁面列表
        """
        if not content.strip():
            return []
        
        # 按 ## 標題分割內容
        sections = content.split('\n## ')
        
        if len(sections) <= 1:
            # 沒有找到 ## 標題，返回整個內容作為一頁
            return [content.strip()] if content.strip() else []
        
        pages = []
        
        # 處理第一個部分（可能沒有 ## 前綴）
        first_section = sections[0].strip()
        if first_section:
            # 檢查是否以 ## 開頭
            if first_section.startswith('## '):
                # 移除 ## 前綴
                first_section = first_section[3:].strip()
            if first_section:
                pages.append(first_section)
        
        # 處理其餘部分（都有 ## 前綴）
        for section in sections[1:]:
            if section.strip():
                # 確保有 ## 前綴
                if not section.startswith('## '):
                    section = '## ' + section
                pages.append(section.strip())
        
        return pages
    
    def _extract_page_title(self, page_content: str, page_number: int) -> str:
        """
        從頁面內容中提取標題。
        
        Args:
            page_content: 頁面內容
            page_number: 頁面編號
            
        Returns:
            提取的標題，如果沒有找到則返回預設標題
        """
        if not page_content.strip():
            return f"Page {page_number}"
        
        lines = page_content.strip().split('\n')
        
        # 尋找第一個非空行作為標題
        for line in lines:
            line = line.strip()
            if line:
                # 移除 markdown 標題符號
                if line.startswith('#'):
                    line = line.lstrip('#').strip()
                # 移除其他 markdown 符號
                line = line.replace('**', '').replace('*', '').replace('`', '')
                if line:
                    return line[:50]  # 限制標題長度
        
        # 如果沒有找到合適的標題，使用預設標題
        return f"Page {page_number}"
    
    def convert_file_to_pages(self, file_path: str, output_filename: Optional[str] = None) -> List[str]:
        """
        將檔案轉換為頁面列表（每頁一個字串）。
        
        Args:
            file_path: 檔案的路徑
            output_filename: 可選的自訂輸出檔案名稱（不含副檔名）
            
        Returns:
            頁面內容列表，每個元素代表一頁的內容
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not self.is_supported_file(file_path):
            raise ValueError(f"Unsupported file format: {file_path.suffix}. Supported formats: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}")
        
        try:
            logger.info(f"Converting file to pages: {file_path.name}")
            
            # 將檔案轉換為 markdown
            result: DocumentConverterResult = self.converter.convert(str(file_path))
            
            # 如果未啟用頁面分割，返回空列表
            if not self.enable_page_splitting:
                logger.info(f"Page splitting disabled, returning empty pages list for: {file_path.name}")
                return []
            
            # 根據檔案類型分割頁面
            pages = []
            if file_path.suffix.lower() in ['.pdf']:
                # PDF 檔案：按頁面分割（使用頁面分隔符）
                content = result.text_content
                # 嘗試按頁面分割（這裡使用簡單的分割方法）
                # 實際的頁面分割可能需要更複雜的邏輯
                pages = [content]  # 暫時返回整個內容作為一頁
            elif file_path.suffix.lower() in ['.pptx', '.ppt']:
                # PowerPoint 檔案：按幻燈片分割
                content = result.text_content
                # 按幻燈片標題分割
                slides = content.split('<!-- Slide number:')
                if len(slides) > 1:
                    pages = [slides[0]] + [f'<!-- Slide number:{slide}' for slide in slides[1:]]
                else:
                    pages = [content]
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                # Excel 檔案：使用 ## 標題分割
                content = result.text_content
                pages = self._split_by_headers(content)
            else:
                # 其他檔案類型：使用 ## 標題分割
                content = result.text_content
                pages = self._split_by_headers(content)
            
            logger.info(f"Successfully converted to {len(pages)} pages: {file_path.name}")
            return pages
            
        except Exception as e:
            logger.error(f"Error converting {file_path.name} to pages: {str(e)}")
            raise
    
    def convert_excel_to_sheets(self, file_path: str, output_filename: Optional[str] = None) -> List[Dict[str, str]]:
        """
        將 Excel 檔案轉換為工作表列表。
        
        Args:
            file_path: Excel 檔案的路徑
            output_filename: 可選的自訂輸出檔案名稱（不含副檔名）
            
        Returns:
            工作表列表，每個元素包含 'title' 和 'content' 鍵
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.suffix.lower() in ['.xlsx', '.xls']:
            raise ValueError(f"File is not an Excel file: {file_path}")
        
        try:
            logger.info(f"Converting Excel file to sheets: {file_path.name}")
            
            # 將 Excel 檔案轉換為 markdown
            result: DocumentConverterResult = self.converter.convert(str(file_path))
            
            # 使用 ## {標題} 來分割工作表
            content = result.text_content
            sheets = []
            
            # 按 ## 標題分割內容
            sections = content.split('\n## ')
            
            if len(sections) > 1:
                # 第一個部分可能沒有 ## 前綴，需要特殊處理
                first_section = sections[0]
                if first_section.strip():
                    # 如果第一個部分有內容，檢查是否以 ## 開頭
                    if first_section.startswith('## '):
                        # 移除 ## 前綴
                        title = first_section[3:].split('\n')[0].strip()
                        content_text = first_section[3 + len(title):].strip()
                    else:
                        # 沒有 ## 前綴，可能是整個內容
                        title = 'Sheet1'
                        content_text = first_section.strip()
                    
                    if content_text:
                        sheets.append({
                            'title': title,
                            'content': content_text
                        })
                
                # 處理其餘部分
                for section in sections[1:]:
                    if section.strip():
                        lines = section.split('\n')
                        title = lines[0].strip()
                        content_text = '\n'.join(lines[1:]).strip()
                        
                        if content_text:
                            sheets.append({
                                'title': title,
                                'content': content_text
                            })
            else:
                # 沒有找到 ## 標題，將整個內容作為一個工作表
                sheets = [{
                    'title': 'Sheet1',
                    'content': content
                }]
            
            logger.info(f"Successfully converted to {len(sheets)} sheets: {file_path.name}")
            return sheets
            
        except Exception as e:
            logger.error(f"Error converting {file_path.name} to sheets: {str(e)}")
            raise
    
    def convert_file_with_metadata(self, file_path: str, output_filename: Optional[str] = None) -> Dict[str, Union[str, List[str], List[Dict[str, str]]]]:
        """
        將檔案轉換並返回包含完整元資料的結果。
        
        Args:
            file_path: 檔案的路徑
            output_filename: 可選的自訂輸出檔案名稱（不含副檔名）
            
        Returns:
            包含轉換結果和元資料的字典
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not self.is_supported_file(file_path):
            raise ValueError(f"Unsupported file format: {file_path.suffix}. Supported formats: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}")
        
        try:
            logger.info(f"Converting file with metadata: {file_path.name}")
            
            # 將檔案轉換為 markdown
            result: DocumentConverterResult = self.converter.convert(str(file_path))
            
            # 構建結果字典
            conversion_result = {
                'file_name': file_path.name,
                'file_type': file_path.suffix.lower(),
                'full_text': result.text_content,
                'title': result.title if hasattr(result, 'title') else file_path.stem,
                'metadata': {}
            }
            
            # 獲取頁面內容
            pages = self.convert_file_to_pages(str(file_path))
            conversion_result['pages'] = pages
            
            # 如果啟用頁面分割且有頁面，添加頁面標題
            if self.enable_page_splitting and pages:
                page_titles = []
                for i, page_content in enumerate(pages, 1):
                    # 嘗試從頁面內容中提取標題
                    title = self._extract_page_title(page_content, i)
                    page_titles.append(title)
                conversion_result['page_titles'] = page_titles
            
            # 如果是 Excel 檔案，添加工作表資訊
            if file_path.suffix.lower() in ['.xlsx', '.xls']:
                sheets = self.convert_excel_to_sheets(str(file_path))
                conversion_result['sheets'] = sheets
            
            # 添加基本元資料
            conversion_result['metadata'] = {
                'file_size': file_path.stat().st_size,
                'file_modified': file_path.stat().st_mtime,
                'conversion_timestamp': __import__('time').time()
            }
            
            logger.info(f"Successfully converted with metadata: {file_path.name}")
            return conversion_result
            
        except Exception as e:
            logger.error(f"Error converting {file_path.name} with metadata: {str(e)}")
            raise
    
    def get_conversion_stats(self) -> dict:
        """
        取得轉換過程的統計資訊。
        
        Returns:
            包含轉換統計資訊的字典
        """
        input_files = []
        for ext in self.SUPPORTED_EXTENSIONS:
            input_files.extend(list(self.input_dir.glob(f"**/*{ext}")))
        
        output_mds = list(self.output_dir.glob("**/*.md"))
        
        return {
            "input_files_count": len(input_files),
            "output_mds_count": len(output_mds),
            "input_directory": str(self.input_dir.absolute()),
            "output_directory": str(self.output_dir.absolute()),
            "supported_extensions": sorted(self.SUPPORTED_EXTENSIONS)
        }


def main():
    """命令列使用的主要函式。"""
    import argparse
    
    parser = argparse.ArgumentParser(description="使用 markitdown 將各種檔案轉換為 Markdown")
    parser.add_argument("--input-dir", default="raw_docs", help="包含檔案的輸入目錄")
    parser.add_argument("--output-dir", default="markdown/converted", help="markdown 檔案的輸出目錄")
    parser.add_argument("--subdir", help="要處理的輸入目錄內子目錄")
    parser.add_argument("--file", help="要轉換的特定檔案")
    parser.add_argument("--extension", help="要轉換的特定副檔名（例如 .xlsx, .pptx）")
    
    args = parser.parse_args()
    
    converter = MarkitdownConverter(args.input_dir, args.output_dir)
    
    if args.file:
        # 轉換單一檔案
        result = converter.convert_file_to_markdown(args.file)
        print(f"Converted: {result}")
    elif args.extension:
        # 轉換特定副檔名的檔案
        if args.subdir:
            results = converter.convert_by_extension(args.extension, args.subdir)
        else:
            results = converter.convert_by_extension(args.extension)
        
        print(f"Converted {len(results)} {args.extension} files")
        for result in results:
            print(f"  - {result}")
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
        print(f"  Input files: {stats['input_files_count']}")
        print(f"  Output MDs: {stats['output_mds_count']}")
        print(f"  Supported extensions: {', '.join(stats['supported_extensions'])}")


if __name__ == "__main__":
    main()
