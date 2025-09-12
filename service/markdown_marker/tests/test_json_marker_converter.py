"""
JSON Marker Converter 測試

測試 JSON Marker 轉換器的各種功能
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加父目錄到 Python 路徑
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 測試導入
try:
    from json_marker_converter import JsonMarkerConverter, create_json_marker_converter
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.config.parser import ConfigParser
    from bs4 import BeautifulSoup
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required packages not available")
class TestJsonMarkerConverter:
    """JSON Marker 轉換器測試類"""
    
    def setup_method(self):
        """每個測試方法前的設置"""
        self.converter = None
        self.temp_dir = None
    
    def teardown_method(self):
        """每個測試方法後的清理"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_converter_initialization(self):
        """測試轉換器初始化"""
        with patch('json_marker_converter.ConfigParser') as mock_config, \
             patch('json_marker_converter.create_model_dict') as mock_models, \
             patch('json_marker_converter.PdfConverter') as mock_converter:
            
            mock_config.return_value.generate_config_dict.return_value = {"output_format": "json"}
            mock_models.return_value = {}
            mock_converter.return_value = Mock()
            
            converter = JsonMarkerConverter()
            assert converter is not None
            assert converter.converter is not None
    
    def test_md_escape(self):
        """測試 Markdown 轉義功能"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter'):
            
            converter = JsonMarkerConverter()
            
            # 測試管道符號轉義
            assert converter._md_escape("test|text") == "test\\|text"
            assert converter._md_escape("normal text") == "normal text"
            assert converter._md_escape("") == ""
    
    def test_table_html_to_md_simple(self):
        """測試簡單表格轉換"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter'):
            
            converter = JsonMarkerConverter()
            
            # 簡單表格
            html = """
            <table>
                <tr><th>Name</th><th>Age</th></tr>
                <tr><td>John</td><td>25</td></tr>
                <tr><td>Jane</td><td>30</td></tr>
            </table>
            """
            
            result = converter._table_html_to_md(html)
            assert "| Name | Age |" in result
            assert "| John | 25 |" in result
            assert "| Jane | 30 |" in result
    
    def test_table_html_to_md_complex(self):
        """測試複雜表格轉換（保留 HTML）"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter'):
            
            converter = JsonMarkerConverter()
            
            # 有 rowspan 的複雜表格
            html = """
            <table>
                <tr><th rowspan="2">Item</th><th>Q1</th><th>Q2</th></tr>
                <tr><td>100</td><td>200</td></tr>
            </table>
            """
            
            result = converter._table_html_to_md(html)
            assert "complex table; keep HTML" in result
            assert "<table>" in result
    
    def test_table_html_to_md_empty(self):
        """測試空表格處理"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter'):
            
            converter = JsonMarkerConverter()
            
            # 空表格
            result = converter._table_html_to_md("")
            assert result == ""
            
            # 無表格標籤
            result = converter._table_html_to_md("<div>No table here</div>")
            assert result == ""
    
    def test_block_to_md_title(self):
        """測試標題區塊轉換"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter'):
            
            converter = JsonMarkerConverter()
            
            # 模擬標題區塊
            block = Mock()
            block.block_type = "title"
            block.text = "Test Title"
            
            result = converter._block_to_md(block)
            assert "## Test Title" in result
    
    def test_block_to_md_paragraph(self):
        """測試段落區塊轉換"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter'):
            
            converter = JsonMarkerConverter()
            
            # 模擬段落區塊
            block = Mock()
            block.block_type = "paragraph"
            block.text = "This is a test paragraph."
            
            result = converter._block_to_md(block)
            assert "This is a test paragraph." in result
    
    def test_block_to_md_equation(self):
        """測試方程式區塊轉換"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter'):
            
            converter = JsonMarkerConverter()
            
            # 模擬方程式區塊
            block = Mock()
            block.block_type = "equation"
            block.text = "x^2 + y^2 = z^2"
            
            result = converter._block_to_md(block)
            assert "$x^2 + y^2 = z^2$" in result
    
    def test_block_to_md_figure(self):
        """測試圖片區塊轉換"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter'):
            
            converter = JsonMarkerConverter()
            
            # 模擬圖片區塊
            block = Mock()
            block.block_type = "figure"
            block.caption = "Test Figure"
            
            result = converter._block_to_md(block)
            assert "![figure]" in result
            assert "Test Figure" in result
    
    def test_marker_json_pages(self):
        """測試頁面提取功能"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter') as mock_converter_class:
            
            # 模擬轉換器
            mock_converter = Mock()
            mock_converter_class.return_value = mock_converter
            
            # 模擬頁面數據
            mock_page1 = Mock()
            mock_page1.children = [Mock(), Mock()]
            mock_page2 = Mock()
            mock_page2.children = [Mock()]
            
            mock_rendered = Mock()
            mock_rendered.children = [mock_page1, mock_page2]
            mock_converter.return_value = mock_rendered
            
            converter = JsonMarkerConverter()
            pages = converter.marker_json_pages("test.pdf")
            
            assert len(pages) == 2
            assert len(pages[0].children) == 2
            assert len(pages[1].children) == 1
    
    def test_marker_json_to_markdown(self):
        """測試 JSON 到 Markdown 轉換"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter') as mock_converter_class:
            
            # 模擬轉換器
            mock_converter = Mock()
            mock_converter_class.return_value = mock_converter
            
            # 模擬頁面數據
            mock_page = Mock()
            mock_page.children = []
            
            mock_rendered = Mock()
            mock_rendered.children = [mock_page]
            mock_converter.return_value = mock_rendered
            
            converter = JsonMarkerConverter()
            result = converter.marker_json_to_markdown("test.pdf")
            
            assert "## Page 1" in result
            assert "---" in result
    
    def test_convert_pdf_to_markdown_file_not_found(self):
        """測試檔案不存在錯誤處理"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter'):
            
            converter = JsonMarkerConverter()
            
            with pytest.raises(FileNotFoundError):
                converter.convert_pdf_to_markdown("nonexistent.pdf")
    
    def test_convert_multiple_pdfs_directory_not_found(self):
        """測試目錄不存在錯誤處理"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter'):
            
            converter = JsonMarkerConverter()
            
            with pytest.raises(FileNotFoundError):
                converter.convert_multiple_pdfs("nonexistent_directory")
    
    def test_get_page_info(self):
        """測試頁面資訊獲取"""
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter') as mock_converter_class:
            
            # 模擬轉換器
            mock_converter = Mock()
            mock_converter_class.return_value = mock_converter
            
            # 模擬頁面數據
            mock_page = Mock()
            mock_block1 = Mock()
            mock_block1.block_type = "paragraph"
            mock_block2 = Mock()
            mock_block2.block_type = "title"
            mock_page.children = [mock_block1, mock_block2]
            
            mock_rendered = Mock()
            mock_rendered.children = [mock_page]
            mock_converter.return_value = mock_rendered
            
            # 創建臨時 PDF 檔案
            self.temp_dir = tempfile.mkdtemp()
            test_pdf = os.path.join(self.temp_dir, "test.pdf")
            with open(test_pdf, "w") as f:
                f.write("dummy pdf content")
            
            converter = JsonMarkerConverter()
            page_info = converter.get_page_info(test_pdf)
            
            assert page_info["file_name"] == "test.pdf"
            assert page_info["total_pages"] == 1
            assert len(page_info["pages"]) == 1
            assert page_info["pages"][0]["page_number"] == 1
            assert page_info["pages"][0]["block_count"] == 2
    
    def test_create_json_marker_converter(self):
        """測試便利函數"""
        with patch('json_marker_converter.JsonMarkerConverter') as mock_converter_class:
            mock_converter = Mock()
            mock_converter_class.return_value = mock_converter
            
            result = create_json_marker_converter()
            assert result == mock_converter
            mock_converter_class.assert_called_once_with(None)
    
    def test_create_json_marker_converter_with_locations(self):
        """測試帶模型位置的便利函數"""
        with patch('json_marker_converter.JsonMarkerConverter') as mock_converter_class:
            mock_converter = Mock()
            mock_converter_class.return_value = mock_converter
            
            model_locations = {"layout_model": "/path/to/model"}
            result = create_json_marker_converter(model_locations)
            assert result == mock_converter
            mock_converter_class.assert_called_once_with(model_locations)


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required packages not available")
class TestJsonMarkerConverterIntegration:
    """JSON Marker 轉換器整合測試"""
    
    def setup_method(self):
        """每個測試方法前的設置"""
        self.temp_dir = None
    
    def teardown_method(self):
        """每個測試方法後的清理"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_full_conversion_workflow(self):
        """測試完整轉換工作流程"""
        # 這個測試需要實際的 Marker 環境，所以用 mock
        with patch('json_marker_converter.ConfigParser'), \
             patch('json_marker_converter.create_model_dict'), \
             patch('json_marker_converter.PdfConverter') as mock_converter_class:
            
            # 模擬轉換器
            mock_converter = Mock()
            mock_converter_class.return_value = mock_converter
            
            # 模擬頁面數據
            mock_page = Mock()
            mock_block = Mock()
            mock_block.block_type = "paragraph"
            mock_block.text = "Test content"
            mock_page.children = [mock_block]
            
            mock_rendered = Mock()
            mock_rendered.children = [mock_page]
            mock_converter.return_value = mock_rendered
            
            # 創建臨時 PDF 檔案
            self.temp_dir = tempfile.mkdtemp()
            test_pdf = os.path.join(self.temp_dir, "test.pdf")
            with open(test_pdf, "w") as f:
                f.write("dummy pdf content")
            
            converter = JsonMarkerConverter()
            result = converter.convert_pdf_to_markdown(test_pdf)
            
            assert "## Page 1" in result
            assert "Test content" in result


if __name__ == "__main__":
    pytest.main([__file__])
