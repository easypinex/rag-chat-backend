"""
MarkitdownConverter 的測試案例。
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from service.markdown.markitdown_converter import MarkitdownConverter


class TestMarkitdownConverter:
    """MarkitdownConverter 的測試案例。"""
    
    def setup_method(self):
        """設定測試環境。"""
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        
        # 建立測試目錄
        self.input_dir.mkdir(parents=True)
        self.output_dir.mkdir(parents=True)
        
        # 初始化轉換器
        self.converter = MarkitdownConverter(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir)
        )
    
    def teardown_method(self):
        """清理測試環境。"""
        shutil.rmtree(self.temp_dir)
    
    def test_converter_initialization(self):
        """測試轉換器初始化。"""
        assert self.converter.input_dir == self.input_dir
        assert self.converter.output_dir == self.output_dir
        assert self.output_dir.exists()
    
    def test_output_directory_creation(self):
        """測試如果輸出目錄不存在則會建立。"""
        new_output_dir = Path(self.temp_dir) / "new_output"
        converter = MarkitdownConverter(
            input_dir=str(self.input_dir),
            output_dir=str(new_output_dir)
        )
        assert new_output_dir.exists()
    
    def test_get_conversion_stats(self):
        """測試轉換統計資訊。"""
        stats = self.converter.get_conversion_stats()
        
        assert "input_pdfs_count" in stats
        assert "output_mds_count" in stats
        assert "input_directory" in stats
        assert "output_directory" in stats
        assert stats["input_pdfs_count"] == 0  # 空目錄中沒有 PDF
        assert stats["output_mds_count"] == 0  # 還沒有 markdown 檔案
    
    def test_convert_nonexistent_file(self):
        """測試轉換不存在的檔案。"""
        with pytest.raises(FileNotFoundError):
            self.converter.convert_pdf_to_markdown("nonexistent.pdf")
    
    def test_convert_non_pdf_file(self):
        """測試轉換非 PDF 檔案。"""
        # 建立文字檔案
        text_file = self.input_dir / "test.txt"
        text_file.write_text("This is a text file")
        
        with pytest.raises(ValueError, match="File is not a PDF"):
            self.converter.convert_pdf_to_markdown(str(text_file))
    
    def test_convert_empty_directory(self):
        """測試轉換空目錄。"""
        results = self.converter.convert_directory()
        assert results == []
    
    def test_convert_nonexistent_subdirectory(self):
        """測試轉換不存在的子目錄。"""
        with pytest.raises(FileNotFoundError):
            self.converter.convert_directory("nonexistent_subdir")


def test_integration_with_real_pdfs():
    """與真實 PDF 檔案的整合測試（如果可用的話）。"""
    # 此測試只有在 raw_docs 目錄中有實際 PDF 檔案時才會執行
    raw_docs_path = Path("raw_docs/old_version")
    
    if not raw_docs_path.exists():
        pytest.skip("raw_docs/old_version directory not found")
    
    # 尋找要測試的 PDF 檔案
    pdf_files = list(raw_docs_path.glob("*.pdf"))
    if not pdf_files:
        pytest.skip("No PDF files found in raw_docs/old_version")
    
    # 使用第一個 PDF 檔案進行測試
    test_pdf = pdf_files[0]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "output"
        converter = MarkitdownConverter(
            input_dir=str(raw_docs_path.parent),
            output_dir=str(output_dir)
        )
        
        # 轉換測試 PDF
        result = converter.convert_pdf_to_markdown(
            str(test_pdf),
            f"test_{test_pdf.stem}"
        )
        
        # 驗證輸出檔案已建立
        assert Path(result).exists()
        assert Path(result).suffix == ".md"
        
        # 驗證內容不為空
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0


if __name__ == "__main__":
    pytest.main([__file__])
