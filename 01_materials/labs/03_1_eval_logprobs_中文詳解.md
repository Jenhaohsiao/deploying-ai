# 評估模型輸出 - Logprobs (對數機率) 詳細教學

## 📚 這個檔案在教什麼?

這個教學會教您如何使用 **logprobs (對數機率)** 來評估 AI 模型的信心程度。簡單來說,就是讓 AI 不只告訴您答案,還告訴您「它有多確定這個答案」!

---

## 🎯 學習目標

1. 了解什麼是 logprobs 及其用途
2. 學習如何從 OpenAI API 獲取 logprobs
3. 使用 logprobs 改善分類任務
4. 設定信心門檻來決定是否需要人工協助
5. 實際應用:新聞標題分類

---

## 📖 基礎知識補充

### 什麼是 Logprobs (對數機率)?

**簡單比喻**: 
想像 AI 是一個學生在考選擇題:

```
問題: 這篇新聞是關於什麼?
A. 商業 (90% 確定) ← AI 非常確定
B. 政治 (8% 確定)
C. 體育 (1.5% 確定)
D. 藝術 (0.5% 確定)
```

**Logprobs 就是用數學方式表達 AI 對每個選項的信心程度**。

### 為什麼用「對數」(Log)?

**數學定義**:
```
logprobs = log(probability)
```

**為什麼不直接用機率?**

1. **數值穩定性**: 機率可能非常小 (如 0.0000001),用對數避免精度損失
2. **計算方便**: 乘法變加法 (log(a×b) = log(a) + log(b))
3. **範圍更直觀**: 對數機率是負數,越接近 0 表示越確定

**機率與對數機率對照表**:

| 機率 (Probability) | 對數機率 (Logprob) | 意義 |
|-------------------|-------------------|------|
| 1.0 (100%) | 0.0 | 絕對確定 |
| 0.5 (50%) | -0.693 | 一半一半 |
| 0.1 (10%) | -2.303 | 不太確定 |
| 0.01 (1%) | -4.605 | 幾乎不可能 |
| 0.001 (0.1%) | -6.908 | 非常不可能 |

**轉換公式**:
```python
import numpy as np

# 對數機率 → 機率
probability = np.exp(logprob)

# 機率 → 對數機率
logprob = np.log(probability)
```

---

## 🔧 API 參數說明

### 重要參數

OpenAI API 提供兩個關鍵參數來獲取 logprobs:

#### 1. `logprobs` (布林值)

```python
logprobs = True  # 啟用,返回輸出 token 的對數機率
logprobs = False # 關閉 (預設)
```

**功能**: 決定是否返回輸出 token 的對數機率

#### 2. `top_logprobs` (整數 0-20)

```python
top_logprobs = 2  # 返回前 2 個最可能的 token
top_logprobs = 5  # 返回前 5 個最可能的 token
```

**功能**: 指定在每個 token 位置返回多少個最可能的選項

**注意**: 使用 `top_logprobs` 時必須設定 `logprobs=True`

---

## 💻 程式碼詳解

### 步驟一: 環境設置

#### 程式碼區塊 1-3: 載入環境與初始化

```python
# 載入環境變數 (API 金鑰)
%load_ext dotenv
%dotenv ../../05_src/.secrets

# 匯入必要套件
from openai import OpenAI
import numpy as np
import os

# 創建 OpenAI 客戶端
client = OpenAI()
```

**解釋**:
- `dotenv`: 從 `.secrets` 檔案讀取 `OPENAI_API_KEY`
- `numpy`: 用於數學計算 (對數機率轉機率)
- `client`: 與 OpenAI API 溝通的介面

---

### 步驟二: 建立通用函數介面

#### 程式碼區塊 4-5: 完成請求函數

```python
def get_completion(
    input: list[dict[str, str]],           # 對話訊息
    model: str = "gpt-4o-mini",            # 使用的模型
    max_tokens=500,                        # 最大輸出長度
    temperature=0,                         # 創意度 (0=保守)
    tools=None,                            # 工具/函數呼叫
    logprobs=None,                         # 是否返回對數機率
    top_logprobs=None,                     # 返回前 N 個最可能的 token
) -> str:
    params = {
        "model": model,
        "input": input,
        "max_output_tokens": max_tokens,
        "temperature": temperature,
        "tools": tools,
        "include": ["message.output_text.logprobs"] if logprobs else [],
        "top_logprobs": top_logprobs,
    }
    if tools:
        params["tools"] = tools

    completion = client.responses.create(**params)
    return completion
```

