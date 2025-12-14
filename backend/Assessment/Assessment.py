#回复质量评估系统
import datetime
from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

class ResponseQualityEvaluator:
    """回复质量评估系统"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model="qwen-plus",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    def evaluate_response(self, user_query: str, agent_response: str, knowledge_base: list = None) -> Dict[str, Any]:
        """评估回复质量"""
        evaluation_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个客服回复质量评估专家，请客观评估以下客服回复的质量。"),
            ("user", """
            请根据以下维度评估客服回复质量，给出1-5分的评分（5分为最高）：

            用户问题：{user_query}
            客服回复：{agent_response}
            参考知识库：{knowledge_base}

            评估维度：
            1. 准确性：回复内容是否准确无误
            2. 完整性：是否全面回答了用户问题
            3. 相关性：回复是否与问题相关
            4. 友好度：语言表达是否礼貌专业
            5. 实用性：解决方案是否切实可行

            请给出各维度评分及总体评价。
            """)
        ])

        evaluator = evaluation_prompt | self.llm
        result = evaluator.invoke({
            "user_query": user_query,
            "agent_response": agent_response,
            "knowledge_base": knowledge_base or []
        })

        return {
            "evaluation_result": result.content,
            "timestamp": datetime.datetime.now().isoformat()
        }
