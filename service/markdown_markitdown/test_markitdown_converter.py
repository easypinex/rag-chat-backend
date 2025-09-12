"""
Test cases for the MarkitdownConverter.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from service.markdown.markitdown_converter import MarkitdownConverter


class TestMarkitdownConverter:
    """Test cases for MarkitdownConverter."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        
        # Create test directories
        self.input_dir.mkdir(parents=True)
        self.output_dir.mkdir(parents=True)
        
        # Initialize converter
        self.converter = MarkitdownConverter(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir)
        )
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_converter_initialization(self):
        """Test converter initialization."""
        assert self.converter.input_dir == self.input_dir
        assert self.converter.output_dir == self.output_dir
        assert self.output_dir.exists()
    
    def test_output_directory_creation(self):
        """Test that output directory is created if it doesn't exist."""
        new_output_dir = Path(self.temp_dir) / "new_output"
        converter = MarkitdownConverter(
            input_dir=str(self.input_dir),
            output_dir=str(new_output_dir)
        )
        assert new_output_dir.exists()
    
    def test_get_conversion_stats(self):
        """Test conversion statistics."""
        stats = self.converter.get_conversion_stats()
        
        assert "input_pdfs_count" in stats
        assert "output_mds_count" in stats
        assert "input_directory" in stats
        assert "output_directory" in stats
        assert stats["input_pdfs_count"] == 0  # No PDFs in empty directory
        assert stats["output_mds_count"] == 0  # No markdown files yet
    
    def test_convert_nonexistent_file(self):
        """Test conversion of non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.converter.convert_pdf_to_markdown("nonexistent.pdf")
    
    def test_convert_non_pdf_file(self):
        """Test conversion of non-PDF file."""
        # Create a text file
        text_file = self.input_dir / "test.txt"
        text_file.write_text("This is a text file")
        
        with pytest.raises(ValueError, match="File is not a PDF"):
            self.converter.convert_pdf_to_markdown(str(text_file))
    
    def test_convert_empty_directory(self):
        """Test conversion of empty directory."""
        results = self.converter.convert_directory()
        assert results == []
    
    def test_convert_nonexistent_subdirectory(self):
        """Test conversion of non-existent subdirectory."""
        with pytest.raises(FileNotFoundError):
            self.converter.convert_directory("nonexistent_subdir")


def test_integration_with_real_pdfs():
    """Integration test with real PDF files (if available)."""
    # This test would only run if there are actual PDF files in the raw_docs directory
    raw_docs_path = Path("raw_docs/old_version")
    
    if not raw_docs_path.exists():
        pytest.skip("raw_docs/old_version directory not found")
    
    # Find a PDF file to test with
    pdf_files = list(raw_docs_path.glob("*.pdf"))
    if not pdf_files:
        pytest.skip("No PDF files found in raw_docs/old_version")
    
    # Use the first PDF file for testing
    test_pdf = pdf_files[0]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "output"
        converter = MarkitdownConverter(
            input_dir=str(raw_docs_path.parent),
            output_dir=str(output_dir)
        )
        
        # Convert the test PDF
        result = converter.convert_pdf_to_markdown(
            str(test_pdf),
            f"test_{test_pdf.stem}"
        )
        
        # Verify the output file was created
        assert Path(result).exists()
        assert Path(result).suffix == ".md"
        
        # Verify the content is not empty
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0


if __name__ == "__main__":
    pytest.main([__file__])
