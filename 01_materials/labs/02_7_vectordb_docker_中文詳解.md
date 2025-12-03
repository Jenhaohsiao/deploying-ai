# 向量資料庫 (Vector DB) - Docker 版本詳細教學

## 📚 這個檔案在教什麼?

這個教學會教您如何使用 **向量資料庫 (Vector Database)** 來儲存和搜尋文字資料。想像一下,您有成千上萬篇音樂評論,想要快速找到「具有出色人聲和製作的專輯」,向量資料庫就能幫您做到這件事!

---

## 🎯 學習目標

1. 了解什麼是向量資料庫及其用途
2. 學習如何使用 Docker 運行 Chroma DB
3. 將文字轉換成向量 (embeddings) 並儲存
4. 使用語義搜尋找到相關內容
5. 結合向量搜尋和結構化資料查詢

---

## 📖 基礎知識補充

### 什麼是向量 (Vector/Embedding)?

**簡單比喻**: 想像每個句子都是一個點在多維空間中的位置。意思相近的句子會靠得很近,意思不同的句子會離得很遠。

```
例如:
"我喜歡這張專輯" → [0.2, 0.8, 0.3, ...]
"這張唱片很棒" → [0.3, 0.7, 0.4, ...]  (很接近!)
"今天天氣很好" → [0.9, 0.1, 0.2, ...]  (很遠!)
```

### 什麼是 Chroma DB?

Chroma DB 是一個專門儲存向量的資料庫,讓您可以:
- 儲存大量文字及其向量表示
- 快速找到語義相似的內容
- 輕鬆整合到 AI 應用中

### 什麼是 Docker?

Docker 就像一個「軟體集裝箱」,把應用程式和所有需要的東西打包在一起,讓您不用擔心安裝問題。

---

## 🚀 步驟一: 設置環境

### 程式碼區塊 1-3: 環境準備

```markdown
# 原文:
In this notebook, we use a containerized version of Chroma DB. To set up, you will need the following:

1. Install Docker Desktop by following the link and Download Docker Desktop for your operating system.
2. In a terminal window, navigate to the folder ./05_src/chromadb/
3. Run the command `docker compose up -d`, which will start the Chroma DB server.
```

**中文翻譯與解釋**:

在這個筆記本中,我們使用容器化版本的 Chroma DB。設置步驟如下:

1. **安裝 Docker Desktop**
   - 前往 https://www.docker.com/products/docker-desktop/
   - 下載並安裝適合您作業系統的版本

2. **導航到正確的資料夾**
   ```powershell
   # 在 PowerShell 中執行:
   cd .\05_src\chromadb
   ```

3. **啟動 Chroma DB 伺服器**
   ```powershell
   docker compose up -d
   ```
   - `docker compose`: Docker 的編排工具
   - `up`: 啟動服務
   - `-d`: 在背景執行 (detached mode)

**💡 新手提示**: 
- 執行 `docker compose up -d` 後,Chroma DB 會在背景運行
- 您可以用 `docker ps` 檢查容器是否正在運行
- 用 `docker compose down` 停止服務

---

## 📥 步驟二: 下載批次處理結果

### 程式碼區塊 4-5: 載入環境變數

```python
%load_ext dotenv
%dotenv ../../05_src/.secrets
```

**解釋**:
- `%load_ext dotenv`: 載入 dotenv 擴充功能
- `%dotenv`: 從 `.secrets` 檔案讀取 API 金鑰等敏感資訊
- **為什麼需要?** OpenAI API 需要金鑰才能使用

### 程式碼區塊 6-7: 設定批次描述

```python
batch_description = 'Pitchfork reviews content embeddings 2025-10-18 12:17:17'
```

**解釋**:
- 這是之前創建的批次處理任務的描述
- 用來識別我們要下載哪個批次的結果
- **背景知識**: OpenAI 的 Batch API 可以批次處理大量請求,費用更便宜

