from datetime import datetime
from langchain_core.messages import HumanMessage
from configuration import get_llm_model
from state import GraphState
from prompts import answer_generation_prompt


def generate_answer(state: GraphState):
    """검증된 정보만 포함한 답변 생성"""
    question = state["question"]
    context = state.get("context", [])
    exhibitions = state.get("exhibitions", [])
    db_results = state.get("db_results", "")
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_year = datetime.now().year
    
    llm = get_llm_model()
    
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
                exhibition_text += f"- **Source:** {ex.source_url}\n"
    
    context_str = "\n\n".join(context) if isinstance(context, list) else context
    
    prompt = f"""Provide exhibition information based on the user's question.

            TODAY'S DATE: {current_date}

            CRITICAL: 
            - Only include exhibitions that are CURRENTLY ongoing or UPCOMING
            - Do NOT include any exhibitions that ended before {current_date}
            - Only include {current_year} or later exhibitions

            ## Question
            {question}

            ## Search Results
            {context_str}

            ## Extracted Exhibition Information
            {exhibition_text if exhibition_text else 'No extracted information'}

            Based on the above VERIFIED information only, provide a helpful response.
            If no verified exhibitions were found, suggest:
            1. Official museum websites to check
            2. How to search for accurate information
            3. Apologize for not finding specific verified results

            Answer in Korean."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {"answer": response.content}