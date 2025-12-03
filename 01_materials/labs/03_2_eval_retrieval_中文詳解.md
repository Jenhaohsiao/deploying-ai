# 評估檢索品質 - 使用 Logprobs 檢測幻覺 詳細教學

## 📚 這個檔案在教什麼?

這個教學會教您如何使用 **logprobs (對數機率)** 來評估 RAG 系統的檢索品質,並防止 AI 產生**幻覺 (Hallucination)** - 也就是編造不存在的資訊!

---

## 🎯 學習目標

1. 了解什麼是 RAG (檢索增強生成)
2. 認識 AI 幻覺問題及其危害
3. 學習如何用 logprobs 評估資訊充分性
4. 實作信心檢測機制
5. 區分「簡單問題」與「困難問題」

---

## 📖 基礎知識補充

### 什麼是 RAG (Retrieval-Augmented Generation)?

**RAG = 檢索增強生成**

**簡單比喻**: 
想像 AI 是一個學生在開卷考試:
1. **檢索 (Retrieval)**: 先從課本找相關資料
2. **增強 (Augmented)**: 用找到的資料來支持答案
3. **生成 (Generation)**: 根據資料寫出答案

```
傳統 AI: 憑記憶回答 (可能記錯或編造)
         ↓
RAG AI:  先查資料 → 根據資料回答 (更可靠)
```

### 什麼是幻覺 (Hallucination)?

**定義**: AI 編造不存在或不正確的資訊

**範例**:

```
❌ 幻覺回答:
問: Ada Lovelace 有沒有跟查爾斯·狄更斯合作?
答: 是的,他們合作創作了一本關於計算機的書。
     ↑ 文章中沒有這個資訊,AI 編造的!

✅ 正確回答:
答: 文章中只提到她認識狄更斯,但沒有提到合作細節。
```

### 為什麼會產生幻覺?

1. **訓練資料限制**: AI 只知道訓練時學到的東西
2. **過度自信**: AI 總是會給答案,即使不確定
3. **檢索失敗**: RAG 沒找到相關資訊,AI 就開始猜
4. **理解錯誤**: 誤解文章內容

### 本教學的解決方案

**核心概念**: 讓 AI 先自我評估「資訊是否充足」

```
流程圖:
問題 → 檢索文章 → AI 自我檢查:「資訊夠嗎?」
                           ↓
                    夠(高信心) → 回答
                           ↓
                    不夠(低信心) → 「我不確定」或「需要更多資訊」
```

---

## 💻 程式碼詳解

### 步驟一: 環境設置

#### 程式碼區塊 1-2: 載入環境

```python
%load_ext dotenv
%dotenv ../../05_src/.secrets
```

**解釋**:
- 載入 OpenAI API 金鑰
- 從 `.secrets` 檔案讀取敏感資訊

---

### 步驟二: 準備測試資料

#### 程式碼區塊 3: Ada Lovelace 文章與測試問題

```python
# 檢索到的文章 (關於 Ada Lovelace)
ada_lovelace_article = """
Augusta Ada King, Countess of Lovelace (née Byron; 10 December 1815 - 27 November 1852) 
was an English mathematician and writer, chiefly known for her work on Charles Babbage's 
proposed mechanical general-purpose computer, the Analytical Engine...
"""
```

**中文翻譯與摘要**:

**Ada Lovelace 生平簡介**:

1. **基本資訊**
   - 全名: Augusta Ada King, Countess of Lovelace
   - 出生: 1815年12月10日
   - 逝世: 1852年11月27日 (享年36歲)
   - 國籍: 英國
   - 職業: 數學家、作家

2. **家庭背景**
   - 父親: 詩人拜倫勳爵 (Lord Byron)
   - 母親: Lady Byron (改革者)
   - 特殊之處: 拜倫唯一的婚生子女
   - 家庭悲劇: 出生一個月後父母分居,父親離開英國,8歲時父親在希臘去世

3. **教育與興趣**
   - 母親擔心她繼承父親的「瘋狂」,刻意培養她對數學和邏輯的興趣
   - 儘管如此,她仍然關心父親,將兩個兒子命名為 Byron 和 Gordon
   - 去世後按她的要求葬在父親旁邊