### 程式碼區塊 8: 查詢批次狀態

```python
from openai import OpenAI

client = OpenAI()

batch_processes = client.batches.list().to_dict()
batch_info = [
    {'batch_id': batch['id'],
     'description': batch['metadata']['description'],
     'status': batch['status'],
     'request_counts': batch['request_counts'],
     'output_file_id': batch['output_file_id'],
     'input_file_id': batch['input_file_id']}
    for batch in batch_processes['data'] 
    if batch['metadata']['description'] == batch_description
]
```

**逐行解釋**:

1. **創建 OpenAI 客戶端**
   ```python
   client = OpenAI()
   ```
   - 這會自動讀取您的 API 金鑰

2. **列出所有批次**
   ```python
   batch_processes = client.batches.list().to_dict()
   ```
   - 取得您帳號下所有的批次處理任務

3. **篩選特定批次**
   ```python
   batch_info = [...]  # 列表推導式
   ```
   - 只保留符合 `batch_description` 的批次
   - 提取重要資訊: ID、狀態、檔案 ID 等

**輸出範例**:
```python
[
    {
        'batch_id': 'batch_abc123',
        'description': 'Pitchfork reviews content embeddings 2025-10-18 12:17:17',
        'status': 'completed',  # 完成狀態
        'request_counts': {'total': 1000, 'completed': 1000},
        'output_file_id': 'file-xyz789',
        'input_file_id': 'file-input123'
    }
]
```

---

## ✅ 步驟三: 檢查批次完成狀態

### 程式碼區塊 9-10: 篩選已完成的批次

```python
batch_complete = [
    batch for batch in batch_info if batch['status'] == 'completed'
]
```

**解釋**:
- 只保留狀態為 'completed' 的批次
- **為什麼?** 只有完成的批次才有結果可以下載

### 程式碼區塊 11-12: 檢查輸出格式

```python
response = client.files.content(batch_complete[0]['output_file_id'])
text_response = response.text
lines = text_response.split('\n')
print(lines[0])
```

**解釋**:
- 下載第一個完成批次的輸出檔案
- 將內容分割成行
- 印出第一行來檢查格式

**輸出範例** (JSONL 格式):
```json
{"id": "batch_req_abc", "custom_id": "review_001_chunk_0", "response": {"status_code": 200, "body": {"data": [{"embedding": [0.1, 0.2, ...]}]}}}
```

---

## 🔄 步驟四: 處理嵌入向量和文字

### 程式碼區塊 13: 主要處理函數

```python
import json 

def get_text_and_embeddings(batch):
    embedding_lines = get_content_from_file(batch, 'output_file_id')
    text_lines = get_content_from_file(batch, 'input_file_id')
    return embedding_lines, text_lines

def get_content_from_file(batch, key):
    file = client.files.content(batch[key])
    text = file.text
    lines = text.split('\n')
    content_lines = [json.loads(line) for line in lines if line.strip()]
    return content_lines
```

**詳細解釋**:

**`get_content_from_file` 函數**:
1. 從 OpenAI 下載檔案內容
2. 將文字按行分割
3. 將每一行的 JSON 解析成 Python 字典
4. 過濾空行

**`get_text_and_embeddings` 函數**:
- 同時獲取兩個檔案:
  - **輸出檔案**: 包含嵌入向量 (embeddings)
  - **輸入檔案**: 包含原始文字

**為什麼需要兩個檔案?**
- 輸出檔案只有向量,沒有原文
- 我們需要用 `custom_id` 將它們配對起來

### 程式碼區塊 14-15: 創建 Chroma 輸入格式

```python
def create_chroma_inputs(embedding_lines, text_lines):
    chroma_inputs = []
    text_dict = {item['custom_id']: item['body']['input'] for item in text_lines}
    for embed_item in embedding_lines:
        custom_id = embed_item['custom_id']
        text = text_dict.get(custom_id, "")
        chroma_input = {
            'id': embed_item['custom_id'],
            'embedding': embed_item['response']['body']['data'][0]['embedding'],
            'text': text
        }
        chroma_inputs.append(chroma_input)
    return chroma_inputs
```

