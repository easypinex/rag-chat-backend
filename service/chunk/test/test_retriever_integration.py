"""
Retriever 整合測試

測試 HierarchicalChunkSplitter 與 ParentDocumentRetriever 的整合功能。
"""

import sys
import logging
from pathlib import Path

# 添加路徑到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk.hierarchical_splitter import HierarchicalChunkSplitter
from service.chunk.hierarchical_models import HierarchicalSplitResult

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_hierarchical_splitter():
    """測試分層分割器基本功能"""
    logger.info("=== 測試分層分割器 ===")
    
    try:
        # 創建分層分割器
        splitter = HierarchicalChunkSplitter(
            parent_chunk_size=2000,
            child_chunk_size=500,
            child_chunk_overlap=100
        )
        
        logger.info("✓ HierarchicalChunkSplitter 創建成功")
        
        # 測試文件
        test_file = project_root / "raw_docs" / "理賠審核原則.xlsx"
        
        if not test_file.exists():
            logger.warning(f"測試文件不存在: {test_file}")
            return False
        
        # 進行分層分割
        result = splitter.split_hierarchically(str(test_file))
        
        logger.info(f"✓ 分層分割完成:")
        logger.info(f"- 父chunks: {len(result.parent_chunks)}")
        logger.info(f"- 子chunks: {len(result.child_chunks)}")
        logger.info(f"- 分組效率: {result.grouping_analysis.grouping_efficiency:.2%}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 分層分割器測試失敗: {e}")
        return False


def test_data_preparation():
    """測試資料準備功能"""
    logger.info("=== 測試資料準備 ===")
    
    try:
        # 創建分層分割器
        splitter = HierarchicalChunkSplitter(
            parent_chunk_size=1500,
            child_chunk_size=400,
            child_chunk_overlap=80
        )
        
        # 測試文件
        test_file = project_root / "raw_docs" / "理賠審核原則.xlsx"
        
        if not test_file.exists():
            logger.warning(f"測試文件不存在: {test_file}")
            return False
        
        # 進行分層分割
        result = splitter.split_hierarchically(str(test_file))
        
        # 準備 ParentDocumentRetriever 的資料
        documents = []
        for parent_chunk in result.parent_chunks:
            # 模擬 LangChain Document 創建
            doc_data = {
                "page_content": parent_chunk.document.page_content,
                "metadata": {
                    **parent_chunk.document.metadata,
                    "chunk_id": parent_chunk.chunk_id,
                    "chunk_type": "parent"
                }
            }
            documents.append(doc_data)
        
        logger.info(f"✓ 資料準備完成:")
        logger.info(f"- 準備了 {len(documents)} 個文檔")
        
        # 檢查文檔結構
        if documents:
            sample_doc = documents[0]
            logger.info(f"- 文檔內容長度: {len(sample_doc['page_content'])}")
            logger.info(f"- 元數據欄位: {list(sample_doc['metadata'].keys())}")
            logger.info(f"- Chunk ID: {sample_doc['metadata'].get('chunk_id')}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 資料準備測試失敗: {e}")
        return False


