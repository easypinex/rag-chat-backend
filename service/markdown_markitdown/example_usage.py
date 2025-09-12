"""
Example usage of the MarkitdownConverter.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from service.markdown.markitdown_converter import MarkitdownConverter


def example_single_file_conversion():
    """Example: Convert a single PDF file."""
    print("=== Single File Conversion Example ===")
    
    converter = MarkitdownConverter()
    
    # Convert a specific PDF file
    pdf_path = "raw_docs/old_version/台灣人壽e樂活一年定期住院日額健康保險.pdf"
    
    try:
        result = converter.convert_pdf_to_markdown(pdf_path)
        print(f"Successfully converted: {result}")
    except FileNotFoundError:
        print(f"PDF file not found: {pdf_path}")
    except Exception as e:
        print(f"Error converting PDF: {e}")


def example_directory_conversion():
    """Example: Convert all PDF files in old_version directory."""
    print("\n=== Directory Conversion Example ===")
    
    converter = MarkitdownConverter()
    
    try:
        # Convert all PDFs in old_version directory
        results = converter.convert_old_version_docs()
        
        print(f"Converted {len(results)} files:")
        for result in results:
            print(f"  - {result}")
            
    except Exception as e:
        print(f"Error converting directory: {e}")


def example_custom_directories():
    """Example: Convert with custom input and output directories."""
    print("\n=== Custom Directories Example ===")
    
    converter = MarkitdownConverter(
        input_dir="raw_docs/old_version",
        output_dir="markdown/converted"
    )
    
    try:
        # Convert all PDFs in the input directory
        results = converter.convert_directory()
        
        print(f"Converted {len(results)} files:")
        for result in results:
            print(f"  - {result}")
            
    except Exception as e:
        print(f"Error converting directory: {e}")


def example_subdirectory_conversion():
    """Example: Convert PDFs in a specific subdirectory."""
    print("\n=== Subdirectory Conversion Example ===")
    
    converter = MarkitdownConverter()
    
    try:
        # Convert PDFs in the dm subdirectory
        results = converter.convert_directory("old_version/dm")
        
        print(f"Converted {len(results)} files from dm subdirectory:")
        for result in results:
            print(f"  - {result}")
            
    except Exception as e:
        print(f"Error converting subdirectory: {e}")


def example_conversion_stats():
    """Example: Get conversion statistics."""
    print("\n=== Conversion Statistics Example ===")
    
    converter = MarkitdownConverter()
    
    stats = converter.get_conversion_stats()
    
    print("Conversion Statistics:")
    print(f"  Input PDFs: {stats['input_pdfs_count']}")
    print(f"  Output MDs: {stats['output_mds_count']}")
    print(f"  Input Directory: {stats['input_directory']}")
    print(f"  Output Directory: {stats['output_directory']}")


def main():
    """Run all examples."""
    print("MarkitdownConverter Usage Examples")
    print("=" * 50)
    
    # Run examples
    example_single_file_conversion()
    example_directory_conversion()
    example_custom_directories()
    example_subdirectory_conversion()
    example_conversion_stats()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()