**參數詳解**:

1. **input**: 對話訊息列表
   ```python
   [{"role": "user", "content": "將這篇新聞分類"}]
   ```

2. **model**: 選擇模型
   - `gpt-4o-mini`: 便宜、快速
   - `gpt-4o`: 更強大但較貴

3. **temperature**: 控制隨機性
   - `0`: 完全確定性,每次相同輸入得到相同輸出
   - `0.7`: 中等創意
   - `1.0`: 高創意,輸出多變

4. **logprobs=True**: 啟用對數機率輸出

5. **top_logprobs=2**: 顯示前 2 個最可能的選項

**為什麼需要這個函數?**
- 將複雜的 API 呼叫封裝起來
- 可以重複使用,不用每次都寫一大串參數
- 方便實驗不同設定

---

### 步驟三: 準備測試資料

#### 程式碼區塊 6: 新聞標題資料集

```python
headlines = [
    # 經典文學作品 vs 新聞標題 (測試模糊性)
    "War and Peace in the Modern Era",         # 可能是政治或藝術
    "'War and Peace' in the Modern Era",       # 加引號,更明確是藝術
    "The Art of the Deal",                     # 商業書籍,也可能是藝術
    
    # 紐約時報 (NYT) 標題
    "Louvre Closed After Thieves Steal 'Priceless' Jewels in Brazen Daylight Robbery",  # 藝術
    "The Risk That Built America",             # 商業或政治
    "Who should the Dodgers rather face in the World Series, the Mariners or the Blue Jays?",  # 體育
    
    # 紐約客 (New Yorker) 標題
    "Justin Trudeau and Katy Perry's Teen-Age Dream",  # 政治或藝術
    "Shohei Ohtani and the Dodgers Are a Sight to Behold",  # 體育
    "A Tech Millionaire's Costly Quest to Prove His Brother Was Murdered",  # 商業或政治
    "The AI Boom and the Spectre of 1929"      # 商業
]
```

**資料集設計巧思**:

1. **包含模糊案例**
   - "War and Peace in the Modern Era" - 可能是政治分析或文學評論
   - "'War and Peace' in the Modern Era" - 引號暗示是文學作品

2. **涵蓋所有類別**
   - Business (商業): AI Boom, Tech Millionaire
   - Politics (政治): Justin Trudeau
   - Sports (體育): Dodgers, World Series
   - Art (藝術): Louvre, War and Peace

3. **真實新聞來源**
   - NYT: 紐約時報
   - New Yorker: 紐約客
   - 測試模型對真實世界資料的表現

---

### 步驟四: 設計分類提示詞

#### 程式碼區塊 7: 分類提示詞模板

```python
CLASSIFICATION_PROMPT = """You will be given a headline of a news article.
Classify the article into one of the following categories: Business, Politics, Sports, and Art.
Return only the name of the category, and nothing else.
MAKE SURE your output is one of the four categories stated.
Article headline: {headline}"""
```

**中文翻譯**:
```
您將獲得一篇新聞文章的標題。
請將文章分類到以下類別之一: Business (商業)、Politics (政治)、Sports (體育)、Art (藝術)。
只返回類別名稱,不要其他內容。
確保您的輸出是上述四個類別之一。
文章標題: {headline}
```

**提示詞設計要點**:

1. **清晰的任務說明**
   ```
   "You will be given a headline of a news article."
   → 明確告訴 AI 輸入是什麼
   ```

2. **限定輸出選項**
   ```
   "Classify the article into one of the following categories: ..."
   → 只能從 4 個類別中選擇
   ```

3. **格式要求**
   ```
   "Return only the name of the category, and nothing else."
   → 只要類別名稱,不要解釋
   ```

4. **強調約束**
   ```
   "MAKE SURE your output is one of the four categories stated."
   → 再次強調,防止 AI 自創類別
   ```

5. **使用變數插槽**
   ```python
   {headline}  # 稍後用 .format(headline=...) 替換
   ```

**為什麼這樣設計?**
- **結構化輸出**: 方便程式解析
- **減少錯誤**: 明確限制可能的輸出
- **可重複使用**: 模板可套用到任何標題

---

### 步驟五: 基本分類 (不使用 Logprobs)

#### 程式碼區塊 8-9: 簡單分類測試

