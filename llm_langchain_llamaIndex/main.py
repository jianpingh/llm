from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.openai import OpenAIEmbedding  # ✅ 新版导入方式

# 1️⃣ 代理版 OpenAI API Key 和代理地址
OPENAI_API_KEY = "sk-YL99cPdQUr7hbYg6ciOucPyN3NF7tgsz08DDF8lyDwPwfst1"  # 替换成你的 Key
OPENAI_API_BASE = "https://api.chatanywhere.tech/v1"  # 替换成你的代理地址

# 2️⃣ 使用 LlamaIndex 提供的 OpenAI Embedding（可走代理）
embed_model = OpenAIEmbedding(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE
)

# 3️⃣ 设置全局 Embedding
Settings.embed_model = embed_model

# 4️⃣ 加载文档并创建索引
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)

# 5️⃣ 创建检索引擎
query_engine = index.as_query_engine()

# 6️⃣ 用户问题
user_question = "什么是心理健康？"

# 7️⃣ LlamaIndex 检索上下文
retrieved_context = query_engine.query(user_question).response

# 8️⃣ LangChain LLM（同样走代理）
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE
)

# 9️⃣ LangChain 提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个心理健康领域的专家，回答用户问题时要专业、简洁。"),
    ("user", "问题：{question}\n\n相关上下文：{context}")
])

# 10️⃣ 拼接提示并生成回答
final_prompt = prompt.format_messages(
    question=user_question,
    context=retrieved_context
)
response = llm.invoke(final_prompt)

# 11️⃣ 输出结果
print("=== LlamaIndex 检索到的上下文 ===")
print(retrieved_context)
print("\n=== LangChain + LlamaIndex 生成的最终回答 ===")
print(response.content)