**步驟拆解**:

1. **創建文字字典**
   ```python
   text_dict = {item['custom_id']: item['body']['input'] for item in text_lines}
   ```
   - 例如: `{'review_001_chunk_0': '這張專輯很棒...'}`
   - 方便快速查找

2. **配對嵌入向量和文字**
   ```python
   for embed_item in embedding_lines:
       custom_id = embed_item['custom_id']
       text = text_dict.get(custom_id, "")
   ```
   - 用 `custom_id` 作為鑰匙
   - 找到對應的原始文字

3. **建立 Chroma 格式**
   ```python
   chroma_input = {
       'id': custom_id,
       'embedding': [...],  # 向量
       'text': "原始文字"
   }
   ```

**最終格式範例**:
```python
{
    'id': 'review_001_chunk_0',
    'embedding': [0.1, 0.2, 0.3, ..., 0.5],  # 1536 維向量
    'text': 'This album features stunning vocals and innovative production...'
}
```

### 程式碼區塊 16-19: 批次處理

```python
from tqdm import tqdm

def process_batch_for_chromadb(batch):
    embedding_lines, text_lines = get_text_and_embeddings(batch)
    chroma_inputs = create_chroma_inputs(embedding_lines, text_lines)
    return chroma_inputs

def process_batches_for_chromadb(batches):
    all_chroma_inputs = []
    for batch in tqdm(batches, desc="Processing batches"):
        chroma_inputs = process_batch_for_chromadb(batch)
        all_chroma_inputs.extend(chroma_inputs)
    return all_chroma_inputs

# 執行處理
chroma_inputs = process_batches_for_chromadb(batch_complete)
```

**解釋**:
- `tqdm`: 顯示進度條 (很貼心!)
- 處理所有已完成的批次
- 合併成一個大列表

---

## 💾 步驟五: 載入資料到 Chroma DB

### 程式碼區塊 20-23: 設置和載入函數

```python
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os

def setup_collection(chroma_url:str="http://localhost:8000",
                     collection_name: str = "pitchfork_reviews"):
    chroma_client = chromadb.HttpClient(host=chroma_url)
    collections = chroma_client.list_collections()
    
    # 如果集合已存在,先刪除
    if collection_name in [col.name for col in collections]:
        chroma_client.delete_collection(name=collection_name)

    # 創建新集合
    collection = chroma_client.create_collection(
        name=collection_name,
        embedding_function=OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small")
    )
    return collection
```

**重點解釋**:

1. **連接到 Chroma**
   ```python
   chroma_client = chromadb.HttpClient(host=chroma_url)
   ```
   - 預設連接到 `http://localhost:8000`
   - 這是 Docker 容器的地址

2. **創建集合 (Collection)**
   - 類似資料庫中的「表格」
   - 儲存特定主題的向量資料

3. **設置嵌入函數**
   ```python
   embedding_function=OpenAIEmbeddingFunction(...)
   ```
   - **重要**: 查詢時也要用相同的模型!
   - 這樣才能確保向量相容

### 載入資料函數

```python
def load_embeddings_to_db(chroma_inputs:list[dict], 
                          collection_name:str,
                          chroma_url:str="http://localhost:8000",
                          batch_size:int=1000):
    
    collection = setup_collection(chroma_url=chroma_url, collection_name=collection_name)

    # 分批載入 (避免一次傳太多資料)
    for i in tqdm(range(0, len(chroma_inputs), batch_size)):
        batch = chroma_inputs[i:i + batch_size]
        collection.add(
            documents=[item['text'] for item in batch],
            embeddings=[item['embedding'] for item in batch],
            ids=[item['id'] for item in batch]
        )
```