```python
for headline in headlines:
    print(f"\nHeadline: {headline}")
    response = get_completion(
        [{"role": "user", "content": CLASSIFICATION_PROMPT.format(headline=headline)}],
        model="gpt-4o-mini",
    )
    print(f"Category: {response.output_text}\n")
```

**輸出範例**:
```
Headline: War and Peace in the Modern Era
Category: Politics

Headline: 'War and Peace' in the Modern Era
Category: Art

Headline: The Art of the Deal
Category: Business

Headline: Louvre Closed After Thieves Steal 'Priceless' Jewels...
Category: Art

Headline: Shohei Ohtani and the Dodgers Are a Sight to Behold
Category: Sports
```

**觀察重點**:

1. **引號的影響**
   - 沒引號: "War and Peace in the Modern Era" → Politics
   - 有引號: "'War and Peace' in the Modern Era" → Art
   - 引號暗示這是書名

2. **只有答案,沒有信心程度**
   - AI 說 "Politics",但我們不知道它有多確定
   - 可能是 99% 確定,也可能只有 51% 確定

**問題**:
- ❌ 不知道 AI 的信心程度
- ❌ 無法判斷哪些分類需要人工檢查
- ❌ 沒有次佳選項的資訊

---

### 步驟六: 使用 Logprobs 改進分類

#### 程式碼區塊 10-11: 顯示 Top-2 選項與機率

```python
for headline in headlines:
    print(f"\nHeadline: {headline}")
    
    # 啟用 logprobs,顯示前 2 個選項
    API_RESPONSE = get_completion(
        [{"role": "user", "content": CLASSIFICATION_PROMPT.format(headline=headline)}],
        model="gpt-4o-mini",
        logprobs=True,      # ← 關鍵: 啟用對數機率
        top_logprobs=2,     # ← 顯示前 2 個最可能的 token
    )
    
    # 提取前 2 個最可能的 token 及其對數機率
    top_n_logprobs = API_RESPONSE.output[0].content[0].logprobs[0].top_logprobs
    
    output_content = ""
    for i, logprob in enumerate(top_n_logprobs, start=1):
        # 計算線性機率 (百分比)
        linear_prob = np.round(np.exp(logprob.logprob) * 100, 2)
        
        output_content += (
            f"Output token {i}: {logprob.token}, "
            f"logprobs: {logprob.logprob}, "
            f"linear probability: {linear_prob}%\n"
        )
    
    print(output_content)
    print("\n")
```

**程式碼拆解**:

1. **啟用 Logprobs**
   ```python
   logprobs=True,
   top_logprobs=2,
   ```
   - 要求 API 返回前 2 個最可能的選項

2. **提取資料結構**
   ```python
   top_n_logprobs = API_RESPONSE.output[0].content[0].logprobs[0].top_logprobs
   ```
   
   **資料結構路徑**:
   ```
   API_RESPONSE
   └── output[0]           # 第一個輸出
       └── content[0]      # 第一個內容區塊
           └── logprobs[0] # 第一個 token 的 logprobs
               └── top_logprobs  # 前 N 個最可能的 token
   ```

3. **轉換對數機率為機率**
   ```python
   linear_prob = np.round(np.exp(logprob.logprob) * 100, 2)
   ```
   
   **數學過程**:
   ```
   logprob = -0.1053  (對數機率)
   ↓ 取指數
   probability = e^(-0.1053) = 0.90
   ↓ 轉百分比
   linear_prob = 0.90 × 100 = 90%
   ↓ 四捨五入
   90.00%
   ```

**輸出範例**:

```
Headline: War and Peace in the Modern Era
Output token 1: Politics, logprobs: -0.5234, linear probability: 59.23%
Output token 2: Art, logprobs: -0.9234, linear probability: 39.67%


Headline: 'War and Peace' in the Modern Era
Output token 1: Art, logprobs: -0.0513, linear probability: 95.00%
Output token 2: Politics, logprobs: -3.0234, linear probability: 4.87%


Headline: Shohei Ohtani and the Dodgers Are a Sight to Behold
Output token 1: Sports, logprobs: -0.0010, linear probability: 99.90%
Output token 2: Art, logprobs: -6.9078, linear probability: 0.10%
```

**深入分析**:

### 案例 1: 模糊標題 (低信心)
```
Headline: War and Peace in the Modern Era
Output token 1: Politics, logprobs: -0.5234, linear probability: 59.23%
Output token 2: Art, logprobs: -0.9234, linear probability: 39.67%
```

