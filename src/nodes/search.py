from datetime import datetime
from tavily import TavilyClient
from langchain_core.messages import HumanMessage
from configuration import get_llm_model, get_tavily_api_key
from state import GraphState


def db_search(state: GraphState):
    """DB 검색 노드"""
    question = state["question"]
    
    db_results = f'<Document source="database"/>\nNo database results for: {question}\n</Document>'
    
    return {"db_results": db_results}


def search_tavily(state: GraphState):
    """Tavily 웹 검색 노드 - 개선된 검색"""
    question = state["question"]
    current_year = datetime.now().year
    
    try:
        tavily_client = TavilyClient(api_key=get_tavily_api_key())
        
        search_queries = [
            f"{question} {current_year}",
            f"{question} exhibition art museum",
        ]
        
        all_results = []
        
        for query in search_queries:
            try:
                search_results = tavily_client.search(
                    query=query,
                    max_results=5,
                    search_depth="advanced",
                    # include_domains 제거! → 전체 웹 검색
                )
                results = search_results.get("results", [])
                all_results.extend(results)
            except Exception as e:
                print(f"Error: {e}")
        
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        if unique_results:
            formatted_docs = "\n\n---\n\n".join([
                f'<Document href="{r["url"]}" title="{r.get("title", "")}"/>\n{r["content"]}\n</Document>'
                for r in unique_results[:10]
            ])
            
            return {"web_results": formatted_docs, "context": [formatted_docs]}
        else:
            no_results = '<Document source="tavily"/>\nNo search results found.\n</Document>'
            return {"web_results": no_results, "context": [no_results]}
            
    except Exception as e:
        error_msg = f'<Document source="tavily-error"/>\nSearch failed: {str(e)}\n</Document>'
        return {"web_results": error_msg, "context": [error_msg]}


def search_gpt(state: GraphState):
    """GPT 추가 정보 - 검색 결과 기반으로만"""
    question = state["question"]
    context = state.get("context", [])
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    llm = get_llm_model()
    
    context_str = "\n".join(context) if context else ""
    has_real_results = context_str and "No search results found" not in context_str and "Search failed" not in context_str
    
    if has_real_results:
        prompt = f"""Based on the search results below, provide additional context about the exhibitions.

        Search Results:
        {context_str}

        Question: {question}

        RULES:
        1. Only elaborate on information that exists in the search results
        2. Do not add new exhibitions that are not in the search results
        3. Keep your response factual and based on the sources

        Answer in Korean."""
    else:
        prompt = f"""The web search did not return any results for: {question}

        Since no search results were found, please:
        1. Suggest official museum/gallery websites to check for {question}
        2. Do NOT fabricate or make up exhibition names
        3. Honestly state that specific exhibition information could not be found

        Answer in Korean."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    formatted = f'<Document source="gpt-reference" date="{current_date}"/>\n{response.content}\n</Document>'
    
    return {"context": [formatted]}


def transform_query(state: GraphState):
    """검색 쿼리 변환 노드"""
    question = state["question"]
    current_year = datetime.now().year
    
    llm = get_llm_model()
    prompt = f"""The previous search didn't return relevant results.

Original question: {question}

Create a more specific search query for finding art exhibitions.
Focus on: official museum names, {current_year}-{current_year+1} dates, specific locations.

Return only the improved search query (no explanation)."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    new_query = response.content.strip()
    
    return {"question": new_query}