**為什麼要分批?**
- 如果一次載入太多資料,可能會:
  - 記憶體不足
  - 網路逾時
  - 效能下降
- 1000 筆一批是個不錯的平衡點

### 執行載入

```python
vector_db_client_url = "http://localhost:8000"
load_embeddings_to_db(
    chroma_inputs=chroma_inputs,
    collection_name="pitchfork_reviews",
    chroma_url=vector_db_client_url, 
    batch_size=1000
)
```

**執行後會看到**:
```
Processing batches: 100%|██████████| 5/5 [00:10<00:00,  2.00s/it]
```

---

## 🗄️ 步驟六: 載入額外資訊到 SQL 資料庫

### 程式碼區塊 24-27: 載入 JSONL 檔案

```python
import json

def load_jsonl(file:str):
    data = []
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data
```

**JSONL 格式說明**:
- JSON Lines: 每行一個 JSON 物件
- 適合處理大型資料集
- 可以逐行讀取,不用一次載入全部

**範例 JSONL 檔案內容**:
```json
{"reviewid": "001", "title": "Album Name", "artist": "Artist Name", "score": 8.5}
{"reviewid": "002", "title": "Another Album", "artist": "Another Artist", "score": 7.2}
```

### 上傳到 SQL 資料庫

```python
import pandas as pd
import sqlalchemy as sa
import os

doc_folder = "../../05_src/documents/"
tables = ["artists", "reviews", "labels", "genres"]

def upload_tables_to_sql(tables:list[str], doc_folder:str):
    engine = sa.create_engine(os.getenv("SQL_URL"))
    for table_name in tables:
        file_path = os.path.join(doc_folder, f"pitchfork_{table_name}.jsonl")
        data = load_jsonl(file_path)
        df = pd.DataFrame(data)
        with engine.connect() as conn:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Loaded {df.shape} records from {file_path}")
```

**資料表結構**:

1. **artists** (藝術家表)
   - 藝術家 ID、名稱等

2. **reviews** (評論表)
   - 評論 ID、專輯名稱、評分等

3. **labels** (唱片公司表)
   - 唱片公司資訊

4. **genres** (音樂類型表)
   - 專輯的音樂類型

**為什麼需要 SQL 資料庫?**
- **向量資料庫** (Chroma): 儲存文字內容,用於語義搜尋
- **SQL 資料庫**: 儲存結構化資料 (評分、藝術家名稱等)
- **結合使用**: 先用向量搜尋找到相關評論,再用 SQL 查詢詳細資訊

### 程式碼區塊 28-29: 查詢額外資訊

```python
def additional_details(review_id:str):
    engine = sa.create_engine(os.getenv("SQL_URL"))
    query = f"""
    SELECT r.reviewid,
        r.title,
        r.artist,
        r.score,
        g.genre
    FROM reviews AS r
    LEFT JOIN genres as g
        ON r.reviewid = g.reviewid
    WHERE r.reviewid = '{review_id}'
    """
    with engine.connect() as conn:
        result = pd.read_sql(query, conn)
    
    if not result.empty:
        row = result.iloc[0]
        details = {
            "reviewid": row['reviewid'],
            "album": row['title'],
            "score": row['score'],
            "artist": row['artist']
        }
        return details
    else:
        return {}
```

**SQL 查詢解釋**:

```sql
SELECT r.reviewid, r.title, r.artist, r.score, g.genre
FROM reviews AS r              -- 主表: reviews
LEFT JOIN genres as g          -- 左連接: genres
    ON r.reviewid = g.reviewid -- 連接條件: reviewid 相同
WHERE r.reviewid = '{review_id}'  -- 只查詢特定評論
```

**LEFT JOIN 說明**:
- 保留 reviews 表的所有記錄
- 如果有對應的 genre,就加上
- 如果沒有對應的 genre,genre 欄位為 NULL

### 輔助函數

