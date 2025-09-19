"""
Retriever 整合範例

展示如何使用 HierarchicalChunkSplitter 與 LangChain ParentDocumentRetriever 整合。

重要：ParentDocumentRetriever 的正確工作流程：
1. 使用 child chunks 進行向量檢索（更精確的匹配）
2. 對檢索到的 child chunks 進行 rerank（提高相關性）
3. 根據 rerank 後的 child chunks 找出對應的 parent chunks
4. 將 parent chunks 傳遞給 LLM（保持完整上下文）
"""

import sys
import logging
from pathlib import Path
from typing import List, Tuple, Optional

# 添加路徑到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from service.chunk.hierarchical_splitter import HierarchicalChunkSplitter
from service.chunk.hierarchical_models import HierarchicalSplitResult

# 嘗試導入 LangChain 相關套件
try:
    from langchain_core.documents import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    Document = None

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HierarchicalRetriever:
    """整合 HierarchicalChunkSplitter 與 ParentDocumentRetriever 的包裝類"""
    
    def __init__(self, 
                 parent_chunk_size: int = 2000,      # 預設值，適合中文32k embedding
                 child_chunk_size: int = 350,        # 預設值，約100-150 tokens，適合中文rerank 512
                 child_chunk_overlap: int = 50,       # 預設值，保持中文語義連貫性
                 embedding_model: str = "BAAI/bge-small-en-v1.5",
                 rerank_model: str = "BAAI/bge-reranker-large"):
        """
        初始化分層檢索器
        
        Args:
            parent_chunk_size: 父chunk大小
            child_chunk_size: 子chunk大小
            child_chunk_overlap: 子chunk重疊
            embedding_model: 嵌入模型名稱
            rerank_model: 重排序模型名稱
        """
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.child_chunk_overlap = child_chunk_overlap
        
        # 初始化分層分割器
        self.hierarchical_splitter = HierarchicalChunkSplitter(
            parent_chunk_size=parent_chunk_size,
            child_chunk_size=child_chunk_size,
            child_chunk_overlap=child_chunk_overlap,
            keep_tables_together=True,
            normalize_output=True
        )
        
        # 初始化檢索器組件（模擬，實際使用時需要安裝相應套件）
        self._setup_retriever_components(embedding_model, rerank_model)
        
        logger.info(f"HierarchicalRetriever initialized")
        logger.info(f"Parent chunk size: {parent_chunk_size}, Child chunk size: {child_chunk_size}")
    
    def _setup_retriever_components(self, embedding_model: str, rerank_model: str):
        """設置檢索器組件（模擬版本）"""
        try:
            # 嘗試導入必要的套件
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            from langchain.retrievers import ParentDocumentRetriever
            from langchain.storage import InMemoryStore
            from langchain_community.vectorstores import FAISS
            from langchain_community.embeddings import HuggingFaceBgeEmbeddings
            from sentence_transformers import CrossEncoder
            from langchain_core.documents import Document
            
            # 初始化嵌入模型
            self.embeddings = HuggingFaceBgeEmbeddings(model_name=embedding_model)
            self.vectorstore = FAISS.from_texts(["dummy"], embedding=self.embeddings)
            self.store = InMemoryStore()
            
            # 初始化分割器
            self.child_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.child_chunk_size, 
                chunk_overlap=self.child_chunk_overlap
            )
            self.parent_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.parent_chunk_size, 
                chunk_overlap=200  # 使用預設值
            )
            
            # 初始化 ParentDocumentRetriever
            self.retriever = ParentDocumentRetriever(
                vectorstore=self.vectorstore.as_retriever(search_kwargs={"k": 50}),
                docstore=self.store,
                child_splitter=self.child_splitter,
                parent_splitter=self.parent_splitter
            )
            
            # 初始化重排序器
            self.reranker = CrossEncoder(rerank_model, max_length=512)
            
            logger.info("✓ Retriever components initialized successfully")
            
        except ImportError as e:
            logger.warning(f"⚠ 無法導入檢索器套件: {e}")
            logger.warning("請安裝: pip install langchain langchain-community sentence-transformers transformers")
            self.retriever = None
            self.reranker = None
    
    def add_documents_from_file(self, file_path: str) -> Optional[HierarchicalSplitResult]:
        """從文件添加文檔到檢索器"""
        try:
            logger.info(f"Processing file: {file_path}")
            
            # 使用分層分割器處理文件
            result = self.hierarchical_splitter.split_hierarchically(file_path)
            
            if not self.retriever:
                logger.warning("檢索器未初始化，跳過添加文檔")
                return result
            
            # 準備文檔 - ParentDocumentRetriever 需要正確的父子關係
            parent_documents = []
            child_documents = []
            
            # 準備父文檔
            for parent_chunk in result.parent_chunks:
                if not LANGCHAIN_AVAILABLE:
                    logger.warning("LangChain 不可用，跳過文檔準備")
                    return result
                parent_doc = Document(
                    page_content=parent_chunk.document.page_content,
                    metadata={
                        **parent_chunk.document.metadata,
                        "chunk_id": parent_chunk.chunk_id,
                        "chunk_type": "parent"
                    }
                )
                parent_documents.append(parent_doc)
            
            # 準備子文檔
            for child_chunk in result.child_chunks:
                child_doc = Document(
                    page_content=child_chunk.document.page_content,
                    metadata={
                        **child_chunk.document.metadata,
                        "chunk_id": child_chunk.chunk_id,
                        "parent_id": child_chunk.parent_chunk_id,
                        "chunk_type": "child"
                    }
                )
                child_documents.append(child_doc)
            
            # 添加到檢索器（ParentDocumentRetriever 會自動處理父子關係）
            self.retriever.add_documents(parent_documents)
            
            logger.info(f"✓ Added {len(parent_documents)} parent documents to retriever")
            return result
            
        except Exception as e:
            logger.error(f"添加文檔失敗: {e}")
            return None
    
    def retrieve_with_rerank(self, query: str, top_k: int = 8) -> Tuple[List, List]:
        """檢索並重排序 - 使用 child chunks 進行檢索和 rerank"""
        if not self.retriever or not self.reranker:
            logger.warning("檢索器或重排序器未初始化")
            return [], []
        
        try:
            # 步驟1: 使用 child chunks 進行向量檢索（更精確的匹配）
            child_docs = self.retriever.vectorstore.similarity_search(query, k=50)
            logger.info(f"Retrieved {len(child_docs)} child documents")
            
            # 步驟2: 使用 Cross-Encoder 對 child chunks 進行重排序
            pairs = [(query, d.page_content) for d in child_docs]
            scores = self.reranker.predict(pairs)
            ranked = sorted(zip(child_docs, scores), key=lambda x: x[1], reverse=True)
            top_child_docs = [d for d, _ in ranked[:top_k]]
            
            logger.info(f"Reranked to top {len(top_child_docs)} child documents")
            
            # 步驟3: 根據 rerank 後的 child chunks 獲取對應的父文檔
            parent_docs = []
            for child_doc in top_child_docs:
                parent_id = child_doc.metadata.get("parent_id")
                if parent_id:
                    parent_doc = self.store.mget([parent_id])
                    if parent_doc and parent_doc[0]:
                        parent_docs.append(parent_doc[0])
            
            logger.info(f"Retrieved {len(parent_docs)} parent documents")
            return parent_docs, top_child_docs
            
        except Exception as e:
            logger.error(f"檢索失敗: {e}")
            return [], []
    
    def get_retrieval_stats(self) -> dict:
        """獲取檢索統計信息"""
        if not self.retriever:
            return {"status": "retriever_not_initialized"}
        
        try:
            # 獲取向量庫統計
            vectorstore_size = len(self.vectorstore.index_to_docstore_id)
            store_size = len(self.store.yield_keys())
            
            return {
                "vectorstore_documents": vectorstore_size,
                "docstore_documents": store_size,
                "status": "ready"
            }
        except Exception as e:
            return {"status": f"error: {e}"}


