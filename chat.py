import os
import re
import pickle
import json
import requests
from PIL import Image
from pprint import pprint
from dotenv import load_dotenv
from rdflib import Graph

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain.chat_models import ChatOllama
from langchain_core.messages import AIMessage

import faiss
from uuid import uuid4
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

vec_path = "Data/vector_store"
context_path = "Data/context.pkl"

# embeddings = OllamaEmbeddings(model="mxbai-embed-large")
# vector_store = FAISS.load_local(vec_path, embeddings, allow_dangerous_deserialization=True)

def chat_llm(llm, query, context_dict, vector_store):
    results = vector_store.similarity_search(
        query,
        k=1,
        # filter={"source": "tweet"},
    )
    # for res in results:
    #     print(f"* {res.page_content} [{res.metadata}]")
    
    # retrieve the right artifact 
    # simply pick the top one
    item_id = results[0].metadata['item_id']
    context = context_dict[item_id]["full_text"]
    
    messages = [
        (
            "system",
            f"You are a helpful assistant in museum to explain the artifact. \
            You have the knowledge about the artifact: {context}. \
            Please answer the question \
            and then introduce detailed information about this artifact, \
            Your answer must include the identifier, created period, and 3-4 sentences as its description ",
        ),
        ("human", query),
    ]
    
    ai_msg = llm.invoke(messages)
    # print('-'* 30 + " Context of the Artifact " + '-'* 30)
    # print(context)
    # print('-'* 30 + " LLM answer " + '-'* 30)
    # print(ai_msg.content)
    return ai_msg.content

def chat_llm_multilingual(llm, query, item_id, context_dict):

    context = context_dict[item_id]['full_text']
    
    messages = [
        (
            "system",
            f"You are a helpful assistant in museum to explain the artifact in multiple languages. \
            You have the knowledge about this artifact: {context}. \
            Please detect the language of each user question. Always respond in the language detected. (you don't need to explictly output the detected language), \
            and then answer the question in the detected language, \
            Your answer must include the identifier",
        ),
        ("human", query),
    ]
    
    ai_msg = llm.invoke(messages)
    # print('-'* 30 + " Context of the Artifact " + '-'* 30)
    # print(context)
    # print('-'* 30 + " LLM answer " + '-'* 30)
    # print(ai_msg.content)
    return ai_msg.content

if __name__ == "__main__":
    # llm = ChatOllama(model="llama3.1", temperature=0)
    llm = ChatOllama(model="llama3.2:1b", temperature=0)
    vec_path = "Data/vector_store"
    context_path = "Data/context.pkl"

    with open(context_path, 'rb') as f:
        context_dict = pickle.load(f)


    item_id = '16157'
    query = "这是个艺术品源于哪个时代创建"
    output = chat_llm_multilingual(llm, query, item_id, context_dict)
    print(output)

    

    # embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    # vector_store = FAISS.load_local(vec_path, embeddings, allow_dangerous_deserialization=True)
    
    # query = "which artifact was created from the following period: 1930-1959?"
    # chat_llm(llm, query, context_dict, vector_store)