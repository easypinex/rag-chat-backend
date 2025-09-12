#!/usr/bin/env python3
"""
類型定義使用範例

展示 JsonMarkerConverter 的輸入輸出類型
"""

import sys
from pathlib import Path

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from json_marker_converter import (
        JsonMarkerConverter, 
        PageInfo, 
        PageBlockInfo
    )
    from typing import get_type_hints
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"❌ 依賴套件未安裝: {e}")
    DEPENDENCIES_AVAILABLE = False


def demonstrate_types():
    """展示類型定義和使用方法"""
    print("🔍 JsonMarkerConverter 類型定義展示")
    print("=" * 50)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 依賴套件未安裝，跳過演示")
        return
    
    # 展示類型定義
    print("📋 類型定義:")
    print("  - List[str] (頁面列表：字符串列表)")
    print("  - PageBlockInfo = TypedDict (單頁區塊資訊)")
    print("  - PageInfo = TypedDict (頁面資訊結構)")
    print()
    
    # 展示方法簽名
    print("🔧 主要方法簽名:")
    converter = JsonMarkerConverter()
    
    # 獲取類型提示
    hints = get_type_hints(converter.marker_json_pages)
    print(f"  - marker_json_pages(input_pdf: str) -> {hints.get('return', 'List[str]')}")
    
    hints = get_type_hints(converter.get_page_info)
    print(f"  - get_page_info(pdf_path: str) -> {hints.get('return', 'PageInfo')}")
    print()
    
    # 展示實際使用
    print("💡 實際使用範例:")
    print("""
    # 獲取頁面列表
    pages: List[str] = converter.marker_json_pages("document.pdf")
    
    # 檢查頁面類型（現在都是字符串）
    for i, page in enumerate(pages, 1):
        print(f"第 {i} 頁: {len(page)} 字元的 Markdown 內容")
        print(f"內容預覽: {page[:100]}...")
    
    # 獲取頁面資訊（使用 TypedDict）
    info: PageInfo = converter.get_page_info("document.pdf")
    print(f"檔案: {info['file_name']}")
    print(f"總頁數: {info['total_pages']}")
    
    # 遍歷頁面資訊（類型安全）
    for page_info in info['pages']:
        print(f"第 {page_info['page_number']} 頁:")
        print(f"  - 區塊數量: {page_info['block_count']}")
        print(f"  - 區塊類型: {page_info['block_types']}")
    """)


def demonstrate_page_content_types():
    """展示頁面內容類型"""
    print("\n📄 頁面內容類型說明:")
    print("-" * 30)
    
    print("✅ 統一的字符串類型 (str):")
    print("   - 所有頁面都是字符串類型")
    print("   - 每個字符串是一頁的 Markdown 內容")
    print("   - 內容已按智能策略分割（按標題和段落）")
    print()
    
    print("🔍 實際處理流程:")
    print("   1. Marker 返回 MarkdownOutput 對象")
    print("   2. 提取 markdown 屬性（字符串）")
    print("   3. 按智能策略分割為多頁")
    print("   4. 返回 List[str]，每頁都是 Markdown 字符串")
    print()
    
    print("💡 優勢:")
    print("   - 類型統一，無需類型檢查")
    print("   - 直接可用的 Markdown 內容")
    print("   - 簡化的 API 設計")


def demonstrate_page_info_structure():
    """展示頁面資訊結構"""
    print("\n📊 頁面資訊結構說明:")
    print("-" * 30)
    
    print("使用 TypedDict 的清晰結構:")
    print("""
    class PageBlockInfo(TypedDict):
        page_number: int           # 頁碼
        block_count: int           # 區塊數量
        block_types: Dict[str, int]  # 區塊類型分布
    
    class PageInfo(TypedDict):
        file_name: str             # 檔案名稱
        total_pages: int           # 總頁數
        pages: List[PageBlockInfo]  # 每頁詳細資訊列表
    
    # 使用範例
    info: PageInfo = {
        'file_name': 'document.pdf',
        'total_pages': 10,
        'pages': [
            {
                'page_number': 1,
                'block_count': 5,
                'block_types': {'paragraph': 3, 'title': 1, 'table': 1}
            },
            # ... 更多頁面
        ]
    }
    """)


def main():
    """主函數"""
    print("🚀 JsonMarkerConverter 類型定義和使用範例")
    print("=" * 60)
    
    demonstrate_types()
    demonstrate_page_content_types()
    demonstrate_page_info_structure()
    
    print("\n✅ 類型定義展示完成!")
    print("\n💡 提示:")
    print("  - 使用類型提示可以獲得更好的 IDE 支援")
    print("  - 類型定義讓代碼更清晰和可維護")
    print("  - 實際使用時會根據 Marker 輸出自動處理")


if __name__ == "__main__":
    main()
