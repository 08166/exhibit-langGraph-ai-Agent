import streamlit as st
import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from graphs.graph import graph

load_dotenv()

st.set_page_config(
    page_title="Exhibition Research System",
    page_icon="",
    layout="wide"
)

st.title("전시 정보 검색")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "analysts" not in st.session_state:
    st.session_state.analysts = []
if "step" not in st.session_state:
    st.session_state.step = "input"
if "answer" not in st.session_state:
    st.session_state.answer = ""
if "exhibitions" not in st.session_state:
    st.session_state.exhibitions = []
if "config" not in st.session_state:
    st.session_state.config = None

if st.session_state.step == "input":
    st.subheader("Step 1: 전시회 관련 질문을 입력해주세요")

    if "question" not in st.session_state:
        st.session_state.question = ""

    question = st.text_input(
        "어떤 전시 정보를 찾고 계신가요?",
        key="question_input",
        placeholder="예: 독일 뮌헨에서 열리는 전시회를 찾아줘"
    )

    if st.button("검색 시작", type="primary"):
        if not question.strip():
            st.warning("질문을 입력해주세요.")
        else:
            with st.spinner("DB 검색 및 애널리스트 생성 중..."):
                st.session_state.thread_id = str(uuid.uuid4())
                
                config = RunnableConfig(
                    recursion_limit=20,
                    configurable={"thread_id": st.session_state.thread_id}
                )

                inputs = {
                    "question": question,
                }

                for event in graph.stream(inputs, config):
                    for node_name, state_update in event.items():
                        if "db_relevance" in state_update:
                            if state_update["db_relevance"] == "yes":
                                st.success("Found relevant data in DB!")
                            else:
                                st.info("No DB data found. Proceeding to Multi-Agent Search...")

                state = graph.get_state(config)
                st.session_state.config = config
                st.session_state.question = question

                if state.next == ():
                    st.session_state.answer = state.values.get("answer", "")
                    st.session_state.exhibitions = state.values.get("exhibitions", [])
                    st.session_state.step = "result"
                else:
                    st.session_state.analysts = state.values.get("analysts", [])
                    st.session_state.step = "feedback"

                st.rerun()

elif st.session_state.step == "feedback":
    st.subheader("Step 2: Analysts 검토 (Human-in-the-Loop)")

    st.markdown(f"**Question:** {st.session_state.question}")
    st.markdown("---")

    st.markdown(f"### Analysts ({len(st.session_state.analysts)})")

    for i, analyst in enumerate(st.session_state.analysts, 1):
        with st.expander(f"{i}. {analyst.name} - {analyst.role}"):
            st.markdown(f"**Affiliation:** {analyst.affiliation}")
            st.markdown(f"**Region:** {analyst.region}")
            st.markdown(f"**Description:** {analyst.description}")

    st.markdown("---")

    feedback = st.text_area(
        "피드백 (애널리스트 수정 요청):",
        placeholder="Example: 한국 전시 전문가를 추가해주세요."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("새로운 Analyst 구성"):
            if feedback:
                with st.spinner("Regenerating analysts..."):
                    graph.update_state(
                        st.session_state.config,
                        {
                            "human_analyst_feedback": feedback,
                            "question": st.session_state.question
                        },
                        as_node="human_feedback"
                    )

                    for event in graph.stream(None, st.session_state.config):
                        pass

                    state = graph.get_state(st.session_state.config)
                    st.session_state.analysts = state.values.get("analysts", [])
                    st.rerun()
            else:
                st.warning("Please enter feedback to regenerate analysts.")

    with col2:
        if st.button("검색", type="primary"):
            graph.update_state(
                st.session_state.config,
                {"human_analyst_feedback": None},
                as_node="human_feedback"
            )
            st.session_state.step = "research"
            st.rerun()

elif st.session_state.step == "research":
    st.subheader("Step 3: 검색 중")

    progress_bar = st.progress(0)
    status_text = st.empty()
    log_container = st.empty()

    logs = []

    with st.spinner("병렬 검색 및 데이터 추출 중..."):
        step_count = 0
        for event in graph.stream(None, st.session_state.config):
            for node_name, _ in event.items():
                step_count += 1
                progress = min(step_count / 8, 1.0)
                progress_bar.progress(progress)

                log_entry = f"- {node_name}: completed"
                logs.append(log_entry)
                log_container.code("\n".join(logs), language="text")

        progress_bar.progress(1.0)
        status_text.success("검색 완료!")

        final_state = graph.get_state(st.session_state.config)
        st.session_state.answer = final_state.values.get("answer", "")
        st.session_state.exhibitions = final_state.values.get("exhibitions", [])
        st.session_state.step = "result"
        st.rerun()

elif st.session_state.step == "result":
    st.subheader("Step 4: 결과")

    st.markdown("### 답변")
    st.markdown(st.session_state.answer)

    st.markdown("---")
    
    exhibitions = st.session_state.exhibitions
    st.markdown(f"### 추출된 전시 데이터 ({len(exhibitions)}개)")
    
    if not exhibitions:
        st.warning("추출된 전시 데이터가 없습니다.")
    else:
        for i, ex in enumerate(exhibitions, 1):
            st.markdown(f"#### {i}. {ex.title}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if ex.title_en:
                    st.markdown(f"**English Title:** {ex.title_en}")
                if ex.period:
                    st.markdown(f"**Period:** {ex.period}")
                if ex.artist:
                    st.markdown(f"**Artist:** {ex.artist}")
            
            with col2:
                if ex.location:
                    st.markdown(f"**Location:** {ex.location}")
                location_parts = []
                if ex.city:
                    location_parts.append(ex.city)
                if ex.country:
                    location_parts.append(ex.country)
                if location_parts:
                    st.markdown(f"**City/Country:** {', '.join(location_parts)}")
            
            if ex.description:
                st.markdown(f"**Description:** {ex.description}")
            
            tags = []
            if ex.genre:
                tags.extend(ex.genre)
            if ex.style:
                tags.extend(ex.style)
            if tags:
                st.markdown(f"**Tags:** {', '.join(tags)}")
            
            links = []
            if ex.ticket_url:
                links.append(f"[Ticket]({ex.ticket_url})")
            if ex.source_url:
                links.append(f"[Source]({ex.source_url})")
            if links:
                st.markdown(f"**Links:** {' | '.join(links)}")
            
            st.markdown("---")

    if st.button("새로운 검색 시작"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.step = "input"
        st.session_state.analysts = []
        st.session_state.answer = ""
        st.session_state.exhibitions = []
        st.session_state.config = None
        st.rerun()