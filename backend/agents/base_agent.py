from typing import List, Dict, Any, Optional
from langchain.agents import create_agent,AgentState
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.tools import tool
import datetime
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
import json
from pydantic import StrictStr
import os

class CustomerServiceAgent:
    """智能客服基础Agent"""

    def __init__(self, model_name: str = "qwen-plus", temperature: float = 0.1):
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=StrictStr(self._get_api_key()),
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        # 创建Agent
        self.agent = self._create_agent()

    def _get_api_key(self) -> str:
        """安全获取API密钥"""
        import os
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("OPENAI_API_KEY")

    def _create_agent(self) :
        """创建React Agent"""

        # 自定义客服prompt

        class CustomMemory(AgentState):
            user_id: str
            preferences: Dict[str, Any]

        #设定工单创建工具
        @tool
        def create_ticket(key : str) :
            """
            工单创建工具，无法解决的客服问题要求使用这个工具创建工单
            Args：
                key：用户反映的问题的关键字
            """
            # prompt = {"messages":[{"role": "user", "content":"总结问题的关键词"}]}
            # res = self.agent.invoke(prompt,config={"configurable": {"thread_id": "user1"}})
            ticket_data = {
                "main_error":key,
                "ticket_id": f"TICKET_{int(datetime.datetime.now().timestamp())}",
                "created_time": datetime.datetime.now().isoformat(),
                "expected_resolution_time": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
            }

            # 确定文件路径（同级目录下的 tickets.json）
            file_path = os.path.join(os.path.dirname(__file__), "tickets.json")

            # 读取现有工单数据
            tickets = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        tickets = json.load(f)
                        print("已读取工单数据")
                        print(file_path)
                    except json.JSONDecodeError:
                        print("文件已损坏，请检查文件内容")
                        tickets = []

            # 添加新工单
            tickets.append(ticket_data)

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(tickets, f, ensure_ascii=False, indent=2)
            """创建工单"""
            return f"工单已创建，预计解决时间：{datetime.datetime.now() + datetime.timedelta(days=1)},"
        agent = create_agent(
            model=self.llm,
            tools=[create_ticket],
            system_prompt="你是一个专业的客服助手。叫老六",
            checkpointer=InMemorySaver(),
        )


        return agent

    def process_query(self, user_input: str, user_id: str = None,knowledge_base: list = None) -> Dict[str, Any]:
        """处理用户查询"""

        print("用户问题：", user_input)
        custom_prompt = ChatPromptTemplate.from_messages(["""你是一个专业的客服助手。请根据以下信息帮助用户解决问题：
                系统限制：
                1. 如果用户的问题需要个人信息验证，请要求用户提供订单号或注册邮箱
                2. 对于技术问题，先尝试从知识库寻找解决方案
                3. 如果问题复杂，建议调用工单创建工具，创建工单并告知预计解决时间，只有用户反映了问题才能创建工单
                历史对话：
                当前问题：{input}
                知识库：{Knowledge}
                """])
        prompt = custom_prompt.format_prompt(input=user_input, Knowledge=knowledge_base)
        f_prompt = {"messages":[{"role": "user", "content": prompt.to_messages()[0].content}]}
        config1 = {"configurable": {"thread_id": user_id}}
            # 执行Agent
        response = self.agent.invoke(f_prompt,config=config1)


        return response['messages'][-1].content