4. **婚姻**
   - 1835年嫁給 William King
   - 1838年丈夫被封為 Earl of Lovelace,她成為 Countess of Lovelace

5. **科學貢獻**
   - **18歲時**: 與數學家 Charles Babbage (被稱為「計算機之父」) 建立合作關係
   - **1833年6月**: 透過家庭教師 Mary Somerville 認識 Babbage
   - **1842-1843年**: 翻譯義大利工程師 Luigi Menabrea 關於分析引擎的文章
   - **重要貢獻**: 在翻譯中加入詳細的七篇「註釋」(Notes)

6. **歷史地位**
   - **第七篇註釋**: 包含被許多人認為是**第一個電腦程式**的演算法
   - **爭議**: 有些歷史學家認為 Babbage 在1836/1837年的筆記才是第一個程式
   - **遠見**: 認識到計算機的能力超越純粹計算,而 Babbage 本人只專注於計算功能
   - **哲學**: 提出「詩意科學」(poetical science) 的概念
   - **洞察**: 探討人類和社會如何將技術作為協作工具

---

### 測試問題設計

```python
# 簡單問題 (文章中有明確答案)
easy_questions = [
    "What nationality was Ada Lovelace?",
    "What was an important finding from Lovelace's seventh note?",
]

# 中等難度問題 (文章中沒有完整資訊)
medium_questions = [
    "Did Lovelace collaborate with Charles Dickens",
    "What concepts did Lovelace build with Charles Babbage",
]
```

**中文翻譯與分析**:

#### 🟢 簡單問題 (Easy Questions)

**問題 1**: "What nationality was Ada Lovelace?"
- **中文**: Ada Lovelace 是哪國人?
- **答案在文章中**: ✅ 明確提到 "English mathematician"
- **正確答案**: 英國 (English)
- **信心程度**: 應該非常高 (>95%)

**問題 2**: "What was an important finding from Lovelace's seventh note?"
- **中文**: Lovelace 第七篇註釋的重要發現是什麼?
- **答案在文章中**: ✅ "the seventh one contained what many consider to be the first computer program"
- **正確答案**: 第一個電腦程式
- **信心程度**: 應該很高 (>90%)

#### 🟡 中等難度問題 (Medium Questions)

**問題 1**: "Did Lovelace collaborate with Charles Dickens"
- **中文**: Lovelace 有沒有跟查爾斯·狄更斯合作?
- **文章中的資訊**: ⚠️ 只提到 "the author Charles Dickens" 是她的接觸對象
- **問題**: 「接觸」≠「合作」
- **正確態度**: 資訊不足,無法確定
- **信心程度**: 應該較低 (<70%)

**問題 2**: "What concepts did Lovelace build with Charles Babbage"
- **中文**: Lovelace 跟 Charles Babbage 一起建立了什麼概念?
- **文章中的資訊**: ⚠️ 提到她「翻譯文章」、「加註釋」,但沒有明確說「一起建立概念」
- **問題**: 文章沒有直接回答「建立了什麼概念」
- **正確態度**: 資訊不完整
- **信心程度**: 應該中等或較低 (<80%)

**問題設計的巧思**:
- ✅ **對比測試**: 簡單 vs 困難,測試 AI 能否區分
- ✅ **真實場景**: 模擬實際 RAG 應用中的問題
- ✅ **檢測幻覺**: 看 AI 會不會在資訊不足時編造答案

---

### 步驟三: 建立評估函數

#### 程式碼區塊 4-6: OpenAI 客戶端與通用函數

```python
from openai import OpenAI
import numpy as np
client = OpenAI()

def get_completion(
    input: list[dict[str, str]],
    model: str = "gpt-4o-mini",
    max_tokens=500,
    temperature=0,
    tools=None,
    logprobs=None,
    top_logprobs=None,
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

**解釋**: 這是通用的 API 呼叫函數,與上一個教學相同。

---

### 步驟四: 設計評估提示詞

#### 程式碼區塊 7-8: 資訊充分性評估提示詞

```python
PROMPT = """You retrieved this article: {article}. The question is: {question}.
Before even answering the question, consider whether you have sufficient information in the article to answer the question fully.
Your output should JUST be the boolean true or false, of if you have sufficient information in the article to answer the question.
Respond with just one word, the boolean true or false. You must output the word 'True', or the word 'False', nothing else.
"""
```

**中文翻譯與詳解**:

```
您檢索到這篇文章: {article}。問題是: {question}。

