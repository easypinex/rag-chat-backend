# 分層分割系統 (Hierarchical Chunking System)

## 概述

本系統實現了基於 LangChain ParentDocumentRetriever 模式的分層分割功能，專門解決表格內容切割過大的問題。系統使用物件清楚表達中間傳遞的資料，提供精準的 250-400 字 chunk 控制。

## 核心特性

### 1. 分層分割架構

- **Parent Splitter**: 使用 MarkdownHeaderTextSplitter 保持語義完整性
- **Child Splitter**: 使用 RecursiveCharacterTextSplitter 精準控制長度
- **目標長度**: 250-400 字的子 chunks
- **表格友好**: 特別優化大型表格的處理

### 2. 資料模型

- `ParentChunk`: 父層 chunk 資料模型
- `ChildChunk`: 子層 chunk 資料模型
- `GroupingAnalysis`: 分組分析資料模型
- `HierarchicalSplitResult`: 分層分割結果資料模型

### 3. 分析功能

- 詳細的分組統計
- 大小分佈分析
- 表格處理效率分析
- 分組效率計算

## 快速開始

### 基本使用

```python
from service.chunk.hierarchical_splitter import HierarchicalChunkSplitter

# 創建分層分割器（中文優化）
splitter = HierarchicalChunkSplitter(
    parent_chunk_size=2000,      # 父chunk大小（預設值，適合中文32k embedding）
    parent_chunk_overlap=200,    # 父chunk重疊（預設值，保持中文語義連貫性）
    child_chunk_size=350,        # 子chunk大小（預設值，約100-150 tokens，適合中文rerank 512）
    child_chunk_overlap=50,      # 子chunk重疊（預設值，保持中文語義連貫性）
    keep_tables_together=True,   # 保持表格完整性（預設值）
    normalize_output=True        # 正規化輸出（預設值）
)

# 進行分層分割
result = splitter.split_hierarchically(
    input_data="path/to/your/file.pdf",
    output_excel=True,
    output_path="output/hierarchical_chunks.xlsx"
)

# 查看結果
print(f"父chunks: {len(result.parent_chunks)}")
print(f"子chunks: {len(result.child_chunks)}")
print(f"分組效率: {result.grouping_analysis.grouping_efficiency:.2%}")
```

### 使用分析器

```python
from service.chunk.analysis.analysis import DocumentAnalyzer

# 創建分層分析器（中文優化）
analyzer = DocumentAnalyzer(
    use_hierarchical=True,
    chunk_size=2000,        # 父chunk大小（預設值，適合中文32k embedding）
    chunk_overlap=200,      # 父chunk重疊（預設值，保持中文語義連貫性）
    child_chunk_size=350,   # 子chunk大小（預設值，約100-150 tokens，適合中文rerank 512）
    child_chunk_overlap=50   # 子chunk重疊（預設值，保持中文語義連貫性）
)

# 分析單個文件
result = analyzer.analyze_single_file("your_file.pdf")

# 查看分層信息
if result['hierarchical_info']:
    hierarchical_info = result['hierarchical_info']
    print(f"父chunks: {hierarchical_info['parent_chunks_count']}")
    print(f"子chunks: {hierarchical_info['child_chunks_count']}")
    print(f"分組效率: {hierarchical_info['grouping_analysis']['grouping_efficiency']:.2%}")
```

## 命令行使用

### 分層分割模式（使用預設值）

```bash
python service/chunk/analysis/analysis.py --use-hierarchical
```

### 傳統分割模式

```bash
python service/chunk/analysis/analysis.py --use-hierarchical=False
```

### 分析特定文件（使用預設值）

```bash
python service/chunk/analysis/analysis.py --file "your_file.pdf" --use-hierarchical
```

### 自定義參數（如需要）

```bash
python service/chunk/analysis/analysis.py --use-hierarchical --chunk-size 2000 --chunk-overlap 200 --child-chunk-size 350 --child-chunk-overlap 50
```

## 輸出格式

### Excel 輸出

分層分割會產生包含以下工作表的 Excel 文件：

- **分層Chunks**: 垂直合併的父子chunks，包含層級、Chunk ID、父Chunk ID等欄位
- **分組分析**: 分組統計和分析結果
- **分層摘要**: 整體統計摘要

#### 分層Chunks工作表格式

