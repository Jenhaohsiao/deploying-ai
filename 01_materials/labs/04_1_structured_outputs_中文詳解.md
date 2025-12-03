# 結構化輸出 (Structured Outputs) - 完整中文詳解

## 📚 什麼是結構化輸出?

**結構化輸出**是指讓 AI 模型回應的內容遵循特定的格式和結構,而不是自由格式的文字。這在我們需要把 AI 的回應傳遞給系統的其他組件時特別有用。

### 為什麼需要結構化輸出?

想像一下這些情況:
- 你想讓 AI 從一段文字中提取姓名、日期和地點
- 你需要 AI 生成的資料儲存到資料庫
- 你要把 AI 的回應傳給另一個程式處理

如果 AI 只是隨意回答,格式可能每次都不同,程式就很難處理。結構化輸出就像是給 AI 一個表格,要求它按照欄位填寫。

---

## 🔧 方法一: OpenAI API 結構化輸出

### 背景知識

以前,OpenAI 介面提供 JSON 輸出,但這不能確保資料符合特定的結構規範(例如資料類型可能不會被強制執行)。現在,我們可以使用 **Pydantic** 來定義輸出的結構規範。

### 什麼是 Pydantic?

[Pydantic](https://docs.pydantic.dev/latest/) 是 Python 的資料驗證函式庫。簡單來說:
- 它幫助我們定義資料應該長什麼樣子
- 自動檢查資料是否符合我們的要求
- 如果資料格式錯誤,會自動報錯

### Pydantic 的基本概念

1. **Models (模型)**: 繼承自 `BaseModel` 的類別
2. **Fields (欄位)**: 類別中的屬性,用來定義資料的類型和規則

### 實際範例: 提取日曆事件

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

# 定義一個日曆事件的結構
class CalendarEvent(BaseModel):
    name: str              # 事件名稱(字串)
    date: str              # 日期(字串)
    participants: list[str] # 參與者名單(字串列表)

# 使用 OpenAI API 解析結構化輸出
response = client.responses.parse(
    model="gpt-4o-mini",
    input=[
        {"role": "system", "content": "Extract the event information."},
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on Friday.",
        },
    ],
    text_format=CalendarEvent,
)

event = response.output_parsed
```

**這個例子在做什麼?**
1. 我們告訴 AI 一段文字:「Alice 和 Bob 星期五要去科學展」
2. AI 會自動把資訊拆解成:
   - name: "science fair" (事件名稱)
   - date: "Friday" (日期)
   - participants: ["Alice", "Bob"] (參與者)

### 📖 補充說明

**為什麼用 `list[str]` 而不是 `list`?**
- `list[str]` 表示「字串的列表」,更精確
- 如果有人不小心放入數字,Pydantic 會提醒錯誤

**參考資源:**
- [OpenAI Structured Outputs 官方文件](https://platform.openai.com/docs/guides/structured-outputs)

---

## 🦜 方法二: LangChain 與 Pydantic

### 什麼是 LangChain?

LangChain 是一個框架,讓我們更容易使用大型語言模型(LLM)。它提供了許多便利的功能,包括結構化輸出。

### 範例: 生成結構化的笑話

```python
# 載入環境變數(API 金鑰等)
%load_ext dotenv
%dotenv ../../05_src/.secrets

# 初始化聊天模型
from langchain.chat_models import init_chat_model
llm = init_chat_model("gpt-4o-mini", model_provider="openai")

# 使用 Pydantic 定義笑話的結構
from typing import Optional
from pydantic import BaseModel, Field

class Joke(BaseModel):
    setup: str = Field(description="The setup of the joke")      # 笑話的鋪陳
    punchline: str = Field(description="The punchline of the joke") # 笑話的笑點
    rating: Optional[int] = Field(
        default=None, 
        description="How funny the joke is, from 1 to 10"  # 笑話的有趣程度(1-10分)
    )

# 讓 LLM 輸出符合 Joke 結構的資料
structured_llm = llm.with_structured_output(Joke)

