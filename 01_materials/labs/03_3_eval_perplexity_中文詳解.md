# 評估模型輸出 - 困惑度 (Perplexity) 詳細教學

## 📚 這個檔案在教什麼?

這個教學會教您如何使用 **困惑度 (Perplexity)** 來評估 AI 模型的信心程度。想像 AI 在回答問題時,困惑度就像是「結巴程度」- 越不結巴(困惑度越低),表示 AI 越有信心!

---

## 🎯 學習目標

1. 了解什麼是困惑度 (Perplexity)
2. 學習困惑度的數學計算方法
3. 使用困惑度評估單次模型輸出
4. 比較不同問題的模型信心程度
5. 理解困惑度與準確度的關係

---

## 📖 基礎知識補充

### 什麼是困惑度 (Perplexity)?

**定義**: 困惑度是衡量 AI 模型「不確定性」或「驚訝程度」的指標。

**生活化比喻**:

想像您在玩「接龍遊戲」:

```
情境 1: 高信心 (低困惑度)
問: 「太陽從東邊____」
AI 心想: 「一定是『升起』!」(非常確定)
困惑度: 1.05 (幾乎不困惑)

情境 2: 低信心 (高困惑度)
問: 「薛丁格的貓是活的還是死的?」
AI 心想: 「呃...這個...可能是...嗯...」(很困惑)
困惑度: 15.3 (非常困惑)
```

### 困惑度的直觀理解

**想像 AI 在做選擇題**:

```
低困惑度 (Perplexity ≈ 1-2):
選項: A(95%) B(3%) C(1%) D(1%)
→ AI 非常確定選 A

中困惑度 (Perplexity ≈ 5-10):
選項: A(40%) B(30%) C(20%) D(10%)
→ AI 有點猶豫

高困惑度 (Perplexity ≈ 20+):
選項: A(25%) B(25%) C(25%) D(25%)
→ AI 完全不知道選哪個
```

### 數學定義

**公式**:
```
Perplexity = exp(-平均(logprobs))
         = e^(-(logprob₁ + logprob₂ + ... + logprob_n) / n)
```

**詳細拆解**:

**步驟 1**: 獲取每個 token 的 logprob
```python
tokens:   ["Yes",  ",",   " it",  " has"]
logprobs: [-0.1,  -0.05, -0.2,  -0.15]
```

**步驟 2**: 計算平均值
```python
平均 logprob = (-0.1 + -0.05 + -0.2 + -0.15) / 4
            = -0.5 / 4
            = -0.125
```

**步驟 3**: 取負號
```python
-平均 logprob = -(-0.125) = 0.125
```

**步驟 4**: 指數運算
```python
Perplexity = e^0.125 = 1.133
```

**解讀**: 困惑度 1.133 表示 AI 非常有信心!

---

## 🔢 困惑度數值解讀表

| 困惑度範圍 | 信心程度 | 含義 | 比喻 |
|-----------|---------|------|------|
| 1.0 - 1.5 | 極高信心 | AI 幾乎確定答案 | 「1+1=?」的確定性 |
| 1.5 - 3.0 | 高信心 | AI 很確定答案 | 「台灣的首都是?」 |
| 3.0 - 5.0 | 中等信心 | AI 有點把握 | 「這部電影好看嗎?」 |
| 5.0 - 10.0 | 低信心 | AI 不太確定 | 「明天會下雨嗎?」 |
| 10.0 - 20.0 | 很低信心 | AI 很不確定 | 「樂透號碼是?」 |
| 20.0+ | 極低信心 | AI 完全困惑 | 「薛丁格的貓活著嗎?」 |

---

## 💡 困惑度 vs Logprobs 的關係

### Logprobs (對數機率)
- **範圍**: 負無窮大 到 0
- **越接近 0**: 越確定
- **例子**: -0.01 (99%確定), -3.0 (5%確定)

### Perplexity (困惑度)
- **範圍**: 1 到 正無窮大
- **越接近 1**: 越確定
- **例子**: 1.01 (很確定), 20.0 (很困惑)

### 轉換關係

```python
# Logprobs → Perplexity
logprobs = [-0.1, -0.05, -0.2, -0.15]
perplexity = np.exp(-np.mean(logprobs))

# 理解轉換
平均 logprob = -0.125  (負數,越接近 0 越好)
    ↓ 取負號
0.125               (正數)
    ↓ 指數運算
e^0.125 = 1.133     (困惑度,越接近 1 越好)
```

**視覺化**:

```
Logprobs (越接近 0 越好)          Perplexity (越接近 1 越好)
-6  -5  -4  -3  -2  -1   0   →   403 148  55  20  7.4 2.7  1
 ↑                        ↑        ↑                        ↑
很不確定                很確定    很困惑                很有信心
```

---

## 💻 程式碼詳解

### 步驟一: 環境設置

#### 程式碼區塊 1-3: 載入環境與初始化

```python
# 載入環境變數
%load_ext dotenv
%dotenv ../../05_src/.secrets

# 匯入套件
from openai import OpenAI
import numpy as np

# 創建客戶端
client = OpenAI()
```

**解釋**: 標準設置,與之前教學相同。

---

### 步驟二: 準備測試問題

#### 程式碼區塊 4: 不同類型的問題

