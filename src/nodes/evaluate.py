from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from configuration import get_llm_gpt
from constants import get_all_art_keywords, get_all_exclude_keywords
from state import ExhibitionInfo, GraphState, GradeDocuments, GradeHallucinations, ExhibitionList
from prompts import db_grade_prompt, hallucination_prompt, exhibition_extract_prompt
from validators.data_cleaner import DataCleaner
from validators.exhibition_validator import ExhibitionValidator

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

    if (not db_results or "DB 검색 오류" in db_results or "SQL 쿼리 생성 실패" in db_results):
        return {"db_relevance": "no"}

    result_count = db_results.count("(")

    if result_count < 5:
        return {"db_relevance": "partial"}

    llm = get_llm_gpt()
    structured_llm = llm.with_structured_output(GradeDocuments)
    
    result = structured_llm.invoke([
        SystemMessage(content=db_grade_prompt),
        HumanMessage(content=f"Question: {question}\n\nDB Results: {db_results}")
    ])
    
    return {"db_relevance": result.binary_score}


def route_after_db(state: GraphState):
    """DB 검색 후 라우팅 결정"""

    db_relevance = state.get("db_relevance")
    if db_relevance == "partial":
        return "create_analysts"
    elif db_relevance == "yes":
        return "generate_answer"
    else:
        return "create_analysts"


def hallucination_check(state: GraphState):
    """엄격한 환각 체크 노드"""
    context = state.get("context", [])
    answer = state.get("answer", "")
    
    if not answer:
        return {"hallucination_score": "yes"}
    
    llm = get_llm_gpt()
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
    """전시 데이터 추출 및 검증"""
    # 1. 입력 데이터 준비
    context = state.get("context", [])
    question = state["question"]
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_year = datetime.now().year
    
    llm = get_llm_gpt()
    structured_llm = llm.with_structured_output(ExhibitionList)
    
    context_str = "\n\n".join(context) if isinstance(context, list) else context
    
    prompt = exhibition_extract_prompt.format(
        context_str=context_str,
        question=question,
        current_date=current_date,
        current_year=current_year
    )
    
    result = structured_llm.invoke([HumanMessage(content=prompt)])
    
    validator = ExhibitionValidator(
        art_keywords=get_all_art_keywords(),
        exclude_keywords=get_all_exclude_keywords()
    )
    cleaner = DataCleaner()
    
    verified = []
    
    for ex in result.exhibitions:
        if not is_valid_url(ex.source_url):
            continue
        
        is_valid, reason = validator.validate(ex)
        if not is_valid:
            continue
        
        fields_to_clean = ["hours", "closed_days", "location", "city", "country"]
        
        for field in fields_to_clean:
            original = getattr(ex, field)
            cleaned = cleaner.clean_field(original)
            
            if original and not cleaned:
                continue
            setattr(ex, field, cleaned)
        
        if ex.official_website and cleaner.is_aggregator_domain(ex.official_website):
            ex.official_website = ""
        
        if ex.ticket_url and not is_valid_url(ex.ticket_url):
            ex.ticket_url = ""
        
        verified.append(ex)
    
    return {"exhibitions": verified}
