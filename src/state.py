import operator
from typing import Annotated, List, TypedDict
from pydantic import BaseModel, Field


class Analyst(BaseModel):
    name: str = Field(description="분석가 이름")
    role: str = Field(description="역할")
    affiliation: str = Field(description="소속")
    region: str = Field(description="담당 지역")
    description: str = Field(description="전문 분야")

    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nRegion: {self.region}\nDescription: {self.description}"


class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(description="분석가 목록")


class ExhibitionInfo(BaseModel):
    title: str = Field(description="전시 제목")
    title_en: str = Field(default="", description="영문 제목")
    description: str = Field(default="", description="전시 설명")
    period: str = Field(default="", description="전시 기간")
    hours: str = Field(default="", description="관람 시간")
    closed_days: str = Field(default="", description="휴관일")
    location: str = Field(default="", description="전시 장소")
    country: str = Field(default="", description="국가")
    city: str = Field(default="", description="도시")
    artist: str = Field(default="", description="작가명")
    genre: List[str] = Field(default=[], description="장르 키워드")
    style: List[str] = Field(default=[], description="스타일 키워드")
    ticket_url: str = Field(default="", description="예매 링크")
    source_url: str = Field(default="", description="출처 URL")


class ExhibitionList(BaseModel):
    exhibitions: List[ExhibitionInfo] = Field(default=[], description="전시 정보 목록")


class GraphState(TypedDict):
    question: str
    db_results: str
    web_results: str
    context: Annotated[list, operator.add]
    db_relevance: str
    hallucination_score: str
    analysts: List[Analyst]
    max_analysts: int
    human_analyst_feedback: str
    exhibitions: List[ExhibitionInfo]
    answer: str


class GradeDocuments(BaseModel):
    binary_score: str = Field(description="'yes' or 'no'")


class GradeHallucinations(BaseModel):
    binary_score: str = Field(description="'yes' if grounded, 'no' if hallucination")