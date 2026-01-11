from typing import Optional

FAKE_PATTERNS = [
    "xxx", "xxxx", "n/a", "tbd", "미정", "정보 없음",
    "123-456", "000-0000", "1-1-1", "???"
]

AGGREGATOR_DOMAINS = [
    "exposale.net", "we-artonline.com", "eventbrite",
    "ticketmaster", "meetup.com", "allevents.in"
]


class DataCleaner:
    """데이터 제거 클래스"""
    
    def __init__(self, fake_patterns: list[str] = None):
        self.fake_patterns = fake_patterns or FAKE_PATTERNS
    
    def clean_field(self, value: Optional[str]) -> str:
        if not value:
            return ""
        
        normalized = value.lower().replace(" ", "").replace("-", "")
        
        if self._contains_fake_pattern(normalized):
            return ""
        
        if self._has_consecutive_x(normalized):
            return ""
        
        return value
    
    def _contains_fake_pattern(self, text: str) -> bool:
        return any(
            pattern.replace("-", "") in text 
            for pattern in self.fake_patterns
        )
    
    def _has_consecutive_x(self, text: str, min_count: int = 3) -> bool:
        return "x" * min_count in text
    
    def is_aggregator_domain(self, url: str, domains: list[str] = None) -> bool:
        if not url:
            return False
        
        domains = domains or AGGREGATOR_DOMAINS
        return any(domain in url.lower() for domain in domains)