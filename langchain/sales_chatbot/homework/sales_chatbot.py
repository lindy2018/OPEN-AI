import gradio as gr
import random
import time
import os
import openai

from typing import List

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_base = "https://hzf-gpt.openai.azure.com/"
api_version = "2023-07-01-preview"
open_ai_type = 'azure'


def getOpenAIEmbeddingObject() -> OpenAIEmbeddings:
    """
    获取Azure OpenAI Embeddings对象
    """
    embeddings = OpenAIEmbeddings(
        deployment="embedding",  # 部署名称
        openai_api_base=api_base,
        openai_api_type=open_ai_type,
        openai_api_key=api_key,
        chunk_size=1,  # 限定并发数为1
    )
    return embeddings

def getChatOpenAIObject() -> ChatOpenAI:
    """
    获取ChatOpenAI对象
    """
    openai.api_type = 'azure'
    openai.api_version=api_version
    chat = ChatOpenAI(
        deployment_id="gpt-4",  # 部署名称
        openai_api_base=api_base,
        openai_api_key=api_key,
        temperature=0
    )
    return chat

def initialize_sales_bot(vector_store_dir: str = "real_estates_sale"):
    db = FAISS.load_local(vector_store_dir, getOpenAIEmbeddingObject())

    llm = getChatOpenAIObject()

    global SALES_BOT
    SALES_BOT = RetrievalQA.from_chain_type(
        llm,
        retriever=db.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.8},
        ),
    )
    # 返回向量数据库的检索结果
    SALES_BOT.return_source_documents = True

    return SALES_BOT


def sales_chat(message, history):
    print(f"[message]{message}")
    print(f"[history]{history}")
    # TODO: 从命令行参数中获取
    enable_chat = True

    ans = SALES_BOT({"query": message})
    # 如果检索出结果，或者开了大模型聊天模式
    # 返回 RetrievalQA combine_documents_chain 整合的结果
    if ans["source_documents"] or enable_chat:
        print(f"[result]{ans['result']}")
        print(f"[source_documents]{ans['source_documents']}")
        return ans["result"]
    # 否则输出套路话术
    else:
        return "这个问题我要问问领导"


def launch_gradio():
    demo = gr.ChatInterface(
        fn=sales_chat,
        title="房产销售",
        # retry_btn=None,
        # undo_btn=None,
        chatbot=gr.Chatbot(height=600),
    )

    demo.launch(share=False, server_name="0.0.0.0")


if __name__ == "__main__":
    # 初始化房产销售机器人
    initialize_sales_bot()
    # 启动 Gradio 服务
    launch_gradio()
