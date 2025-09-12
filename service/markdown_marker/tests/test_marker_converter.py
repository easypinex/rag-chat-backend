"""
Marker Converter 測試檔案

測試基於 Marker 套件的 PDF 到 Markdown 轉換功能
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from marker_converter import MarkerConverter, create_marker_converter


class TestMarkerConverter:
    """Marker 轉換器測試類"""
    
    def setup_method(self):
        """測試前的設置"""
        self.test_dir = Path(__file__).parent
        self.raw_docs_dir = self.test_dir.parent.parent / "raw_docs" / "old_version"
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """測試後的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('service.markdown2.marker_converter.MARKER_AVAILABLE', True)
    @patch('service.markdown2.marker_converter.create_model_dict')
    @patch('service.markdown2.marker_converter.PdfConverter')
    def test_marker_converter_init(self, mock_pdf_converter, mock_create_model_dict):
        """測試 Marker 轉換器初始化"""
        mock_artifact_dict = Mock()
        mock_create_model_dict.return_value = mock_artifact_dict
        mock_converter_instance = Mock()
        mock_pdf_converter.return_value = mock_converter_instance
        
        converter = MarkerConverter()
        
        assert converter.converter == mock_converter_instance
        mock_create_model_dict.assert_called_once()
        mock_pdf_converter.assert_called_once_with(artifact_dict=mock_artifact_dict)
    
    @patch('service.markdown2.marker_converter.MARKER_AVAILABLE', False)
    def test_marker_converter_init_without_marker(self):
        """測試在沒有 Marker 套件時的初始化"""
        with pytest.raises(ImportError, match="Marker package is not available"):
            MarkerConverter()
    
    @patch('service.markdown2.marker_converter.MARKER_AVAILABLE', True)
    @patch('service.markdown2.marker_converter.create_model_dict')
    @patch('service.markdown2.marker_converter.PdfConverter')
    def test_marker_converter_init_with_custom_locations(self, mock_pdf_converter, mock_create_model_dict):
        """測試使用自定義模型位置的初始化"""
        mock_artifact_dict = Mock()
        mock_create_model_dict.return_value = mock_artifact_dict
        mock_converter_instance = Mock()
        mock_pdf_converter.return_value = mock_converter_instance
        
        model_locations = {"model1": "/path/to/model1", "model2": "/path/to/model2"}
        converter = MarkerConverter(model_locations)
        
        # 注意：新的 API 可能不直接使用 model_locations 參數
        assert converter.model_locations == model_locations
        mock_create_model_dict.assert_called_once()
    
    @patch('service.markdown2.marker_converter.MARKER_AVAILABLE', True)
    @patch('service.markdown2.marker_converter.create_model_dict')
    @patch('service.markdown2.marker_converter.PdfConverter')
    @patch('service.markdown2.marker_converter.text_from_rendered')
    def test_convert_pdf_to_markdown(self, mock_text_from_rendered, mock_pdf_converter, mock_create_model_dict):
        """測試 PDF 到 Markdown 的轉換"""
        # 設置 mock
        mock_artifact_dict = Mock()
        mock_create_model_dict.return_value = mock_artifact_dict
        mock_converter_instance = Mock()
        mock_pdf_converter.return_value = mock_converter_instance
        
        mock_rendered = Mock()
        mock_converter_instance.return_value = mock_rendered
        mock_text_from_rendered.return_value = ("# Test Markdown\n\nThis is test content.", None, [])
        
        # 建立測試 PDF 檔案
        test_pdf = Path(self.temp_dir) / "test.pdf"
        test_pdf.write_text("fake pdf content")
        
        converter = MarkerConverter()
        result = converter.convert_pdf_to_markdown(str(test_pdf))
        
        assert result == "# Test Markdown\n\nThis is test content."
        mock_converter_instance.assert_called_once_with(str(test_pdf))
        mock_text_from_rendered.assert_called_once_with(mock_rendered)
        
        # 檢查輸出檔案是否建立
        output_file = test_pdf.with_suffix('.md')
        assert output_file.exists()
        assert output_file.read_text(encoding='utf-8') == result
    
    @patch('service.markdown2.marker_converter.MARKER_AVAILABLE', True)
    @patch('service.markdown2.marker_converter.create_model_dict')
    @patch('service.markdown2.marker_converter.PdfConverter')
    def test_convert_pdf_to_markdown_file_not_found(self, mock_pdf_converter, mock_create_model_dict):
        """測試轉換不存在的 PDF 檔案"""
        mock_artifact_dict = Mock()
        mock_create_model_dict.return_value = mock_artifact_dict
        mock_converter_instance = Mock()
        mock_pdf_converter.return_value = mock_converter_instance
        
        converter = MarkerConverter()
        
        with pytest.raises(FileNotFoundError):
            converter.convert_pdf_to_markdown("nonexistent.pdf")
    
    @patch('service.markdown2.marker_converter.MARKER_AVAILABLE', True)
    @patch('service.markdown2.marker_converter.create_model_dict')
    @patch('service.markdown2.marker_converter.PdfConverter')
    @patch('service.markdown2.marker_converter.text_from_rendered')
    def test_convert_pdf_with_images(self, mock_text_from_rendered, mock_pdf_converter, mock_create_model_dict):
        """測試包含圖片的 PDF 轉換"""
        # 設置 mock
        mock_artifact_dict = Mock()
        mock_create_model_dict.return_value = mock_artifact_dict
        mock_converter_instance = Mock()
        mock_pdf_converter.return_value = mock_converter_instance
        
        # 建立測試圖片檔案
        test_image = Path(self.temp_dir) / "test_image.png"
        test_image.write_text("fake image content")
        
        mock_rendered = Mock()
        mock_converter_instance.return_value = mock_rendered
        mock_text_from_rendered.return_value = (
            "# Test with Image\n\n![Image](test_image.png)", 
            None, 
            [str(test_image)]
        )
        
        # 建立測試 PDF 檔案
        test_pdf = Path(self.temp_dir) / "test_with_images.pdf"
        test_pdf.write_text("fake pdf content")
        
        converter = MarkerConverter()
        result = converter.convert_pdf_to_markdown(str(test_pdf))
        
        assert result == "# Test with Image\n\n![Image](test_image.png)"
        
        # 檢查圖片目錄是否建立
        output_file = test_pdf.with_suffix('.md')
        images_dir = output_file.parent / f"{output_file.stem}_images"
        assert images_dir.exists()
    
    @patch('service.markdown2.marker_converter.MARKER_AVAILABLE', True)
    @patch('service.markdown2.marker_converter.create_model_dict')
    @patch('service.markdown2.marker_converter.PdfConverter')
    @patch('service.markdown2.marker_converter.text_from_rendered')
    def test_convert_multiple_pdfs(self, mock_text_from_rendered, mock_pdf_converter, mock_create_model_dict):
        """測試批量轉換多個 PDF 檔案"""
        mock_artifact_dict = Mock()
        mock_create_model_dict.return_value = mock_artifact_dict
        mock_converter_instance = Mock()
        mock_pdf_converter.return_value = mock_converter_instance
        
        # 建立測試 PDF 檔案
        test_pdf1 = Path(self.temp_dir) / "test1.pdf"
        test_pdf2 = Path(self.temp_dir) / "test2.pdf"
        test_pdf1.write_text("fake pdf content 1")
        test_pdf2.write_text("fake pdf content 2")
        
        mock_rendered1 = Mock()
        mock_rendered2 = Mock()
        mock_converter_instance.side_effect = [mock_rendered1, mock_rendered2]
        mock_text_from_rendered.side_effect = [
            ("# Test 1\n\nContent 1.", None, []),
            ("# Test 2\n\nContent 2.", None, [])
        ]
        
        converter = MarkerConverter()
        results = converter.convert_multiple_pdfs(self.temp_dir)
        
        assert len(results) == 2
        assert "test1.pdf" in results
        assert "test2.pdf" in results
        assert results["test1.pdf"] == "# Test 1\n\nContent 1."
        assert results["test2.pdf"] == "# Test 2\n\nContent 2."
    
    @patch('service.markdown2.marker_converter.MARKER_AVAILABLE', True)
    @patch('service.markdown2.marker_converter.create_model_dict')
    @patch('service.markdown2.marker_converter.PdfConverter')
    def test_get_conversion_info(self, mock_pdf_converter, mock_create_model_dict):
        """測試獲取轉換資訊"""
        mock_artifact_dict = Mock()
        mock_create_model_dict.return_value = mock_artifact_dict
        mock_converter_instance = Mock()
        mock_pdf_converter.return_value = mock_converter_instance
        
        # 建立測試 PDF 檔案
        test_pdf = Path(self.temp_dir) / "test_info.pdf"
        test_pdf.write_text("fake pdf content for info test")
        
        converter = MarkerConverter()
        info = converter.get_conversion_info(str(test_pdf))
        
        assert info["file_name"] == "test_info.pdf"
        assert info["extension"] == ".pdf"
        assert info["marker_available"] is True
        assert "file_size" in info
        assert "file_size_mb" in info
        assert "modified_time" in info
    
    def test_create_marker_converter_function(self):
        """測試建立 Marker 轉換器的便利函數"""
        with patch('service.markdown2.marker_converter.MARKER_AVAILABLE', True):
            with patch('service.markdown2.marker_converter.create_model_dict') as mock_create_model_dict:
                with patch('service.markdown2.marker_converter.PdfConverter') as mock_pdf_converter:
                    mock_artifact_dict = Mock()
                    mock_create_model_dict.return_value = mock_artifact_dict
                    mock_converter_instance = Mock()
                    mock_pdf_converter.return_value = mock_converter_instance
                    
                    converter = create_marker_converter()
                    assert isinstance(converter, MarkerConverter)
                    
                    # 測試使用自定義模型位置
                    model_locations = {"test": "/path/to/test"}
                    converter2 = create_marker_converter(model_locations)
                    assert converter2.model_locations == model_locations


class TestMarkerConverterIntegration:
    """Marker 轉換器整合測試"""
    
    def setup_method(self):
        """測試前的設置"""
        self.test_dir = Path(__file__).parent
        self.raw_docs_dir = self.test_dir.parent.parent / "raw_docs" / "old_version"
    
    @pytest.mark.skipif(not os.path.exists("/Users/pin/Desktop/workspace/rag-chat-backend/raw_docs/old_version"), 
                        reason="Raw docs directory not found")
    def test_with_real_pdf_files(self):
        """使用真實 PDF 檔案進行測試（需要 Marker 套件已安裝）"""
        if not os.path.exists(self.raw_docs_dir):
            pytest.skip("Raw docs directory not found")
        
        pdf_files = list(self.raw_docs_dir.glob("*.pdf"))
        if not pdf_files:
            pytest.skip("No PDF files found in raw_docs")
        
        # 只測試第一個 PDF 檔案
        test_pdf = pdf_files[0]
        
        try:
            converter = MarkerConverter()
            info = converter.get_conversion_info(str(test_pdf))
            
            assert info["file_name"] == test_pdf.name
            assert info["extension"] == ".pdf"
            assert info["file_size"] > 0
            
        except ImportError:
            pytest.skip("Marker package not installed")
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
