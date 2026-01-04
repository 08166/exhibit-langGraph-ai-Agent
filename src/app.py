import uuid
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from graphs.graph import main_graph

load_dotenv()


def save_graph_image(filename: str = "graph.png"):
    """그래프 이미지 저장"""
    try:
        png_data = main_graph.get_graph().draw_mermaid_png()
        with open(filename, "wb") as f:
            f.write(png_data)
        print(f"graph Saved to {filename}")
    except Exception as e:
        print(f"graph png save failed: {e}")


def run_exhibition_search(question: str, max_analysts: int = 3):
    """전시 정보 검색 실행"""
    
    config = RunnableConfig(
        recursion_limit=30,
        configurable={"thread_id": str(uuid.uuid4())}
    )

    inputs = {
        "question": question,
        "max_analysts": max_analysts,
    }

    print("=" * 60)
    print(f"Question {question}")
    print(f"Max Analysts {max_analysts}")
    print("=" * 60)

    print("\nStep 1 DB Search & Analyst Generation")
    print("-" * 40)
    
    for event in main_graph.stream(inputs, config):
        for node_name, state_update in event.items():
            print(f"  - {node_name}: completed")
            
            if "db_relevance" in state_update:
                relevance = state_update["db_relevance"]
                print(f"    > DB Relevance: {relevance}")
                if relevance == "no":
                    print("    > Proceeding to Multi-Agent Search...")

    state = main_graph.get_state(config)
    
    if state.next == ("human_feedback",):
        analysts = state.values.get("analysts", [])
        
        print(f"\nAnalysts Created Total: {len(analysts)}")
        print("-" * 40)
        for i, analyst in enumerate(analysts, 1):
            print(f"  {i}. {analyst.name}")
            print(f"     Role: {analyst.role}")
            print(f"     Region: {analyst.region}")
        
        print("\nHuman Feedback")
        feedback = input("Enter feedback (or press Enter to continue): ").strip()
        
        if not feedback:
            feedback = None
        
        main_graph.update_state(
            config,
            {"human_analyst_feedback": feedback},
            as_node="human_feedback"
        )
        
        print("\nStep 2 Parallel Search by Analysts")
        print("-" * 40)
        
        for event in main_graph.stream(None, config):
            for node_name, _ in event.items():
                print(f"  - {node_name}: completed")

    final_state = main_graph.get_state(config)
    answer = final_state.values.get("answer", "")
    exhibitions = final_state.values.get("exhibitions", [])
    
    print("\n" + "=" * 60)
    print("Answer")
    print("=" * 60)
    print(answer)
    
    if exhibitions:
        print("\n" + "=" * 60)
        print(f"Extracted Exhibition Data Total: {len(exhibitions)}")
        print("=" * 60)
        for i, ex in enumerate(exhibitions, 1):
            print(f"\n{i}. {ex.title}")
            print(f"English Title: {ex.title_en}")
            print(f"Period: {ex.period}")
            print(f"Location: {ex.location} ({ex.city}, {ex.country})")
            print(f"Artist: {ex.artist}")
            if ex.source_url:
                print(f"   Source: {ex.source_url}")

    print(f"\nNext Node: {final_state.next}")
    
    return answer, exhibitions


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Exhibition Research System")
    print("Open Deep Research based Multi-Agent System")
    print("=" * 60)
    
    save_graph_image("graph.png")
    
    print("\n[Input]")
    question = input("Enter your question about exhibitions: ").strip()
    
    if not question:
        question = "파리 전시에 대해서 알려줘"
        print(f"  > Using default question: {question}")
    
    max_analysts_input = input("Enter number of analysts (default: 3): ").strip()
    max_analysts = int(max_analysts_input) if max_analysts_input.isdigit() else 3
    
    answer, exhibitions = run_exhibition_search(question, max_analysts)
    
    return answer, exhibitions


if __name__ == "__main__":
    main()