在回答問題之前,請先考慮您在文章中是否有充足的資訊來完整回答這個問題。

您的輸出應該只是布林值 true 或 false,表示您在文章中是否有充足的資訊來回答問題。

只用一個字回答,布林值 true 或 false。您必須輸出 'True' 或 'False',不要其他內容。
```

**提示詞設計要點**:

1. **明確任務**
   ```
   "Before even answering the question, consider..."
   → 強調先評估,不要直接回答
   ```

2. **具體標準**
   ```
   "whether you have sufficient information"
   → 判斷標準: 資訊是否充足
   ```

3. **嚴格輸出格式**
   ```
   "Respond with just one word, the boolean true or false"
   → 只能輸出 'True' 或 'False'
   → 方便程式解析
   ```

4. **重複強調**
   ```
   "You must output the word 'True', or the word 'False', nothing else."
   → 再次強調格式,防止 AI 輸出解釋
   ```

**為什麼這樣設計?**

| 元素 | 目的 |
|------|------|
| 提供文章 | 讓 AI 知道可用的資訊範圍 |
| 提供問題 | 明確要評估的目標 |
| 強調「充足」 | 不是部分資訊,要完整資訊 |
| 布林值輸出 | 二元判斷,方便用 logprobs 評估信心 |
| 重複強調格式 | 確保輸出一致性 |

---

### 步驟五: 實作檢測函數

#### 程式碼區塊 9: 資訊充分性檢測函數

```python
def has_sufficient_context_for_answer(article, question):
    output = ""
    
    # 呼叫 API,啟用 logprobs
    API_RESPONSE = get_completion(
        [
            {
                "role": "user",
                "content": PROMPT.format(
                    article=article, 
                    question=question
                ),
            }
        ],
        model="gpt-4o-mini",
        logprobs=True,  # ← 關鍵: 獲取信心程度
    )
    
    # 格式化輸出
    output += f'Question: {question}\n'
    
    # 提取第一個 token 的 logprob
    logprob = API_RESPONSE.output[0].content[0].logprobs[0]
    
    # 計算線性機率
    linear_prob = np.round(np.exp(logprob.logprob) * 100, 2)
    
    output += f'has_sufficient_context_for_answer: {logprob.token}, '
    output += f'logprobs: {logprob.logprob}, '
    output += f'linear probability: {linear_prob}%\n'
    
    return output
```

**逐步解析**:

#### 1. API 呼叫
```python
API_RESPONSE = get_completion(
    [{"role": "user", "content": PROMPT.format(article=article, question=question)}],
    model="gpt-4o-mini",
    logprobs=True,
)
```

**過程**:
- 將文章和問題插入提示詞模板
- 發送給 GPT-4o-mini 模型
- 要求返回 logprobs (信心程度)

#### 2. 提取 Logprob
```python
logprob = API_RESPONSE.output[0].content[0].logprobs[0]
```

**資料結構**:
```
API_RESPONSE
└── output[0]              # 第一個輸出
    └── content[0]         # 第一個內容區塊
        └── logprobs[0]    # 第一個 token 的 logprobs
            ├── token      # "True" 或 "False"
            └── logprob    # 對數機率值
```

#### 3. 計算線性機率
```python
linear_prob = np.round(np.exp(logprob.logprob) * 100, 2)
```

**數學轉換**:
```
logprob = -0.0513  (對數機率)
↓
probability = e^(-0.0513) = 0.95
↓
percentage = 0.95 × 100 = 95%
↓
rounded = 95.00%
```

#### 4. 格式化輸出
```python
output += f'Question: {question}\n'
output += f'has_sufficient_context_for_answer: {logprob.token}, '
output += f'logprobs: {logprob.logprob}, '
output += f'linear probability: {linear_prob}%\n'
```

**輸出範例**:
```
Question: What nationality was Ada Lovelace?
has_sufficient_context_for_answer: True, logprobs: -0.0234, linear probability: 97.69%
```

---

### 步驟六: 執行測試

#### 程式碼區塊 10-11: 測試簡單問題

```python
# 簡單問題
for qn in easy_questions:
    output = has_sufficient_context_for_answer(ada_lovelace_article, qn)
    print(output)
