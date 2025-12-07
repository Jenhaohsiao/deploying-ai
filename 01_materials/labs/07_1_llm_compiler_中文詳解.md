# LLM Compiler 中文詳解 - 給初學者的完整指南

## 📚 目錄
1. [什麼是 MCP?](#什麼是-mcp)
2. [什麼是 LLM Compiler?](#什麼是-llm-compiler)
3. [為什麼需要它?](#為什麼需要它)
4. [核心概念解釋](#核心概念解釋)
5. [三大組件詳解](#三大組件詳解)
6. [完整代碼範例](#完整代碼範例)
7. [實際應用場景](#實際應用場景)
8. [常見問題解答](#常見問題解答)

---

## 什麼是 MCP?

### MCP 基礎概念

**MCP (Model Context Protocol)** 是一個標準化的協定,讓 AI 應用程式能夠安全地連接到外部資料來源和工具。

### 日常生活比喻
想像 MCP 就像是「萬用插頭轉接器」:
- **傳統做法**: 每個國家的插座不同,你需要為每個國家準備不同的插頭
- **使用 MCP**: 有了標準化的轉接器,一個插頭就能在任何地方使用

同樣地,MCP 讓 AI 模型能夠用統一的方式連接到各種不同的服務和工具。

### MCP 的三個關鍵角色

#### 1. MCP Host (主機)
- **角色**: 協調和管理一個或多個 MCP 客戶端的 AI 應用程式
- **比喻**: 就像是一個總經理,負責管理和協調所有的工作
- **例子**: VS Code、Claude Desktop、OpenAI API

#### 2. MCP Client (客戶端)
- **角色**: 維持與 MCP 伺服器的連接,並為 MCP 主機獲取上下文資訊
- **比喻**: 就像是一個中間人或傳令員,負責傳遞訊息
- **功能**: 它是主機和伺服器之間的橋樑

#### 3. MCP Server (伺服器)
- **角色**: 向 MCP 客戶端提供上下文資訊和工具的程式
- **比喻**: 就像是一個專門的服務提供商,例如天氣服務、資料庫查詢服務
- **例子**: 天氣查詢伺服器、檔案管理伺服器、數學計算服務

### MCP 運作流程圖

```
┌─────────────────┐
│   MCP Host      │  例如: VS Code、OpenAI API
│   (總經理)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MCP Client    │  負責連接和通訊
│   (傳令員)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MCP Server    │  提供工具和資料
│  (服務提供商)   │  例如: 搜尋、計算、查詢
└─────────────────┘
```

### 實際範例: 天氣查詢

當你問 AI「舊金山現在的天氣如何?」時:

1. **MCP Host (AI 應用)**: 收到用戶問題
2. **MCP Client**: 識別需要天氣資訊,連接到天氣 MCP 伺服器
3. **MCP Server**: 查詢天氣 API,返回結果
4. **MCP Client**: 將結果傳回給 Host
5. **MCP Host**: 整合資訊,生成回答給用戶

### 為什麼 MCP 很重要?

**1. 標準化**
- 不需要為每個工具寫專門的整合代碼
- 一次實作,到處使用

**2. 安全性**
- 統一的安全協定
- 可控制的權限管理

**3. 擴展性**
- 輕鬆添加新工具和服務
- 支援多個伺服器同時運作

**4. 靈活性**
- AI 可以動態選擇需要的工具
- 支援複雜的工作流程

### MCP 與 LLM Compiler 的關係

在本教程中:
- **MCP Server** 提供各種工具(如搜尋、數學計算)
- **LLM Compiler** 智能地規劃如何使用這些工具
- 兩者結合,創造出強大且高效的 AI 代理系統

---

## 什麼是 LLM Compiler?

### 基本概念

**LLM Compiler** 是一個創新的 AI 代理(Agent)架構,專門設計用來提升 AI 執行複雜任務的效率和速度。

### 名詞解釋

#### 什麼是「Compiler」(編譯器)?

在電腦科學中,**編譯器**是一個將高階程式碼轉換成機器可執行指令的程式。它的特點是:
1. **分析整個程式**:一次性查看所有代碼
2. **優化執行順序**:重新排列指令以提高效率
3. **識別依賴關係**:確定哪些操作必須按順序執行,哪些可以並行

**LLM Compiler 借用了這個概念**:
- 不是逐步執行任務(像解釋器)
- 而是先分析整個問題,制定最優執行計劃
- 然後平行處理獨立的任務

### 簡單比喻

想像你要辦一場派對,需要做很多事情:
- 買食材
- 準備場地
- 邀請朋友
- 準備音樂

**傳統 AI 代理(順序執行,像解釋器)**:
```
步驟 1: 買食材 (1小時)
步驟 2: 準備場地 (1小時)  
步驟 3: 邀請朋友 (30分鐘)
步驟 4: 準備音樂 (30分鐘)
總時間: 3小時
```
- 一件一件做,做完一件才做下一件
- 每做完一件事,還要思考「接下來該做什麼?」
- 效率低,浪費時間

**LLM Compiler(智能規劃和並行執行)**:
```
規劃階段:分析所有任務和依賴關係
執行階段:
  並行組 1: 買食材 + 邀請朋友 (同時進行,1小時)
  並行組 2: 準備場地 + 準備音樂 (同時進行,1小時)
總時間: 2小時
```
- 先分析哪些事可以同時進行
- 識別哪些任務必須按順序(如先準備場地才能佈置)
- 平行處理獨立任務,大幅縮短時間!

### 正式定義

LLM Compiler 是由 **Kim 等人在 2023 年**發表的 AI 代理架構(論文:[An LLM Compiler for Parallel Function Calling](https://arxiv.org/abs/2312.04511)),其核心創新包括:

#### 1. 加速執行 (Speed Optimization)
- **並行處理**:同時執行多個獨立的任務
- **提前調度**:不等待前一個任務完成就開始準備下一個
- **效率提升**:在某些場景下可節省 40-50% 的執行時間

#### 2. 節省成本 (Cost Reduction)
- **減少 LLM 調用**:一次性規劃所有步驟,而不是每步都問 LLM「下一步做什麼?」
- **智能緩存**:避免重複執行相同的任務
- **經濟效益**:每次 LLM 調用都要花錢,減少調用次數可顯著降低成本

#### 3. 智能排程 (Intelligent Scheduling)
- **DAG 管理**:使用有向無環圖(Directed Acyclic Graph)表示任務依賴關係
- **依賴解析**:自動識別任務之間的依賴,確保執行順序正確
- **動態調整**:如果某個任務失敗,可以重新規劃剩餘步驟

### LLM Compiler vs 傳統 AI 代理

| 特性 | 傳統 AI 代理 | LLM Compiler |
|------|-------------|--------------|
| **執行方式** | 順序執行(Sequential) | 並行執行(Parallel) |
| **規劃策略** | 逐步決定(每次只看下一步) | 一次性規劃(看整個任務) |
| **LLM 調用** | 頻繁(每步都調用) | 較少(主要用於規劃) |
| **速度** | 較慢 | 快速(2-3倍提升) |
| **成本** | 較高 | 較低 |
| **適用場景** | 簡單單步驟任務 | 複雜多步驟任務 |

### 工作原理概述

```
用戶問題: "舊金山和紐約的溫度總和是多少?"

┌─────────────────────────────────────────┐
│ 傳統 AI 代理                              │
├─────────────────────────────────────────┤
│ 1. LLM: "我需要查舊金山溫度"              │
│ 2. 執行: search("SF temp") → 15°C       │
│ 3. LLM: "接下來查紐約溫度"                │
│ 4. 執行: search("NY temp") → 10°C       │
│ 5. LLM: "現在計算總和"                    │
│ 6. 執行: math("15 + 10") → 25°C         │
│ 總 LLM 調用: 3次                         │
│ 總時間: ~6-8秒                            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ LLM Compiler                             │
├─────────────────────────────────────────┤
│ 1. LLM: "規劃完整任務流程"                │
│    → Task 1: search("SF temp")          │
│    → Task 2: search("NY temp")          │
│    → Task 3: math("${1} + ${2}")        │
│                                          │
│ 2. 執行階段:                              │
│    並行: Task 1 + Task 2 (同時進行)      │
│    等待: Task 3 (依賴 1 和 2)            │
│                                          │
│ 總 LLM 調用: 1次(規劃) + 1次(驗證)       │
│ 總時間: ~3-4秒                            │
└─────────────────────────────────────────┘
```

### 核心優勢總結

**1. 時間效率 (Time Efficiency)**
- 通過並行執行,可將執行時間縮短 40-50%
- 特別適合需要多次 API 調用的任務

**2. 經濟效益 (Cost Efficiency)**
- 減少 LLM 調用次數,降低 API 成本
- 在大規模應用中可節省顯著費用

**3. 可靠性 (Reliability)**
- 清晰的依賴管理,減少執行錯誤
- 支援任務失敗後的重新規劃

**4. 可擴展性 (Scalability)**
- 易於添加新工具和功能
- 支援複雜的多步驟工作流程

### 實際應用範例

#### 範例 1: 數據分析任務
```
問題: "比較蘋果和微軟過去一年的股價表現"

LLM Compiler 規劃:
1. get_stock_data("AAPL", "1y")  # 可並行
2. get_stock_data("MSFT", "1y")  # 可並行
3. calculate_performance("${1}")  # 依賴任務1
4. calculate_performance("${2}")  # 依賴任務2
5. compare("${3}", "${4}")        # 依賴任務3和4

執行時間: ~5秒 (vs 傳統方法的 ~12秒)
```

#### 範例 2: 多城市資訊查詢
```
問題: "東京、倫敦、紐約的天氣和當地時間"

LLM Compiler 規劃:
1. weather("Tokyo")    # 三個任務可並行
2. weather("London")   #
3. weather("NYC")      #
4. time("Tokyo")       # 三個任務可並行
5. time("London")      #
6. time("NYC")         #
7. format_results("${1-6}")  # 依賴所有前面的任務

執行時間: ~3秒 (vs 傳統方法的 ~15秒)
```

---

## 為什麼需要它?

### 問題場景
假設用戶問:「舊金山的溫度加上紐約的溫度是多少?」

**傳統方法的問題**:
```
步驟 1: 查詢舊金山溫度 → 等待結果 → 得到 15°C
步驟 2: 查詢紐約溫度 → 等待結果 → 得到 10°C  
步驟 3: 計算 15 + 10 → 25°C
總時間: 可能需要 6-10 秒
```

**LLM Compiler 的優勢**:
```
步驟 1: 同時查詢舊金山和紐約溫度(平行處理)
步驟 2: 兩個結果都回來後,立即計算
總時間: 可能只需要 3-5 秒
```

### 節省成本
- 傳統方法可能需要多次調用 LLM 來決定「下一步做什麼」
- LLM Compiler 一次規劃所有步驟,減少 LLM 調用次數
- 每次調用都要花錢,所以這能大幅降低成本!

---

## 核心概念解釋

### 0. LangGraph 基礎

在深入 LLM Compiler 之前,我們需要先理解 **LangGraph** - 這是構建 LLM Compiler 的底層框架。

#### 什麼是 LangGraph?

**簡單定義**: LangGraph 是一個用於構建有狀態、多步驟 AI 應用的框架。

**日常比喻**:
- 想像一個工作流程圖,每個節點是一個步驟
- LangGraph 讓你定義這些步驟和它們之間的連接
- 就像組裝樂高積木,每個積木是一個功能單元

#### LangGraph 的關鍵組件

**1. 節點 (Nodes)**
- 代表一個具體的操作或功能
- 例如: "規劃任務"、"執行搜索"、"生成答案"

```python
# 定義一個節點
def plan_and_schedule(state):
    # 執行規劃邏輯
    return {"messages": new_messages}
```

**2. 邊 (Edges)**
- 連接節點,定義執行流程
- 兩種類型:
  - **普通邊**: 總是執行 A → B
  - **條件邊**: 根據條件決定走哪條路

```python
# 普通邊: START → plan
graph.add_edge(START, "plan_and_schedule")

# 條件邊: 根據結果決定下一步
graph.add_conditional_edges("join", should_continue)
```

**3. 狀態 (State)**
- 儲存整個流程中的信息
- 在各個節點間共享和更新

```python
class State(TypedDict):
    messages: list  # 對話歷史
    tasks: list     # 待執行任務
    observations: dict  # 已完成任務的結果
```

#### LangGraph 執行流程示例

```python
# 創建圖
graph = StateGraph(State)

# 添加節點
graph.add_node("規劃", planner)
graph.add_node("執行", executor)
graph.add_node("回答", answerer)

# 定義流程
graph.add_edge(START, "規劃")
graph.add_edge("規劃", "執行")
graph.add_edge("執行", "回答")
graph.add_edge("回答", END)

# 執行
chain = graph.compile()
result = chain.invoke({"messages": [user_question]})
```

**流程圖**:
```
START → 規劃 → 執行 → 回答 → END
```

#### 為什麼需要 LangGraph?

**1. 狀態管理**
- 自動處理信息在各步驟間的傳遞
- 不用手動管理複雜的變量

**2. 靈活控制流**
- 可以循環、分支、重試
- 支援複雜的業務邏輯

**3. 可視化和調試**
- 清晰的流程圖
- 容易找出問題所在

**4. 可組合性**
- 小節點可以組合成大系統
- 可重用的組件

#### LangGraph vs 傳統方法

**傳統方法 (Sequential)**:
```python
result1 = step1()
result2 = step2(result1)
result3 = step3(result2)
# 難以處理條件分支和循環
```

**LangGraph 方法**:
```python
# 定義流程圖,自動處理狀態傳遞
graph.add_edge("step1", "step2")
graph.add_conditional_edges("step2", decide_next)
# 清晰、靈活、易維護
```

#### 與 LLM Compiler 的關係

LLM Compiler 使用 LangGraph 來:
1. **組織三大組件**: Planner、Task Fetcher、Joiner 都是 LangGraph 的節點
2. **管理工作流**: 使用條件邊實現重規劃邏輯
3. **維護狀態**: 追蹤任務進度和結果

### 1. 工具 (Tools) 詳解

#### 什麼是工具?

**定義**: 工具是 AI 可以調用的外部函數或服務。

**為什麼需要工具?**
- LLM 本身只能生成文本
- 無法執行實際操作(搜索、計算、查詢數據庫等)
- 工具讓 LLM 能夠"做事",而不只是"說話"

#### 工具的組成部分

**1. 工具名稱**
```python
name = "tavily_search"
```

**2. 工具描述**
```python
description = "搜索引擎工具,用於查找即時信息"
```
- LLM 根據描述決定何時使用這個工具

**3. 輸入參數 (Schema)**
```python
class SearchInput(BaseModel):
    query: str  # 搜索查詢
    max_results: int = 5  # 最多返回幾個結果
```

**4. 執行函數**
```python
def _run(self, query: str, max_results: int = 5):
    # 實際執行搜索
    results = search_api.search(query, max_results)
    return results
```

#### 工具調用流程

```
1. 用戶問題: "舊金山的天氣如何?"
   ↓
2. LLM 分析: "需要搜索最新天氣信息"
   ↓
3. LLM 生成工具調用:
   {
     "tool": "tavily_search",
     "args": {"query": "San Francisco weather"}
   }
   ↓
4. 系統執行工具
   ↓
5. 返回結果: "舊金山: 15°C, 多雲"
   ↓
6. LLM 整合結果生成回答
```

#### 常見工具類型

**1. 搜索工具**
```python
from langchain_tavily import TavilySearch

search = TavilySearch(
    max_results=1,
    description="搜索引擎,用於查找最新信息"
)
```

**2. 計算工具**
```python
from math_tools import get_math_tool

calculator = get_math_tool(llm)
# 可以解決數學問題、執行運算
```

**3. 資料庫查詢工具**
```python
@tool
def query_database(query: str) -> str:
    """查詢產品資料庫"""
    result = db.execute(query)
    return result
```

**4. API 調用工具**
```python
@tool  
def get_weather(city: str) -> str:
    """獲取指定城市的天氣"""
    response = weather_api.get(city)
    return response.json()
```

#### 自定義工具範例

```python
from langchain.tools import tool

@tool
def fibonacci(n: int) -> int:
    """計算斐波那契數列的第 n 項"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 使用
result = fibonacci.invoke({"n": 10})
print(result)  # 55
```

#### 工具的最佳實踐

**1. 清晰的描述**
```python
# ❌ 不好的描述
description = "搜索"

# ✅ 好的描述  
description = "在網上搜索最新信息。適用於需要即時數據、新聞、天氣等場景。"
```

**2. 明確的參數**
```python
class SearchArgs(BaseModel):
    query: str = Field(description="要搜索的具體問題或關鍵詞")
    max_results: int = Field(default=5, description="返回的最大結果數量")
```

**3. 錯誤處理**
```python
@tool
def safe_divide(a: float, b: float) -> str:
    """安全除法,處理除零錯誤"""
    try:
        return str(a / b)
    except ZeroDivisionError:
        return "錯誤: 不能除以零"
```

### 2. DAG (有向無環圖) - Directed Acyclic Graph

**什麼是圖?**
想像一張地鐵路線圖,各個站點(節點)之間有路線(邊)連接。

**什麼是「有向」?**
路線有方向性,就像單行道,只能從 A 到 B,不能反向。

**什麼是「無環」?**
不會繞圈圈回到起點。就像任務流程,不會陷入無限循環。

**在 LLM Compiler 中的應用**:
```
任務 1: 查詢舊金山溫度 (沒有依賴,可以立即執行)
任務 2: 查詢紐約溫度 (沒有依賴,可以立即執行)
任務 3: 計算總和 (依賴任務 1 和 2,必須等它們完成)

DAG 示意:
[任務1] ──┐
           ├─→ [任務3]
[任務2] ──┘
```

### 3. 並行處理 (Parallel Processing) 深入理解

#### 什麼是並行處理?

**定義**: 同時執行多個獨立的任務,而不是一個接一個地執行。

**日常生活類比**:

**順序處理 (Sequential)**:
```
早上的routine:
8:00-8:30  煮咖啡 ☕  
8:30-9:00  洗衣服 👕 (等待)
9:00-9:30  吃早餐 🍳
總時間: 1.5 小時
```

**並行處理 (Parallel)**:
```
早上的routine:
8:00-8:30  煮咖啡 ☕ + 同時啟動洗衣機 👕
8:30-9:00  吃早餐 🍳 (洗衣機還在運轉)
總時間: 1 小時 (節省 30 分鐘!)
```

#### 為什麼並行處理能加速?

**關鍵概念: 等待時間 (Wait Time)**

當你調用 API 或搜索時:
```
發送請求 (0.1秒) → 等待服務器處理 (2秒) → 接收結果 (0.1秒)
```

在等待的 2 秒內,CPU 是空閒的!並行處理就是利用這段時間執行其他任務。

#### Python 中的並行實現

**1. 使用 ThreadPoolExecutor**

```python
from concurrent.futures import ThreadPoolExecutor, wait

# 定義要執行的任務
def search_sf_temp():
    return tavily_search("San Francisco temperature")

def search_ny_temp():
    return tavily_search("New York temperature")

# 並行執行
with ThreadPoolExecutor() as executor:
    # 提交任務到線程池
    future1 = executor.submit(search_sf_temp)
    future2 = executor.submit(search_ny_temp)
    
    # 等待所有任務完成
    wait([future1, future2])
    
    # 獲取結果
    sf_temp = future1.result()  # "15°C"
    ny_temp = future2.result()  # "10°C"
```

**時間對比**:
```
順序執行:
Task1: 2秒 + Task2: 2秒 = 4秒總時間

並行執行:
Task1: 2秒 }
Task2: 2秒 } 同時進行 = 2秒總時間
```

**2. 使用 asyncio (異步方式)**

```python
import asyncio

async def search_sf_temp():
    return await async_search("San Francisco temperature")

async def search_ny_temp():
    return await async_search("New York temperature")

# 並行執行
async def main():
    results = await asyncio.gather(
        search_sf_temp(),
        search_ny_temp()
    )
    sf_temp, ny_temp = results

asyncio.run(main())
```

#### 並行 vs 並發 vs 順序

**順序 (Sequential)**:
```
Task1 ━━━━━━━━►
             Task2 ━━━━━━━━►
                          Task3 ━━━━━━━━►
時間 ════════════════════════════════════►
```

**並發 (Concurrent)**: 切換執行
```
Task1 ━━►  ━━►  ━━►
    Task2  ━━►  ━━►  ━━►
       Task3  ━━►  ━━►  ━━►
時間 ════════════════════════►
```

**並行 (Parallel)**: 真正同時執行
```
Task1 ━━━━━━━━━━━━━━►
Task2 ━━━━━━━━━━━━━━►
Task3 ━━━━━━━━━━━━━━►
時間 ════════════════►
```

#### 何時使用並行處理?

**✅ 適合並行的場景**:
1. **I/O 密集型任務** (API 調用、數據庫查詢、文件讀寫)
   - 大部分時間在等待
   - 並行可以大幅提升效率

2. **獨立任務**
   - 任務之間沒有依賴關係
   - 可以任意順序執行

**❌ 不適合並行的場景**:
1. **CPU 密集型任務** (複雜計算、圖像處理)
   - Python 的 GIL (Global Interpreter Lock) 會限制真正的並行
   - 需要使用 multiprocessing 而不是 threading

2. **有依賴關係的任務**
   - 任務 B 需要任務 A 的結果
   - 必須等待 A 完成

#### LLM Compiler 中的並行處理

```python
def schedule_task(task_unit):
    """調度和執行單個任務"""
    task, observations, config = task_unit
    
    # 等待依賴滿足
    while True:
        deps = task["dependencies"]
        # 檢查所有依賴是否完成
        if all(dep in observations for dep in deps):
            break
        time.sleep(0.1)  # 短暫等待
    
    # 依賴滿足,執行任務
    result = execute(task, observations, config)
    return result

# 並行調度所有任務
with ThreadPoolExecutor() as executor:
    # 同時提交所有任務
    futures = [
        executor.submit(schedule_task, (task, obs, config))
        for task in tasks
    ]
    
    # 等待所有完成
    wait(futures)
```

**實際執行示例**:
```
任務列表:
1. search("SF temp")      # 無依賴
2. search("NY temp")      # 無依賴  
3. math("${1} + ${2}")    # 依賴 1, 2

執行時間軸:
t=0.0s: 任務1開始 ━━━━━━━━━━━━►
t=0.0s: 任務2開始 ━━━━━━━━━━━━► (並行!)
t=0.0s: 任務3等待... (依賴未滿足)

t=2.0s: 任務1完成 ✓
t=2.1s: 任務2完成 ✓
t=2.1s: 任務3開始 ━━► (依賴滿足)
t=2.5s: 任務3完成 ✓

總時間: 2.5秒 (vs 順序執行的 6秒)
```

#### 並行處理的陷阱和注意事項

**1. 競態條件 (Race Condition)**
```python
# ❌ 危險: 多個線程修改同一個變量
counter = 0

def increment():
    global counter
    counter += 1

# 可能導致數據不一致

# ✅ 安全: 使用鎖
from threading import Lock

lock = Lock()
counter = 0

def safe_increment():
    with lock:
        global counter
        counter += 1
```

**2. 資源限制**
```python
# 限制並發數量,避免API限流
with ThreadPoolExecutor(max_workers=5) as executor:
    # 最多同時5個請求
    futures = [executor.submit(task) for task in tasks]
```

**3. 錯誤處理**
```python
future = executor.submit(risky_task)
try:
    result = future.result(timeout=10)  # 10秒超時
except Exception as e:
    print(f"任務失敗: {e}")
```

### 3. 依賴管理 (Dependency Management)

**什麼是依賴?**
任務 B 需要任務 A 的結果才能執行,我們就說「B 依賴於 A」。

**符號表示**:
- `$1` 或 `${1}` 表示「第 1 個任務的結果」
- 例如:`math("${1} + ${2}")` 表示「把第 1 和第 2 個任務的結果相加」

**代碼範例**:
```python
# 任務規劃
1. search("San Francisco temperature")  # 任務 1
2. search("New York temperature")       # 任務 2  
3. math("${1} + ${2}")                  # 任務 3,依賴於 1 和 2
```

---

## 三大組件詳解

### 組件 1: Planner(規劃器)

#### 作用
就像建築師,負責規劃整個工作流程,決定要執行哪些任務、順序如何。

#### 輸入輸出
- **輸入**:用戶的問題(例如:「舊金山的溫度加 5 是多少?」)
- **輸出**:一系列待執行任務的列表

#### 工作原理

**1. 接收問題**
```python
question = "What's the temperature in SF raised to the 3rd power?"
```

**2. 分析並生成計劃**
Planner 會調用 LLM,生成類似這樣的計劃:
```plaintext
Thought: First I need to find the temperature in San Francisco
1. search(query="San Francisco temperature")
Thought: Then I need to raise it to the 3rd power  
2. math(problem="${1} to the power of 3", context=["$1"])
3. join()
```

**3. 解析任務**
使用 `LLMCompilerPlanParser` 將文本解析成結構化的任務對象:
```python
Task {
    idx: 1,
    tool: TavilySearch,
    args: {"query": "San Francisco temperature"},
    dependencies: [],
    thought: "First I need to find the temperature..."
}
```

#### 關鍵代碼解析

```python
def create_planner(llm, tools, base_prompt):
    # 1. 準備工具描述
    tool_descriptions = "\n".join(
        f"{i + 1}. {tool.description}\n"
        for i, tool in enumerate(tools)
    )
    
    # 2. 填充提示模板
    planner_prompt = base_prompt.partial(
        num_tools=len(tools) + 1,  # +1 for join()
        tool_descriptions=tool_descriptions,
    )
    
    # 3. 組合成可執行鏈
    return (
        planner_prompt 
        | llm  # 調用 LLM 生成計劃
        | LLMCompilerPlanParser(tools=tools)  # 解析成任務
    )
```

**重新規劃(Re-planning)**

如果第一次嘗試失敗或不完整,Planner 可以根據之前的執行結果重新規劃:

```python
replanner_prompt = base_prompt.partial(
    replan='你已經得到了之前的計劃和執行結果,請基於這些信息創建新的計劃。'
           '在新計劃中,不要重複已經執行過的任務。'
)
```

---

### 組件 2: Task Fetching Unit(任務調度單元)

#### 作用
就像工廠的生產線調度員,負責:
1. 檢查每個任務的依賴是否滿足
2. 一旦依賴滿足,立即執行任務
3. 使用多線程並行處理獨立任務

#### 核心概念:依賴解析

**什麼是依賴解析?**
將 `${1}` 這樣的變量替換成實際的值。

**代碼實現**:
```python
def _resolve_arg(arg, observations):
    # observations 儲存已完成任務的結果
    # 例如: observations = {1: "15°C", 2: "10°C"}
    
    ID_PATTERN = r"\$\{?(\d+)\}?"  # 匹配 $1 或 ${1}
    
    def replace_match(match):
        idx = int(match.group(1))  # 提取數字
        return str(observations.get(idx))  # 返回對應結果
    
    return re.sub(ID_PATTERN, replace_match, arg)
```

**範例**:
```python
# 假設已有結果
observations = {1: "15", 2: "10"}

# 解析參數
arg = "math('${1} + ${2}')"
resolved = _resolve_arg(arg, observations)
# 結果: "math('15 + 10')"
```

#### 調度邏輯

**1. 檢查依賴**
```python
def schedule_pending_task(task, observations):
    while True:
        deps = task["dependencies"]  # 例如: [1, 2]
        
        # 檢查所有依賴是否都已完成
        if any([dep not in observations for dep in deps]):
            time.sleep(0.2)  # 依賴未滿足,等待
            continue
        
        # 依賴已滿足,執行任務!
        schedule_task.invoke({"task": task, "observations": observations})
        break
```

**2. 並行執行**
```python
with ThreadPoolExecutor() as executor:
    for task in tasks:
        if has_unsatisfied_dependencies(task):
            # 提交到線程池,等待依賴滿足
            futures.append(
                executor.submit(schedule_pending_task, task, observations)
            )
        else:
            # 沒有依賴,立即執行
            schedule_task.invoke({"task": task, "observations": observations})
    
    # 等待所有任務完成
    wait(futures)
```

#### 完整流程示意

```
時間軸:
t=0s:  [任務1開始] [任務2開始] (並行)
t=2s:  任務1完成 → 結果: "15°C"
t=2.5s: 任務2完成 → 結果: "10°C"
t=2.5s: 任務3開始 (依賴滿足) → math("15 + 10")
t=3s:  任務3完成 → 結果: "25"
```

---

### 組件 3: Joiner(連接器)

#### 作用
就像項目經理的最終審查,決定:
1. 是否已經得到足夠信息回答用戶?
2. 還是需要執行更多任務(重新規劃)?

#### 兩種可能的輸出

**1. FinalResponse(最終回應)**
```python
class FinalResponse(BaseModel):
    response: str  # 給用戶的答案
```

範例:
```python
{
    "thought": "我已經得到舊金山的溫度是15°C",
    "action": FinalResponse(
        response="舊金山目前的溫度是 15°C"
    )
}
```

**2. Replan(重新規劃)**
```python
class Replan(BaseModel):
    feedback: str  # 對之前嘗試的分析和建議
```

範例:
```python
{
    "thought": "我需要更多信息來回答這個問題",
    "action": Replan(
        feedback="之前的搜索沒有找到確切溫度,需要用不同的搜索詞重試"
    )
}
```

#### 決策邏輯

```python
def _parse_joiner_output(decision: JoinOutputs):
    if isinstance(decision.action, Replan):
        # 需要重新規劃!
        return {
            "messages": [
                SystemMessage(content=f"上次的反饋: {decision.action.feedback}")
            ]
        }
    else:
        # 已經可以回答!
        return {
            "messages": [
                AIMessage(content=decision.action.response)
            ]
        }
```

#### 實際運作範例

**場景**:用戶問「找出東京當前溫度,並用記憶卡的形式總結」

**第一輪**:
```
Planner → 任務: search("Tokyo temperature")
執行 → 結果: "東京: 18°C"
Joiner → 決策: 需要 Replan!
反饋: "我找到了溫度,但還沒有製作記憶卡格式"
```

**第二輪**:
```
Planner → 任務: 根據溫度數據製作記憶卡
執行 → 生成格式化的記憶卡
Joiner → 決策: FinalResponse!
回應: "【記憶卡】正面:東京溫度 背面:18°C"
```

---

## 完整代碼範例

### 設置環境

```python
# 1. 載入環境變量
%load_ext dotenv
%dotenv ../../05_src/.env

# 2. 設置 API 金鑰
import os
import getpass

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key: ")
if "TAVILY_API_KEY" not in os.environ:
    os.environ["TAVILY_API_KEY"] = getpass.getpass("Tavily API Key: ")
```

**知識補充 - 什麼是環境變量?**
- 就像保險箱裡的密碼,避免直接寫在代碼中
- `.env` 文件儲存敏感信息(API 金鑰等)
- `dotenv` 套件幫我們安全地載入這些信息

### 定義工具

```python
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from math_tools import get_math_tool

# 創建計算工具
calculate = get_math_tool(ChatOpenAI(model="gpt-4o"))

# 創建搜索工具
search = TavilySearch(
    max_results=1,
    description='tavily_search(query="搜索查詢") - 搜索引擎工具'
)

# 工具列表
tools = [search, calculate]
```

**知識補充 - 什麼是工具(Tools)?**
- 工具是 AI 可以調用的函數
- `search`:在網上搜索信息
- `calculate`:執行數學計算
- AI 會根據問題自動選擇合適的工具

### 測試計算工具

```python
# 測試:計算「舊金山溫度加 5」
result = calculate.invoke({
    "problem": "What's the temp of sf + 5?",
    "context": ["The temperature of sf is 32 degrees"]
})

print(result)  # 輸出: 37
```

**解析**:
- `problem`:要解決的數學問題
- `context`:提供背景信息(舊金山是 32 度)
- 工具會自動提取數字並計算 32 + 5 = 37

### 創建 Planner

```python
from langchain import hub

# 載入預設的提示模板
prompt = hub.pull("wfh/llm-compiler")

# 創建規劃器
llm = ChatOpenAI(model="gpt-4o-mini")
planner = create_planner(llm, tools, prompt)
```

**測試 Planner**:
```python
question = "What's the temperature in SF raised to the 3rd power?"

# 串流輸出計劃
for task in planner.stream([HumanMessage(content=question)]):
    print(f"工具: {task['tool']}")
    print(f"參數: {task['args']}")
    print("---")
```

**預期輸出**:
```
工具: TavilySearch
參數: {'query': 'San Francisco temperature'}
---
工具: math
參數: {'problem': '${1} to the power of 3', 'context': ['$1']}
---
工具: join
參數: {}
---
```

### 組合成完整圖

```python
from langgraph.graph import END, StateGraph, START

# 定義狀態
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 創建圖
graph_builder = StateGraph(State)

# 添加節點
graph_builder.add_node("plan_and_schedule", plan_and_schedule)
graph_builder.add_node("join", joiner)

# 定義邊
graph_builder.add_edge(START, "plan_and_schedule")
graph_builder.add_edge("plan_and_schedule", "join")

# 條件邊:決定是結束還是繼續
def should_continue(state):
    messages = state["messages"]
    if isinstance(messages[-1], AIMessage):
        return END  # 已有最終答案
    return "plan_and_schedule"  # 需要重新規劃

graph_builder.add_conditional_edges("join", should_continue)

# 編譯圖
chain = graph_builder.compile()
```

**圖結構示意**:
```
START → plan_and_schedule → join → [END 或 回到 plan_and_schedule]
```

---

## 實際應用場景

### 場景 1: 簡單查詢

**問題**:「紐約的 GDP 是多少?」

```python
for step in chain.stream(
    {"messages": [HumanMessage(content="What's the GDP of New York?")]}
):
    print(step)
```

**執行流程**:
```
1. Planner 生成計劃:
   - 任務1: search("New York GDP")
   - 任務2: join()

2. Task Fetching Unit 執行:
   - 執行搜索 → 得到結果

3. Joiner 決定:
   - 已有足夠信息
   - 返回 FinalResponse: "紐約的 GDP 約為 1.5 兆美元"
```

### 場景 2: 多跳查詢(需要多次搜索)

**問題**:「最老的鵡鵡活了多久,比平均壽命長多少?」

```python
steps = chain.stream({
    "messages": [HumanMessage(
        content="What's the oldest parrot alive, and how much longer is that than the average?"
    )]
})
```

**執行流程**:
```
第一輪規劃:
1. search("oldest parrot alive")
2. search("average parrot lifespan")  
3. math("${1} - ${2}")

執行:
- 任務1和2並行執行
- 任務3等待前兩個完成後計算

Joiner:
- FinalResponse: "最老的鵡鵡活了83歲,比平均壽命(25歲)長58年"
```

### 場景 3: 多步驟數學

**問題**:「計算 ((3*(4+5)/0.5)+3245) + 8,然後計算 32/4.23,最後求兩者之和」

```python
chain.stream({
    "messages": [HumanMessage(
        content="What's ((3*(4+5)/0.5)+3245) + 8? What's 32/4.23? What's the sum of those two values?"
    )]
})
```

**LLM Compiler 的優勢**:
```
傳統方法(Sequential):
1. 計算第一個表達式 → 等待
2. 計算第二個表達式 → 等待  
3. 計算總和

LLM Compiler(Parallel):
1. 同時計算兩個表達式 (並行!)
2. 兩個都完成後,立即計算總和

時間節省: 約 40-50%
```

### 場景 4: 複雜重規劃

**問題**:「找出東京當前溫度,然後用記憶卡總結這個信息」

```python
chain.stream({
    "messages": [HumanMessage(
        content="Find the current temperature in Tokyo, then respond with a flashcard summarizing this information"
    )]
})
```

**執行流程**:
```
第一輪:
Planner → search("Tokyo temperature")
執行 → "東京: 18°C"
Joiner → Replan("找到溫度了,但還沒製作記憶卡")

第二輪:
Planner → 生成記憶卡格式的任務
執行 → 製作記憶卡
Joiner → FinalResponse(返回格式化的記憶卡)
```

---

## 常見問題解答

### Q1: LLM Compiler 和普通 AI 代理有什麼區別?

**普通 AI 代理(Chain-of-Thought)**:
```
問題 → 思考步驟1 → 執行 → 思考步驟2 → 執行 → ... → 答案
```
- 每次只執行一個動作
- 需要頻繁調用 LLM 決定下一步
- 慢且昂貴

**LLM Compiler**:
```
問題 → 一次性規劃所有步驟 → 並行執行 → 答案
```
- 多個獨立任務同時執行
- 減少 LLM 調用次數
- 快且經濟

### Q2: 什麼時候應該使用 LLM Compiler?

**適合使用的情況**:
- ✅ 任務可以分解成多個子任務
- ✅ 某些子任務可以並行處理
- ✅ 需要多次工具調用(搜索、計算等)
- ✅ 對響應速度有要求
- ✅ 需要控制成本

**不適合使用的情況**:
- ❌ 簡單的單步驟問題
- ❌ 任務之間有複雜的循環依賴
- ❌ 需要頻繁的用戶交互

### Q3: DAG 如何防止無限循環?

**無環的保證**:
- 任務只能依賴「之前」的任務(索引更小的任務)
- 不允許「未來」的任務(索引更大的任務)
- 自然形成「單向流動」,不可能循環

**範例**:
```python
# ✅ 合法
1. search("A")
2. search("B") 
3. math("${1} + ${2}")  # 依賴 1 和 2

# ❌ 非法(會被檢測並拒絕)
1. search("A")
2. math("${3}")  # 不能依賴還沒定義的任務3!
3. search("${1}")
```

### Q4: 並行處理會不會造成資源問題?

**資源管理**:
```python
# 使用線程池控制併發數
with ThreadPoolExecutor(max_workers=5) as executor:
    # 最多同時執行 5 個任務
    futures = [executor.submit(task) for task in tasks]
```

**建議**:
- 根據 API 速率限制調整 `max_workers`
- 監控內存使用情況
- 對於大規模任務,考慮使用任務隊列(如 Celery)

### Q5: 如何處理任務失敗?

**錯誤處理機制**:
```python
def _execute_task(task, observations, config):
    try:
        return tool.invoke(args, config)
    except Exception as e:
        # 返回錯誤信息,而不是崩潰
        return f"ERROR: {repr(e)}"
```

**Joiner 的角色**:
- 檢測到錯誤信息
- 決定是否需要 Replan
- 生成新的策略重試

### Q6: 如何優化性能?

**優化策略**:

1. **減少 LLM 調用**:
```python
# 使用更小的模型做規劃
planner_llm = ChatOpenAI(model="gpt-4o-mini")  # 便宜快速

# 使用更強的模型做 Joining
joiner_llm = ChatOpenAI(model="gpt-4o")  # 更準確
```

2. **緩存結果**:
```python
# 如果同樣的查詢重複出現,使用緩存
from langchain.cache import InMemoryCache
langchain.llm_cache = InMemoryCache()
```

3. **限制消息歷史長度**:
```python
def select_recent_messages(state, max_messages=10):
    return {"messages": state["messages"][-max_messages:]}
```

### Q7: 實現中有哪些已知限制?

**當前限制**:

1. **解析格式脆弱**:
   - 工具參數超過 1-2 個時容易出錯
   - 解決:使用 streaming tool calling

2. **變量替換不夠強健**:
   - `${1}` 語法在複雜情況下可能失敗
   - 解決:使用 fine-tuned 模型或更嚴格的語法

3. **狀態過長**:
   - 多次重規劃會導致消息歷史過長
   - 解決:添加消息壓縮器

**改進建議**:
```python
# 1. 使用 Pydantic 模型約束參數
class SearchArgs(BaseModel):
    query: str
    max_results: int = 1

# 2. 實現消息壓縮
def compress_messages(messages, max_tokens=4000):
    # 保留最重要的消息
    # 壓縮或刪除冗余內容
    pass
```

---

## 關鍵要點總結

### 🎯 核心優勢
1. **速度**:並行執行獨立任務,大幅縮短總時間
2. **成本**:減少 LLM 調用次數,降低費用
3. **可靠性**:清晰的依賴管理,減少錯誤

### 🏗️ 架構組件
1. **Planner**:規劃任務 DAG
2. **Task Fetching Unit**:調度和執行任務
3. **Joiner**:決定完成或重規劃

### 💡 最佳實踐
1. 為工具提供清晰的描述
2. 合理設置並發限制
3. 實現錯誤處理和重試機制
4. 監控和優化性能

### ⚠️ 注意事項
1. 不是所有問題都適合並行處理
2. 需要仔細設計工具的描述和參數
3. 複雜的重規劃可能增加延遲

---

## 延伸學習資源

### 論文
- [LLMCompiler 原論文](https://arxiv.org/abs/2312.04511)
- 關鍵概念:DAG 調度、依賴解析、動態規劃

### 相關框架
- **LangGraph**:構建狀態機式的 AI 應用
- **LangChain**:LLM 應用開發框架
- **Agent Frameworks**:AutoGPT, BabyAGI 等

### 進階主題
1. **Fine-tuning Planner**:訓練專門的規劃模型
2. **分布式執行**:將任務分配到多台機器
3. **成本優化**:智能選擇模型和緩存策略

---

## 實踐練習

### 練習 1:簡單的溫度查詢
```python
# 任務:查詢兩個城市溫度並比較
question = "Compare the temperature of Tokyo and London"

# 預期計劃:
# 1. search("Tokyo temperature")
# 2. search("London temperature")  
# 3. math("${1} - ${2}")
# 4. join()
```

### 練習 2:多步驟計算
```python
# 任務:複雜數學表達式
question = "Calculate (100 + 50) * 2, then divide by 3"

# 提示:應該分解成多個 math() 調用
```

### 練習 3:自定義工具
```python
# 嘗試添加新工具,例如「天氣預報工具」
from langchain_core.tools import StructuredTool

def get_weather_forecast(city: str, days: int = 3):
    # 實現獲取天氣預報的邏輯
    pass

weather_tool = StructuredTool.from_function(
    name="weather_forecast",
    func=get_weather_forecast,
    description="獲取指定城市未來幾天的天氣預報"
)

tools = [search, calculate, weather_tool]
```

---

## 結語

LLM Compiler 代表了 AI 代理架構的重要進步,通過智能的任務規劃和並行執行,顯著提升了性能和成本效益。

雖然實現有一定複雜度,但理解其核心原理(DAG、並行處理、依賴管理)後,你就能構建高效的 AI 應用。

**下一步行動**:
1. 運行筆記本中的範例代碼
2. 嘗試自己的問題和工具
3. 深入研究 LangGraph 文檔
4. 實驗不同的優化策略

祝學習愉快! 🚀
