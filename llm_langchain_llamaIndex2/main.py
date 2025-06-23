from langchain_community.embeddings import HuggingFaceEmbeddings  # ✅ 注意新版路径
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings

# 1️⃣ 使用 HuggingFace 本地 Embeddings（GPU 自动支持）
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 2️⃣ 将 Embedding 设置为 LlamaIndex 默认嵌入器
Settings.embed_model = embeddings

# 3️⃣ 加载文档
documents = SimpleDirectoryReader("data").load_data()

# 4️⃣ 创建索引并构建查询引擎
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# 5️⃣ 用户问题
user_question = "什么是心理健康？"

# 6️⃣ 检索上下文
retrieved_context = query_engine.query(user_question).response

# 7️⃣ LangChain LLM（走代理）
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key="sk-YL99cPdQUr7hbYg6ciOucPyN3NF7tgsz08DDF8lyDwPwfst1",
    base_url="https://api.chatanywhere.tech/v1"
)
# 8️⃣ 构建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个心理健康领域的专家，回答用户问题时要专业、简洁。"),
    ("user", "问题：{question}\n\n相关上下文：{context}")
])

# 9️⃣ 调用 LLM 生成回答
final_prompt = prompt.format_messages(
    question=user_question,
    context=retrieved_context
)
response = llm.invoke(final_prompt)

# 🔟 输出结果
print("=== LlamaIndex 检索到的上下文 ===")
print(retrieved_context)
print("\n=== LangChain + LlamaIndex 生成的最终回答 ===")
print(response.content)