```

**預期輸出**:

```
Question: What nationality was Ada Lovelace?
has_sufficient_context_for_answer: True, logprobs: -0.0234, linear probability: 97.69%

Question: What was an important finding from Lovelace's seventh note?
has_sufficient_context_for_answer: True, logprobs: -0.0512, linear probability: 95.01%
```

**分析**:

| 問題 | AI 判斷 | 信心程度 | 解讀 |
|------|---------|----------|------|
| Ada 國籍? | True | 97.69% | ✅ 非常確定資訊充足 |
| 第七篇註釋發現? | True | 95.01% | ✅ 確定資訊充足 |

**為什麼信心這麼高?**
1. 文章中有明確、直接的答案
2. 不需要推理或解釋
3. 資訊完整無歧義

---

#### 程式碼區塊 12-13: 測試中等難度問題

```python
# 中等難度問題
for qn in medium_questions:
    output = has_sufficient_context_for_answer(ada_lovelace_article, qn)
    print(output)
```

**預期輸出**:

```
Question: Did Lovelace collaborate with Charles Dickens
has_sufficient_context_for_answer: False, logprobs: -0.3567, linear probability: 70.02%

Question: What concepts did Lovelace build with Charles Babbage
has_sufficient_context_for_answer: False, logprobs: -0.8945, linear probability: 40.88%
```

**分析**:

| 問題 | AI 判斷 | 信心程度 | 解讀 |
|------|---------|----------|------|
| 跟狄更斯合作? | False | 70.02% | ⚠️ 中等信心,資訊不足 |
| 跟 Babbage 建立概念? | False | 40.88% | ⚠️ 低信心,很不確定 |

**深入解讀**:

### 問題 1: "Did Lovelace collaborate with Charles Dickens"

**文章內容**:
> "contacts which she used to further her education, including the author Charles Dickens"

**分析**:
- ✅ 文章提到: 她認識狄更斯 (contact)
- ❌ 文章沒說: 他們是否合作 (collaborate)
- 🤔 "認識" ≠ "合作"
- **AI 判斷**: False (70% 信心)
- **正確**: ✅ AI 正確判斷資訊不足

### 問題 2: "What concepts did Lovelace build with Charles Babbage"

**文章內容**:
> "a long working relationship and friendship with Charles Babbage"
> "Ada translated an article... supplementing it with notes"

**分析**:
- ✅ 文章提到: 長期工作關係、翻譯文章、加註釋
- ❌ 文章沒說: 他們「一起建立」了哪些「概念」
- 🤔 文章描述她的工作,但沒有明確說「共同建立概念」
- **AI 判斷**: False (40.88% 信心)
- **注意**: 信心很低 (40.88%),表示 AI 也很猶豫!

**為什麼第二題信心更低?**
1. **更模糊**: "build concepts" 是抽象概念
2. **需要推理**: 需要從多處資訊綜合判斷
3. **邊界不清**: 什麼算「建立概念」?翻譯算不算?

---

## 🎯 實際應用場景

### 場景 1: RAG 問答系統的安全閥

```python
def safe_rag_answer(article, question, confidence_threshold=85):
    """
    安全的 RAG 問答系統,只在有充足資訊時回答
    """
    # 步驟 1: 檢查資訊充分性
    check_response = get_completion(
        [{"role": "user", "content": PROMPT.format(article=article, question=question)}],
        model="gpt-4o-mini",
        logprobs=True,
    )
    
    logprob = check_response.output[0].content[0].logprobs[0]
    confidence = np.exp(logprob.logprob) * 100
    has_info = logprob.token
    
    print(f"📊 資訊充分性檢查:")
    print(f"   判斷: {has_info}")
    print(f"   信心: {confidence:.2f}%\n")
    
    # 步驟 2: 根據信心決定是否回答
    if has_info == "True" and confidence >= confidence_threshold:
        # 信心足夠,回答問題
        print("✅ 資訊充足,生成答案...\n")
        answer_response = get_completion(
            [{"role": "user", "content": f"Based on this article: {article}\n\nAnswer: {question}"}],
            model="gpt-4o-mini",
        )
        return answer_response.output_text
    else:
        # 信心不足,拒絕回答
        print("⚠️ 資訊不足,無法可靠回答\n")
        return "I don't have sufficient information in the provided article to answer this question confidently."

