from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader

from langchain_community.llms import Ollama
from langchain_community.graphs import Neo4jGraph

from dotenv import load_dotenv

from rdflib import Graph
from neo4j import GraphDatabase

from langchain_experimental.graph_transformers.llm import LLMGraphTransformer
import getpass
import os

# Load environment variable for OpenAI API key

if __name__ == "__main__":
    load_dotenv()
    
    loader = TextLoader("./Data/items_filtered.ttl")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    texts = text_splitter.split_documents(documents)
    # Initialize LLM
    llm = Ollama(model="llama3.2:1b")

    # Extract Knowledge Graph
    llm_transformer = LLMGraphTransformer(llm=llm)
    # graph_documents = llm_transformer.convert_to_graph_documents(texts)

    g = Graph()
    g.parse("Data/items_filtered.ttl", format="turtle")