def example_basic_integration():
    """範例：基本整合使用"""
    logger.info("=== 基本整合範例 ===")
    
    try:
        # 創建分層檢索器（使用預設值）
        retriever = HierarchicalRetriever()
        
        # 測試文件
        test_file = project_root / "raw_docs" / "理賠審核原則.xlsx"
        
        if not test_file.exists():
            logger.warning(f"測試文件不存在: {test_file}")
            return False
        
        # 添加文檔
        result = retriever.add_documents_from_file(str(test_file))
        
        if result:
            logger.info(f"✓ 文檔處理完成:")
            logger.info(f"- 父chunks: {len(result.parent_chunks)}")
            logger.info(f"- 子chunks: {len(result.child_chunks)}")
            
            # 獲取檢索統計
            stats = retriever.get_retrieval_stats()
            logger.info(f"檢索器統計: {stats}")
            
            # 模擬檢索（如果檢索器可用）
            if retriever.retriever:
                query = "理賠審核"
                parent_docs, child_docs = retriever.retrieve_with_rerank(query, top_k=3)
                
                if parent_docs:
                    logger.info(f"✓ 檢索成功:")
                    logger.info(f"- 父文檔數量: {len(parent_docs)}")
                    logger.info(f"- 子文檔數量: {len(child_docs)}")
                    
                    # 顯示第一個父文檔的預覽
                    if parent_docs:
                        preview = parent_docs[0].page_content[:200]
                        logger.info(f"第一個父文檔預覽: {preview}...")
                else:
                    logger.info("⚠ 檢索結果為空")
            else:
                logger.info("⚠ 檢索器不可用，跳過檢索測試")
            
            return True
        else:
            logger.error("✗ 文檔處理失敗")
            return False
            
    except Exception as e:
        logger.error(f"基本整合範例失敗: {e}")
        return False