# 使用範例
print("=" * 60)
print("問題 1: What nationality was Ada Lovelace?")
print("=" * 60)
answer1 = safe_rag_answer(ada_lovelace_article, "What nationality was Ada Lovelace?")
print(f"答案: {answer1}\n")

print("=" * 60)
print("問題 2: Did Lovelace collaborate with Charles Dickens?")
print("=" * 60)
answer2 = safe_rag_answer(ada_lovelace_article, "Did Lovelace collaborate with Charles Dickens?")
print(f"答案: {answer2}\n")
```

**預期輸出**:

```
============================================================
問題 1: What nationality was Ada Lovelace?
============================================================
📊 資訊充分性檢查:
   判斷: True
   信心: 97.69%

✅ 資訊充足,生成答案...

答案: Ada Lovelace was English.

============================================================
問題 2: Did Lovelace collaborate with Charles Dickens?
============================================================
📊 資訊充分性檢查:
   判斷: False
   信心: 70.02%

⚠️ 資訊不足,無法可靠回答

答案: I don't have sufficient information in the provided article to answer this question confidently.
```

**優勢**:
- ✅ **防止幻覺**: 不會編造答案
- ✅ **透明度**: 明確告訴使用者為什麼不回答
- ✅ **可調整**: 可以調整 `confidence_threshold`

---

### 場景 2: 多文章檢索品質評估

```python
def evaluate_retrieval_quality(articles, question, min_confidence=80):
    """
    評估多個檢索到的文章,找出最有用的
    """
    print(f"🔍 評估問題: {question}\n")
    print(f"檢索到 {len(articles)} 篇文章\n")
    
    results = []
    
    for i, article in enumerate(articles, 1):
        response = get_completion(
            [{"role": "user", "content": PROMPT.format(article=article, question=question)}],
            model="gpt-4o-mini",
            logprobs=True,
        )
        
        logprob = response.output[0].content[0].logprobs[0]
        confidence = np.exp(logprob.logprob) * 100
        has_info = logprob.token
        
        results.append({
            'article_num': i,
            'has_info': has_info,
            'confidence': confidence,
            'article': article[:100] + "..."  # 只顯示前 100 字元
        })
        
        print(f"文章 {i}:")
        print(f"  有充足資訊: {has_info}")
        print(f"  信心程度: {confidence:.2f}%")
        print(f"  內容預覽: {article[:80]}...")
        print()
    
    # 找出最有用的文章
    useful_articles = [r for r in results if r['has_info'] == 'True' and r['confidence'] >= min_confidence]
    
    if useful_articles:
        best = max(useful_articles, key=lambda x: x['confidence'])
        print(f"✅ 最佳文章: 文章 {best['article_num']} (信心: {best['confidence']:.2f}%)")
        return best['article_num']
    else:
        print(f"⚠️ 沒有找到信心 ≥ {min_confidence}% 的有用文章")
        return None

# 使用範例
articles = [
    "Ada Lovelace was a British mathematician...",
    "Charles Babbage invented the Analytical Engine...",
    ada_lovelace_article,
]

