# LangGraph를 활용한 전시 정보 검색 AI Agent

> 테디노트님의 강의 및 코드를 참조하여 구현하였습니다 ([teddylee](https://github.com/teddylee777/langchain-kr/tree/main/17-LangGraph/02-Structures)) </br>
> [open_deep_research](https://github.com/langchain-ai/open_deep_research)를 참조하였습니다 


## 추가 된 내용
1. DB 연동 하여 데이터 검색
2. 데이터 검증 강화
3. input, output에 대한 prompt 변경

### 문제
- 현재 사이드 프로젝트로 **해외/국내 전시 통합 앱**을 출시 준비 중입니다.
- **해외 전시**: 공식 API 없으므로, 수작업 데이터 수집
- **국내 전시**: OpenAPI 제공되나 일부 데이터 누락
- **결과**: 사용자에게 제공할 충분한 데이터 부족

### 해결 목표
부족한 전시 데이터를 **자동으로 수집하고 검증**할 수 있도록 구축

## 구현 방법

### 1. Adaptive RAG + Multi-Agent

데이터 신뢰도에 따라 단계적으로 검색하는 **Adaptive RAG 패턴** 적용했습니다.

#### workflow
- **DB 검색**: DB 연동 예정 이므로, DB 조회 실패 시 Tavily, GPT 로 전시 정보를 먼저 수집
- **tavliy 검색 결과** : 사용자 입력값으로만 조회 시 결과가 나오지 않아 검색 쿼리를 transform_query메서드를 활용하여 확장하여 재검색 할 수 있도록 구현
- **Multi-Agent**: 지역별/장르별 애널리스트를 추가하여 병렬로 검색으로 검색범위 확장
- **Self-Correction**: 검색 결과가 부족하면 쿼리를 변환하여 재검색, 최대 5회 재시도할 수 있도록 구현
- **Hallucination 방지**: 
    - URL 검증 : example.com 같은 도메인은 제외 하고 실제 존재하는 url을 찾을 수 있도록 구현, 
    - 날짜 검증 : 과거 전시를 제외한 사용자 입력 기준 날짜 이후로 검색


### 2. 주요 기술 목적

1. Multi-Agent
- 최대 3명의 애널리스트를 생성하고 검색 범위를 넓혔습니다.
2. self-Correction loop 
- 할루시네이션을 방지 하기 위해서 자가 검증을 할 수 있도록 했습니다.
- 사용자 입력값에 광범위한 검색 방향을 교정
3. Structured Data Extraction
- 프롬프트 및 state를 활용하여 비정형 데이터를 데이터베이스에 저장할 수 있도록 가공

### 사용한 기술

| 구분 | 기술 |
|------|------|
| **Framework** | LangGraph 
| **LLM** | GPT-4o-mini 
| **Search** | Tavily API 
| **streamlit**| frontend

### 3. 동작 예시

1. https://ai.coffit.today 접속
2. 지역 및 나라에 대한 전시회 검색
3. 추천 애널리스트 확인
4. (선택사항) 애널리스트 재구성을 위한 피드백 입력 (예시 : 유럽에 전시 전문가를 찾아서 추가해줘


### 기술적 학습
1. **LangGraph의 Send API**: 멀티 에이전트 병렬 처리 패턴 습득
2. **Prompt Engineering**: 할루시네이션 방지를 위한 까다로운 프롬프트 작성 방법
3. **Self-Correction Pattern**: 재시도 코드
4. **TypedDict vs Pydantic**: 상태 관리는 TypedDict, LLM 출력은 Pydantic

