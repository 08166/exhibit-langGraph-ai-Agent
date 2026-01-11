from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import Send
from state import GraphState
from nodes.analysts import create_analysts, human_feedback
from nodes.search import db_search, search_tavily, search_gpt, transform_query
from nodes.evaluate import (
    grade_db_results, 
    route_after_db, 
    hallucination_check, 
    route_after_hallucination,
    extract_exhibition_data
)
from nodes.answer import generate_answer


def initiate_parallel_search(state: GraphState):
    """병렬 검색 시작 (Send API)"""
    human_analyst_feedback = state.get("human_analyst_feedback")

    if human_analyst_feedback:
        return "create_analysts"

    analysts = state.get("analysts", [])
    if not analysts:
        return "create_analysts"

    return [
        Send(
            "search_by_analyst",
            {
                "analyst": analyst,
                "question": state.get("question", ""),
            },
        )
        for analyst in analysts
    ]


def search_by_analyst(state):
    """각 Analyst의 전문 분야 기반 병렬 검색"""
    analyst = state.get("analyst") 
    question = state["question"]
    
    if analyst:
        search_question = f"{question} {analyst.role} {analyst.affiliation}"
    else:
        search_question = question
    
    search_state = {"question": search_question}
    tavily_result = search_tavily(search_state)
    
    search_state["context"] = tavily_result.get("context", [])
    gpt_result = search_gpt(search_state)
    
    combined_context = tavily_result.get("context", []) + gpt_result.get("context", [])
    
    return {"context": combined_context}


def create_main_graph():
    """메인 그래프 생성 """
    
    workflow = StateGraph(GraphState)

    workflow.add_node("db_search", db_search)
    workflow.add_node("grade_db_results", grade_db_results)
    
    workflow.add_node("create_analysts", create_analysts)
    
    workflow.add_node("search_by_analyst", search_by_analyst)
    
    workflow.add_node("hallucination_check", hallucination_check)
    workflow.add_node("transform_query", transform_query)
    workflow.add_node("extract_exhibition_data", extract_exhibition_data)
    
    workflow.add_node("generate_answer", generate_answer)

    workflow.add_edge(START, "db_search")
    workflow.add_edge("db_search", "grade_db_results")
    
    workflow.add_conditional_edges(
        "grade_db_results",
        route_after_db,
        {
            "generate_answer": "generate_answer",
            "create_analysts": "create_analysts",
        }
    )

    workflow.add_conditional_edges(
        "create_analysts",
        initiate_parallel_search,
        ["search_by_analyst"]  # "create_analysts" 제거
    )
    
    workflow.add_edge("search_by_analyst", "hallucination_check")
    
    workflow.add_conditional_edges(
        "hallucination_check",
        route_after_hallucination,
        {
            "extract_data": "extract_exhibition_data",
            "transform_query": "transform_query",
        }
    )
    
    workflow.add_edge("transform_query", "search_by_analyst")
    
    workflow.add_edge("extract_exhibition_data", "generate_answer")
    
    workflow.add_edge("generate_answer", END)

    memory = MemorySaver()
    return workflow.compile(
        checkpointer=memory
    )


graph = create_main_graph()