best_article = evaluate_retrieval_quality(
    articles, 
    "What nationality was Ada Lovelace?",
    min_confidence=80
)
```

**用途**:
- 從多個檢索結果中挑選最相關的
- 評估檢索系統的品質
- 決定是否需要再檢索更多文章

---

### 場景 3: 信心分級回應系統

```python
def graded_confidence_answer(article, question):
    """
    根據信心程度提供不同等級的回應
    """
    # 檢查資訊充分性
    check_response = get_completion(
        [{"role": "user", "content": PROMPT.format(article=article, question=question)}],
        model="gpt-4o-mini",
        logprobs=True,
    )
    
    logprob = check_response.output[0].content[0].logprobs[0]
    confidence = np.exp(logprob.logprob) * 100
    has_info = logprob.token
    
    # 生成答案
    answer_response = get_completion(
        [{"role": "user", "content": f"Based on this article: {article}\n\nAnswer: {question}"}],
        model="gpt-4o-mini",
    )
    answer = answer_response.output_text
    
    # 根據信心程度添加不同的前綴
    if has_info == "True" and confidence >= 95:
        prefix = "✅ [高信心] "
        note = ""
    elif has_info == "True" and confidence >= 80:
        prefix = "✓ [中等信心] "
        note = "\n💡 提示: 答案基於文章資訊,但可能不完整。"
    elif has_info == "False" and confidence >= 70:
        prefix = "⚠️ [低信心] "
        note = "\n⚠️ 警告: 文章中資訊可能不足,以下答案僅供參考。"
    else:
        prefix = "❌ [極低信心] "
        note = "\n❌ 重要: 文章中沒有充足資訊,建議不要依賴此答案。"
    
    print(f"問題: {question}")
    print(f"信心評估: {has_info} ({confidence:.2f}%)\n")
    print(f"{prefix}{answer}{note}")
    print("\n" + "=" * 60 + "\n")

# 測試所有問題
all_questions = easy_questions + medium_questions

for q in all_questions:
    graded_confidence_answer(ada_lovelace_article, q)
```

**輸出範例**:

```
問題: What nationality was Ada Lovelace?
信心評估: True (97.69%)

✅ [高信心] Ada Lovelace was English.

============================================================

問題: Did Lovelace collaborate with Charles Dickens
信心評估: False (70.02%)

⚠️ [低信心] The article mentions that Charles Dickens was among her contacts, but doesn't specify if they collaborated.
⚠️ 警告: 文章中資訊可能不足,以下答案僅供參考。

============================================================
```

---

## 📊 信心程度解讀指南

### 信心等級分類

| 信心範圍 | 等級 | 建議行動 | 圖示 |
|---------|------|---------|------|
| 95-100% | 極高 | 直接使用答案 | ✅ |
| 85-94% | 高 | 可使用,但標注來源 | ✓ |
| 70-84% | 中等 | 需要人工審核 | ⚠️ |
| 50-69% | 低 | 需要補充資訊 | 🔍 |
| 0-49% | 極低 | 不建議使用 | ❌ |

### 決策樹

```
獲取 logprob 信心分數
    ↓
信心 ≥ 95%? ── 是 → 直接回答
    ↓ 否
信心 ≥ 85%? ── 是 → 回答 + 標注不確定性
    ↓ 否
信心 ≥ 70%? ── 是 → 提供答案 + 強烈警告
    ↓ 否
信心 < 70% ── → 拒絕回答或觸發再檢索
```

---

## 🔬 深入理解: 為什麼 Logprobs 能檢測資訊充分性?

### 理論基礎

**核心概念**: AI 在輸出 "True" 或 "False" 時的信心程度,反映了它對判斷的確定性。

**數學解釋**:

```
P(True | 文章包含充足資訊) ≈ 高機率 (如 0.95)
P(True | 文章資訊不足) ≈ 低機率 (如 0.60)
```

### 實驗觀察

**簡單問題** (文章有明確答案):
```python
Question: What nationality was Ada Lovelace?
Article: "was an English mathematician..."
         ↓
AI 判斷: True
Logprob: -0.0234
Confidence: 97.69%
         ↓
解讀: AI 在文章中看到 "English",非常確定資訊充足
```

**困難問題** (文章資訊模糊):
```python
Question: Did Lovelace collaborate with Charles Dickens?
Article: "contacts... including the author Charles Dickens"
         ↓
AI 判斷: False
Logprob: -0.3567
Confidence: 70.02%
         ↓
解讀: AI 看到 "contacts" 但不確定是否等於 "collaborate"
      信心程度降低
```

### 視覺化信心分布

```
高信心 True (資訊充足)
████████████████████████████████████████ 97.69%
簡單問題: Ada 的國籍?