**解讀**:
- ⚠️ **信心不足**: 第一選項只有 59.23%
- ⚠️ **選項接近**: 第二選項有 39.67%,很接近
- 💡 **建議**: 需要人工檢查!

### 案例 2: 明確標題 (高信心)
```
Headline: 'War and Peace' in the Modern Era
Output token 1: Art, logprobs: -0.0513, linear probability: 95.00%
Output token 2: Politics, logprobs: -3.0234, linear probability: 4.87%
```

**解讀**:
- ✅ **高信心**: 第一選項有 95%
- ✅ **差距明顯**: 第二選項只有 4.87%
- 💡 **建議**: 可以自動分類

### 案例 3: 超級明確 (超高信心)
```
Headline: Shohei Ohtani and the Dodgers Are a Sight to Behold
Output token 1: Sports, logprobs: -0.0010, linear probability: 99.90%
Output token 2: Art, logprobs: -6.9078, linear probability: 0.10%
```

**解讀**:
- ✅ **極高信心**: 第一選項接近 100%
- ✅ **絕對優勢**: 第二選項幾乎不可能
- 💡 **建議**: 絕對可以自動分類

---

## 🎯 Logprobs 的實際應用

### 程式碼區塊 12: 總結用途

```markdown
原文:
In this classification task, we see the usefulness of logprobs: 
+ We can determine the degree to which a model is "sure" about a classification that it has proposed. 
+ Based on logprobs, we can set a threshold under which human assistance is needed. 
+ Alternatively, we can set the logic of our code to provide several options if the logprobs are within a threshold.
```

**中文翻譯與延伸**:

在這個分類任務中,我們看到 logprobs 的實用性:

### 1️⃣ **判斷模型信心程度**

```python
if linear_prob > 95:
    confidence = "非常確定"
elif linear_prob > 80:
    confidence = "相當確定"
elif linear_prob > 60:
    confidence = "有點確定"
else:
    confidence = "不太確定"
```

### 2️⃣ **設定人工介入門檻**

```python
def classify_with_human_check(headline):
    response = get_completion([...], logprobs=True, top_logprobs=2)
    top_logprobs = response.output[0].content[0].logprobs[0].top_logprobs
    
    top1_prob = np.exp(top_logprobs[0].logprob) * 100
    top2_prob = np.exp(top_logprobs[1].logprob) * 100
    
    # 如果第一選項低於 80% 或與第二選項差距小於 20%
    if top1_prob < 80 or (top1_prob - top2_prob) < 20:
        print(f"⚠️ 信心不足,需要人工檢查")
        print(f"選項 1: {top_logprobs[0].token} ({top1_prob:.2f}%)")
        print(f"選項 2: {top_logprobs[1].token} ({top2_prob:.2f}%)")
        return "NEEDS_HUMAN_REVIEW"
    else:
        print(f"✅ 自動分類: {top_logprobs[0].token} ({top1_prob:.2f}%)")
        return top_logprobs[0].token
```

**使用範例**:
```python
classify_with_human_check("War and Peace in the Modern Era")
# 輸出:
# ⚠️ 信心不足,需要人工檢查
# 選項 1: Politics (59.23%)
# 選項 2: Art (39.67%)
# → NEEDS_HUMAN_REVIEW

classify_with_human_check("Shohei Ohtani and the Dodgers Are a Sight to Behold")
# 輸出:
# ✅ 自動分類: Sports (99.90%)
# → Sports
```

### 3️⃣ **提供多個選項**

```python
def classify_with_options(headline, threshold=15):
    response = get_completion([...], logprobs=True, top_logprobs=4)
    top_logprobs = response.output[0].content[0].logprobs[0].top_logprobs
    
    # 計算所有選項的機率
    options = []
    for logprob in top_logprobs:
        prob = np.exp(logprob.logprob) * 100
        options.append((logprob.token, prob))
    
    # 如果前幾個選項機率接近,返回多個
    top_prob = options[0][1]
    suggested = [options[0]]
    
    for option in options[1:]:
        if top_prob - option[1] < threshold:  # 差距小於門檻
            suggested.append(option)
    
    if len(suggested) > 1:
        print(f"🤔 有多個可能的分類:")
        for cat, prob in suggested:
            print(f"  - {cat}: {prob:.2f}%")
    else:
        print(f"✅ 明確分類: {suggested[0][0]} ({suggested[0][1]:.2f}%)")
    
    return suggested
```