```python
def get_reviewid_from_custom_id(custom_id:str):
    return custom_id.split('_')[0]
```

**解釋**:
- `custom_id` 格式: `"review_001_chunk_0"`
- 分割後取第一部分: `"review"`
- 不對! 應該取 `"001"`

**可能的修正**:
```python
def get_reviewid_from_custom_id(custom_id:str):
    parts = custom_id.split('_')
    return parts[1] if len(parts) > 1 else custom_id
```

---

## 🔍 步驟七: 生成提示詞 (Prompt)

### 程式碼區塊 30-31: 連接到 Chroma

```python
chroma = chromadb.HttpClient(host=vector_db_client_url)
collection = chroma.get_collection(
    name="pitchfork_reviews", 
    embedding_function=OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-3-small")
)
```

**重點**:
- 使用與儲存時相同的 `embedding_function`
- 這樣查詢向量才能與儲存的向量比較

### 程式碼區塊 32: 測試查詢

```python
collection.query(
    query_texts=["A great album with stunning vocals and production."],
    n_results=3
)
```

**輸出範例**:
```python
{
    'ids': [['review_123_chunk_0', 'review_456_chunk_2', 'review_789_chunk_1']],
    'distances': [[0.15, 0.23, 0.31]],  # 越小越相似
    'documents': [['文字內容1', '文字內容2', '文字內容3']]
}
```

### 程式碼區塊 33: 完整的提示詞生成系統

```python
def get_context_data(query:str, collection, top_n:int):
    # 1. 向量搜尋
    results = collection.query(
        query_texts=[query],
        n_results=top_n
    )
    
    # 2. 為每個結果添加額外資訊
    context_data = []
    for idx, custom_id in enumerate(results['ids'][0]):
        review_id = get_reviewid_from_custom_id(custom_id)
        details = additional_details(review_id)  # SQL 查詢
        details['text'] = results['documents'][0][idx]
        context_data.append(details)
    
    return context_data
```

**流程圖**:
```
使用者查詢
    ↓
向量搜尋 (Chroma DB) → 找到最相似的 3 篇評論片段
    ↓
提取 custom_id → 轉換成 review_id
    ↓
SQL 查詢 → 獲取專輯名稱、藝術家、評分
    ↓
組合資料 → 文字內容 + 結構化資訊
```

### 生成結構化提示詞

```python
def generate_prompt(query:str, collection, top_n:int):
    context_data = get_context_data(query, collection, top_n)
    
    # 開頭說明
    prompt = f"Given a query, provide a detailed response using the context from relevant Pitchfork reviews. The context will contain references to {top_n} album reviews.\n\n"
    
    # 評分標準
    prompt += f"The score is numeric and its scale is from 0 to 10, with 10 being the highest rating. Any album with a score greater than 8.0 is considered a must-listen; album with a score greater than 6.5 is good.\n\n"
    
    # 使用者查詢
    prompt += f"<query>{query}</query>\n\n"
    
    # 上下文資料
    prompt += "<context>\n"
    for k, context in enumerate(context_data):
        prompt += f"<album {k}>\n"
        prompt += f"- Album Title: {context.get('album', 'N/A')}\n" 
        prompt += f"- Album Artist: {context.get('artist', 'N/A')}\n"
        prompt += f"- Album Score: {context.get('score', 'N/A')}\n"
        prompt += f"- Review Quote: {context.get('text', 'N/A')}\n"
        prompt += f"</album {k}>\n\n"
    prompt += "</context>\n\n"
    
    # 結尾指示
    prompt += "\nBased on the context and nothing else, provide a detailed response to the query."
    return prompt
```

