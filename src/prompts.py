from constants import get_exclude_list_string, get_keyword_list_string


analyst_instructions = """You are tasked with creating a set of AI analyst personas for an Art Exhibition Research System.
Follow these instructions carefully:
1. First, review the research topic:

{topic}
        
2. Examine any editorial feedback that has been optionally provided: 
        
{human_analyst_feedback}
    
3. Create analysts with diverse perspectives:
- gugnae jeonsi jeonmunga (Korean domestic exhibitions) - haeoe jeonsi jeonmunga (International exhibitions - Europe, USA, Asia) - jangleubyeol jeonmunga (Contemporary, Classical, Digital Art, etc.)
156
- Domestic exhibition specialist (Korean domestic exhibitions)
- International exhibition specialist (Europe, USA, Asia)
- Genre specialist (Contemporary, Classical, Digital Art, etc.)
                    
4. Pick the top {max_analysts} analysts.

5. Each analyst should have:
- A realistic Korean or English name
- A specific role and affiliation
- A region they specialize in
- A description of their expertise"""


hallucination_prompt = """You are a STRICT grader assessing whether an LLM generation is grounded in the retrieved facts.

CRITICAL RULES:
1. The answer must ONLY contain information that appears EXACTLY in the context.
2. If exhibition names, dates, or locations are mentioned that are NOT in the context, mark as 'no'.
3. Generic or vague information without specific sources is considered hallucination.
4. Made-up exhibition titles that cannot be verified from the context are hallucination.

Give 'yes' ONLY if:
- Every exhibition name mentioned exists in the source documents
- Every date and location can be traced back to the context
- All claims have corresponding evidence in the context

Give 'no' if:
- Any exhibition information seems fabricated
- Dates or details are too specific without source verification
- The answer contains information not found in any source document"""


transform_query_prompt = """The previous search didn't return relevant results.
        
Original question: {question}

Please reformulate this into a better search query that might find:
- More specific exhibition information
- Alternative search terms
- Broader or narrower scope as needed"""


db_grade_prompt = """You are evaluating if database search results are relevant to the user's question.

Give 'yes' if:
- The results contain actual exhibition data (title, date, location, description, keywords)
- The data matches the user's query

Give 'no' if:
- Results are empty or contain errors
- No relevant exhibition information found"""


extract_data_prompt = """You are extracting VERIFIED exhibition information from search results.

STRICT RULES:
1. ONLY extract information that is EXPLICITLY stated in the source documents.
2. If a field is not clearly mentioned in the sources, leave it EMPTY (do not guess or infer).
3. Every exhibition MUST have a verifiable source_url from the context.
4. If you cannot find a direct URL source for an exhibition, DO NOT include that exhibition.
5. Do not create or fabricate exhibition names - only use exact names from sources.
6. Prefer English exhibition titles when available for easier verification.

For each VERIFIED exhibition, extract:
- title: The exact exhibition name from the source (in original language)
- title_en: English title if available (for searchability)
- description: Only description text from source (not your summary)
- period: Only if exact dates are in the source
- hours: Only if explicitly stated
- closed_days: Only if explicitly stated
- location: Venue name from source
- country: Country from source
- city: City from source
- artist: Artist names from source
- genre: Only if mentioned in source
- style: Only if mentioned in source
- ticket_url: Direct ticket link from source
- source_url: REQUIRED - The exact URL where this info was found

If information is not available in the source, leave the field EMPTY.
DO NOT include exhibitions without a verifiable source_url."""


answer_generation_prompt = """You are providing VERIFIED exhibition information to the user.

STRICT RULES:
1. Only include exhibitions that have a verifiable source URL.
2. Do not invent or fabricate exhibition names, dates, or details.
3. If information is not available, say "정보를 찾지 못했습니다" - do not guess.
4. Include the source URL for each exhibition so users can verify.
5. Prefer providing fewer accurate results over many unverified ones.

For each exhibition, provide:
- Exhibition Title (Korean and English - searchable)
- Exhibition Period (only if confirmed by source)
- Venue and Location
- Artist Information (only if confirmed)
- Source URL (required)
If you cannot find verified information for a topic, honestly state that the search did not return reliable results and suggest the user search directly on museum websites."""

slq_prompt = """You are a MySQL expert. Generate a SQL query to answer the user's question.

Database schema:
{table_info}

IMPORTANT INSTRUCTIONS:
1. ALWAYS prioritize 'exhibit' table - this contains exhibition titles, artists, descriptions
2. JOIN with 'exhibit_halls' table to get venue location/hours information
3. Use these columns:
    - exhibit: title, ticket_url, description, poster_url, start_date, end_date, status
    - exhibit_hall: name, country, city, address, hours, closed_days, phone, website
4. Filter for ONGOING exhibitions (status='ONGOING' or end_date >= CURDATE())
5. LIMIT to {top_k} results
6. Output ONLY the SQL query starting with "SQLQuery:"

Example query structure:
SQLQuery: SELECT e.title, e.description, e.start_date, e.end_date, h.name, h.country, h.city, h.address, h.hours, h.website 
FROM exhibit e 
JOIN exhibit_hall h ON e.exhibit_hall_id = h.id 
WHERE h.country LIKE '%keyword%' AND e.status='ONGOING' 
LIMIT {top_k}

User question: {input}
Dialect: {dialect}

SQLQuery:"""

