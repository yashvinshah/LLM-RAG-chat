# -*- coding: utf-8 -*-
"""Wikipedia RAG.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JQVwCAltNtHTluESq5Rr07CXSbwUhg5j
"""

# !pip install requests beautifulsoup4 sentence-transformers transformers langchain_google_genai langchain langchain_community faiss_cpu rank_bm25 -qqq

import os
import re
import requests
from bs4 import BeautifulSoup
from getpass import getpass
from dotenv import load_dotenv
import logging

from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.tools.retriever import create_retriever_tool
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_community.retrievers import WikipediaRetriever

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

def scrape(article_title):
    base_url = "https://en.wikipedia.org/wiki/"
    url = base_url + article_title
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    content_div = soup.find('div', id='mw-content-text')
    return clean_text(clean_text(content_div.text))

def clean_text(text):
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\((.*?citation needed.*?)\)', '', text, flags=re.IGNORECASE)
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def retrieve(query):
    wikipedia_text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50, length_function=len)
    article_text = scrape(query)
    texts = wikipedia_text_splitter.split_text(article_text)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", task_type="RETRIEVAL_DOCUMENT")
    vectorstore = FAISS.from_texts(texts, embeddings)
    retriever = BM25Retriever.from_texts(texts=texts, vectorstore=vectorstore, k=10)
    return retriever

def retriever_tool(retriever):
    return create_retriever_tool(retriever, "Wikipedia", "Searches and returns information from Wikipedia based on the topic provided.")

def build(query):
    retriever = retrieve(query)
    if not retriever:
        logging.error("Failed to retrieve information from Wikipedia.")
        return None
    model = GoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, maxRetries = 5)
    
    agent = create_conversational_retrieval_agent(
        llm=model,
        tools=[retriever_tool(retriever)],
        verbose=False
    )
    return agent

def ask_agent(question):
    if agent is None:
        return "No relevant data found for the question."

    retrieved_info = agent.tools[0].run(question)

    prompt = f"You are a helpful AI assistant. You have access to the following information from Wikipedia: \n\n{retrieved_info}\n\nPlease answer the following question based *only* on the information provided above. Do not use any external knowledge or information beyond what is provided in the Wikipedia text. \n{question}\n\nAnswer:"
    response = agent.invoke({"input": prompt}) 
    final_output = response['output']

    if final_output == "":
        return "No relevant information available."

    return final_output


agent = build("Tesla,_Inc.")
print("Question: Summarize the wikipedia page")
print(ask_agent("Summarize the wikipedia page"))
print()
print("Question: What is bye in German?")
print(ask_agent("What is bye in German?"))
print()


