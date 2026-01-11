# 예술 전시 장르 및 스타일 키워드 정의
predefined_keywords = {
    "GENRE": [
        {"id": 1, "name": "현대 미술", "en": "contemporary art", "keywords": ["contemporary", "modern art", "현대"]},
        {"id": 2, "name": "순수 미술", "en": "fine art", "keywords": ["fine art", "순수", "순수미술"]},
        {"id": 3, "name": "사진", "en": "photography", "keywords": ["photography", "photo", "사진"]},
        {"id": 4, "name": "회화", "en": "painting", "keywords": ["painting", "paint", "회화", "그림"]},
        {"id": 5, "name": "조각", "en": "sculpture", "keywords": ["sculpture", "sculpt", "조각"]},
        {"id": 6, "name": "디지털/미디어 아트", "en": "digital/media art", "keywords": ["digital", "media art", "디지털", "미디어"]},
        {"id": 7, "name": "공예", "en": "craft", "keywords": ["craft", "공예", "handcraft"]},
        {"id": 8, "name": "설치 미술", "en": "installation art", "keywords": ["installation", "설치"]},
        {"id": 9, "name": "역사/고전 미술", "en": "historical/classical art", "keywords": ["historical", "classical", "역사", "고전"]},
        {"id": 10, "name": "근대 미술", "en": "modern art", "keywords": ["modern", "근대"]},
        {"id": 19, "name": "팝아트", "en": "pop art", "keywords": ["pop art", "팝아트", "pop"]},
    ],
    "STYLE": [
        {"id": 11, "name": "몰입형", "en": "immersive", "keywords": ["immersive", "몰입", "experience"]},
        {"id": 12, "name": "인터랙티브", "en": "interactive", "keywords": ["interactive", "인터랙티브", "interaction"]},
        {"id": 13, "name": "VR/AR", "en": "VR/AR", "keywords": ["vr", "ar", "virtual", "augmented", "가상현실"]},
        {"id": 14, "name": "공간 연출", "en": "spatial design", "keywords": ["spatial", "space", "공간", "연출"]},
        {"id": 15, "name": "미디어 아트", "en": "media art", "keywords": ["media", "미디어", "video art"]},
        {"id": 16, "name": "사운드 기반", "en": "sound-based", "keywords": ["sound", "audio", "사운드", "음향"]},
        {"id": 17, "name": "팝업", "en": "pop-up", "keywords": ["popup", "pop-up", "팝업"]},
        {"id": 18, "name": "퍼포먼스", "en": "performance", "keywords": ["performance", "퍼포먼스", "performing"]},
    ]
}

art_related_keywords = [
    "art", "exhibition", "museum", "gallery", "artist", "artwork",
    "미술", "전시", "작품", "예술", "갤러리", "뮤지엄", "아트", "박물관",
    "biennale", "비엔날레", "artfair", "art fair", "아트페어"
]

exclude_keywords = {
    "auto": ["auto", "car", "automotive", "vehicle", "자동차", "차량"],
    "pet": ["pet", "animal", "애완동물", "반려동물"],
    "food": ["food", "cooking", "culinary", "cuisine", "음식", "요리", "식품"],
    "tech": ["tech conference", "semiconductor", "IT", "기술 컨퍼런스", "반도체"],
    "business": ["trade show", "business", "무역", "비즈니스", "산업"],
    "other": ["real estate", "부동산", "job fair", "취업박람회"]
}


def get_all_art_keywords():
    """모든 예술 관련 키워드 추출"""
    keywords = set(art_related_keywords)
    
    for genre in predefined_keywords["GENRE"]:
        keywords.update(genre.get("keywords", []))
    
    for style in predefined_keywords["STYLE"]:
        keywords.update(style.get("keywords", []))
    
    return list(keywords)


def get_all_exclude_keywords():
    """모든 제외 키워드 추출"""
    keywords = []
    for category, words in exclude_keywords.items():
        keywords.extend(words)
    return keywords


def get_keyword_list_string():
    """LLM 프롬프트용 키워드 리스트 문자열 생성"""
    result = "## Available Keywords:\n\n### GENRE:\n"
    for kw in predefined_keywords["GENRE"]:
        result += f"- {kw['id']}: {kw['name']} ({kw['en']})\n"
    result += "\n### STYLE:\n"
    for kw in predefined_keywords["STYLE"]:
        result += f"- {kw['id']}: {kw['name']} ({kw['en']})\n"
    return result


def get_exclude_list_string():
    """LLM 프롬프트용 제외 키워드 리스트 문자열 생성"""
    result = "## Excluded Categories:\n\n"
    for category, words in exclude_keywords.items():
        result += f"### {category.upper()}:\n"
        result += f"- {', '.join(words)}\n"
    return result