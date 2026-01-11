import asyncio
from typing import List, Dict
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tavily import AsyncTavilyClient

from configuration import get_llm_gpt
from state import GraphState


async def search_gpt_async(state: GraphState):
    """GPT + Deep Tavily Search with async parallel execution"""
    question = state["question"]
    context = state.get("context", [])
    current_date = datetime.now().strftime("%Y-%m-%d")

    llm = get_llm_gpt()
    tavily_client = AsyncTavilyClient(api_key="YOUR_TAVILY_API_KEY")

    # Step 1: Generate multiple search queries for comprehensive research
    query_generation_prompt = PromptTemplate.from_template("""
Given the following question, generate 3-5 diverse search queries that would help gather comprehensive information.
Each query should explore different aspects or angles of the question.
Question: {question}
Generate search queries (one per line):
""")

    chain = query_generation_prompt | llm | StrOutputParser()
    search_queries_text = await chain.ainvoke({"question": question})
    search_queries = [q.strip() for q in search_queries_text.strip().split('\n') if q.strip()]

    # Step 2: Execute all Tavily searches in parallel
    async def tavily_search(query: str) -> Dict:
        try:
            result = await tavily_client.search(
                query=query,
                search_depth="advanced",  # Deep search mode
                max_results=5,
                include_answer=True,
                include_raw_content=False
            )
            return {"query": query, "result": result, "error": None}
        except Exception as e:
            return {"query": query, "result": None, "error": str(e)}

    # Execute all searches concurrently
    search_tasks = [tavily_search(query) for query in search_queries]
    search_results = await asyncio.gather(*search_tasks)

    # Step 3: Aggregate and format Tavily results
    tavily_context = []
    for search_data in search_results:
        if search_data["error"]:
            continue

        result = search_data["result"]
        if result and result.get("results"):
            for item in result["results"]:
                source_info = f"""
<Document source="tavily-search" url="{item.get('url', 'N/A')}" date="{current_date}">
Title: {item.get('title', 'N/A')}
Content: {item.get('content', 'N/A')}
Score: {item.get('score', 'N/A')}
</Document>
"""
                tavily_context.append(source_info)

        # Add Tavily's AI-generated answer if available
        if result and result.get("answer"):
            tavily_context.append(f"""
<Document source="tavily-answer" date="{current_date}">
{result['answer']}
</Document>
""")

    # Step 4: Combine with existing context
    context_str = "\n".join(context) if context else ""
    all_context = context_str + "\n" + "\n".join(tavily_context)
    has_real_results = bool(tavily_context) or (context_str and "No search results found" not in context_str)

    # Step 5: Generate comprehensive GPT synthesis
    if has_real_results:
        synthesis_prompt = PromptTemplate.from_template("""
You are a research synthesizer. Based on the following search results and context, provide a comprehensive, well-structured answer to the question.
Context and Search Results:
{context_str}
Question: {question}
Provide a detailed, factual answer with proper citations. Structure your response clearly with sections if needed.
""")
        chain = synthesis_prompt | llm | StrOutputParser()
        response = await chain.ainvoke({"context_str": all_context, "question": question})
    else:
        fallback_prompt = PromptTemplate.from_template("""
No search results were found. Based on your knowledge (current date: {current_date}), provide the best possible answer to:
Question: {question}
Note: This answer is based on general knowledge without recent search results.
""")
        chain = fallback_prompt | llm | StrOutputParser()
        response = await chain.ainvoke({"question": question, "current_date": current_date})

    formatted = f'<Document source="gpt-synthesis" date="{current_date}">\n{response}\n</Document>'

    # Return all context including Tavily results and GPT synthesis
    return {"context": tavily_context + [formatted]}