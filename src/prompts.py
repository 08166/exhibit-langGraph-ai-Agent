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
- The results contain actual exhibition data (titles, dates, locations)
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