**使用範例**:
```python
classify_with_options("War and Peace in the Modern Era", threshold=20)
# 輸出:
# 🤔 有多個可能的分類:
#   - Politics: 59.23%
#   - Art: 39.67%
# → [('Politics', 59.23), ('Art', 39.67)]

classify_with_options("Shohei Ohtani and the Dodgers Are a Sight to Behold", threshold=20)
# 輸出:
# ✅ 明確分類: Sports (99.90%)
# → [('Sports', 99.90)]
```

---

## 🔬 進階應用場景

### 場景 1: 內容審核系統

```python
def moderate_content(text):
    """
    判斷內容是否安全,不確定時標記為待審
    """
    response = get_completion(
        [{"role": "user", "content": f"Is this content safe? Answer 'Safe' or 'Unsafe': {text}"}],
        logprobs=True,
        top_logprobs=2
    )
    
    top_logprobs = response.output[0].content[0].logprobs[0].top_logprobs
    safe_prob = np.exp(top_logprobs[0].logprob) * 100
    
    if top_logprobs[0].token == "Safe" and safe_prob > 95:
        return "AUTO_APPROVED"
    elif top_logprobs[0].token == "Unsafe" and safe_prob > 95:
        return "AUTO_REJECTED"
    else:
        return "MANUAL_REVIEW"  # 不確定,需要人工審核
```

### 場景 2: 情感分析信心評估

```python
def sentiment_analysis_with_confidence(review):
    """
    分析評論情感,並報告信心程度
    """
    response = get_completion(
        [{"role": "user", "content": f"Sentiment (Positive/Negative/Neutral): {review}"}],
        logprobs=True,
        top_logprobs=3
    )
    
    top_logprobs = response.output[0].content[0].logprobs[0].top_logprobs
    
    results = []
    for logprob in top_logprobs:
        sentiment = logprob.token
        confidence = np.exp(logprob.logprob) * 100
        results.append({
            'sentiment': sentiment,
            'confidence': confidence
        })
    
    return results

# 使用範例
review = "The product is okay, but could be better."
results = sentiment_analysis_with_confidence(review)
# 輸出:
# [
#   {'sentiment': 'Neutral', 'confidence': 65.23},
#   {'sentiment': 'Negative', 'confidence': 28.45},
#   {'sentiment': 'Positive', 'confidence': 6.32}
# ]
```

### 場景 3: A/B 測試提示詞

```python
def compare_prompts(headline, prompt_a, prompt_b):
    """
    比較兩個提示詞的信心程度,選擇更確定的
    """
    response_a = get_completion([{"role": "user", "content": prompt_a.format(headline=headline)}],
                                 logprobs=True, top_logprobs=1)
    response_b = get_completion([{"role": "user", "content": prompt_b.format(headline=headline)}],
                                 logprobs=True, top_logprobs=1)
    
    logprob_a = response_a.output[0].content[0].logprobs[0].top_logprobs[0].logprob
    logprob_b = response_b.output[0].content[0].logprobs[0].top_logprobs[0].logprob
    
    confidence_a = np.exp(logprob_a) * 100
    confidence_b = np.exp(logprob_b) * 100
    
    print(f"Prompt A 信心: {confidence_a:.2f}%")
    print(f"Prompt B 信心: {confidence_b:.2f}%")
    
    if confidence_a > confidence_b:
        print("→ Prompt A 更確定")
    else:
        print("→ Prompt B 更確定")
```

---

## 📊 視覺化 Logprobs

### 簡單的文字圖表

```python
def visualize_logprobs(headline, top_n=4):
    """
    用文字圖表顯示各選項的機率
    """
    response = get_completion(
        [{"role": "user", "content": CLASSIFICATION_PROMPT.format(headline=headline)}],
        logprobs=True,
        top_logprobs=top_n
    )
    
    top_logprobs = response.output[0].content[0].logprobs[0].top_logprobs
    
    print(f"\n標題: {headline}\n")
    print("分類機率分布:")
    print("-" * 50)
    
    for logprob in top_logprobs:
        category = logprob.token
        prob = np.exp(logprob.logprob) * 100
        bar_length = int(prob / 2)  # 50% = 25 個字元
        bar = "█" * bar_length
        
        print(f"{category:12} | {bar} {prob:.2f}%")
    
    print("-" * 50)

# 使用範例
visualize_logprobs("War and Peace in the Modern Era")
```

