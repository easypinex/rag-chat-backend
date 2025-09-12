#!/usr/bin/env python3
"""
TypedDict 結構演示

展示新的 TypedDict 類型定義的優勢
"""

import sys
from pathlib import Path

# 添加父目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from json_marker_converter import PageInfo, PageBlockInfo
    from typing import get_type_hints
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"❌ 依賴套件未安裝: {e}")
    DEPENDENCIES_AVAILABLE = False


def demonstrate_typedict_advantages():
    """展示 TypedDict 的優勢"""
    print("🎯 TypedDict 結構優勢展示")
    print("=" * 50)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 依賴套件未安裝，跳過演示")
        return
    
    print("📋 舊的複雜類型定義:")
    print("  PageInfo = Dict[str, Union[str, int, List[Dict[str, Union[int, Dict[str, int]]]]]]")
    print("  ❌ 難以閱讀和理解")
    print("  ❌ IDE 無法提供良好的自動完成")
    print("  ❌ 類型檢查困難")
    print()
    
    print("✨ 新的 TypedDict 結構:")
    print("  class PageBlockInfo(TypedDict):")
    print("      page_number: int")
    print("      block_count: int")
    print("      block_types: Dict[str, int]")
    print()
    print("  class PageInfo(TypedDict):")
    print("      file_name: str")
    print("      total_pages: int")
    print("      pages: List[PageBlockInfo]")
    print("  ✅ 清晰易讀")
    print("  ✅ IDE 提供完整的自動完成")
    print("  ✅ 類型檢查更準確")
    print()


def demonstrate_type_safety():
    """展示類型安全的使用"""
    print("🛡️ 類型安全使用範例:")
    print("-" * 30)
    
    # 創建一個範例 PageInfo 結構
    sample_page_info: PageBlockInfo = {
        'page_number': 1,
        'block_count': 5,
        'block_types': {'paragraph': 3, 'title': 1, 'table': 1}
    }
    
    sample_info: PageInfo = {
        'file_name': 'sample.pdf',
        'total_pages': 10,
        'pages': [sample_page_info]
    }
    
    print("✅ 類型安全的訪問:")
    print(f"  檔案名稱: {sample_info['file_name']}")
    print(f"  總頁數: {sample_info['total_pages']}")
    print(f"  第一頁區塊數: {sample_info['pages'][0]['block_count']}")
    print(f"  第一頁區塊類型: {sample_info['pages'][0]['block_types']}")
    print()
    
    print("🔍 IDE 支援:")
    print("  - 自動完成: sample_info[''] 會顯示可用的鍵")
    print("  - 類型提示: 鼠標懸停會顯示具體的類型")
    print("  - 錯誤檢查: 錯誤的鍵名會被 IDE 標記")
    print()


def demonstrate_nested_structure():
    """展示嵌套結構的清晰性"""
    print("🏗️ 嵌套結構清晰性:")
    print("-" * 30)
    
    print("舊的複雜嵌套:")
    print("  Dict[str, Union[str, int, List[Dict[str, Union[int, Dict[str, int]]]]]]")
    print("  ❌ 難以理解嵌套層級")
    print("  ❌ 不知道每個層級的具體結構")
    print()
    
    print("新的 TypedDict 結構:")
    print("  PageInfo:")
    print("    ├── file_name: str")
    print("    ├── total_pages: int")
    print("    └── pages: List[PageBlockInfo]")
    print("        └── PageBlockInfo:")
    print("            ├── page_number: int")
    print("            ├── block_count: int")
    print("            └── block_types: Dict[str, int]")
    print("  ✅ 清晰的層級結構")
    print("  ✅ 每個層級都有明確的類型")
    print("  ✅ 易於理解和維護")
    print()


def demonstrate_usage_examples():
    """展示實際使用範例"""
    print("💡 實際使用範例:")
    print("-" * 30)
    
    print("1. 創建頁面資訊:")
    print("""
    # 創建單頁資訊
    page_info: PageBlockInfo = {
        'page_number': 1,
        'block_count': 3,
        'block_types': {'paragraph': 2, 'title': 1}
    }
    
    # 創建完整資訊
    info: PageInfo = {
        'file_name': 'document.pdf',
        'total_pages': 5,
        'pages': [page_info]
    }
    """)
    
    print("2. 類型安全的訪問:")
    print("""
    # IDE 會提供自動完成
    print(f"檔案: {info['file_name']}")  # IDE 知道這是 str
    print(f"頁數: {info['total_pages']}")  # IDE 知道這是 int
    
    # 嵌套訪問也有類型提示
    for page in info['pages']:  # IDE 知道這是 List[PageBlockInfo]
        print(f"第 {page['page_number']} 頁")  # IDE 知道這是 int
        print(f"區塊數: {page['block_count']}")  # IDE 知道這是 int
    """)
    
    print("3. 類型檢查:")
    print("""
    # mypy 或其他類型檢查器會驗證類型
    # 錯誤的類型會被檢測出來
    # info['file_name'] = 123  # ❌ 類型錯誤
    # info['pages'][0]['page_number'] = "1"  # ❌ 類型錯誤
    """)


def main():
    """主函數"""
    print("🚀 TypedDict 結構演示")
    print("=" * 60)
    
    demonstrate_typedict_advantages()
    demonstrate_type_safety()
    demonstrate_nested_structure()
    demonstrate_usage_examples()
    
    print("✅ TypedDict 演示完成!")
    print("\n💡 總結:")
    print("  - TypedDict 讓複雜的嵌套類型變得清晰")
    print("  - 提供更好的 IDE 支援和類型檢查")
    print("  - 代碼更易讀、易維護")
    print("  - 減少類型相關的錯誤")


if __name__ == "__main__":
    main()
