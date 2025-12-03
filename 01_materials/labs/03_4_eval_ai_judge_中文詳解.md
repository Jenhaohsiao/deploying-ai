# AI 作為評審者 - 完整中文教學指南

## 📚 課程概述

這個教學將教您如何使用 AI 模型來評估其他 AI 模型的輸出品質。就像請一位專家老師來評改學生的作業一樣！

---

## 🎯 什麼是 AI as Judge (AI 作為評審者)?

### 基本概念
- **G-Eval** 是一個評估框架,使用 LLM (大型語言模型) 作為評審者來評估其他 LLM 的輸出
- 可以根據**任何標準**進行評估
- 由 **DeepEval** 函式庫實現,這是一個包含更多測試工具的完整評估套件

### 為什麼需要 AI 評審者?
傳統上,評估 AI 輸出需要人工審查,但這樣:
- ⏰ 耗時
- 💰 成本高
- 📊 難以大規模進行

使用 AI 作為評審者可以:
- ✅ 自動化評估流程
- ✅ 保持一致的評估標準
- ✅ 快速處理大量測試案例

**相關資源:**
- [G-Eval 文檔](https://deepeval.com/docs/metrics-llm-evals)
- [DeepEval 官方網站](https://deepeval.com/)

---

## 🔧 環境設定

### Cell 1: 載入環境變數

```python
%load_ext dotenv
%dotenv ../../05_src/.secrets
```

**解釋:**
- `%load_ext dotenv`: 載入 dotenv 擴充功能
- `%dotenv`: 從 `.secrets` 檔案載入 API 金鑰等敏感資訊
- 這樣可以安全地管理您的 OpenAI API 金鑰,不會暴露在程式碼中

---

## 📖 準備測試資料

### Cell 2: 讀取文學作品

```python
from openai import OpenAI
import os

document_folder = "../../05_src/documents/"
blue_cross_file = "the_blue_cross.txt"
file_path = os.path.join(document_folder, blue_cross_file)

with open(file_path, "r", encoding="utf-8") as f:
    blue_cross_text = f.read()
```

**解釋:**
- 讀取一個名為 "The Blue Cross" (藍十字) 的故事文本
- 使用 `os.path.join()` 確保路徑在不同作業系統上都能正常運作
- `encoding="utf-8"` 確保能正確讀取各種語言的文字

---

## 💬 建立測試用的提示詞

### Cell 3: 定義系統指令和提示模板

```python
instructions = "You are an helpful assistant that summarizes works of fiction with a quirky and bubbly approach."
PROMPT = """
    Summarize the following story in at most four paragraphs. Please include all key characters and plot points.
    <story>
    {story}
    </story>
    In addition to the summary, add an introduction paragraph where you greet the reader and a conclusion where you share an opinion about the story.
"""
```

**中文翻譯:**
- **instructions (系統指令):** "你是一個樂於助人的助手,以古怪活潑的方式總結虛構作品。"
- **PROMPT (提示詞):** "用最多四個段落總結以下故事。請包含所有關鍵角色和情節要點。除了總結之外,請添加一個問候讀者的開場段落,以及一個分享您對故事看法的結論段落。"

**設計考量:**
- 要求特定的風格 ("quirky and bubbly" - 古怪活潑)
- 明確的結構要求 (開場、總結、結論)
- 限制長度 (最多四個段落)

---

## 🤖 生成 AI 回應

### Cell 4: 呼叫 OpenAI API

```python
client = OpenAI()
response = client.responses.create(
    model="gpt-4o-mini",
    instructions=instructions,
    input=[
        {"role": "user", 
         "content": PROMPT.format(story=blue_cross_text)}
    ],
    temperature=1.2
)
```

**參數說明:**
- `model="gpt-4o-mini"`: 使用 GPT-4 的精簡版本 (更快、更便宜)
- `instructions`: 系統層級的指令,定義 AI 的角色
- `input`: 使用者的輸入,將故事文本插入到提示模板中
- `temperature=1.2`: 
  - 控制輸出的創意程度
  - 範圍 0-2,數值越高越有創意
  - 1.2 表示相對較高的創意性

**補充知識 - Temperature 參數:**
- 0.0-0.3: 非常確定性,適合事實性任務
- 0.7-0.9: 平衡的創意,適合一般對話
- 1.0-2.0: 高創意性,適合創意寫作

### Cell 5: 查看生成的回應

```python
response.output_text
```

**解釋:**
- 顯示 AI 生成的故事摘要
- 這將是我們後續要評估的「實際輸出」

---

## 📊 評估指標 1: 答案相關性 (Answer Relevancy)

### Cell 6: 理解答案相關性指標

**什麼是答案相關性?**
- 評估 LLM 的實際輸出與提供的輸入之間的相關程度
- 這個指標是「自我解釋」的,會提供評分的理由

**計算公式:**

$$
AnswerRelevancy = \frac{相關陳述數量}{總陳述數量}
$$

**範例說明:**
- 如果輸出有 10 個陳述,其中 7 個與問題相關
- 答案相關性 = 7/10 = 0.7 (70%)

**參考資料:** [Answer Relevancy 文檔](https://deepeval.com/docs/metrics-answer-relevancy)

### Cell 7: 設定相關性測試

```python
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

metric = AnswerRelevancyMetric(
    threshold=0.7,
    model="gpt-4o-mini",
    include_reason=True
)

test_case = LLMTestCase(
    input=PROMPT.format(story=blue_cross_text),
    actual_output=response.output_text
)
```

**參數詳解:**
- `threshold=0.7`: 設定通過標準為 70%
  - 分數 ≥ 0.7 表示測試通過
  - 分數 < 0.7 表示測試失敗
- `model="gpt-4o-mini"`: 使用此模型作為評審者
- `include_reason=True`: 要求提供評分理由
- `input`: 原始的問題/提示
- `actual_output`: AI 生成的回答

### Cell 8: 執行評估

```python
metric.measure(test_case)
```

**這個步驟會:**
1. 將輸入和輸出發送給評審者 AI
2. 評審者分析輸出的每個陳述
3. 判斷哪些陳述與輸入相關
4. 計算相關性分數

### Cell 9: 查看評估結果

```python
print(metric.score, metric.reason)
```

**輸出包含:**
- `metric.score`: 數值分數 (0.0 到 1.0)
- `metric.reason`: 文字說明,解釋為什麼給這個分數

---

## 🎓 其他實用的評估指標

### Cell 10: DeepEval 提供的其他指標

#### 1. **Faithfulness (忠實度)**
```
評估 actual_output 是否與 retrieval_context 的內容事實一致
```
- **使用情境:** RAG (檢索增強生成) 系統
- **檢查重點:** AI 是否編造了上下文中沒有的資訊
- **範例:** 如果上下文說「巴黎是法國首都」,但輸出說「巴黎是德國首都」,忠實度會很低

[Faithfulness 文檔](https://deepeval.com/docs/metrics-faithfulness)

#### 2. **Contextual Precision (上下文精確度)**
```
評估 retrieval_context 中與輸入相關的節點是否排名高於不相關的節點
```
- **使用情境:** 評估檢索系統的品質
- **檢查重點:** 最相關的資訊是否排在前面
- **範例:** 搜尋「Python 程式設計」時,Python 教學應該排在 Python 蛇類的資訊前面

[Contextual Precision 文檔](https://deepeval.com/docs/metrics-contextual-precision)

#### 3. **Contextual Recall (上下文召回率)**
```
評估 retrieval_context 與 expected_output 的一致程度
```
- **使用情境:** 檢查是否檢索到所有必要的資訊
- **檢查重點:** 檢索的上下文是否包含產生正確答案所需的所有資訊

[Contextual Recall 文檔](https://deepeval.com/docs/metrics-contextual-recall)

#### 4. **Contextual Relevancy (上下文相關性)**
```
評估 retrieval_context 中呈現的資訊對於給定輸入的整體相關性
```
- **使用情境:** 評估檢索的資訊品質
- **檢查重點:** 檢索的資訊是否真的有助於回答問題

[Contextual Relevancy 文檔](https://deepeval.com/docs/metrics-contextual-relevancy)

---

## 🏆 G-Eval: 最靈活的評估框架

### Cell 11: G-Eval 簡介

**什麼是 G-Eval?**
- 使用 LLM 作為評審者的框架
- 結合**思維鏈 (Chain-of-Thoughts, CoT)** 技術
- 可以根據**任何自訂標準**評估 LLM 輸出
- DeepEval 提供的最多功能的評估指標

**思維鏈 (CoT) 是什麼?**
- 讓 AI 逐步思考,而不是直接給答案
- 就像學生解數學題時要「顯示計算過程」
- 提高評估的透明度和準確性

[G-Eval 文檔](https://deepeval.com/docs/metrics-llm-evals)

---

## 🔍 G-Eval 實作範例

### Cell 12: 準備新的測試提示

```python
instructions = "You are an helpful assistant that specializes in works of fiction."
PROMPT = """
    Based on the story below, answer the question provided.
    <story>
    {story}
    </story>
    <question>
    Who is the main antagonist in the story and what motivates their actions?
    </question>
"""
```

**中文翻譯:**
- **instructions:** "你是一個專精於虛構作品的有用助手。"
- **PROMPT:** "根據下面的故事,回答提供的問題。問題:故事中的主要反派是誰?他們的行為動機是什麼?"

### Cell 13 & 14: 生成回答

```python
client = OpenAI()
response = client.responses.create(
    model="gpt-4o-mini",
    instructions=instructions,
    input=[
        {"role": "user", 
         "content": PROMPT.format(story=blue_cross_text)}
    ],
    temperature=0.7
)
```

**注意 temperature 的變化:**
- 從 1.2 降到 0.7
- 因為這次需要更精確的事實性回答,而不是創意寫作

---

## ✅ 方法 1: 使用單一標準評估

### Cell 15: 評估標準的最直接方式

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

correctness_metric = GEval(
    name="Correctness",
    criteria="Determine whether the actual output is factually correct based on the context.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
)
```

**參數說明:**
- `name="Correctness"`: 指標名稱為「正確性」
- `criteria`: 評估標準
  - **中文:** "判斷實際輸出是否基於上下文在事實上正確"
- `evaluation_params`: 要評估的參數
  - `INPUT`: 原始問題
  - `ACTUAL_OUTPUT`: AI 的回答

**這個設定會讓評審者 AI:**
1. 閱讀原始問題 (INPUT)
2. 閱讀 AI 的回答 (ACTUAL_OUTPUT)
3. 判斷回答是否事實正確
4. 給出 0-1 的分數

### Cell 16: 執行評估

```python
test_case = LLMTestCase(
    input=PROMPT.format(story=blue_cross_text),
    actual_output=response.output_text
)
evaluate(test_cases=[test_case], metrics=[correctness_metric])
```

**流程:**
1. 建立測試案例
2. 使用 `evaluate()` 函數執行評估
3. 可以同時測試多個案例 (`test_cases` 是陣列)
4. 可以使用多個指標 (`metrics` 是陣列)

---

## 📝 方法 2: 使用詳細的評估步驟

### Cell 17: 定義評估步驟

```python
correctness_metric = GEval(
    name="Correctness",
    evaluation_steps=[
        "Check whether the facts in 'actual output' contradicts any facts in 'input'",
        "You should also heavily penalize omission of detail",
        "Vague language, or contradicting OPINIONS, are not OK"
    ],
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
)
```

**中文翻譯評估步驟:**
1. "檢查'實際輸出'中的事實是否與'輸入'中的任何事實相矛盾"
2. "你還應該嚴重懲罰遺漏細節的情況"
3. "模糊的語言或相互矛盾的觀點是不可接受的"

**為什麼使用評估步驟而不是標準?**

| 評估標準 (Criteria) | 評估步驟 (Steps) |
|---|---|
| 單一、概括性的描述 | 多個、具體的檢查點 |
| 適合簡單評估 | 適合複雜評估 |
| 評審者自行決定如何評估 | 引導評審者的思考過程 |

**評估步驟的優勢:**
- ✅ 更精確的控制
- ✅ 更一致的評估結果
- ✅ 更容易除錯和改進
- ✅ 評估過程更透明

### Cell 18: 執行詳細評估

```python
test_case = LLMTestCase(
    input=PROMPT.format(story=blue_cross_text),
    actual_output=response.output_text
)
evaluate(test_cases=[test_case], metrics=[correctness_metric])
```

**這次評估會:**
1. 按照定義的三個步驟逐一檢查
2. 對每個步驟給出評估
3. 綜合所有步驟得出最終分數

---

## 🎯 實務應用建議

### 何時使用哪種方法?

#### 使用單一標準 (Criteria) 當:
- 評估標準很簡單明確
- 需要快速評估
- 評估者 AI 已經很了解該領域

#### 使用評估步驟 (Steps) 當:
- 需要細緻的評估
- 評估標準複雜
- 需要確保評估的一致性
- 需要除錯評估流程

### 設定門檻值 (Threshold) 的技巧

```python
metric = AnswerRelevancyMetric(threshold=0.7)
```

**建議的門檻值:**
- **0.5-0.6**: 寬鬆標準,初期開發
- **0.7-0.8**: 中等標準,大多數應用
- **0.9-1.0**: 嚴格標準,關鍵應用

### 組合多個指標

```python
metrics = [
    AnswerRelevancyMetric(threshold=0.7),
    correctness_metric,
    GEval(name="Completeness", criteria="..."),
]
evaluate(test_cases=[test_case], metrics=metrics)
```

**好處:**
- 全面評估輸出品質
- 找出不同類型的問題
- 建立更穩健的 AI 系統

---

## 📈 最佳實踐

### 1. 建立測試資料集
```python
test_cases = [
    LLMTestCase(input=prompt1, actual_output=output1),
    LLMTestCase(input=prompt2, actual_output=output2),
    # ... 更多測試案例
]
```

### 2. 定期運行評估
- 在每次模型更新後
- 在改變提示詞後
- 在調整參數後

### 3. 記錄評估結果
```python
results = evaluate(test_cases=test_cases, metrics=metrics)
# 儲存結果以便追蹤改進
```

### 4. 迭代改進
1. 運行評估
2. 分析失敗的案例
3. 調整提示詞或模型
4. 重新評估

---

## 🔗 延伸學習資源

### DeepEval 官方文檔
- [完整指標列表](https://deepeval.com/docs/metrics-introduction)
- [進階評估技巧](https://deepeval.com/docs/evaluation-introduction)
- [最佳實踐指南](https://deepeval.com/docs/getting-started)

### 相關概念
- **RAG (Retrieval-Augmented Generation)**: 檢索增強生成
- **Few-Shot Learning**: 少樣本學習
- **Prompt Engineering**: 提示工程

### 實作專案建議
1. 建立自己的評估管道
2. 比較不同模型的表現
3. 開發特定領域的評估指標
4. 自動化品質保證流程

---

## 💡 常見問題 FAQ

### Q1: 為什麼要用 AI 評估 AI?
**A:** 人工評估太慢且昂貴,AI 評審者可以快速、一致地評估大量輸出。

### Q2: AI 評審者會出錯嗎?
**A:** 會!所以建議:
- 使用多個指標
- 定期人工抽查
- 持續調整評估標準

### Q3: 如何選擇評審者模型?
**A:** 
- **gpt-4o**: 最準確,但較貴
- **gpt-4o-mini**: 平衡性能和成本
- **gpt-3.5-turbo**: 最便宜,但可能不夠準確

### Q4: Threshold 設多少合適?
**A:** 根據應用的重要性:
- 聊天機器人: 0.6-0.7
- 客戶服務: 0.7-0.8
- 醫療/法律: 0.9+

---

## 🎓 總結

### 你學到了什麼:
1. ✅ AI as Judge 的概念和重要性
2. ✅ 使用 DeepEval 進行自動化評估
3. ✅ 答案相關性指標的計算和應用
4. ✅ G-Eval 框架的兩種使用方式
5. ✅ 如何設計有效的評估標準和步驟
6. ✅ 多種評估指標的應用場景

### 下一步學習:
- 探索其他 DeepEval 指標
- 建立自訂評估標準
- 整合評估到 CI/CD 流程
- 研究進階的提示工程技巧

---

**祝您學習愉快! 🚀**
