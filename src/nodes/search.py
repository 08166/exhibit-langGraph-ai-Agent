from datetime import datetime
from database import db
from tavily import TavilyClient
from configuration import get_llm_gpt, get_tavily_api_key
from prompts import query_rewrite_prompt, search_fallback_prompt, search_expansion_prompt, slq_prompt
from state import GraphState
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def db_search(state: GraphState):
    """DB 검색 노드"""
    question = state["question"]
    llm = get_llm_gpt()
    
    try:
        table_info = db.get_table_info()
        
        prompt = PromptTemplate.from_template(slq_prompt).partial(
            dialect=db.dialect,
            top_k=10,
            table_info=table_info
        )
        
        chain = prompt | llm | StrOutputParser()
        sql_response = chain.invoke({"input": question})
        
        sql_query = None
        if "SQLQuery:" in sql_response:
            sql_query = sql_response.split("SQLQuery:")[-1].strip()
        elif "```sql" in sql_response.lower():
            sql_query = sql_response.split("```sql")[-1].split("```")[0].strip()
        elif "```" in sql_response:
            parts = sql_response.split("```")
            if len(parts) >= 2:
                sql_query = parts[1].strip()
        elif "SELECT" in sql_response.upper():
            sql_query = sql_response[sql_response.upper().find("SELECT"):].strip()
        
        if sql_query:
            sql_query = sql_query.replace("```", "").strip()
            sql_query = " ".join(sql_query.split())
            if sql_query.endswith(";"):
                sql_query = sql_query[:-1]
            
            result = db.run(sql_query)
            
            if result and result.strip() and result.strip() != "[]":
                db_results = '<Document source="database"/>\n' + question + '에 대한 DB 검색 결과:\n\n' + result + '\n</Document>'
            else:
                db_results = '<Document source="database"/>\nDB에서 "' + question + '" 관련 데이터를 찾지 못했습니다.\n</Document>'
        else:
            db_results = '<Document source="database"/>\nSQL 쿼리 생성 실패.\n</Document>'
    
    except Exception as e:
        db_results = '<Document source="database"/>\nDB 검색 오류: ' + str(e) + '\n</Document>'
    
    return {"db_results": db_results}


def search_tavily(state: GraphState):
    """Tavily 웹 검색 노드"""
    question = state["question"]
    current_year = datetime.now().year
    
    try:
        tavily_client = TavilyClient(api_key=get_tavily_api_key())
        
        search_queries = [
            f"{question} "
            f"Art Exhibition Museum Gallery"
            f"{current_year} {current_year + 1}"
            f"Modern Painting, Sculpture, Photography, etc."
        ]

        all_results = []
        
        for query in search_queries:
            try:
                search_results = tavily_client.search(
                    query=query,
                    max_results=5,
                    search_depth="advanced",
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
    """GPT 추가 정보 """
    question = state["question"]
    context = state.get("context", [])
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    llm = get_llm_gpt()
    
    context_str = "\n".join(context) if context else ""
    has_real_results = context_str and "No search results found" not in context_str and "Search failed" not in context_str
    
    if has_real_results:
        prompt = PromptTemplate.from_template(search_expansion_prompt)
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"context_str": context_str, "question": question})
    else:
        prompt = PromptTemplate.from_template(search_fallback_prompt)
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"question": question}, {"current_date": current_date})
    
    formatted = f'<Document source="gpt-reference" date="{current_date}"/>\n{response}\n</Document>'
    
    return {"context": [formatted]}


def transform_query(state: GraphState):
    """검색 쿼리 변환 노드"""

    question = state["question"]
    current_year = datetime.now().year
    retry_count = state.get("retry_count", 0)
    
    llm = get_llm_gpt()

    prompt = PromptTemplate.from_template(query_rewrite_prompt)
    chain = prompt | llm | StrOutputParser()

    new_query = chain.invoke({
        "question": question,
        "current_year": current_year,
        "next_year": current_year+1,
    })
    
    return {"question": new_query.strip(), "retry_count": retry_count + 1}