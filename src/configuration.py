import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

load_dotenv()


def get_llm_gpt(model: str = "gpt-4o-mini", temperature: float = 0.7) -> ChatOpenAI:
    return ChatOpenAI(model=model, temperature=temperature)

def get_tavily_api_key():
    return os.getenv("TAVILY_API_KEY")

def get_llm_ollama(model: str = "llama3:14b", temperature: float = 0) -> ChatOllama:
    return ChatOllama(model=model, temperature=temperature)