中等信心 False (資訊不足)
████████████████████████████ 70.02%
中等問題: 是否跟狄更斯合作?

低信心 False (資訊嚴重不足)
████████████████ 40.88%
困難問題: 跟 Babbage 建立了什麼概念?
```

---

## 💡 最佳實踐建議

### 1. 提示詞設計

**✅ 好的提示詞**:
```python
"You must output ONLY 'True' or 'False'"
→ 明確、嚴格的格式要求
```

**❌ 不好的提示詞**:
```python
"Do you think you can answer this?"
→ 模糊,可能得到 "maybe", "probably" 等回答
```

### 2. 信心門檻設定

**保守策略** (高品質優先):
```python
confidence_threshold = 90  # 只有 >90% 才回答
→ 適合: 醫療、法律等高風險領域
```

**平衡策略** (品質與覆蓋率平衡):
```python
confidence_threshold = 80  # >80% 回答,其他人工
→ 適合: 一般客服、知識問答
```

**激進策略** (覆蓋率優先):
```python
confidence_threshold = 70  # >70% 就回答
→ 適合: 低風險應用,如娛樂內容
```

### 3. 多層檢查機制

```python
def robust_rag_answer(article, question):
    # 第一層: 資訊充分性檢查
    has_info, info_confidence = check_has_sufficient_info(article, question)
    
    if not has_info or info_confidence < 80:
        return "資訊不足"
    
    # 第二層: 生成答案
    answer = generate_answer(article, question)
    
    # 第三層: 答案品質檢查 (可選)
    answer_quality = check_answer_quality(answer, article)
    
    if answer_quality < 70:
        return "答案品質不佳,需人工檢查"
    
    return answer
```

### 4. 日誌記錄

```python
import logging

def log_confidence_check(question, has_info, confidence):
    logging.info(f"Question: {question}")
    logging.info(f"Has sufficient info: {has_info}")
    logging.info(f"Confidence: {confidence:.2f}%")
    
    if confidence < 80:
        logging.warning(f"Low confidence detected: {confidence:.2f}%")
```

**用途**:
- 追蹤系統表現
- 發現問題模式
- 持續改進

---

## ⚠️ 常見陷阱與解決方案

### 陷阱 1: 過度依賴單一檢查

**問題**:
```python
# ❌ 只檢查一次
if has_info == "True":
    return answer  # 可能還是會幻覺!
```

**解決**:
```python
# ✅ 多重檢查
if has_info == "True" and confidence >= 85:
    # 再檢查答案與文章的一致性
    if verify_answer_consistency(answer, article):
        return answer
```

### 陷阱 2: 忽略邊界案例

**問題**:
```python
# ❌ 二元判斷
if confidence > 50:
    use_answer = True
else:
    use_answer = False
```

**解決**:
```python
# ✅ 分級處理
if confidence >= 90:
    return ("high_confidence", answer)
elif confidence >= 75:
    return ("medium_confidence", answer + " [需驗證]")
elif confidence >= 60:
    return ("low_confidence", "資訊可能不足")
else:
    return ("no_confidence", "無法回答")
```

### 陷阱 3: 沒有人工反饋迴路

**問題**:
```python
# ❌ 完全自動化,沒有學習機制
answer = auto_answer(question)
return answer
```

**解決**:
```python
# ✅ 加入人工反饋
answer, confidence = auto_answer_with_confidence(question)

if confidence < 85:
    # 標記需人工審核
    mark_for_human_review(question, answer, confidence)
    
    # 收集人工反饋
    human_feedback = get_human_feedback(question, answer)
    
    # 用於改進系統
    store_feedback_for_training(question, answer, human_feedback)
