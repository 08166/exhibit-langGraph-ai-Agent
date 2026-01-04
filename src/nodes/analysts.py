from langchain_core.messages import HumanMessage, SystemMessage
from configuration import get_llm_model
from state import GraphState, Perspectives
from prompts import analyst_instructions


def create_analysts(state: GraphState):
    """분석가 페르소나 생성 (Multi-Agent)"""
    question = state.get("question", "")
    max_analysts = state.get("max_analysts", 3)
    human_analyst_feedback = state.get("human_analyst_feedback", "")

    if not question:
        return {"analysts": []}

    llm = get_llm_model()
    structured_llm = llm.with_structured_output(Perspectives)

    system_message = analyst_instructions.format(
        topic=question,
        human_analyst_feedback=human_analyst_feedback,
        max_analysts=max_analysts,
    )

    analysts = structured_llm.invoke(
        [SystemMessage(content=system_message)]
        + [HumanMessage(content="Generate the set of analysts for exhibition research.")]
    )

    return {"analysts": analysts.analysts}


def human_feedback(state: GraphState):
    """Human-in-the-Loop 중단점"""
    pass