```python
prompts = [
    "In a short sentence, has artifical intelligence grown in the last decade?",
    "In a short sentence, is Schrödinger's cat alive?",
    "In a single word, yes or no, is Schrodinger's cat alive?",
    "In a short sentence, what is the capital of Nuevo Leon?",
    "Can you make an omelette without breaking eggs?",
]
```

**中文翻譯與分析**:

#### 🟢 問題 1: "In a short sentence, has artificial intelligence grown in the last decade?"
**中文**: 用一句話回答,人工智慧在過去十年有成長嗎?

**特性**:
- ✅ **事實性問題**: 有明確的答案
- ✅ **廣為人知**: 訓練資料中有大量相關資訊
- 📊 **預期困惑度**: 低 (1.5-3.0)
- 💡 **預期答案**: "Yes, artificial intelligence has grown significantly in the last decade."

**為什麼困惑度低?**
- AI 對這個主題非常熟悉
- 答案幾乎是共識
- 每個詞都很確定

---

#### 🔴 問題 2: "In a short sentence, is Schrödinger's cat alive?"
**中文**: 用一句話回答,薛丁格的貓是活的嗎?

**特性**:
- ⚠️ **哲學悖論**: 沒有確定答案
- 🤔 **量子力學思想實驗**: 貓同時是活的和死的
- 📊 **預期困惑度**: 高 (10.0-20.0+)
- 💡 **預期答案**: "According to quantum mechanics, it is both alive and dead until observed." (模糊的回答)