**輸出**:
```
標題: War and Peace in the Modern Era

分類機率分布:
--------------------------------------------------
Politics     | █████████████████████████████ 59.23%
Art          | ███████████████████ 39.67%
Business     | █ 0.95%
Sports       | ▌ 0.15%
--------------------------------------------------
```

---

## 🎓 理論補充: Token 與分類

### 什麼是 Token?

**定義**: Token 是 AI 處理文字的基本單位

**範例**:
```python
句子: "The cat sat on the mat."
Tokens: ["The", " cat", " sat", " on", " the", " mat", "."]
```

**在分類任務中**:
- 我們要求 AI 只輸出一個 token: 類別名稱
- 例如: "Sports", "Politics", "Art", "Business"

### 為什麼看第一個 Token 的 Logprobs?

```python
top_n_logprobs = API_RESPONSE.output[0].content[0].logprobs[0].top_logprobs
#                                                          ↑
#                                                    第一個 token (索引 0)
```

**原因**:
1. 我們的提示詞要求: "Return only the name of the category"
2. AI 的回應只有一個 token: 類別名稱
3. 所以我們只需要看第一個 token 的機率分布

**完整回應範例**:
```python
{
    'output': [
        {
            'content': [
                {
                    'logprobs': [
                        {
                            'token': 'Sports',
                            'logprob': -0.001,
                            'top_logprobs': [
                                {'token': 'Sports', 'logprob': -0.001},  # 99.90%
                                {'token': 'Art', 'logprob': -6.908}      # 0.10%
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
```

---

## 💡 最佳實踐建議

### 1. 選擇合適的 `top_logprobs` 值

```python
# 二元分類 (是/否)
top_logprobs = 2  # 足夠

# 多類別分類 (4-6 個類別)
top_logprobs = 3  # 看前 3 個

# 複雜分類 (10+ 個類別)
top_logprobs = 5  # 看前 5 個

# 最大值
top_logprobs = 20  # API 限制
```

### 2. 設定合理的信心門檻

```python
# 保守策略 (減少錯誤)
high_confidence_threshold = 90  # 只有 >90% 才自動分類

# 平衡策略
medium_confidence_threshold = 75  # >75% 自動,其他人工

# 激進策略 (減少人工工作量)
low_confidence_threshold = 60  # >60% 就自動
```

### 3. 考慮成本

```python
# Logprobs 會增加 token 使用量!
# 啟用 logprobs=True, top_logprobs=5 可能增加 10-20% 成本

# 建議: 只在需要時使用
if critical_classification:
    use_logprobs = True
else:
    use_logprobs = False
```

### 4. 溫度設定

```python
# 分類任務: 使用 temperature=0
# 原因: 我們要確定性的結果,不需要創意

get_completion(
    [...],
    temperature=0,  # 每次相同輸入得到相同輸出
    logprobs=True
)
```

---

## ⚠️ 常見陷阱

### 陷阱 1: 忘記啟用 logprobs

```python
# ❌ 錯誤: 設定了 top_logprobs 但沒啟用 logprobs
response = get_completion(
    [...],
    top_logprobs=2  # 這不會生效!
)

# ✅ 正確
response = get_completion(
    [...],
    logprobs=True,      # 必須啟用
    top_logprobs=2
)
```

### 陷阱 2: 提示詞不夠明確

```python
# ❌ 不好的提示詞
prompt = "What category is this headline?"
# 問題: AI 可能回答 "This is a sports headline" (多個 token)

# ✅ 好的提示詞
prompt = "Classify into: Sports, Politics, Art, Business. Output only the category name."
# AI 會回答 "Sports" (單一 token)
```

### 陷阱 3: 誤解機率總和

```python
# ⚠️ 注意: top_logprobs 的機率不一定加總為 100%!

# 如果有 10 個可能的 token,你只看前 2 個:
# Token 1: 60%
# Token 2: 30%
# ... 其他 8 個 token 佔 10%

# 所以 60% + 30% = 90% ≠ 100%
```

---

## 🔍 除錯技巧

### 檢查完整回應結構

```python
import json

response = get_completion(
    [...],
    logprobs=True,
    top_logprobs=2
)

# 印出完整的 JSON 結構
print(json.dumps(response.model_dump(), indent=2))

# 您會看到:
# {
#   "output": [
#     {
#       "content": [
#         {
#           "logprobs": [
#             {
#               "token": "Sports",
#               "logprob": -0.001,
#               "top_logprobs": [...]
#             }
#           ]
#         }
#       ]
#     }
#   ]
# }
```

