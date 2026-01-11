from datetime import datetime
from langchain_core.messages import HumanMessage
from configuration import get_llm_gpt
from state import GraphState
from prompts import final_answer_prompt, slq_prompt
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def generate_answer(state: GraphState):
    """검증된 정보만 포함한 답변 생성"""
    question = state["question"]
    context = state.get("context", [])
    exhibitions = state.get("exhibitions", [])
    db_results = state.get("db_results", "")
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_year = datetime.now().year
    
    llm = get_llm_gpt()
    
    exhibition_text = ""
    if exhibitions:
        for i, ex in enumerate(exhibitions, 1):
            if ex.source_url:
                exhibition_text += f"""### {i}. {ex.title}"""
                if ex.title_en:
                    exhibition_text += f"- **English Title:** {ex.title_en} \n"
                if ex.period:
                    exhibition_text += f"- **Period:** {ex.period}\n"
                if ex.location:
                    exhibition_text += f"- **Location:** {ex.location}"
                    if ex.city:
                        exhibition_text += f", {ex.city}"
                    if ex.country:
                        exhibition_text += f", {ex.country}"
                    exhibition_text += "\n"
                if ex.artist:
                    exhibition_text += f"- **Artist:** {ex.artist}\n"
                if ex.description:
                    exhibition_text += f"- **Description:** {ex.description}\n"
                if ex.hours:
                    exhibition_text += f"- **Hours:** {ex.hours}\n"
                if ex.closed_days:
                    exhibition_text += f"- **Closed:** {ex.closed_days}\n"
                if ex.genre:
                    exhibition_text += f"- **Genre:** {', '.join(ex.genre)}\n"
                if ex.ticket_url:
                    exhibition_text += f"- **Tickets:** {ex.ticket_url}\n"
                if ex.official_website:
                    exhibition_text += f"- **Official Website:** {ex.official_website}\n"
                exhibition_text += f"- **Source:** {ex.source_url}\n"
    
    context_str = "\n\n".join(context) if isinstance(context, list) else context
    
    prompt = PromptTemplate.from_template(final_answer_prompt)
    
    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke({
        "question": question,
        "db_results": db_results,
        "context_str": context_str,
        "exhibition_text": exhibition_text,
        "current_date": current_date,
        "current_year": current_year,
    })
    
    return {"answer": answer.strip()}