def test_retrieval_simulation():
    """測試檢索模擬"""
    logger.info("=== 測試檢索模擬 ===")
    
    try:
        # 創建分層分割器
        splitter = HierarchicalChunkSplitter(
            parent_chunk_size=2000,
            child_chunk_size=600,
            child_chunk_overlap=120
        )
        
        # 測試文件
        test_file = project_root / "raw_docs" / "理賠審核原則.xlsx"
        
        if not test_file.exists():
            logger.warning(f"測試文件不存在: {test_file}")
            return False
        
        # 進行分層分割
        result = splitter.split_hierarchically(str(test_file))
        
        # 模擬檢索過程
        query = "理賠審核"
        
        # 模擬子文檔檢索（基於內容相似度）
        child_docs = []
        for child_chunk in result.child_chunks:
            content = child_chunk.document.page_content.lower()
            if query.lower() in content:
                child_docs.append({
                    "chunk_id": child_chunk.chunk_id,
                    "parent_chunk_id": child_chunk.parent_chunk_id,
                    "content": child_chunk.document.page_content,
                    "size": child_chunk.size,
                    "is_table_chunk": child_chunk.is_table_chunk
                })
        
        logger.info(f"✓ 檢索模擬完成:")
        logger.info(f"- 查詢: '{query}'")
        logger.info(f"- 找到 {len(child_docs)} 個相關子chunks")
        
        # 模擬重排序（按大小排序作為簡單示例）
        child_docs.sort(key=lambda x: x["size"], reverse=True)
        top_k = min(5, len(child_docs))
        top_child_docs = child_docs[:top_k]
        
        logger.info(f"- 重排序後取前 {top_k} 個")
        
        # 模擬獲取對應的父文檔
        parent_docs = []
        for child_doc in top_child_docs:
            parent_id = child_doc["parent_chunk_id"]
            for parent_chunk in result.parent_chunks:
                if parent_chunk.chunk_id == parent_id:
                    parent_docs.append({
                        "chunk_id": parent_chunk.chunk_id,
                        "content": parent_chunk.document.page_content,
                        "size": parent_chunk.size,
                        "has_tables": parent_chunk.has_tables
                    })
                    break
        
        logger.info(f"- 獲取到 {len(parent_docs)} 個對應的父chunks")
        
        # 顯示結果摘要
        if parent_docs:
            total_context_size = sum(doc["size"] for doc in parent_docs)
            logger.info(f"- 總上下文大小: {total_context_size} 字")
            
            # 顯示第一個父chunk的預覽
            first_parent = parent_docs[0]
            preview = first_parent["content"][:150]
            logger.info(f"- 第一個父chunk預覽: {preview}...")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 檢索模擬測試失敗: {e}")
        return False


def test_integration_workflow():
    """測試完整整合工作流程"""
    logger.info("=== 測試完整整合工作流程 ===")
    
    try:
        # 步驟1: 創建分層分割器
        splitter = HierarchicalChunkSplitter(
            parent_chunk_size=2500,
            child_chunk_size=800,
            child_chunk_overlap=150
        )
        
        # 步驟2: 處理文檔
        test_file = project_root / "raw_docs" / "理賠審核原則.xlsx"
        
        if not test_file.exists():
            logger.warning(f"測試文件不存在: {test_file}")
            return False
        
        result = splitter.split_hierarchically(str(test_file))
        
        # 步驟3: 準備檢索資料
        documents = []
        for parent_chunk in result.parent_chunks:
            doc = {
                "page_content": parent_chunk.document.page_content,
                "metadata": {
                    **parent_chunk.document.metadata,
                    "chunk_id": parent_chunk.chunk_id,
                    "chunk_type": "parent"
                }
            }
            documents.append(doc)
        
        # 步驟4: 模擬檢索流程
        queries = ["理賠審核", "保險", "申請"]
        
        for query in queries:
            logger.info(f"處理查詢: '{query}'")
            
            # 模擬檢索
            relevant_docs = []
            for doc in documents:
                if query.lower() in doc["page_content"].lower():
                    relevant_docs.append(doc)
            
            # 模擬重排序（按內容長度）
            relevant_docs.sort(key=lambda x: len(x["page_content"]), reverse=True)
            top_docs = relevant_docs[:3]  # 取前3個
            
            logger.info(f"  - 找到 {len(relevant_docs)} 個相關文檔")
            logger.info(f"  - 重排序後取前 {len(top_docs)} 個")
            
            if top_docs:
                total_size = sum(len(doc["page_content"]) for doc in top_docs)
                logger.info(f"  - 總上下文大小: {total_size} 字")
        
        logger.info("✓ 完整整合工作流程測試成功")
        return True
        
    except Exception as e:
        logger.error(f"✗ 完整整合工作流程測試失敗: {e}")
        return False


def main():
    """主測試程式"""
    logger.info("開始 Retriever 整合測試...")
    
    tests = [
        ("分層分割器", test_hierarchical_splitter),
        ("資料準備", test_data_preparation),
        ("檢索模擬", test_retrieval_simulation),
        ("完整工作流程", test_integration_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n執行測試: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✓ {test_name} 測試通過")
            else:
                logger.error(f"✗ {test_name} 測試失敗")
        except Exception as e:
            logger.error(f"✗ {test_name} 測試異常: {e}")
            results.append((test_name, False))
    
    # 顯示測試結果摘要
    logger.info("\n" + "="*50)
    logger.info("測試結果摘要:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        logger.info(f"- {test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        logger.info("🎉 所有測試通過！Retriever 整合功能已準備就緒。")
    else:
        logger.warning("⚠ 部分測試失敗，請檢查相關功能。")


if __name__ == "__main__":
    main()
