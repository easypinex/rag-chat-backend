"""
PDF to Markdown converter using Microsoft's markitdown library.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from markitdown import MarkItDown

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarkitdownConverter:
    """Converter class for PDF to Markdown using Microsoft's markitdown."""
    
    def __init__(self, input_dir: str = "raw_docs", output_dir: str = "markdown/converted"):
        """
        Initialize the converter.
        
        Args:
            input_dir: Directory containing PDF files to convert
            output_dir: Directory to save converted markdown files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.converter = MarkItDown()
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"MarkitdownConverter initialized")
        logger.info(f"Input directory: {self.input_dir.absolute()}")
        logger.info(f"Output directory: {self.output_dir.absolute()}")
    
    def convert_pdf_to_markdown(self, pdf_path: str, output_filename: Optional[str] = None) -> str:
        """
        Convert a single PDF file to markdown.
        
        Args:
            pdf_path: Path to the PDF file
            output_filename: Optional custom output filename (without extension)
            
        Returns:
            Path to the converted markdown file
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path}")
        
        # Generate output filename if not provided
        if output_filename is None:
            output_filename = pdf_path.stem
        
        output_path = self.output_dir / f"{output_filename}.md"
        
        try:
            logger.info(f"Converting PDF: {pdf_path.name}")
            
            # Convert PDF to markdown
            result = self.converter.convert(str(pdf_path))
            
            # Save the markdown content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
            
            logger.info(f"Successfully converted: {pdf_path.name} -> {output_path.name}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error converting {pdf_path.name}: {str(e)}")
            raise
    
    def convert_directory(self, subdirectory: Optional[str] = None) -> List[str]:
        """
        Convert all PDF files in the input directory (and optionally a subdirectory).
        
        Args:
            subdirectory: Optional subdirectory within input_dir to process
            
        Returns:
            List of paths to converted markdown files
        """
        search_dir = self.input_dir
        if subdirectory:
            search_dir = self.input_dir / subdirectory
        
        if not search_dir.exists():
            raise FileNotFoundError(f"Directory not found: {search_dir}")
        
        # Find all PDF files
        pdf_files = list(search_dir.glob("**/*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {search_dir}")
            return []
        
        logger.info(f"Found {len(pdf_files)} PDF files to convert")
        
        converted_files = []
        failed_files = []
        
        for pdf_file in pdf_files:
            try:
                # Create relative path for output filename to preserve directory structure
                relative_path = pdf_file.relative_to(search_dir)
                output_filename = str(relative_path.with_suffix(''))
                
                # Ensure output subdirectory exists
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
        Convert all PDF files in the old_version directory.
        
        Returns:
            List of paths to converted markdown files
        """
        return self.convert_directory("old_version")
    
    def get_conversion_stats(self) -> dict:
        """
        Get statistics about the conversion process.
        
        Returns:
            Dictionary with conversion statistics
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
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert PDF files to Markdown using markitdown")
    parser.add_argument("--input-dir", default="raw_docs", help="Input directory containing PDF files")
    parser.add_argument("--output-dir", default="markdown/converted", help="Output directory for markdown files")
    parser.add_argument("--subdir", help="Subdirectory within input directory to process")
    parser.add_argument("--file", help="Specific PDF file to convert")
    
    args = parser.parse_args()
    
    converter = MarkitdownConverter(args.input_dir, args.output_dir)
    
    if args.file:
        # Convert single file
        result = converter.convert_pdf_to_markdown(args.file)
        print(f"Converted: {result}")
    else:
        # Convert directory
        if args.subdir:
            results = converter.convert_directory(args.subdir)
        else:
            results = converter.convert_old_version_docs()
        
        print(f"Converted {len(results)} files")
        for result in results:
            print(f"  - {result}")
        
        # Print statistics
        stats = converter.get_conversion_stats()
        print(f"\nStatistics:")
        print(f"  Input PDFs: {stats['input_pdfs_count']}")
        print(f"  Output MDs: {stats['output_mds_count']}")


if __name__ == "__main__":
    main()