| 層級 | Chunk ID   | 父Chunk ID | 索引 | 大小 | 是否表格 | 標題層級 | 標題文字  | 頁碼 | 內容           |
| ---- | ---------- | ---------- | ---- | ---- | -------- | -------- | --------- | ---- | -------------- |
| 父層 | parent_001 |            | 0    | 500  | True     | Header 1 | 測試標題  | 1    | 父chunk內容... |
| 子層 | child_001  | parent_001 | 0    | 300  | True     |          | 測試標題  | 1    | 子chunk內容... |
| 子層 | child_002  | parent_001 | 1    | 200  | False    |          | 測試標題  | 1    | 子chunk內容... |
| 父層 | parent_002 |            | 1    | 800  | False    | Header 2 | 測試標題2 | 2    | 父chunk內容... |
| 子層 | child_003  | parent_002 | 0    | 400  | False    |          | 測試標題2 | 2    | 子chunk內容... |

### 分析報告

分析結果包含：

- 基本統計（chunks 數量、大小分佈）
- 分組分析（父子關係、分組效率）
- 表格處理統計（表格 chunks 比例、碎片化情況）
- 大小分佈（各長度範圍的 chunks 數量）

## 測試和範例

### 運行測試

```bash
python service/chunk/test_hierarchical.py
```

### 查看範例

```bash
python service/chunk/examples/hierarchical_example.py
```

## 架構優勢

### 1. 解決表格切割問題

- 父層保持表格完整性
- 子層精準控制長度
- 智能表格合併和分割

### 2. 提升 LLM 回應品質

- 避免過短的 chunks
- 保持語義上下文完整性
- 優化檢索效果

### 3. 詳細分析能力

- 分組效率分析
- 大小分佈統計
- 表格處理優化建議

## 配置參數

### 分層分割器參數（預設值）

- `parent_chunk_size`: 父層 chunk 大小（預設: 2000字，適合中文32k embedding）
- `parent_chunk_overlap`: 父層 chunk 重疊（預設: 200字，保持中文語義連貫性）
- `child_chunk_size`: 子層 chunk 大小（預設: 350字，約100-150 tokens，適合中文rerank 512）
- `child_chunk_overlap`: 子層 chunk 重疊（預設: 50字，保持中文語義連貫性）
- `keep_tables_together`: 保持表格完整性（預設: True）
- `normalize_output`: 正規化輸出（預設: True）

### 分析器參數（預設值）

- `use_hierarchical`: 是否使用分層分割（預設: True）
- `chunk_size`: 父層 chunk 大小（預設: 2000字）
- `chunk_overlap`: 父層 chunk 重疊（預設: 200字）
- `child_chunk_size`: 子層 chunk 大小（預設: 350字）
- `child_chunk_overlap`: 子層 chunk 重疊（預設: 50字）

## 最佳實踐

### 1. 中文長度設定建議（預設值）

- 父層: 2000 字（預設值，適合中文32k embedding，保持語義完整性）
- 子層: 350 字（預設值，約100-150 tokens，適合中文rerank 512）
- 父層重疊: 200 字（預設值，保持中文語義連貫性）
- 子層重疊: 50 字（預設值，保持中文語義連貫性）

### 2. 表格處理

- 啟用 `keep_tables_together=True`
- 監控表格碎片化情況
- 根據表格大小調整分割策略

### 3. 分析優化

- 定期檢查分組效率
- 監控大小分佈
- 根據結果調整參數

## 故障排除

### 常見問題

1. **導入錯誤**: 確保路徑設定正確
2. **記憶體不足**: 調整 chunk 大小參數
3. **表格切割問題**: 檢查 `keep_tables_together` 設定

### 除錯建議

- 使用測試腳本驗證功能
- 檢查日誌輸出
- 逐步調整參數

## 與 LangChain ParentDocumentRetriever 整合

### 實際使用範例

本系統設計與 LangChain ParentDocumentRetriever 完全兼容。**重要**：ParentDocumentRetriever 的正確工作流程是：
1. 使用 **child chunks** 進行向量檢索
2. 對檢索到的 child chunks 進行 **rerank**
3. 根據 rerank 後的 child chunks 找出對應的 **parent chunks**
4. 將 parent chunks 傳遞給 LLM

以下是實際的整合使用方式：

