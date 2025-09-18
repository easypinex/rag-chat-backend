"""
統一轉換器測試

測試 UnifiedMarkdownConverter 的基本功能。
"""

import unittest
from pathlib import Path
from service.markdown_integrate import UnifiedMarkdownConverter, FormatRouter


class TestUnifiedConverter(unittest.TestCase):
    """統一轉換器測試類"""
    
    def setUp(self):
        """設置測試環境"""
        self.converter = UnifiedMarkdownConverter()
    
    def test_format_router(self):
        """測試格式路由器"""
        # 測試支援的格式
        self.assertTrue(FormatRouter.is_supported("test.pdf"))
        self.assertTrue(FormatRouter.is_supported("test.docx"))
        self.assertTrue(FormatRouter.is_supported("test.xlsx"))
        self.assertFalse(FormatRouter.is_supported("test.xyz"))
        
        # 測試轉換器選擇
        converter_name, file_type = FormatRouter.get_converter_info("test.pdf")
        self.assertEqual(converter_name, "marker")
        self.assertEqual(file_type, ".pdf")
        
        converter_name, file_type = FormatRouter.get_converter_info("test.xlsx")
        self.assertEqual(converter_name, "markitdown")
        self.assertEqual(file_type, ".xlsx")
    
    def test_converter_initialization(self):
        """測試轉換器初始化"""
        # 檢查轉換器是否正確初始化
        self.assertIsNotNone(self.converter)
        
        # 檢查支援的格式
        formats = self.converter.get_supported_formats()
        self.assertIn("marker", formats)
        self.assertIn("markitdown", formats)
        
        # 檢查轉換器狀態
        status = self.converter.get_converter_status()
        self.assertIn("marker", status)
        self.assertIn("markitdown", status)
    
    def test_file_support_check(self):
        """測試檔案支援檢查"""
        # 測試支援的格式
        self.assertTrue(self.converter.is_supported("test.pdf"))
        self.assertTrue(self.converter.is_supported("test.docx"))
        self.assertTrue(self.converter.is_supported("test.xlsx"))
        
        # 測試不支援的格式
        self.assertFalse(self.converter.is_supported("test.xyz"))
        self.assertFalse(self.converter.is_supported("test.unknown"))
    
    def test_nonexistent_file(self):
        """測試不存在的檔案"""
        with self.assertRaises(FileNotFoundError):
            self.converter.convert_file("nonexistent.pdf")
    
    def test_unsupported_format(self):
        """測試不支援的格式"""
        # 創建一個不支援格式的臨時檔案
        temp_file = Path("temp.xyz")
        temp_file.write_text("test content")
        
        try:
            with self.assertRaises(ValueError):
                self.converter.convert_file("temp.xyz")
        finally:
            # 清理臨時檔案
            if temp_file.exists():
                temp_file.unlink()


class TestDataModels(unittest.TestCase):
    """數據模型測試類"""
    
    def test_page_info_creation(self):
        """測試 PageInfo 創建"""
        from service.markdown_integrate import PageInfo
        
        # 測試基本創建
        page = PageInfo(page_number=1, content="test content")
        self.assertEqual(page.page_number, 1)
        self.assertEqual(page.content, "test content")
        self.assertEqual(page.content_length, len("test content"))
        
        # 測試 post_init
        self.assertIsNotNone(page.block_types)
        self.assertIsNotNone(page.tables)
    
    def test_conversion_result_creation(self):
        """測試 ConversionResult 創建"""
        from service.markdown_integrate import ConversionResult, ConversionMetadata
        
        metadata = ConversionMetadata(
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            file_type=".pdf",
            file_size=1024,
            total_pages=1,
            total_tables=0,
            total_content_length=100,
            conversion_timestamp=1234567890.0,
            converter_used="marker"
        )
        
        result = ConversionResult(
            content="test content",
            pages=None,
            metadata=metadata
        )
        
        self.assertEqual(result.content, "test content")
        self.assertIsNotNone(result.pages)  # 應該被 post_init 初始化為空列表
        self.assertEqual(result.metadata.file_name, "test.pdf")


def run_tests():
    """運行測試"""
    print("運行統一轉換器測試...")
    
    # 創建測試套件
    suite = unittest.TestSuite()
    
    # 添加測試
    suite.addTest(unittest.makeSuite(TestUnifiedConverter))
    suite.addTest(unittest.makeSuite(TestDataModels))
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回結果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\n✓ 所有測試通過!")
    else:
        print("\n✗ 有測試失敗!")