```

---

## 🎓 總結

### 核心概念

1. **RAG 系統的挑戰**
   - 檢索可能不完整
   - AI 可能產生幻覺
   - 需要評估資訊充分性

2. **Logprobs 的作用**
   - 評估 AI 的信心程度
   - 檢測資訊是否充足
   - 防止幻覺產生

3. **實務應用**
   - 設定信心門檻
   - 分級回應系統
   - 多文章品質評估

### 關鍵技術

| 技術 | 用途 | 範例 |
|------|------|------|
| 資訊充分性提示詞 | 讓 AI 評估資訊 | "Do you have sufficient information?" |
| Logprobs 信心分數 | 量化 AI 確定性 | 97.69% vs 40.88% |
| 信心門檻 | 決策邊界 | >85% 自動,<85% 人工 |
| 分級回應 | 透明化不確定性 | 高/中/低信心標籤 |

### 價值主張

| 傳統 RAG | 加入 Logprobs 檢測 |
|---------|-------------------|
| 總是回答 | 評估後再決定 |
| 可能幻覺 | 主動檢測風險 |
| 品質不確定 | 量化信心程度 |
| 全自動或全人工 | 智能分流 |

---

## 🚀 下一步學習

### 1. 擴展檢測維度

```python
# 不只檢查「是否有資訊」,還檢查:
- "Is the information relevant?"  # 相關性
- "Is the information recent?"    # 時效性
- "Is the information consistent?" # 一致性
```

### 2. 結合其他評估指標

- **語義相似度**: 答案與文章的相似度
- **事實性檢查**: 與外部知識庫比對
- **引用追蹤**: 答案的每個部分是否都有來源

### 3. 建立評估資料集

```python
# 建立測試集
test_cases = [
    {
        'article': "...",
        'question': "...",
        'expected_has_info': True,
        'expected_confidence_range': (90, 100)
    },
    # ... 更多測試案例
]

# 自動化評估
def evaluate_system(test_cases):
    for case in test_cases:
        result = has_sufficient_context_for_answer(
            case['article'], 
            case['question']
        )
        # 比對預期結果
        assert result.has_info == case['expected_has_info']
```

### 4. 進階: 主動學習

當 AI 不確定時,觸發主動學習:
1. 標記低信心案例
2. 收集人工標註
3. 微調模型或提示詞
4. 持續改進

---

## ❓ 常見問題 (FAQ)

### Q1: 為什麼不直接讓 AI 回答,然後檢查答案的 logprobs?
**A**: 
- **問題**: 生成式答案可能有很多 token,每個 token 的 logprobs 不同
- **解決**: 先用簡單的 True/False 判斷,只需要看一個 token
- **優勢**: 更清晰、更容易解釋

### Q2: Logprobs 信心低就一定代表資訊不足嗎?
**A**: 不一定,也可能是:
- 問題本身模糊
- 提示詞設計不當
- 模型能力限制
- 建議: 結合多種信號判斷

### Q3: 如何處理「部分資訊」的情況?
**A**: 
```python
# 選項 1: 嚴格標準 (全或無)
"Do you have COMPLETE information?"

# 選項 2: 分級標準
"Rate the completeness: Complete/Partial/Insufficient"
```

### Q4: 這個方法適用於所有類型的問題嗎?
**A**: 最適合:
- ✅ 事實性問題 (國籍、日期等)
- ✅ 明確的資訊查詢

不太適合:
- ❌ 開放式問題
- ❌ 需要推理的問題
- ❌ 創意性任務

### Q5: 成本如何?
**A**: 每個問題需要 2 次 API 呼叫:
1. 資訊充分性檢查
2. 實際回答 (如果通過檢查)

建議: 可以批次處理降低成本

### Q6: 如何與現有 RAG 系統整合?
**A**: 
```python
# 現有 RAG
def rag(question):
    articles = retrieve(question)
    answer = generate(articles, question)
    return answer

# 加入 logprobs 檢查
def safe_rag(question):
    articles = retrieve(question)
    
    # 新增: 檢查資訊充分性
    for article in articles:
        if check_sufficient_info(article, question):
            return generate(article, question)
    
    return "資訊不足,無法回答"
```

---

## 📖 延伸閱讀

- [RAG 系統最佳實踐](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Detecting Hallucinations in LLMs](https://arxiv.org/abs/2305.14251)
- [Confidence Estimation in Neural Networks](https://arxiv.org/abs/1706.04599)
- [OpenAI Cookbook: Using Logprobs](https://cookbook.openai.com/examples/using_logprobs)

---

**祝您學習愉快! 有任何問題歡迎隨時詢問! 🎉**
