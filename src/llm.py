from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaEmbeddings
from langchain.chat_models import ChatOllama
from langchain.vectorstores.neo4j_vector import Neo4jVector

from langchain_community.llms import Ollama
from langchain_community.graphs import Neo4jGraph

from dotenv import load_dotenv

from rdflib import Graph
from neo4j import GraphDatabase

from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
import getpass
import os

from langchain_core.documents import Document

# Load environment variable for OpenAI API key

if __name__ == "__main__":
    load_dotenv()
    
    # # loader = TextLoader("./Data/items_filtered.ttl")
    # documents = loader.load()
    # text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    # texts = text_splitter.split_documents(documents)
    # # Initialize LLM
    # # llm = Ollama(model="llama3.2:1b")
    embedding_model = OllamaEmbeddings(model="llama3.2:1b")
    url="neo4j+s://e41c99ec.databases.neo4j.io"
    username="neo4j"
    password="4hdG4sC8pQHxvs6PqtL4P4eBQfMyKQxpj5N0ENkoBcc"
    embeddings = embedding_model

    # Specify the folder path
    folder_path = 'output_documents'

    # List all files in the folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    print(files)
    docs = []
    print("Files in folder:", files)
    for f in files:
        with open(f"output_documents/" + f, 'r', encoding='utf-8') as file:
            docs.append(Document(
                page_content = file.read(),
                # metadata={}
            ))
    
    
    vectorstore = Neo4jVector.from_documents(
        embedding=embeddings,
        documents=docs,
        url=url,
        username=username,
        password=password,
    )
    llm=ChatOllama(model="llama3.2:1b")
    # Extract Knowledge Graph
    # graph_documents = llm_transformer.convert_to_graph_documents(texts)

    # g = Graph()
    # g.parse("Data/items_filtered.ttl", format="turtle")
    # prompt = ""
    # qa_chain = RetrievalQA.from_llm(llm, retriever=vectorstore.as_retriever(), prompt=prompt)
    qa_chain = RetrievalQA.from_llm(llm, retriever=vectorstore.as_retriever())
    
    qa_chain("When is item 15959 created?")