```python
# 安裝必要套件
# pip install langchain langchain-community sentence-transformers transformers

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from sentence_transformers import CrossEncoder

# 導入我們的分層分割器
from service.chunk.hierarchical_splitter import HierarchicalChunkSplitter

# 1) 建立 child splitter（給檢索＋rerank），parent splitter（保留上下文）
child_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)  # 約 300–400 tokens 的量級
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)

# 2) 向量與向量庫
emb = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-en-v1.5")  # 例：你可改中文/多語版本
vectorstore = FAISS.from_texts(["dummy"], embedding=emb)            # 先放個空的，實務請批量寫入
store = InMemoryStore()

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore.as_retriever(search_kwargs={"k": 50}),
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)

# 3) Cross-Encoder Reranker（bge-rerank-large）
reranker = CrossEncoder("BAAI/bge-reranker-large", max_length=512)

def rerank(query, docs, top_k=8):
    pairs = [(query, d.page_content) for d in docs]
    scores = reranker.predict(pairs)  # 越大越相關
    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    return [d for d, _ in ranked[:top_k]]

# 使用時：
# child 層先取 top 50 → 再用 rerank 總結為 top 8 → 把對應 parent 取回給 LLM。
```

### 與 HierarchicalChunkSplitter 整合

```python
# 使用我們的分層分割器準備資料
hierarchical_splitter = HierarchicalChunkSplitter(
    parent_chunk_size=2000,      # 預設值，對應 parent_splitter 的 chunk_size
    parent_chunk_overlap=200,    # 預設值，對應 parent_splitter 的 chunk_overlap
    child_chunk_size=350,        # 預設值，對應 child_splitter 的 chunk_size
    child_chunk_overlap=50,      # 預設值，對應 child_splitter 的 chunk_overlap
    keep_tables_together=True,   # 預設值
    normalize_output=True        # 預設值
)

# 分割文檔
result = hierarchical_splitter.split_hierarchically("your_document.pdf")

# 準備 ParentDocumentRetriever 的資料
documents = []
for parent_chunk in result.parent_chunks:
    # 將父chunk轉換為 LangChain Document
    from langchain_core.documents import Document
    parent_doc = Document(
        page_content=parent_chunk.document.page_content,
        metadata=parent_chunk.document.metadata
    )
    documents.append(parent_doc)

# 準備 ParentDocumentRetriever 的資料
# 注意：ParentDocumentRetriever 需要同時添加 parent 和 child 文檔
parent_documents = []
child_documents = []

for parent_chunk in result.parent_chunks:
    # 父文檔
    parent_doc = Document(
        page_content=parent_chunk.document.page_content,
        metadata={
            **parent_chunk.document.metadata,
            "chunk_id": parent_chunk.chunk_id,
            "chunk_type": "parent"
        }
    )
    parent_documents.append(parent_doc)

for child_chunk in result.child_chunks:
    # 子文檔
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

# 使用 ParentDocumentRetriever 添加文檔
retriever.add_documents(parent_documents)

# 檢索使用：ParentDocumentRetriever 的正確流程
query = "你的查詢問題"

# 步驟1: 使用 child chunks 進行向量檢索（更精確的匹配）
child_docs = retriever.vectorstore.similarity_search(query, k=50)

# 步驟2: 對 child chunks 進行 rerank（提高相關性）
reranked_child_docs = rerank(query, child_docs, top_k=8)

# 步驟3: 根據 rerank 後的 child chunks 找出對應的 parent chunks
parent_docs = []
for child_doc in reranked_child_docs:
    parent_id = child_doc.metadata.get("parent_id")
    if parent_id:
        parent_doc = retriever.docstore.mget([parent_id])
        if parent_doc and parent_doc[0]:
            parent_docs.append(parent_doc[0])

# 步驟4: 將 parent chunks 傳遞給 LLM（保持完整上下文）
final_context = "\n\n".join([doc.page_content for doc in parent_docs])
```

### 進階整合模式