# 請 AI 講一個關於貓的笑話
jk = structured_llm.invoke("Tell me a joke about cats")
```

### 📖 詳細解說

**Field() 是什麼?**
- `Field()` 用來描述每個欄位的細節
- `description` 會告訴 AI 這個欄位應該放什麼內容

**Optional[int] 是什麼意思?**
- `Optional[int]` 表示這個欄位可以是整數,也可以是 `None`(空值)
- `default=None` 表示如果沒有提供,預設值是 `None`

**範例輸出:**
```python
Joke(
    setup="Why don't cats play poker in the jungle?",
    punchline="Too many cheetahs!",
    rating=7
)
```

### 🎯 使用時機

使用 Pydantic 適合:
- 需要嚴格的資料驗證
- 要整合到大型專案
- 需要詳細的欄位描述和預設值

---

## 📋 方法三: LangChain 與 TypedDict

### 什麼是 TypedDict?

[TypedDict](https://typing.python.org/en/latest/spec/typeddict.html) 是 Python 的型別提示工具,可以定義字典(dictionary)中每個鍵(key)應該對應什麼類型的值。

### TypedDict vs Pydantic 的差異

| 特性 | Pydantic | TypedDict |
|------|----------|-----------|
| 資料驗證 | ✅ 自動驗證 | ❌ 只有型別提示 |
| 適用場景 | 嚴格驗證 | 輕量級專案 |
| 學習難度 | 稍難 | 簡單 |

### 範例: 使用 TypedDict 定義笑話

```python
from typing import Optional
from typing_extensions import Annotated, TypedDict

class JokeDict(TypedDict):
    setup: Annotated[str, ..., "The setup of the joke"]  
    # 沒有預設值,必須提供,帶描述
    
    punchline: Annotated[str, ..., "The punchline of the joke"]  
    # 沒有預設值,必須提供,帶描述
    
    rating: Annotated[Optional[int], None, "How funny the joke is, from 1 to 10"]  
    # 預設值為 None,帶描述
```

**使用範例:**
```python
structured_llm_dict = llm.with_structured_output(JokeDict)
jk_dict = structured_llm_dict.invoke("Tell me a joke about dogs")
```

### 📖 Annotated 的語法解釋

`Annotated[類型, 預設值, 描述]` 包含三個部分:
1. **類型**: 資料類型(str, int, list 等)
2. **預設值**: `...` 表示必填,`None` 表示可選
3. **描述**: 告訴 AI 這個欄位的用途

**範例輸出:**
```python
{
    'setup': 'Why did the dog sit in the shade?',
    'punchline': 'Because he didn't want to be a hot dog!',
    'rating': 8
}
```

---

## 🔍 三種方法比較總結

| 方法 | 適用情境 | 優點 | 缺點 |
|------|----------|------|------|
| **OpenAI + Pydantic** | 直接使用 OpenAI API | 官方支援,穩定 | 只能用於 OpenAI |
| **LangChain + Pydantic** | 複雜專案,需要驗證 | 功能完整,可切換模型 | 學習曲線較陡 |
| **LangChain + TypedDict** | 簡單專案,快速開發 | 語法簡單,輕量級 | 缺少自動驗證 |

---

## 💡 初學者常見問題

### Q1: 什麼時候該用結構化輸出?
**A:** 當你需要:
- 把 AI 的回應存入資料庫
- 將資料傳給其他程式
- 確保回應格式一致

### Q2: Pydantic 和 TypedDict 我該選哪個?
**A:** 
- **新手或小專案**: 用 TypedDict,簡單快速
- **正式專案**: 用 Pydantic,有自動驗證更安全

### Q3: Field() 的 description 有什麼用?
**A:** 
- 告訴 AI 這個欄位應該放什麼
- 幫助團隊成員理解程式碼
- 自動生成文件

### Q4: Optional 是什麼意思?
**A:** 
`Optional[int]` = 可以是整數或 `None`(空值)

---

## 🚀 實戰練習建議

### 練習 1: 名片資訊提取
建立一個 Pydantic 模型,從文字中提取:
- 姓名
- 公司
- 電話
- 電子郵件

### 練習 2: 產品評論分析
建立一個結構化輸出,包含:
- 評論文字
- 情緒(正面/負面/中性)
- 評分(1-5星)
- 關鍵字列表

### 練習 3: 行程規劃
讓 AI 從對話中提取旅行計畫:
- 目的地
- 日期範圍
- 預算
- 活動列表

---

## 📚 延伸學習資源

1. **Pydantic 官方文件**: https://docs.pydantic.dev/
2. **LangChain 文件**: https://python.langchain.com/
3. **OpenAI Structured Outputs**: https://platform.openai.com/docs/guides/structured-outputs
4. **Python TypedDict**: https://typing.python.org/en/latest/spec/typeddict.html

---

## 🎓 總結

結構化輸出是 AI 應用開發的重要技能:
- **OpenAI 方法**: 最直接,適合簡單場景
- **Pydantic 方法**: 功能強大,適合正式專案
- **TypedDict 方法**: 輕量簡單,適合快速開發

選擇適合你專案需求的方法,從簡單的開始練習,逐步掌握更複雜的用法!

---

*本文件由原始 `04_1_structured_outputs.ipynb` 翻譯並擴充,加入更多初學者友善的說明和範例。*
