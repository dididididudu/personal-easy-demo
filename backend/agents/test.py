
import base_agent
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore
from dotenv import load_dotenv
import os
from 智能客服系统.backend.Assessment import Assessment
from langgraph.store.memory import M
def run_agent(user_input):
    #运行智能客服系统
    process_cus = user_input
    #检索知识库最匹配的数据
    vector_store = RedisVectorStore(embeddings=embeddings, config=config)
    retriever = vector_store.as_retriever()
    relation = retriever.invoke(process_cus, k=2)
    res = agent1.process_query(user_input=process_cus, user_id="user1", knowledge_base=relation)
    ass = assessment.evaluate_response(user_input, res, relation)
    print(ass)
    return res
import gradio as gr
import random
chat_history = []
def process_query(user_input: str,history:list):
    """处理用户查询"""
    result = run_agent(user_input)
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": result})

    return history,""
if __name__ == "__main__":
    #初始化智能体
    agent1 = base_agent.CustomerServiceAgent()
    #连接Redis数据库
    redis_url = "redis://:@127.0.0.1:6379/0"
    config = RedisConfig(
        index_name="faq-index",
        redis_url=redis_url)
    load_dotenv()
    os.environ["DASHSCOPE_API_KEY"] = os.getenv("OPENAI_API_KEY")
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v1",
    )
    assessment = Assessment.ResponseQualityEvaluator ()
    #使用gradio创建简单的前端页面
    with gr.Blocks() as demo:
        gr.Markdown("# 智能客服系统")
        chatbot = gr.Chatbot(chat_history,label="对话记录")
        with  gr.Row():
            with gr.Column():
                input_text = gr.Textbox(label="用户输入")
                submit_button = gr.Button("提交")
        input_text.submit(
            fn=process_query,
            inputs=[input_text, chatbot],
            outputs=[chatbot, input_text]
        )
        submit_button.click(
            fn=process_query,
            inputs=[input_text, chatbot],  # 注意这里使用chatbot作为历史输入
            outputs=[chatbot, input_text]  # 输出更新后的chatbot和清空的输入框
        )
    demo.launch()