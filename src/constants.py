predefined_keywords = {
        "GENRE": [
        {"id": 1, "name": "현대 미술"},
        {"id": 2, "name": "순수 미술"},
        {"id": 3, "name": "사진"},
        {"id": 4, "name": "회화"},
        {"id": 5, "name": "조각"},
        {"id": 6, "name": "디지털/미디어 아트"},
        {"id": 7, "name": "공예"},
        {"id": 8, "name": "설치 미술"},
        {"id": 9, "name": "역사/고전 미술"},
        {"id": 10, "name": "근대 미술"},
        {"id": 19, "name": "팝아트"},
    ],
    "STYLE": [
        {"id": 11, "name": "몰입형"},
        {"id": 12, "name": "인터랙티브"},
        {"id": 13, "name": "VR/AR"},
        {"id": 14, "name": "공간 연출"},
        {"id": 15, "name": "미디어 아트"},
        {"id": 16, "name": "사운드 기반"},
        {"id": 17, "name": "팝업"},
        {"id": 18, "name": "퍼포먼스"},
    ]
}


def get_keyword_list_string():
    result = "## Available Keywords:\n\n### GENRE:\n"
    for kw in predefined_keywords["GENRE"]:
        result += f"- {kw['id']}: {kw['name']}\n"
    result += "\n### STYLE:\n"
    for kw in predefined_keywords["STYLE"]:
        result += f"- {kw['id']}: {kw['name']}\n"
    return result