### 驗證機率計算

```python
def verify_probability_conversion(logprob_value):
    """
    驗證對數機率轉換是否正確
    """
    probability = np.exp(logprob_value)
    back_to_logprob = np.log(probability)
    
    print(f"原始 logprob: {logprob_value}")
    print(f"轉換後機率: {probability * 100:.2f}%")
    print(f"反向轉換: {back_to_logprob}")
    print(f"誤差: {abs(logprob_value - back_to_logprob):.10f}")

# 測試
verify_probability_conversion(-0.5234)
# 輸出:
# 原始 logprob: -0.5234
# 轉換後機率: 59.23%
# 反向轉換: -0.5234
# 誤差: 0.0000000000
```

---

## 📚 總結

### 核心概念

1. **Logprobs = Log(Probability)**
   - 用對數表示機率
   - 負數,越接近 0 越確定

2. **兩個關鍵參數**
   - `logprobs=True`: 啟用
   - `top_logprobs=N`: 看前 N 個選項

3. **三大應用**
   - 判斷信心程度
   - 設定人工介入門檻
   - 提供多個選項

### 實務價值

| 傳統分類 | 使用 Logprobs |
|---------|--------------|
| 只有答案 | 答案 + 信心程度 |
| 無法判斷可靠性 | 可設定信心門檻 |
| 二元決策 (對/錯) | 連續評估 (0-100%) |
| 全人工或全自動 | 混合工作流程 |

### 何時使用 Logprobs?

✅ **應該使用**:
- 關鍵決策需要信心評估
- 需要人機協作工作流程
- 多類別分類任務
- A/B 測試提示詞效果

❌ **不需要使用**:
- 簡單的生成任務
- 創意寫作
- 成本敏感的應用
- 不需要評估信心的場景

---

## 🚀 下一步學習

1. **探索其他 Token 的 Logprobs**
   ```python
   # 如果 AI 輸出多個 token,可以看每個 token 的機率
   for i, logprob_data in enumerate(API_RESPONSE.output[0].content[0].logprobs):
       print(f"Token {i}: {logprob_data.token}")
   ```

2. **結合其他評估指標**
   - Perplexity (困惑度)
   - BLEU Score (文字生成品質)
   - F1 Score (分類準確度)

3. **建立完整的評估管線**
   ```python
   def evaluate_classification_system(test_data):
       results = {
           'auto_classified': 0,
           'needs_review': 0,
           'accuracy': 0
       }
       # ... 評估邏輯
       return results
   ```

4. **進階: 使用 Logprobs 微調提示詞**
   - 比較不同提示詞的平均信心度
   - 選擇信心度最高的提示詞版本

---

## ❓ 常見問題 (FAQ)

### Q1: Logprobs 會增加成本嗎?
**A**: 會稍微增加,因為 API 需要返回更多資訊。通常增加 10-20% 的 token 使用量。

### Q2: 所有模型都支援 Logprobs 嗎?
**A**: 不是。OpenAI 的 GPT 系列支援,但有些第三方模型可能不支援。

### Q3: 可以獲取輸入 Token 的 Logprobs 嗎?
**A**: 某些 API 支援,但通常我們只關注輸出 token 的 logprobs。

### Q4: Logprobs 可以用於檢測幻覺 (Hallucination) 嗎?
**A**: 可以部分幫助。如果 AI 對某個事實陳述的信心很低,可能是在猜測或幻覺。

### Q5: 為什麼有時候機率加總不到 100%?
**A**: 因為 `top_logprobs=N` 只返回前 N 個最可能的 token,還有其他可能的 token 沒顯示。

### Q6: 可以用 Logprobs 來選擇最佳模型嗎?
**A**: 可以! 比較不同模型對同一任務的平均信心度,選擇最確定的模型。

---

## 📖 延伸閱讀

- [OpenAI Cookbook: Using Logprobs](https://cookbook.openai.com/examples/using_logprobs)
- [Understanding Log Probabilities in Language Models](https://huggingface.co/docs/transformers/perplexity)
- [Confidence Calibration in Neural Networks](https://arxiv.org/abs/1706.04599)
- [Best Practices for Classification with LLMs](https://platform.openai.com/docs/guides/classification)

---

**祝您學習愉快! 有任何問題歡迎隨時詢問! 🎉**