```python
class HierarchicalRetriever:
    """整合 HierarchicalChunkSplitter 與 ParentDocumentRetriever 的包裝類"""
  
    def __init__(self, 
                 parent_chunk_size: int = 2000,      # 預設值
                 child_chunk_size: int = 350,        # 預設值
                 child_chunk_overlap: int = 50,      # 預設值
                 embedding_model: str = "BAAI/bge-small-en-v1.5",
                 rerank_model: str = "BAAI/bge-reranker-large"):
      
        # 初始化分層分割器
        self.hierarchical_splitter = HierarchicalChunkSplitter(
            parent_chunk_size=parent_chunk_size,
            child_chunk_size=child_chunk_size,
            child_chunk_overlap=child_chunk_overlap,
            keep_tables_together=True,
            normalize_output=True
        )
      
        # 初始化檢索器組件
        self.embeddings = HuggingFaceBgeEmbeddings(model_name=embedding_model)
        self.vectorstore = FAISS.from_texts(["dummy"], embedding=self.embeddings)
        self.store = InMemoryStore()
      
        # 初始化 ParentDocumentRetriever
        self.retriever = ParentDocumentRetriever(
            vectorstore=self.vectorstore.as_retriever(search_kwargs={"k": 50}),
            docstore=self.store,
            child_splitter=RecursiveCharacterTextSplitter(
                chunk_size=child_chunk_size, 
                chunk_overlap=child_chunk_overlap
            ),
            parent_splitter=RecursiveCharacterTextSplitter(
                chunk_size=parent_chunk_size, 
                chunk_overlap=200  # 使用預設值
            )
        )
      
        # 初始化重排序器
        self.reranker = CrossEncoder(rerank_model, max_length=512)
  
    def add_documents_from_file(self, file_path: str):
        """從文件添加文檔到檢索器"""
        # 使用分層分割器處理文件
        result = self.hierarchical_splitter.split_hierarchically(file_path)
      
        # 準備父文檔和子文檔
        parent_documents = []
        child_documents = []
        
        # 添加父文檔
        for parent_chunk in result.parent_chunks:
            parent_doc = Document(
                page_content=parent_chunk.document.page_content,
                metadata={
                    **parent_chunk.document.metadata,
                    "chunk_id": parent_chunk.chunk_id,
                    "chunk_type": "parent"
                }
            )
            parent_documents.append(parent_doc)
        
        # 添加子文檔
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
      
        return result
  
    def retrieve_with_rerank(self, query: str, top_k: int = 8):
        """檢索並重排序 - 使用 child chunks 進行檢索和 rerank"""
        # 1. 使用 child chunks 進行向量檢索
        child_docs = self.retriever.vectorstore.similarity_search(query, k=50)
      
        # 2. 使用 Cross-Encoder 對 child chunks 進行重排序
        pairs = [(query, d.page_content) for d in child_docs]
        scores = self.reranker.predict(pairs)
        ranked = sorted(zip(child_docs, scores), key=lambda x: x[1], reverse=True)
        top_child_docs = [d for d, _ in ranked[:top_k]]
      
        # 3. 根據 rerank 後的 child chunks 獲取對應的父文檔
        parent_docs = []
        for child_doc in top_child_docs:
            parent_id = child_doc.metadata.get("parent_id")
            if parent_id:
                parent_doc = self.store.mget([parent_id])
                if parent_doc and parent_doc[0]:
                    parent_docs.append(parent_doc[0])
      
        return parent_docs, top_child_docs

# 使用範例（使用預設值）
retriever = HierarchicalRetriever()

# 添加文檔
result = retriever.add_documents_from_file("your_document.pdf")

# 檢索
query = "你的查詢問題"
parent_docs, child_docs = retriever.retrieve_with_rerank(query, top_k=8)

# 使用父文檔作為上下文
context = "\n\n".join([doc.page_content for doc in parent_docs])
```

### 最佳實踐建議

1. **中文優化參數調優（預設值）**

   - `parent_chunk_size`: 2000 字（預設值，適合中文32k embedding，保持完整上下文）
   - `child_chunk_size`: 350 字（預設值，約100-150 tokens，適合中文rerank 512）
   - `child_chunk_overlap`: 50 字（預設值，保持中文語義連貫性）
   - `parent_chunk_overlap`: 200 字（預設值，父層重疊，保持中文語義連貫性）
2. **表格處理**

   - 啟用 `keep_tables_together=True`
   - 監控表格碎片化情況
   - 根據表格大小調整分割策略
3. **檢索優化**

   - 使用適當的 embedding 模型
   - 調整檢索數量（k=50）和重排序數量（top_k=8）
   - 根據查詢類型調整重排序模型
4. **效能監控**

   - 監控檢索時間
   - 追蹤重排序準確度
   - 分析父子文檔匹配率

## 更新日誌

### v1.0.0

- 實現基本分層分割功能
- 支援表格完整性保持
- 提供詳細分析報告
- 整合到現有分析系統
- 添加與 ParentDocumentRetriever 的完整整合範例
