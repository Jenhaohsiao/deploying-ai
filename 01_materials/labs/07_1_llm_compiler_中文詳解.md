# LLM Compiler 中文詳解 - 給初學者的完整指南

## 📚 目錄
1. [什麼是 LLM Compiler?](#什麼是-llm-compiler)
2. [為什麼需要它?](#為什麼需要它)
3. [核心概念解釋](#核心概念解釋)
4. [三大組件詳解](#三大組件詳解)
5. [完整代碼範例](#完整代碼範例)
6. [實際應用場景](#實際應用場景)
7. [常見問題解答](#常見問題解答)

---

## 什麼是 LLM Compiler?

### 簡單比喻
想像你要辦一場派對,需要做很多事情:
- 買食材
- 準備場地
- 邀請朋友
- 準備音樂

**傳統做法**(一般 AI 代理):你一件一件做,做完一件才做下一件。

**LLM Compiler 做法**:聰明地分析哪些事可以同時進行(買食材和邀請朋友可以同時做),哪些必須等待(準備場地要先於佈置),然後平行處理,大幅縮短時間!

### 正式定義
LLM Compiler 是一個由 Kim 等人在 2023 年提出的 AI 代理架構,主要特點是:
1. **加速執行**:通過並行處理任務來提升速度
2. **節省成本**:減少不必要的 LLM 調用次數
3. **智能排程**:使用 DAG(有向無環圖)來管理任務依賴關係

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

### 1. DAG (有向無環圖) - Directed Acyclic Graph

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

### 2. 並行處理 (Parallel Processing)

**日常生活類比**:
- 單線程(Sequential):洗衣服 → 等待 → 晾衣服 → 等待 → 煮飯
- 多線程(Parallel):啟動洗衣機的同時開始煮飯,節省時間!

**代碼中的實現**:
```python
from concurrent.futures import ThreadPoolExecutor

# 使用線程池同時執行多個任務
with ThreadPoolExecutor() as executor:
    future1 = executor.submit(search_sf_temp)
    future2 = executor.submit(search_ny_temp)
    # 兩個任務同時進行!
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