**薛丁格的貓 (Schrödinger's Cat) 背景**:
```
思想實驗:
1. 貓被放在密封箱子裡
2. 箱子裡有放射性物質,50% 機率衰變
3. 如果衰變,毒氣釋放,貓死亡
4. 在打開箱子觀察之前,貓處於「既活又死」的疊加狀態
5. 只有觀察時,狀態才會「塌縮」成活或死

結論: 沒有明確答案!
```

**為什麼困惑度高?**
- 問題本身就沒有確定答案
- AI 需要在多種回答方式中選擇
- 每個詞都不太確定該怎麼說

---

#### 🟡 問題 3: "In a single word, yes or no, is Schrodinger's cat alive?"
**中文**: 用一個字,yes 或 no,薛丁格的貓是活的嗎?

**特性**:
- 🎯 **強制二選一**: 只能回答 yes 或 no
- 🤔 **但本質上沒答案**: 問題仍然是悖論
- 📊 **預期困惑度**: 非常高 (15.0-25.0+)
- 💡 **預期答案**: "No" 或 "Yes" (但 AI 會非常猶豫)

**為什麼困惑度更高?**
- 限制只能說一個字,但問題本質上無解
- AI 在 "Yes" 和 "No" 之間的機率可能接近 50/50
- 這是最困難的問題類型

---

#### 🟢 問題 4: "In a short sentence, what is the capital of Nuevo Leon?"
**中文**: 用一句話回答,Nuevo León 的首府是什麼?

**背景知識**:
- **Nuevo León**: 墨西哥的一個州
- **首府**: Monterrey (蒙特雷)

**特性**:
- ✅ **事實性問題**: 有明確答案
- 📊 **預期困惑度**: 低-中 (2.0-5.0)
- 💡 **預期答案**: "The capital of Nuevo León is Monterrey."

**為什麼困惑度中等?**
- 答案確定 (Monterrey)
- 但相對冷門,訓練資料可能較少
- 可能在 "Monterrey" 這個詞上稍微猶豫

---

#### 🟡 問題 5: "Can you make an omelette without breaking eggs?"
**中文**: 你能在不打破雞蛋的情況下做煎蛋嗎?

**特性**:
- 🎭 **慣用語/諺語**: "You can't make an omelette without breaking eggs"
- 📊 **預期困惑度**: 低-中 (2.0-4.0)
- 💡 **預期答案**: "No, you can't make an omelette without breaking eggs."

**為什麼設計這個問題?**
- 測試 AI 對常見諺語的理解
- 看 AI 會不會直接回答 "No",還是解釋原因
- 預期信心會相對高

---

### 問題設計的巧思

| 問題類型 | 代表問題 | 預期困惑度 | 測試目的 |
|---------|---------|-----------|---------|
| 確定事實 | AI 成長了嗎? | 低 | 基準線 |
| 哲學悖論 | 薛丁格的貓? | 高 | 測試不確定性 |
| 強制選擇悖論 | 貓活著嗎(yes/no)? | 極高 | 測試極限困惑 |
| 相對冷門事實 | Nuevo León 首府? | 中 | 測試知識廣度 |
| 諺語/常識 | 不打破雞蛋做煎蛋? | 低-中 | 測試常識理解 |

---

### 步驟三: 通用完成函數

#### 程式碼區塊 5: get_completion 函數

```python
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

**解釋**: 與前面教學相同的通用函數。

---

### 步驟四: 計算困惑度

#### 程式碼區塊 6: 主要邏輯

```python
for prompt in prompts:
    # 1. 取得 API 回應 (包含 logprobs)
    API_RESPONSE = get_completion(
        [{"role": "user", "content": prompt}],
        model="gpt-4o-mini",
        logprobs=True,  # ← 關鍵: 獲取 logprobs
    )
    
    # 2. 提取所有 token 的 logprobs
    logprobs = [token.logprob for token in API_RESPONSE.output[0].content[0].logprobs]
    
    # 3. 提取回應文字
    response_text = API_RESPONSE.output[0].content[0].text
    
    # 4. 提取所有 token
    response_text_tokens = [token.token for token in API_RESPONSE.output[0].content[0].logprobs]
    
    # 5. 格式化輸出 (計算對齊)
    max_starter_length = max(len(s) for s in ["Prompt:", "Response:", "Tokens:", "Logprobs:", "Perplexity:"])
    max_token_length = max(len(s) for s in response_text_tokens)
    
    formatted_response_tokens = [s.rjust(max_token_length) for s in response_text_tokens]
    formatted_lps = [f"{lp:.2f}".rjust(max_token_length) for lp in logprobs]

    # 6. 計算困惑度 ★★★ 核心公式 ★★★
    perplexity_score = np.exp(-np.mean(logprobs))
    
    # 7. 印出結果
    print("Prompt:".ljust(max_starter_length), prompt)
    print("Response:".ljust(max_starter_length), response_text, "\n")
    print("Tokens:".ljust(max_starter_length), " ".join(formatted_response_tokens))
    print("Logprobs:".ljust(max_starter_length), " ".join(formatted_lps))
    print("Perplexity:".ljust(max_starter_length), perplexity_score, "\n")
```

**逐步拆解**:

#### 1. 獲取 API 回應
```python
API_RESPONSE = get_completion(
    [{"role": "user", "content": prompt}],
    model="gpt-4o-mini",
    logprobs=True,
)
```

**過程**:
- 發送問題到 GPT-4o-mini
- 要求返回 logprobs
- 獲得完整回應物件

---

#### 2. 提取 Logprobs
```python
logprobs = [token.logprob for token in API_RESPONSE.output[0].content[0].logprobs]
```

**範例**:
```python
# 假設 AI 回答: "Yes, it has."
tokens:   ["Yes",  ",",   " it",  " has",  "."]
logprobs: [-0.05, -0.01, -0.10, -0.08,  -0.02]
```

**資料結構**:
```
API_RESPONSE
└── output[0]
    └── content[0]
        └── logprobs  # 列表,包含每個 token 的資訊
            ├── [0]
            │   ├── token: "Yes"
            │   └── logprob: -0.05
            ├── [1]
            │   ├── token: ","
            │   └── logprob: -0.01
            └── ...
```

---

#### 3-4. 提取文字和 Token
```python
response_text = API_RESPONSE.output[0].content[0].text
# → "Yes, it has."

response_text_tokens = [token.token for token in API_RESPONSE.output[0].content[0].logprobs]
# → ["Yes", ",", " it", " has", "."]
```

**為什麼需要 tokens?**
- 為了顯示每個 token 對應的 logprob
- 幫助理解 AI 在哪些詞上更確定/不確定

---

#### 5. 格式化輸出 (美化顯示)
```python
max_starter_length = max(len(s) for s in ["Prompt:", "Response:", "Tokens:", "Logprobs:", "Perplexity:"])
# → 11 (因為 "Perplexity:" 最長)

max_token_length = max(len(s) for s in response_text_tokens)
# → 如果最長的 token 是 " has" (4 字元),則為 4

formatted_response_tokens = [s.rjust(max_token_length) for s in response_text_tokens]
# → [" Yes", "   ,", "  it", " has", "   ."]
#    (右對齊,方便閱讀)

formatted_lps = [f"{lp:.2f}".rjust(max_token_length) for lp in logprobs]
# → ["-0.05", "-0.01", "-0.10", "-0.08", "-0.02"]
#    (格式化為兩位小數,右對齊)
```

**為什麼要格式化?**
- 讓輸出對齊,容易閱讀
- Token 和 logprob 垂直對應

---

#### 6. 計算困惑度 ★ 核心公式 ★

```python
perplexity_score = np.exp(-np.mean(logprobs))
```

**詳細步驟**:

**假設 logprobs**:
```python
logprobs = [-0.05, -0.01, -0.10, -0.08, -0.02]
```

**步驟 1: 計算平均**
```python
mean_logprob = np.mean(logprobs)
             = (-0.05 + -0.01 + -0.10 + -0.08 + -0.02) / 5
             = -0.26 / 5
             = -0.052
```

**步驟 2: 取負號**
```python
-mean_logprob = -(-0.052) = 0.052
```

**步驟 3: 指數運算**
```python
perplexity = np.exp(0.052)
          = e^0.052
          = 1.0533
```

**結果**: 困惑度 = **1.0533** (非常低,表示高信心!)

---

#### 7. 印出結果

```python
print("Prompt:".ljust(max_starter_length), prompt)
print("Response:".ljust(max_starter_length), response_text, "\n")
print("Tokens:".ljust(max_starter_length), " ".join(formatted_response_tokens))
print("Logprobs:".ljust(max_starter_length), " ".join(formatted_lps))
print("Perplexity:".ljust(max_starter_length), perplexity_score, "\n")
```

**輸出範例**:
```
Prompt:      In a short sentence, has artificial intelligence grown in the last decade?
Response:    Yes, it has grown significantly.

Tokens:         Yes      ,     it    has  grown  significantly      .
Logprobs:     -0.05  -0.01  -0.10  -0.08  -0.15       -0.20  -0.02
Perplexity:  1.0642
```

**解讀**:
- **Token-by-Token 分析**: 可以看到每個詞的確定程度
- **最確定的**: "," (逗號) 只有 -0.01,幾乎確定
- **最不確定的**: "significantly" 有 -0.20,相對不確定
- **整體困惑度**: 1.0642,表示 AI 很有信心

---

## 📊 預期輸出與分析

### 問題 1: AI 成長了嗎?

**輸出範例**:
```
Prompt:      In a short sentence, has artificial intelligence grown in the last decade?
Response:    Yes, artificial intelligence has grown significantly in the last decade.

Tokens:       Yes      ,  artificial  intelligence    has  grown  significantly     in    the   last  decade      .
Logprobs:   -0.03  -0.01       -0.08         -0.05  -0.04  -0.06        -0.15  -0.02  -0.01  -0.03   -0.04  -0.01
Perplexity:  1.054

```

**分析**:
- 🟢 **困惑度 1.054**: 極低,AI 非常確定
- 📊 **最確定的詞**: "," "-0.01", "the" "-0.01" (常見詞)
- 📊 **相對不確定**: "significantly" "-0.15" (有其他選擇如 "greatly", "substantially")
- ✅ **結論**: AI 對這個事實問題很有信心

---

### 問題 2: 薛丁格的貓 (長句回答)

**輸出範例**:
```
Prompt:      In a short sentence, is Schrödinger's cat alive?
Response:    According to the thought experiment, it is both alive and dead until observed.

Tokens:       According     to    the  thought  experiment      ,     it     is   both  alive    and   dead  until  observed      .
Logprobs:        -1.20  -0.15  -0.08    -0.95       -0.85  -0.05  -0.30  -0.25  -0.90  -0.80  -0.35  -0.45  -0.70     -0.65  -0.10
Perplexity:  2.156

```

**分析**:
- 🟡 **困惑度 2.156**: 中等,AI 有些不確定
- 📊 **最不確定的詞**: 
  - "According" -1.20 (可能用 "In", "Based on" 等)
  - "thought" -0.95 (可能用 "quantum", "physics" 等)
  - "both" -0.90 (核心概念,但表達方式多樣)
- 📊 **相對確定**: 標點符號和連接詞
- ⚠️ **結論**: AI 知道要表達「疊加態」的概念,但在用詞上有多種選擇

---

### 問題 3: 薛丁格的貓 (強制 yes/no)

**輸出範例**:
```
Prompt:      In a single word, yes or no, is Schrodinger's cat alive?
Response:    No

Tokens:        No
Logprobs:   -0.69
Perplexity:  1.994

```

**分析**:
- 🔴 **困惑度 1.994**: 雖然只有一個詞,但困惑度不低!
- 📊 **Logprob -0.69**: 表示機率約 50% (e^-0.69 ≈ 0.50)
- 🤔 **含義**: AI 在 "Yes" 和 "No" 之間幾乎是 50/50 猜測
- ⚠️ **結論**: 即使被強迫選擇,AI 內部仍然非常猶豫

**深入理解**:
```python
# 如果 logprob = -0.69
probability = np.exp(-0.69) ≈ 0.50 = 50%

# 這意味著:
P(No) ≈ 50%
P(Yes) ≈ 50%

# AI 本質上在拋硬幣!
```

**對比**:
- 如果 AI 很確定 "No": logprob 應該是 -0.05 或更高 (95%+)
- 實際 logprob -0.69: 表示 AI 極度不確定

---

### 問題 4: Nuevo León 首府

**輸出範例**:
```
Prompt:      In a short sentence, what is the capital of Nuevo Leon?
Response:    The capital of Nuevo León is Monterrey.

Tokens:       The  capital     of  Nuevo   León     is  Monterrey      .
Logprobs:   -0.02    -0.08  -0.04  -0.35  -0.30  -0.03      -0.25  -0.01
Perplexity:  1.147

```

**分析**:
- 🟢 **困惑度 1.147**: 低,AI 整體有信心
- 📊 **不確定的詞**: 
  - "Nuevo" -0.35, "León" -0.30 (拼寫或大小寫可能有變化)
  - "Monterrey" -0.25 (答案本身,但 AI 確實知道)
- 📊 **確定的詞**: "The" -0.02, "." -0.01 (結構性詞彙)
- ✅ **結論**: AI 知道答案,但對冷門地名稍微不那麼確定

---

### 問題 5: 不打破雞蛋做煎蛋

**輸出範例**:
```
Prompt:      Can you make an omelette without breaking eggs?
Response:    No, you cannot make an omelette without breaking eggs.

Tokens:        No      ,    you  cannot   make     an  omelette  without  breaking   eggs      .
Logprobs:   -0.08  -0.02  -0.05   -0.12  -0.06  -0.03     -0.10    -0.08     -0.15  -0.04  -0.01
Perplexity:  1.074

```

**分析**:
- 🟢 **困惑度 1.074**: 很低,AI 很確定
- 📊 **最確定的**: "," -0.02, "." -0.01 (標點符號)
- 📊 **相對不確定**: "breaking" -0.15 (可能用 "cracking")
- ✅ **結論**: AI 認識這個諺語,回答得很有信心

---

## 📈 困惑度對比總結表

| 問題 | 困惑度 | 信心等級 | 原因 |
|------|--------|---------|------|
| AI 成長了嗎? | ~1.05 | 極高 | 確定事實,共識性答案 |
| 薛丁格的貓 (長句)? | ~2.16 | 中等 | 概念確定,但表達方式多樣 |
| 薛丁格的貓 (yes/no)? | ~1.99 | 低 | 被迫二選一,但本質無答案 |
| Nuevo León 首府? | ~1.15 | 高 | 知道答案,但地名稍冷門 |
| 不破蛋做煎蛋? | ~1.07 | 極高 | 常見諺語,確定答案 |

**視覺化**:

```
困惑度越低 = 信心越高
│
1.05 ████████████████████████████████ AI 成長
1.07 ███████████████████████████████  不破蛋做煎蛋
1.15 ██████████████████████████       Nuevo León
1.99 ██████████                       薛丁格 (yes/no)
2.16 ████████                         薛丁格 (長句)
│
0    5    10   15   20   25   30   35
```

---

## 🎯 實際應用場景

### 場景 1: 答案品質檢測

```python
def answer_with_quality_check(prompt, perplexity_threshold=2.0):
    """
    回答問題,並檢查答案品質
    """
    response = get_completion(
        [{"role": "user", "content": prompt}],
        model="gpt-4o-mini",
        logprobs=True,
    )
    
    # 提取資訊
    logprobs = [token.logprob for token in response.output[0].content[0].logprobs]
    answer = response.output[0].content[0].text
    perplexity = np.exp(-np.mean(logprobs))
    
    # 品質評估
    if perplexity <= 1.5:
        quality = "優秀 ✅"
        action = "可直接使用"
    elif perplexity <= 2.5:
        quality = "良好 ✓"
        action = "建議人工審核"
    elif perplexity <= 5.0:
        quality = "中等 ⚠️"
        action = "需要人工審核"
    else:
        quality = "差 ❌"
        action = "不建議使用,重新生成"
    
    print(f"問題: {prompt}")
    print(f"答案: {answer}")
    print(f"困惑度: {perplexity:.3f}")
    print(f"品質評級: {quality}")
    print(f"建議行動: {action}\n")
    
    return {
        'answer': answer,
        'perplexity': perplexity,
        'quality': quality,
        'action': action
    }

# 使用範例
answer_with_quality_check("What is the capital of France?")
# 困惑度: 1.023
# 品質評級: 優秀 ✅
# 建議行動: 可直接使用

answer_with_quality_check("Is Schrödinger's cat alive?")
# 困惑度: 2.156
# 品質評級: 良好 ✓
# 建議行動: 建議人工審核
```

---

### 場景 2: 提示詞 A/B 測試

```python
def compare_prompts(base_question, prompt_templates):
    """
    比較不同提示詞模板的效果
    """
    results = []
    
    for i, template in enumerate(prompt_templates, 1):
        prompt = template.format(question=base_question)
        
        response = get_completion(
            [{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
            logprobs=True,
        )
        
        logprobs = [token.logprob for token in response.output[0].content[0].logprobs]
        answer = response.output[0].content[0].text
        perplexity = np.exp(-np.mean(logprobs))
        
        results.append({
            'prompt_num': i,
            'prompt': prompt,
            'answer': answer,
            'perplexity': perplexity
        })
        
        print(f"提示詞 {i}:")
        print(f"  模板: {template}")
        print(f"  答案: {answer}")
        print(f"  困惑度: {perplexity:.3f}\n")
    
    # 找出最佳提示詞
    best = min(results, key=lambda x: x['perplexity'])
    print(f"✅ 最佳提示詞: 提示詞 {best['prompt_num']} (困惑度: {best['perplexity']:.3f})")
    
    return results

# 使用範例
templates = [
    "{question}",  # 直接問
    "Please answer concisely: {question}",  # 要求簡潔
    "Based on your knowledge, {question}",  # 強調知識基礎
    "In one sentence, {question}",  # 限制長度
]

compare_prompts("What is artificial intelligence?", templates)
```

**輸出範例**:
```
提示詞 1:
  模板: {question}
  答案: Artificial intelligence is the simulation of human intelligence...
  困惑度: 1.245

提示詞 2:
  模板: Please answer concisely: {question}
  答案: AI is machine intelligence.
  困惑度: 1.089

提示詞 3:
  模板: Based on your knowledge, {question}
  答案: Artificial intelligence refers to...
  困惑度: 1.312

提示詞 4:
  模板: In one sentence, {question}
  答案: AI is the simulation of human intelligence by machines.
  困惑度: 1.067

✅ 最佳提示詞: 提示詞 4 (困惑度: 1.067)
```

**結論**: "In one sentence" 的提示詞讓 AI 最有信心!

---

### 場景 3: 多次生成選最佳答案

```python
def generate_best_answer(prompt, num_attempts=5, temperature=0.7):
    """
    生成多個答案,選擇困惑度最低的
    """
    candidates = []
    
    print(f"生成 {num_attempts} 個候選答案...\n")
    
    for i in range(num_attempts):
        response = get_completion(
            [{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
            logprobs=True,
            temperature=temperature,  # 增加多樣性
        )
        
        logprobs = [token.logprob for token in response.output[0].content[0].logprobs]
        answer = response.output[0].content[0].text
        perplexity = np.exp(-np.mean(logprobs))
        
        candidates.append({
            'attempt': i + 1,
            'answer': answer,
            'perplexity': perplexity
        })
        
        print(f"候選 {i+1}: 困惑度 {perplexity:.3f}")
        print(f"  {answer[:80]}...\n")
    
    # 選擇困惑度最低的
    best = min(candidates, key=lambda x: x['perplexity'])
    
    print(f"✅ 選擇候選 {best['attempt']} (困惑度: {best['perplexity']:.3f})")
    print(f"最佳答案: {best['answer']}")
    
    return best

# 使用範例
best = generate_best_answer(
    "Explain quantum computing in simple terms.",
    num_attempts=3,
    temperature=0.7
)
```

---

### 場景 4: 逐 Token 信心分析

```python
def analyze_token_confidence(prompt):
    """
    分析每個 token 的信心程度,找出不確定的部分
    """
    response = get_completion(
        [{"role": "user", "content": prompt}],
        model="gpt-4o-mini",
        logprobs=True,
    )
    
    tokens_data = response.output[0].content[0].logprobs
    
    print(f"問題: {prompt}\n")
    print("Token 信心分析:")
    print("-" * 60)
    
    uncertain_tokens = []
    
    for i, token_data in enumerate(tokens_data, 1):
        token = token_data.token
        logprob = token_data.logprob
        probability = np.exp(logprob) * 100
        
        # 分類信心程度
        if probability >= 90:
            confidence = "極高 ✅"
        elif probability >= 70:
            confidence = "高 ✓"
        elif probability >= 50:
            confidence = "中等 ⚠️"
        else:
            confidence = "低 ❌"
            uncertain_tokens.append((token, probability))
        
        print(f"{i:2d}. '{token:15}' | Prob: {probability:5.1f}% | {confidence}")
    
    print("-" * 60)
    
    # 總體困惑度
    logprobs = [t.logprob for t in tokens_data]
    perplexity = np.exp(-np.mean(logprobs))
    print(f"整體困惑度: {perplexity:.3f}\n")
    
    # 報告不確定的 token
    if uncertain_tokens:
        print("⚠️ 低信心的 token:")
        for token, prob in uncertain_tokens:
            print(f"  - '{token}': {prob:.1f}%")
    else:
        print("✅ 所有 token 都有高信心!")

# 使用範例
analyze_token_confidence("Is Schrödinger's cat alive?")
```

**輸出範例**:
```
問題: Is Schrödinger's cat alive?

Token 信心分析:
------------------------------------------------------------
 1. 'According     ' | Prob:  30.1% | 低 ❌
 2. ' to           ' | Prob:  86.0% | 高 ✓
 3. ' the          ' | Prob:  92.3% | 極高 ✅
 4. ' thought      ' | Prob:  38.6% | 低 ❌
 5. ' experiment   ' | Prob:  42.7% | 低 ❌
 6. ',             ' | Prob:  95.1% | 極高 ✅
 7. ' it           ' | Prob:  74.1% | 高 ✓
 8. ' is           ' | Prob:  77.9% | 高 ✓
 9. ' both         ' | Prob:  40.7% | 低 ❌
10. ' alive        ' | Prob:  44.9% | 低 ❌
11. ' and          ' | Prob:  70.5% | 高 ✓
12. ' dead         ' | Prob:  63.8% | 中等 ⚠️
13. ' until        ' | Prob:  49.7% | 低 ❌
14. ' observed     ' | Prob:  52.2% | 中等 ⚠️
15. '.             ' | Prob:  90.4% | 極高 ✅
------------------------------------------------------------
整體困惑度: 2.156

⚠️ 低信心的 token:
  - 'According': 30.1%
  - ' thought': 38.6%
  - ' experiment': 42.7%
  - ' both': 40.7%
  - ' alive': 44.9%
  - ' until': 49.7%
```

**分析**:
- AI 在關鍵概念詞上都不確定 (thought, both, alive)
- 標點符號和連接詞信心高
- 整體困惑度 2.156 反映了這種不確定性

---

## 🎓 理論深入: 困惑度的數學意義

### 資訊理論視角

**困惑度的本質**: 表示「平均需要多少選擇才能確定下一個 token」

**範例**:

**情況 1: 確定性高 (困惑度 = 1)**
```
問: 「太陽從____升起」
AI 想: 只有一個選擇「東邊」
困惑度 = 1 (不需要選擇,確定是 1 個)
```

**情況 2: 中等不確定 (困惑度 = 4)**
```
問: 「我喜歡吃____」
AI 想: 可能是「蘋果」「香蕉」「麵包」「飯」...大約 4 個同等可能的選擇
困惑度 = 4
```

**情況 3: 高度不確定 (困惑度 = 100)**
```
問: 「下一個字是____」(沒有上下文)
AI 想: 可能是任何一個詞,有 100 個同等可能的選擇
困惑度 = 100
```

### 數學公式詳解

**標準定義**:
```
Perplexity = 2^(-平均 log₂ 機率)
           = e^(-平均 ln 機率)
           = exp(-平均 logprobs)
```

**為什麼用指數?**

想像有 N 個同等可能的選擇:
```
每個選擇的機率 = 1/N
log(1/N) = -log(N)
平均 log 機率 = -log(N)
困惑度 = exp(-(-log(N))) = exp(log(N)) = N
```

**結論**: 困惑度 = 等效選擇數量

---

## 💡 最佳實踐建議

### 1. 困惑度門檻設定

```python
# 根據應用場景設定不同門檻

# 高風險應用 (醫療、法律)
HIGH_RISK_THRESHOLD = 1.5
if perplexity <= HIGH_RISK_THRESHOLD:
    use_answer()
else:
    require_human_review()

# 一般應用 (客服、教育)
MEDIUM_RISK_THRESHOLD = 3.0
if perplexity <= MEDIUM_RISK_THRESHOLD:
    use_answer()
else:
    generate_again_or_review()

# 低風險應用 (娛樂、建議)
LOW_RISK_THRESHOLD = 5.0
if perplexity <= LOW_RISK_THRESHOLD:
    use_answer()
else:
    add_disclaimer()
```

### 2. 結合多種指標

```python
def comprehensive_evaluation(prompt):
    """
    結合困惑度和其他指標
    """
    response = get_completion([{"role": "user", "content": prompt}], logprobs=True)
    
    logprobs = [t.logprob for t in response.output[0].content[0].logprobs]
    answer = response.output[0].content[0].text
    
    # 指標 1: 困惑度
    perplexity = np.exp(-np.mean(logprobs))
    
    # 指標 2: 最低 token 信心
    min_confidence = np.exp(min(logprobs)) * 100
    
    # 指標 3: 答案長度 (太短可能是逃避回答)
    answer_length = len(answer.split())
    
    # 綜合判斷
    if perplexity <= 2.0 and min_confidence >= 30 and answer_length >= 5:
        quality = "優秀"
    elif perplexity <= 3.5 and min_confidence >= 20:
        quality = "良好"
    else:
        quality = "需審核"
    
    return {
        'perplexity': perplexity,
        'min_confidence': min_confidence,
        'answer_length': answer_length,
        'quality': quality
    }
```

### 3. 建立基準線

```python
# 用已知良好答案建立基準

baseline_prompts = [
    "What is 2+2?",
    "What is the capital of France?",
    "Is the sky blue?",
]

baseline_perplexities = []
for prompt in baseline_prompts:
    response = get_completion([{"role": "user", "content": prompt}], logprobs=True)
    logprobs = [t.logprob for t in response.output[0].content[0].logprobs]
    perplexity = np.exp(-np.mean(logprobs))
    baseline_perplexities.append(perplexity)

baseline_avg = np.mean(baseline_perplexities)
print(f"基準困惑度: {baseline_avg:.3f}")

# 新問題的困惑度如果遠高於基準,可能有問題
```

### 4. 日誌與監控

```python
import logging
from datetime import datetime

def log_perplexity(prompt, answer, perplexity):
    """
    記錄困惑度數據,用於分析
    """
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'prompt': prompt,
        'answer': answer,
        'perplexity': perplexity,
    }
    
    logging.info(f"Perplexity: {perplexity:.3f} | Prompt: {prompt[:50]}...")
    
    # 警告高困惑度
    if perplexity > 5.0:
        logging.warning(f"High perplexity detected: {perplexity:.3f}")
    
    return log_entry
```

---

## ⚠️ 常見陷阱與誤區

### 陷阱 1: 誤以為低困惑度 = 正確答案

**問題**:
```python
# ❌ 錯誤假設
if perplexity < 2.0:
    answer_is_correct = True  # 不一定!
```

**事實**:
- 困惑度只表示「信心」,不表示「正確性」
- AI 可能很有信心地給出錯誤答案

**範例**:
```
問: 「1 + 1 = 3,對嗎?」
AI 答: 「No, 1 + 1 = 2.」
困惑度: 1.02 (很低,很有信心)
✅ 這次信心 = 正確

問: 「請編造一個故事」
AI 答: 「Once upon a time...」(流暢的故事)
困惑度: 1.15 (很低,很有信心)
❌ 但故事是編造的(幻覺)!
```

**解決**:
```python
# ✅ 正確做法
if perplexity < 2.0:
    high_confidence = True
    # 仍需要其他方式驗證正確性:
    # - 事實檢查
    # - 多個來源比對
    # - 人工審核
```

---

### 陷阱 2: 忽略問題類型的影響

**問題**:
- 不同類型問題的「正常困惑度」不同
- 用統一標準會誤判

**範例**:

```python
# 事實性問題
Q: "What is 2+2?"
困惑度: 1.01 ← 預期很低

# 開放性問題
Q: "Write a creative story."
困惑度: 3.5 ← 預期較高(創意任務本來就多樣)

# ❌ 錯誤: 用統一標準
if perplexity > 2.0:
    reject()  # 會錯誤拒絕創意任務!
```

**解決**:
```python
# ✅ 根據問題類型設定不同門檻
question_type = classify_question(prompt)

if question_type == "factual":
    threshold = 2.0
elif question_type == "creative":
    threshold = 5.0
elif question_type == "opinion":
    threshold = 4.0

if perplexity <= threshold:
    accept()
```

---

### 陷阱 3: 只看整體困惑度,忽略 Token 級別

**問題**:
```python
# ❌ 只看平均困惑度
overall_perplexity = 2.0  # 看起來還好

# 但可能:
token_1: logprob = -0.01 (很確定)
token_2: logprob = -0.05 (很確定)
token_3: logprob = -5.00 (極不確定!) ← 問題在這!
token_4: logprob = -0.02 (很確定)

# 平均後掩蓋了 token_3 的問題
```

**解決**:
```python
# ✅ 檢查最低信心 token
logprobs = [t.logprob for t in response.output[0].content[0].logprobs]
tokens = [t.token for t in response.output[0].content[0].logprobs]

min_logprob = min(logprobs)
min_idx = logprobs.index(min_logprob)
min_token = tokens[min_idx]

if min_logprob < -3.0:  # 某個 token 極不確定
    print(f"⚠️ 警告: token '{min_token}' 信心極低 ({np.exp(min_logprob)*100:.1f}%)")
```

---

## 🎓 總結

### 核心概念

1. **困惑度 (Perplexity)**
   - 衡量 AI 的不確定性
   - 計算公式: `exp(-平均 logprobs)`
   - 越接近 1 越好(越確定)

2. **困惑度的意義**
   - 資訊理論: 等效選擇數量
   - 實務: AI 的「結巴程度」
   - 信心指標,非正確性指標

3. **實際應用**
   - 答案品質檢測
   - 提示詞優化
   - 多次生成選最佳
   - Token 級別分析

### 關鍵技術

| 概念 | 公式/方法 | 用途 |
|------|----------|------|
| Logprobs | 每個 token 的對數機率 | 基礎數據 |
| 平均 Logprobs | `mean(logprobs)` | 整體表現 |
| 困惑度 | `exp(-mean(logprobs))` | 信心評分 |
| Token 分析 | 逐個檢查 logprob | 找出不確定點 |

### 價值主張

| 無困惑度評估 | 有困惑度評估 |
|------------|-------------|
| 不知道 AI 信心 | 量化信心程度 |
| 無法比較答案 | 可選最佳答案 |
| 無法檢測風險 | 主動識別風險 |
| 一視同仁 | 分級處理 |

---

## 🚀 下一步學習

### 1. 進階困惑度應用

```python
# 動態困惑度追蹤
def perplexity_over_time(prompts):
    """追蹤一系列問題的困惑度變化"""
    perplexities = []
    for prompt in prompts:
        # ... 計算困惑度
        perplexities.append(perplexity)
    
    # 繪製趨勢圖
    plot_perplexity_trend(perplexities)
```

### 2. 結合其他評估指標

- **BLEU Score**: 生成品質
- **ROUGE Score**: 摘要品質
- **BERTScore**: 語義相似度
- **人工評分**: 最終標準

### 3. 自動化評估管線

```python
class AnswerEvaluator:
    def __init__(self):
        self.metrics = []
    
    def evaluate(self, prompt, answer):
        # 困惑度
        perplexity = self.calculate_perplexity(answer)
        
        # 其他指標
        factuality = self.check_factuality(answer)
        coherence = self.check_coherence(answer)
        
        # 綜合評分
        score = self.compute_final_score(perplexity, factuality, coherence)
        
        return score
```

### 4. 建立評估資料集

```python
# 建立標準測試集
test_set = [
    {
        'prompt': "What is 2+2?",
        'expected_perplexity_range': (1.0, 1.5),
        'expected_answer': "4"
    },
    # ... 更多測試案例
]

# 定期評估系統表現
def run_evaluation(test_set):
    for case in test_set:
        result = answer_with_perplexity(case['prompt'])
        assert case['expected_perplexity_range'][0] <= result['perplexity'] <= case['expected_perplexity_range'][1]
```

---

## ❓ 常見問題 (FAQ)

### Q1: 困惑度和 logprobs 有什麼差別?
**A**: 
- **Logprobs**: 每個 token 的信心,範圍是負無窮到 0
- **Perplexity**: 整體信心的綜合指標,範圍是 1 到正無窮
- **關係**: Perplexity = exp(-平均 logprobs)

### Q2: 困惑度多少算好?
**A**: 取決於問題類型:
- **事實問題**: < 2.0 優秀, < 3.0 良好
- **分析問題**: < 4.0 良好
- **創意任務**: < 6.0 可接受
- 建議建立自己的基準線

### Q3: 困惑度低就代表答案正確嗎?
**A**: **不一定!** 困惑度只表示 AI 的信心,不保證正確性。AI 可能很有信心地給出錯誤答案(幻覺)。

### Q4: 如何降低困惑度?
**A**: 
1. **改進提示詞**: 更清晰、更具體
2. **提供上下文**: 給 AI 更多資訊
3. **限制輸出格式**: 減少選擇範圍
4. **降低 temperature**: 讓輸出更確定

### Q5: 可以用困惑度來比較不同模型嗎?
**A**: 可以,但要注意:
- 相同任務、相同提示詞
- 困惑度低不一定代表模型更好
- 需要結合其他指標(準確度、速度等)

### Q6: 困惑度和 temperature 參數有什麼關係?
**A**: 
```python
temperature = 0   → 輸出確定 → 困惑度低
temperature = 0.7 → 輸出多樣 → 困惑度中等
temperature = 1.5 → 輸出隨機 → 困惑度高
```
但 temperature 影響的是「採樣」,logprobs 是原始機率分布。

---

## 📖 延伸閱讀

- [Perplexity in Language Models](https://huggingface.co/docs/transformers/perplexity)
- [Information Theory and Language Models](https://web.stanford.edu/~jurafsky/slp3/)
- [Evaluating Language Generation](https://arxiv.org/abs/2006.14799)
- [OpenAI Cookbook: Logprobs and Perplexity](https://cookbook.openai.com/examples/using_logprobs)

---

**祝您學習愉快! 有任何問題歡迎隨時詢問! 🎉**
