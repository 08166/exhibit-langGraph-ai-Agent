from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from configuration import get_llm_model
from state import GraphState, GradeDocuments, GradeHallucinations, ExhibitionList
from prompts import db_grade_prompt, hallucination_prompt

MAX_RETRIES = 10

FAKE_DOMAINS = [
    "example.com",
    "example.org", 
    "example.net",
    "test.com",
    "sample.com",
    "dummy.com",
    "placeholder.com",
]


def is_valid_url(url: str) -> bool:
    """URL 유효성 검증"""
    if not url or not url.startswith("http"):
        return False
    
    for fake in FAKE_DOMAINS:
        if fake in url.lower():
            return False
    
    return True


def grade_db_results(state: GraphState):
    """DB 검색 결과 관련성 평가 노드"""
    question = state["question"]
    db_results = state["db_results"]
    
    llm = get_llm_model()
    structured_llm = llm.with_structured_output(GradeDocuments)
    
    result = structured_llm.invoke([
        SystemMessage(content=db_grade_prompt),
        HumanMessage(content=f"Question: {question}\n\nDB Results: {db_results}")
    ])
    
    return {"db_relevance": result.binary_score}


def route_after_db(state: GraphState):
    """DB 검색 후 라우팅 결정"""
    if state.get("db_relevance") == "yes":
        return "generate_answer"
    else:
        return "create_analysts"


def hallucination_check(state: GraphState):
    """엄격한 환각 체크 노드"""
    context = state.get("context", [])
    answer = state.get("answer", "")
    
    if not answer:
        return {"hallucination_score": "yes"}
    
    llm = get_llm_model()
    structured_llm = llm.with_structured_output(GradeHallucinations)
    
    context_str = "\n\n".join(context) if isinstance(context, list) else context
    
    result = structured_llm.invoke([
        SystemMessage(content=hallucination_prompt),
        HumanMessage(content=f"Source Documents:\n{context_str}\n\n---\n\nGenerated Answer:\n{answer}")
    ])
    
    return {"hallucination_score": result.binary_score}


def route_after_hallucination(state: GraphState):
    """환각 체크 후 라우팅 결정"""

    retry_count = state.get("retry_count", 0)

    if retry_count >= MAX_RETRIES:
        return "extract_data"
    
    if state.get("hallucination_score") == "yes":
        return "extract_data"
    else:
        return "transform_query"


def extract_exhibition_data(state: GraphState):
    """엄격한 전시 데이터 추출 노드"""
    context = state.get("context", [])
    question = state["question"]
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_year = datetime.now().year
    
    llm = get_llm_model()
    structured_llm = llm.with_structured_output(ExhibitionList)
    
    context_str = "\n\n".join(context) if isinstance(context, list) else context
    
    strict_prompt = f"""Extract VERIFIED and CURRENT exhibition information from the source documents.

            TODAY'S DATE: {current_date}

            CRITICAL RULES:
            1. ONLY extract information that EXPLICITLY appears in the source documents
            2. source_url and ticket_url must be REAL URLs from the documents
            3. DO NOT use example.com, test.com, or any placeholder URLs
            4. If no real URL exists in the source, leave the field EMPTY
            5. Only include exhibitions with dates in {current_year} or later
            6. Do NOT fabricate or guess any information

            URL RULES:
            - source_url: Must be the EXACT URL from the source document (e.g., from <Document href="...">)
            - ticket_url: Must be a REAL ticketing website URL found in the source
            - If you cannot find a real URL, set the field to empty string ""

            Source Documents:
            {context_str}

            Question: {question}"""
    
    result = structured_llm.invoke([
        HumanMessage(content=strict_prompt)
    ])
    
    verified_exhibitions = []
    for ex in result.exhibitions:
        if not is_valid_url(ex.source_url):
            continue
        
        if ex.period:
            if any(year in ex.period for year in ["2020", "2021", "2022", "2023"]):
                if not any(year in ex.period for year in ["2024", "2025", "2026", "2027"]):
                    continue
        
        if ex.ticket_url and not is_valid_url(ex.ticket_url):
            ex.ticket_url = ""
        
        verified_exhibitions.append(ex)
    
    return {"exhibitions": verified_exhibitions}