**生成的提示詞範例**:
```
Given a query, provide a detailed response using the context from relevant Pitchfork reviews. The context will contain references to 3 album reviews.

The score is numeric and its scale is from 0 to 10, with 10 being the highest rating. Any album with a score greater than 8.0 is considered a must-listen; album with a score greater than 6.5 is good.

<query>What are some highly rated albums by emerging indie artists?</query>

<context>
<album 0>
- Album Title: Young Galaxy
- Album Artist: Nova Heart
- Album Score: 8.3
- Review Quote: This indie rock album showcases brilliant songwriting...
</album 0>

<album 1>
- Album Title: Midnight Dreams
- Album Artist: The Lumineers
- Album Score: 8.1
- Review Quote: An innovative approach to folk music...
</album 1>

<album 2>
- Album Title: Electric Waves
- Album Artist: Beach House
- Album Score: 7.9
- Review Quote: Atmospheric production and haunting vocals...
</album 2>
</context>

Based on the context and nothing else, provide a detailed response to the query.
```

### 完整回應生成

```python
def generate_response(query:str, collection, top_n:int=1):
    prompt = generate_prompt(query, collection, top_n)
    print("Generated Prompt:\n", prompt)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides information based on Pitchfork reviews."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content
```

**參數說明**:
- `model="gpt-4o-mini"`: 使用較小、較便宜的模型
- `max_tokens=500`: 限制回應長度
- `temperature=0.7`: 控制創意度 (0=保守, 1=創意)

---

## 🎯 步驟八: 執行查詢

### 程式碼區塊 34-36: 實際查詢

```python
# 查詢
response = generate_response(
    "What are some highly rated albums by emerging indie artists?", 
    collection, 
    3
)

# 顯示結果
print(response)
```

**可能的回應**:
```
Based on the Pitchfork reviews provided, here are some highly rated albums by emerging indie artists:

1. **Young Galaxy by Nova Heart** (Score: 8.3) - This album is considered a must-listen with its brilliant songwriting and innovative indie rock sound.

2. **Midnight Dreams by The Lumineers** (Score: 8.1) - Another must-listen album that brings an innovative approach to folk music...

3. **Electric Waves by Beach House** (Score: 7.9) - While just below the must-listen threshold, this is still a good album featuring atmospheric production...

All three albums demonstrate the creativity and talent of emerging indie artists and are worth exploring.
```

---

## 🎓 總結與實際應用

### 這個系統做了什麼?

1. **資料準備**: 將文字轉換成向量 (embeddings)
2. **資料儲存**: 
   - Chroma DB: 儲存文字和向量
   - SQL DB: 儲存結構化資訊
3. **語義搜尋**: 根據意思找相似內容 (不是關鍵字!)
4. **資訊整合**: 結合向量搜尋和資料庫查詢
5. **AI 回應**: 用 GPT 生成自然語言回答

### 實際應用場景

**1. 音樂推薦系統**
```python
query = "給我一些適合深夜聆聽的氛圍音樂"
# 系統會找到類似描述的評論
```

**2. 客服知識庫**
```python
query = "如何重設密碼?"
# 從成千上萬篇文章中找到最相關的解答
```

**3. 研究論文搜尋**
```python
query = "深度學習在醫療影像的應用"
# 找到語義相關的論文,即使用詞不完全相同
```

### 與傳統搜尋的差異

**傳統關鍵字搜尋**:
```
查詢: "好聽的專輯"
結果: 只會找到包含「好聽」和「專輯」的文字
```

**向量語義搜尋**:
```
查詢: "好聽的專輯"
結果: 找到描述「出色的製作」、「令人驚艷的演出」、「傑出的作品」等
      即使沒有「好聽」這個詞!
```

### 關鍵技術點

1. **Embedding (嵌入向量)**
   - 將文字轉換成數字向量
   - 相似意思的文字會有相似的向量

2. **向量相似度**
   - 使用距離計算 (如餘弦相似度)
   - 找到最接近的向量

3. **批次處理**
   - 降低 API 成本
   - 處理大量資料

4. **混合檢索**
   - 向量搜尋: 找相關內容
   - SQL 查詢: 獲取精確資訊

---

## 💡 進階實驗建議

