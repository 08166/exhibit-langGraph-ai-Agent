import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_llm_model(model: str = "gpt-4o-mini", temperature: float = 0) -> ChatOpenAI:
    return ChatOpenAI(model=model, temperature=temperature)

def get_tavily_api_key():
    return os.getenv("TAVILY_API_KEY")