def example_advanced_usage():
    """範例：進階使用"""
    logger.info("=== 進階使用範例 ===")
    
    try:
        # 創建多個檢索器實例（比較不同配置）
        retrievers = {
            "default": HierarchicalRetriever(),  # 使用預設值
            "small": HierarchicalRetriever(
                parent_chunk_size=1500,
                child_chunk_size=250,
                child_chunk_overlap=30
            ),
            "large": HierarchicalRetriever(
                parent_chunk_size=3000,
                child_chunk_size=500,
                child_chunk_overlap=100
            )
        }
        
        # 測試文件
        test_file = project_root / "raw_docs" / "理賠審核原則.xlsx"
        
        if not test_file.exists():
            logger.warning(f"測試文件不存在: {test_file}")
            return False
        
        results = {}
        
        # 測試不同配置
        for name, retriever in retrievers.items():
            logger.info(f"測試 {name} 配置...")
            
            result = retriever.add_documents_from_file(str(test_file))
            
            if result:
                results[name] = {
                    "parent_chunks": len(result.parent_chunks),
                    "child_chunks": len(result.child_chunks),
                    "avg_children_per_parent": result.grouping_analysis.avg_children_per_parent,
                    "grouping_efficiency": result.grouping_analysis.grouping_efficiency
                }
                
                logger.info(f"✓ {name} 配置完成:")
                logger.info(f"  - 父chunks: {results[name]['parent_chunks']}")
                logger.info(f"  - 子chunks: {results[name]['child_chunks']}")
                logger.info(f"  - 平均每父chunk的子chunks: {results[name]['avg_children_per_parent']:.2f}")
                logger.info(f"  - 分組效率: {results[name]['grouping_efficiency']:.2%}")
            else:
                logger.error(f"✗ {name} 配置失敗")
        
        # 比較結果
        if results:
            logger.info("=== 配置比較 ===")
            for name, stats in results.items():
                logger.info(f"{name}: 效率={stats['grouping_efficiency']:.2%}, "
                          f"父chunks={stats['parent_chunks']}, 子chunks={stats['child_chunks']}")
        
        return len(results) > 0
        
    except Exception as e:
        logger.error(f"進階使用範例失敗: {e}")
        return False


def main():
    """主程式"""
    logger.info("開始 Retriever 整合範例...")
    
    # 範例1: 基本整合
    logger.info("\n" + "="*50)
    result1 = example_basic_integration()
    
    # 範例2: 進階使用
    logger.info("\n" + "="*50)
    result2 = example_advanced_usage()
    
    # 顯示結果摘要
    logger.info("\n" + "="*50)
    logger.info("範例執行結果:")
    logger.info(f"- 基本整合: {'✓ 成功' if result1 else '✗ 失敗'}")
    logger.info(f"- 進階使用: {'✓ 成功' if result2 else '✗ 失敗'}")
    
    if result1 or result2:
        logger.info("🎉 至少一個範例執行成功！")
    else:
        logger.warning("⚠ 所有範例都失敗了，請檢查配置。")


if __name__ == "__main__":
    main()