### 實驗 1: 改變 top_n 參數

```python
# 試試看不同的數量
response_1 = generate_response(query, collection, top_n=1)  # 只參考 1 筆
response_3 = generate_response(query, collection, top_n=3)  # 參考 3 筆
response_5 = generate_response(query, collection, top_n=5)  # 參考 5 筆

# 比較差異
```

**觀察重點**:
- top_n 太小: 資訊可能不夠全面
- top_n 太大: 可能包含不相關的資訊

### 實驗 2: 不同類型的查詢

```python
queries = [
    "具有實驗性質的電子音樂專輯",
    "適合運動時聽的專輯",
    "有深刻歌詞的民謠專輯",
    "2020 年代最佳嘻哈專輯"
]

for query in queries:
    response = generate_response(query, collection, 3)
    print(f"\n查詢: {query}\n回應: {response}\n")
```

### 實驗 3: 修改評分標準

在 `generate_prompt` 函數中修改:

```python
# 原本
prompt += f"Any album with a score greater than 8.0 is considered a must-listen; album with a score greater than 6.5 is good.\n\n"

# 改成更嚴格的標準
prompt += f"Any album with a score greater than 9.0 is considered a masterpiece; greater than 8.5 is excellent; greater than 7.5 is good.\n\n"
```

---

## ❓ 常見問題 (FAQ)

### Q1: 為什麼要用 Docker?
**A**: Docker 讓安裝變簡單,不用擔心版本衝突。一個指令就能啟動 Chroma DB。

### Q2: 向量有多長?
**A**: 使用 `text-embedding-3-small` 模型,每個向量有 **1536 個數字**。

### Q3: 可以搜尋中文嗎?
**A**: 可以! OpenAI 的 embedding 模型支援多種語言,包括中文。

### Q4: 成本如何?
**A**: 
- Batch API: $0.0001 / 1K tokens (便宜 50%)
- text-embedding-3-small: $0.00002 / 1K tokens
- 處理 10,000 篇評論大約 $1-2 USD

### Q5: 資料會永久保存嗎?
**A**: Docker 容器停止後,資料會保留。除非您執行 `docker compose down -v` (刪除 volumes)。

### Q6: 可以用其他向量資料庫嗎?
**A**: 可以! 類似的選項:
- **Pinecone**: 雲端服務,易用但收費
- **Weaviate**: 開源,功能強大
- **Milvus**: 適合超大規模資料
- **FAISS**: Facebook 開發,超快速度

### Q7: 如何提升搜尋品質?
**A**: 
1. **更好的 chunking**: 將文字切得更合理
2. **metadata 過濾**: 先用條件篩選,再做向量搜尋
3. **混合搜尋**: 結合關鍵字和向量搜尋
4. **重排序**: 用更強大的模型對結果重新排序

---

## 🚀 下一步學習

1. **Metadata 過濾**
   ```python
   collection.query(
       query_texts=["indie rock"],
       n_results=5,
       where={"score": {"$gte": 8.0}}  # 只搜尋評分 >= 8.0 的
   )
   ```

2. **混合搜尋 (Hybrid Search)**
   - 結合向量相似度和關鍵字匹配
   - 更精確的結果

3. **RAG (Retrieval-Augmented Generation)**
   - 這個系統就是 RAG 的例子!
   - 檢索 (Retrieval) + 生成 (Generation)

4. **Fine-tuning Embeddings**
   - 用您的資料訓練專屬的 embedding 模型
   - 提升特定領域的搜尋品質

---

## 📚 延伸閱讀

- [Chroma DB 官方文檔](https://docs.trychroma.com/)
- [OpenAI Embeddings 指南](https://platform.openai.com/docs/guides/embeddings)
- [向量資料庫比較](https://github.com/erikbern/ann-benchmarks)
- [RAG 最佳實踐](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

**祝您學習愉快! 有任何問題歡迎隨時詢問! 🎉**
