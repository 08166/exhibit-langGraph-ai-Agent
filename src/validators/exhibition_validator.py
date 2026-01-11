from datetime import datetime
from typing import Optional
from state import ExhibitionInfo


class ExhibitionValidator:
    """전시 정보 검증 클래스"""
    
    def __init__(self, art_keywords: list[str], exclude_keywords: list[str]):
        self.art_keywords = art_keywords
        self.exclude_keywords = exclude_keywords
    
    def is_valid_period(self, period: Optional[str], min_year: int = 2024) -> bool:
        """전시 기간 검증 """
        
        if not period:
            return True
        
        old_years = ["2020", "2021", "2022", "2023"]
        current_years = [str(year) for year in range(min_year, min_year + 4)]
        
        has_old_year = any(year in period for year in old_years)
        has_current_year = any(year in period for year in current_years)
        
        if has_old_year and not has_current_year:
            return False
        
        return True
    
    def is_art_exhibition(self, ex: ExhibitionInfo) -> tuple[bool, str]:
        """전시 검증"""

        title_desc = (ex.title + " " + (ex.description or "")).lower()
        
        for keyword in self.exclude_keywords:
            if keyword.lower() in title_desc:
                return False, f"contains exclude keyword: {keyword}"
        
        has_art_keyword = any(
            keyword.lower() in title_desc 
            for keyword in self.art_keywords
        )
        has_genre = ex.genre and len(ex.genre) > 0
        
        if not (has_art_keyword or has_genre):
            return False, "no art keywords or genre"
        
        return True, ""
    
    def validate(self, ex: ExhibitionInfo) -> tuple[bool, str]:
        """전시 전체 검증"""

        if not self.is_valid_period(ex.period):
            return False, "invalid period (too old)"
        
        is_valid, reason = self.is_art_exhibition(ex)
        if not is_valid:
            return False, reason
        
        return True, ""