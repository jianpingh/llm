# LangGraph 实用指南

## 什么是 LangGraph？

LangGraph 是一个用于构建有状态、多参与者应用程序的库，基于 LangChain 构建。它扩展了 LangChain Expression Language，增加了循环、持久性和人机交互的能力。

## 核心概念

### 1. 状态图（StateGraph）

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class GraphState(TypedDict):
    messages: list
    user_input: str
    result: str

# 创建状态图
workflow = StateGraph(GraphState)
```

### 2. 节点（Nodes）

节点是图中的处理单元，每个节点都是一个函数：

```python
def process_input(state):
    """处理用户输入的节点"""
    user_input = state["user_input"]
    # 处理逻辑
    return {"result": f"处理结果: {user_input}"}

# 添加节点
workflow.add_node("process", process_input)
```

### 3. 边（Edges）

边定义了节点之间的连接关系：

```python
# 添加边
workflow.add_edge("process", END)

# 条件边
def should_continue(state):
    if state["result"]:
        return "end"
    return "continue"

workflow.add_conditional_edges(
    "process",
    should_continue,
    {"end": END, "continue": "process"}
)
```

## 实际应用案例

### 案例1：智能对话系统

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]
    context: str
    intent: str

def analyze_intent(state):
    """分析用户意图"""
    last_message = state["messages"][-1]
    # 意图分析逻辑
    intent = classify_intent(last_message.content)
    return {"intent": intent}

def generate_response(state):
    """生成回复"""
    intent = state["intent"]
    context = state["context"]
    # 生成回复逻辑
    response = create_response(intent, context)
    return {"messages": [AIMessage(content=response)]}

# 构建工作流
workflow = StateGraph(ConversationState)
workflow.add_node("analyze", analyze_intent)
workflow.add_node("respond", generate_response)

workflow.add_edge("analyze", "respond")
workflow.add_edge("respond", END)

workflow.set_entry_point("analyze")
app = workflow.compile()
```

### 案例2：文档处理流水线

```python
class DocumentState(TypedDict):
    raw_text: str
    chunks: list
    embeddings: list
    summary: str

def chunk_document(state):
    """文档分块"""
    text = state["raw_text"]
    chunks = split_text(text, chunk_size=1000)
    return {"chunks": chunks}

def create_embeddings(state):
    """创建嵌入向量"""
    chunks = state["chunks"]
    embeddings = [embed_text(chunk) for chunk in chunks]
    return {"embeddings": embeddings}

def summarize_document(state):
    """文档摘要"""
    chunks = state["chunks"]
    summary = generate_summary(chunks)
    return {"summary": summary}

# 构建文档处理流水线
doc_workflow = StateGraph(DocumentState)
doc_workflow.add_node("chunk", chunk_document)
doc_workflow.add_node("embed", create_embeddings)
doc_workflow.add_node("summarize", summarize_document)

doc_workflow.add_edge("chunk", "embed")
doc_workflow.add_edge("embed", "summarize")
doc_workflow.add_edge("summarize", END)

doc_workflow.set_entry_point("chunk")
```

## 高级特性

### 1. 人机交互

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

def human_review(state):
    """需要人工审核的节点"""
    # 这里会暂停执行，等待人工输入
    return {"status": "pending_review"}

workflow.add_node("review", human_review)

# 编译时添加检查点
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
```

### 2. 持久化状态

```python
# 使用数据库作为检查点
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string("postgresql://...")
app = workflow.compile(checkpointer=checkpointer)

# 运行时指定线程ID
config = {"configurable": {"thread_id": "user_123"}}
result = app.invoke(initial_state, config=config)
```

### 3. 流式处理

```python
# 流式执行
for chunk in app.stream(initial_state, config=config):
    print(f"节点 {chunk['node']} 完成")
    print(f"状态更新: {chunk['state']}")
```

## 最佳实践

### 1. 状态设计

- 保持状态结构简单清晰
- 使用类型注解提高代码可读性
- 避免在状态中存储大量数据

### 2. 节点设计

- 每个节点职责单一
- 节点函数应该是纯函数
- 合理处理异常情况

### 3. 错误处理

```python
def safe_node(state):
    try:
        # 节点逻辑
        result = process_data(state)
        return {"result": result, "error": None}
    except Exception as e:
        return {"result": None, "error": str(e)}
```

### 4. 性能优化

- 使用异步节点处理并发
- 适当使用缓存机制
- 监控图执行性能

## 常见问题

### Q1: 如何处理循环逻辑？

使用条件边创建循环：

```python
def should_continue(state):
    if state["iteration_count"] < 5:
        return "continue"
    return "end"

workflow.add_conditional_edges(
    "process",
    should_continue,
    {"continue": "process", "end": END}
)
```

### Q2: 如何实现并行处理？

```python
from langgraph.graph import StateGraph, END

# 添加并行节点
workflow.add_node("parallel_1", node_1)
workflow.add_node("parallel_2", node_2)

# 从同一节点连接到多个并行节点
workflow.add_edge("start", "parallel_1")
workflow.add_edge("start", "parallel_2")

# 汇聚节点
workflow.add_node("merge", merge_results)
workflow.add_edge("parallel_1", "merge")
workflow.add_edge("parallel_2", "merge")
```

## 总结

LangGraph 为构建复杂的AI应用提供了强大的图计算框架。通过状态图、节点和边的组合，可以实现各种复杂的业务逻辑，同时保持代码的清晰和可维护性。

关键优势：
- 🔄 支持循环和条件逻辑
- 💾 内置状态持久化
- 🤝 人机交互支持
- 📊 可视化执行流程
- 🔧 易于调试和维护
