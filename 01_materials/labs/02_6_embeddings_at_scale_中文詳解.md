# 大規模嵌入向量處理 - 完整中文教學

## 📚 目錄
1. [什麼是嵌入向量 (Embeddings)？](#什麼是嵌入向量)
2. [為什麼需要大規模處理？](#為什麼需要大規模處理)
3. [RAG 是什麼？](#rag-是什麼)
4. [文件處理工具：LangChain](#文件處理工具langchain)
5. [實作步驟詳解](#實作步驟詳解)

---

## 什麼是嵌入向量？

### 🔰 基礎概念
**嵌入向量 (Embeddings)** 就像是把文字轉換成數字的「指紋」。

**舉個例子：**
- 原始文字：「我喜歡吃蘋果」
- 轉換後：[0.23, -0.15, 0.89, 0.12, ...] （一串數字）

### 為什麼要這樣做？
因為電腦不懂中文或英文，但它很會處理數字！把文字轉成數字後，電腦就能：
- 🔍 **搜尋**：找出相似的內容
- 📊 **分類**：把文章自動分門別類
- 🎯 **推薦**：推薦你可能喜歡的內容
- 🚨 **異常偵測**：發現不尋常的內容
- 📈 **相似度計算**：計算兩段文字有多像

---

## 為什麼需要大規模處理？

想像一下，你有一整個圖書館的書要處理：
- ❌ 一本一本慢慢處理 → 可能要等好幾天
- ✅ 批次處理（一次處理很多本）→ 省時又省錢

**實際應用場景：**
- 處理整個公司的文件庫
- 分析成千上萬的客戶評論
- 建立大型的知識庫搜尋系統

---

## RAG 是什麼？

### 📖 完整名稱
**RAG = Retrieval-Augmented Generation**（檢索增強生成）

### 🎯 白話文解釋
就像是給 AI 一個「參考書」系統：

**傳統 AI：**
```
你問問題 → AI 憑記憶回答（可能記錯或不知道）
```

**使用 RAG：**
```
你問問題 → AI 先查資料 → 根據找到的資料回答（更準確！）
```

### 🔄 RAG 工作流程圖解

**第一步：準備資料**
```
完整文件
    ↓
切成小塊（chunks）
    ↓
轉成嵌入向量
    ↓
存入向量資料庫
```

**第二步：回答問題**
```
用戶提問
    ↓
問題也轉成嵌入向量
    ↓
在資料庫中找相似的內容
    ↓
把找到的內容給 AI 參考
    ↓
AI 生成更準確的答案
```

---

## 文件處理工具：LangChain

### 🛠️ LangChain 是什麼？
想像它是一個「AI 工具箱」，裡面有各種處理文件和建立 AI 應用的工具。

### 為什麼要切割文件？

**真實世界的問題：**
1. **AI 有記憶限制**：就像你一次只能記住有限的內容
2. **提升搜尋品質**：小塊內容更精準
3. **節省時間**：處理小塊比處理整本書快
4. **省錢**：AI API 按使用量收費

**比喻：**
- ❌ 把整本百科全書丟給 AI → 它會消化不良
- ✅ 把書切成章節，只給需要的部分 → 快速又精準

---

## 實作步驟詳解

### 步驟 1️⃣：載入文件

#### 🗂️ LangChain 支援的文件格式

**常見格式：**
- 📄 CSV：試算表資料
- 📁 整個資料夾：一次處理所有檔案
- 📝 JSON：結構化資料
- 🌐 網頁：直接從網站抓取內容

**PDF 處理：**
- PyPDF：基本的 PDF 讀取
- Unstructured：進階 PDF 處理
- PDFPlumber：處理複雜排版的 PDF

#### 💡 程式碼範例解說

```python
from langchain_community.document_loaders import JSONLoader

# 設定檔案載入器
loader = JSONLoader(
    "../../05_src/documents/pitchfork_content.jsonl",  # 檔案路徑
    jq_schema=".",          # 讀取所有資料
    content_key="content",  # 主要內容在 "content" 欄位
    json_lines=True,        # 這是 JSONL 格式（每行一個 JSON）
    metadata_func=get_metadata  # 提取額外資訊的函數
)

# 載入所有資料
data = loader.load()
```

**🔍 這段程式做了什麼？**
1. 打開一個 JSONL 檔案（每行都是獨立的 JSON）
2. 讀取每行的 "content" 欄位作為文章內容
3. 用 `get_metadata` 函數提取評論 ID 等額外資訊

---

### 步驟 2️⃣：切割文件

#### ✂️ 為什麼要切割？

**想像這個情境：**
- 你有一篇 10,000 字的文章
- AI 一次只能處理 2,000 字
- 怎麼辦？→ 切成 5 段！

#### 📏 切割策略

**LangChain 提供三種切法：**

1. **按長度切割（最簡單）**
   - 每 1000 個字切一塊
   - 像切蛋糕一樣，每塊一樣大

2. **按文章結構切割（聰明）**
   - 優先保持段落完整
   - 段落太長才切成句子
   - 句子太長才切成詞
   - 像是保持章節結構

3. **按文件格式切割（專業）**
   - Markdown：按標題切
   - HTML：按標籤切
   - JSON：按結構切

#### 💻 實際程式碼

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 建立切割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,        # 每塊最多 2000 字
    chunk_overlap=200,      # 塊與塊之間重疊 200 字
    length_function=len,    # 用字數計算長度
    add_start_index=True    # 記錄每塊的起始位置
)

# 開始切割
chunks = text_splitter.split_documents(data)
```

**🤔 為什麼要「重疊」(overlap)？**
- 避免把一句話切成兩半
- 保持上下文的連貫性
- 就像拍照時要多拍一點邊緣，才能拼接完整

**範例：**
```
第一塊：「...蘋果是一種水果。它含有豐富的維生素...」
第二塊：「...它含有豐富的維生素。蘋果的產地...」
         ↑↑↑ 這部分重疊了！
```

---

### 步驟 3️⃣：批次處理嵌入向量

#### 🚀 什麼是批次 API (Batch API)？

**傳統方式 vs 批次處理：**

**傳統方式：**
```
處理文件 1 → 等待 → 得到結果
處理文件 2 → 等待 → 得到結果
處理文件 3 → 等待 → 得到結果
...（很慢）
```

**批次處理：**
```
一次提交 1000 個文件 → 等 24 小時內 → 一次拿到所有結果
（便宜 50%！）
```

#### 💰 批次處理的優勢

| 項目 | 傳統 API | 批次 API |
|------|----------|----------|
| **價格** | 正常價 | 便宜 50% 💰 |
| **速度** | 立即 (秒級) | 24 小時內 |
| **數量限制** | 受限 | 更高的限制 |
| **適合場景** | 需要立即回應 | 大量資料處理 |

**🎯 什麼時候該用批次 API？**
- ✅ 處理成千上萬的文件
- ✅ 建立整個資料庫的索引
- ✅ 不急著馬上要結果
- ❌ 即時聊天機器人（太慢）
- ❌ 只有幾個文件要處理

---

### 步驟 4️⃣：準備批次檔案

#### 📝 批次檔案格式

批次 API 需要特定格式的 JSONL 檔案（每行一個 JSON）：

```json
{"custom_id": "doc_1", "method": "POST", "url": "/v1/embeddings", "body": {"model": "text-embedding-3-small", "input": "文章內容..."}}
{"custom_id": "doc_2", "method": "POST", "url": "/v1/embeddings", "body": {"model": "text-embedding-3-small", "input": "另一篇文章..."}}
```

**欄位說明：**
- `custom_id`：你自己的編號（方便之後對應）
- `method`：固定是 "POST"
- `url`：API 端點（這裡是嵌入向量 API）
- `body`：就像平常呼叫 API 一樣的參數

#### 🔢 限制說明

**單一批次檔案限制：**
- 📦 最多 50,000 個請求
- 💾 檔案大小最多 200 MB
- 🎯 對於嵌入向量：最多 50,000 個輸入文本

**為什麼要分割成多個檔案？**
```
假設你有 100,000 個文件要處理
→ 需要分成 2 個批次檔案（每個 50,000）
```

#### 💻 自動產生批次檔案的程式

```python
def prep_batch_file_for_embedding(input, output_path, max_lines_per_file=10000):
    """
    這個函數做什麼？
    1. 計算需要幾個檔案
    2. 把資料分配到每個檔案
    3. 產生符合格式的 JSONL 檔案
    """
    total_lines = len(input)
    num_files = (total_lines // max_lines_per_file) + 1
    
    for num_file in range(num_files):
        # 計算這個檔案要包含哪些資料
        start_index = num_file * max_lines_per_file
        end_index = min(start_index + max_lines_per_file, total_lines)
        
        # 產生檔案
        output_file = f"batch_{num_file+1}.jsonl"
        create_single_batch_file(input, start_index, end_index, output_file)
```

---

### 步驟 5️⃣：上傳並執行批次

#### 📤 批次處理完整流程

```
1. 準備批次檔案 (JSONL 格式)
   ↓
2. 上傳到 OpenAI
   ↓
3. 建立批次任務
   ↓
4. 等待處理完成（定期檢查狀態）
   ↓
5. 下載結果
```

#### 🖥️ 上傳檔案

```python
from openai import OpenAI
client = OpenAI()

# 上傳批次檔案
batch_input_file = client.files.create(
    file=open("batch_1.jsonl", "rb"),
    purpose='batch'  # 用途是批次處理
)

print(f"檔案已上傳，ID: {batch_input_file.id}")
```

#### 🚀 建立批次任務

```python
from datetime import datetime

# 建立批次任務
batch_job = client.batches.create(
    input_file_id=batch_input_file.id,  # 剛上傳的檔案 ID
    endpoint="/v1/embeddings",          # 要呼叫的 API
    completion_window="24h",            # 24 小時內完成
    metadata={
        "description": "音樂評論嵌入向量",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
)

print(f"批次任務已建立，ID: {batch_job.id}")
```

#### 📊 檢查批次狀態

```python
# 查看批次狀態
batch_status = client.batches.retrieve(batch_job.id)

print(f"狀態: {batch_status.status}")
print(f"已完成: {batch_status.request_counts.completed}")
print(f"總共: {batch_status.request_counts.total}")
```

**可能的狀態：**
- `validating`：檢查中
- `in_progress`：處理中 ⏳
- `completed`：完成 ✅
- `failed`：失敗 ❌
- `cancelled`：已取消

---

## 🎓 完整範例：處理音樂評論

### 情境說明
假設我們有 Pitchfork 音樂網站的 10,000 篇評論，想要：
1. 切成適當大小的區塊
2. 轉換成嵌入向量
3. 存入資料庫供搜尋使用

### 🔄 完整工作流程

```python
# ========== 第一步：載入評論 ==========
from langchain_community.document_loaders import JSONLoader

loader = JSONLoader(
    "pitchfork_reviews.jsonl",
    jq_schema=".",
    content_key="content",
    json_lines=True
)
data = loader.load()  # 載入 10,000 篇評論

# ========== 第二步：切割成小塊 ==========
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,      # 每塊 2000 字
    chunk_overlap=200     # 重疊 200 字
)
chunks = splitter.split_documents(data)
# 假設切成了 25,000 個小塊

# ========== 第三步：準備批次檔案 ==========
# 25,000 個塊 → 分成 3 個批次檔案（每個 10,000）
prep_batch_file_for_embedding(
    input=chunks,
    output_path='./batch_files/',
    max_lines_per_file=10000
)
# 產生：batch_1.jsonl, batch_2.jsonl, batch_3.jsonl

# ========== 第四步：上傳並執行 ==========
from glob import glob

batch_files = glob('./batch_files/*.jsonl')
batch_jobs = []

for file_path in batch_files:
    # 上傳檔案
    uploaded = client.files.create(
        file=open(file_path, "rb"),
        purpose='batch'
    )
    
    # 建立批次
    job = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/embeddings",
        completion_window="24h"
    )
    batch_jobs.append(job.id)
    print(f"批次 {job.id} 已建立")

# ========== 第五步：等待並檢查 ==========
import time

while True:
    all_done = True
    for job_id in batch_jobs:
        status = client.batches.retrieve(job_id)
        if status.status != 'completed':
            all_done = False
            print(f"批次 {job_id}: {status.status}")
    
    if all_done:
        print("全部完成！")
        break
    
    time.sleep(60)  # 每分鐘檢查一次
```

---

## 🎯 重點總結

### 核心概念
1. **嵌入向量** = 把文字變成數字，讓電腦能計算相似度
2. **RAG** = 給 AI 一個參考書系統，回答更準確
3. **LangChain** = 處理文件的工具箱
4. **批次 API** = 大量處理資料的省錢方式

### 實作流程
```
載入文件 → 切割 → 準備批次檔 → 上傳 → 執行 → 取得結果
```

### 💡 最佳實踐

**切割文件時：**
- ✅ 設定適當的重疊（chunk_overlap）
- ✅ 根據 AI 模型限制決定大小
- ✅ 保持語意完整性

**批次處理時：**
- ✅ 不急的任務用批次 API（省 50% 成本）
- ✅ 遵守每批次 50,000 個請求的限制
- ✅ 用有意義的 custom_id 方便追蹤

**實際應用：**
- 📚 知識庫搜尋
- 🎯 智能客服
- 📊 文件分類
- 🔍 語意搜尋引擎

---

## ❓ 常見問題

### Q1: 為什麼要重疊 (chunk_overlap)？
**A:** 避免重要資訊被切斷。例如：
```
沒有重疊：
  塊1: "...蘋果是"
  塊2: "一種水果..."  ← 意思不完整！

有重疊：
  塊1: "...蘋果是一種水果..."
  塊2: "...蘋果是一種水果..."  ← 保持完整！
```

### Q2: 批次 API 真的便宜一半嗎？
**A:** 是的！但要等最多 24 小時。適合大量離線處理。

### Q3: 一次最多能處理多少文件？
**A:** 單一批次最多 50,000 個請求，但你可以建立多個批次。

### Q4: 如何選擇 chunk_size？
**A:** 根據使用的模型決定：
- GPT-3.5: 建議 1000-2000 字元
- GPT-4: 可以更長
- 嵌入向量: 通常 512-2048 字元

### Q5: 處理中文需要注意什麼？
**A:** 
- 使用支援中文的分詞器
- chunk_size 計算要注意中文字元
- 選擇支援多語言的嵌入模型

---

## 🚀 下一步學習

1. **向量資料庫**：學習如何儲存和搜尋嵌入向量
   - Pinecone
   - Weaviate
   - Chroma

2. **進階 RAG**：
   - 混合搜尋（關鍵字 + 語意）
   - 重新排序 (Reranking)
   - 多步驟檢索

3. **優化技巧**：
   - 如何選擇最佳的切割策略
   - 提升搜尋準確度
   - 降低成本

---

## 📚 延伸閱讀

- [OpenAI Embeddings 官方文件](https://platform.openai.com/docs/guides/embeddings)
- [LangChain 中文文件](https://python.langchain.com/)
- [Batch API 完整指南](https://platform.openai.com/docs/guides/batch)
- [RAG 最佳實踐](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

**🎉 恭喜！你已經掌握了大規模嵌入向量處理的核心概念！**

有任何問題歡迎提問～