search_expansion_prompt = """Based on the search results below, provide additional context about the exhibitions.

Search Results:
{context_str}

Question: {question}

RULES:
1. Only elaborate on information that exists in the search results
2. Do not add new exhibitions that are not in the search results
3. Keep your response factual and based on the sources

Answer in Korean."""

search_fallback_prompt = """The web search did not return any results for: {question}

Since no search results were found, please:
1. Suggest official museum/gallery websites to check for {question}
2. Do NOT fabricate or make up exhibition names
3. Honestly state that specific exhibition information could not be found

Answer in Korean."""

query_rewrite_prompt = """The previous search didn't return relevant results.

Original question: {question}

Create a more specific search query for finding art exhibitions.
Focus on: official museum names, {current_year}-{next_year} dates, specific locations.

Return only the improved search query (no explanation)."""

_keyword_list = get_keyword_list_string()
_exclude_list = get_exclude_list_string()
exhibition_extract_prompt = f"""Extract VERIFIED art/exhibition information ONLY from the provided sources.

TODAY'S DATE: {{current_date}}
CURRENT YEAR: {{current_year}}

## Source Documents
{{context_str}}

## User Question
{{question}}

## CRITICAL FILTERING RULES

{_keyword_list}

### STRICTLY EXCLUDE these types:
{_exclude_list}

### Extraction Rules:
1. ONLY extract **art, museum, gallery exhibitions**
2. MUST match at least ONE category from GENRE or STYLE above
3. Every exhibition MUST have a verifiable `source_url`
4. If period contains years 2020-2023 WITHOUT 2024+, SKIP it (old exhibitions)
5. Do NOT guess or infer - only use explicit information from sources
6. **ABSOLUTELY NO PLACEHOLDERS OR FAKE DATA**:
    - DO NOT use: "XXX", "XXXX", "N/A", "TBD", "미정", "정보 없음"
    - DO NOT use: "1-1-1", "123-456-7890", "+81-XX-XXXX-XXXX"
    - DO NOT invent phone numbers, addresses, or contact info
    - If information is NOT explicitly stated in sources, leave field EMPTY ("")
7. Do NOT guess - only use explicit information from sources

### Required Fields:
- **title**: Exact exhibition name from source
- **title_en**: English title (if available)
- **description**: Description from source (not your summary)
- **period**: Exhibition dates (YYYY-MM-DD format preferred)
- **location**: Venue name
- **country**: Country name
- **city**: City name
- **artist**: Artist names (if mentioned)
- **genre**: List of matching GENRE keywords from above list
- **style**: List of matching STYLE keywords from above list
- **ticket_url**: Ticket purchase link (if available)
- **source_url**: REQUIRED - URL where info was found
- **official_website**: OFFICIAL homepage URL (empty if not found)


**REMEMBER**: Empty field is BETTER than fake/guessed data. Quality over completeness.
Extract ONLY art/cultural exhibitions. Quality over quantity."""


final_answer_prompt = """Provide comprehensive exhibition information combining database and web search results.

TODAY'S DATE: {current_date}

## Question
{question}

## Database Results (Venue + Exhibition Data)
{db_results}

## Web Search Results
{context_str}

## Extracted Exhibition Data
{exhibition_text}

## FORMATTING INSTRUCTIONS

### For each exhibition, provide a MERGED view:

**[Exhibition Number]. 전시 제목**
- **영문 제목**: [English Title if available]
- **기간**: YYYY-MM-DD ~ YYYY-MM-DD
- **장소**: [Venue Name], [City], [Country]
  - 주소: [Full Address]
  - 운영시간: [Hours]
  - 휴무일: [Closed Days]
  - 연락처: [Phone]
- **작가**: [Artist Name]
- **설명**: [Exhibition Description]
- **장르**: [Genre tags from constants.py]
- **스타일**: [Style tags from constants.py]
- **예매**: [Ticket URL]
- **홈페이지**: [Venue Website]
- **출처**: [Source URL]

### Parsing DB Results:

If db_results contains tuples from JOIN query:
- Extract exhibition data (title, description, dates, status)
- Extract venue data (name, country, city, address, hours, phone, website)
- MERGE them into a single unified entry per exhibition

### Quality Filters:

INCLUDE:
- Art, museum, gallery exhibitions
- Exhibitions matching GENRE/STYLE from constants.py
- Current/upcoming exhibitions (2025-2026)

EXCLUDE:
- Ended exhibitions (before {current_date})
- Non-art events (cars, pets, food, tech conferences)
- Exhibitions without verifiable sources

Provide 5-10 high-quality results. Answer in Korean with clear structure."""