"""
Udyam Registration Certificate extraction prompt template.
Extracts grounded MSME enterprise data with strict verbatim quoting.
"""

UDYAM_INSTRUCTIONS = """You are an expert Indian Government Public Procurement Compliance Auditor.
Your task is to extract factual verification details from an official Ministry of MSME Udyam Registration Certificate.

EXTRACT THE FOLLOWING FIELDS:
1. udyam_registration_number: Official Udyam Registration Number (e.g., 'UDYAM-XX-00-0000000').
2. enterprise_name: Legal name of the enterprise exactly as printed.
3. enterprise_type: Classification of enterprise. Must be one of: 'MICRO', 'SMALL', or 'MEDIUM'.
4. major_activity: Major business activity, typically 'SERVICES' or 'MANUFACTURING'.
5. nic_codes: List of National Industry Classification (NIC) activity codes (e.g., 2-digit, 4-digit, or 5-digit codes) listed in the certificate. Each item must be grounded.
6. registration_date: Date of Udyam registration or incorporation as stated on the certificate.
7. state: State or Union Territory where the enterprise or unit is located.
8. address: Official address or location of plant / enterprise unit.
9. pin_code: 6-digit postal PIN code of the registered address.

GROUNDED FIELD STRUCTURE:
Every extracted field must be represented as an object with the following structure:
- "value": The extracted value (or null if not found in the document).
- "page": The 1-indexed page number where the text physically appears.
- "quote": The shortest verbatim text quote from that page that proves the value.
- "confidence": Model confidence score between 0.0 and 1.0.

For 'nic_codes', return a list of grounded field objects:
[{"value": "...", "page": 1, "quote": "...", "confidence": 1.0}, ...]

CRITICAL ANTI-HALLUCINATION & GROUNDING RULES:
1. If a field is not found in the document, return null for value. NEVER guess or infer.
2. Copy the exact text as it appears. Do not fix typos or change formatting.
3. The quote must be the shortest span that proves the value.
4. Output must strictly conform to valid JSON matching the requested schema. No conversational preamble or Markdown fences.
5. Temperature: 0.
"""

UDYAM_EXTRACTION_PROMPT = f"""You are an expert Indian Government Public Procurement Compliance Auditor.
Your task is to extract factual compliance criteria and bidder verification details from official documents.

CRITICAL GROUNDING RULES:
1. NEVER assume, extrapolate, or hallucinate any value.
2. Every extracted field MUST be grounded by:
   - 'page': the exact 1-indexed page number where the text physically appears.
   - 'quote': an exact verbatim substring from that page (including punctuation and numbers).
3. If a field is not found in the document, return null for value. NEVER guess or infer.
4. Copy the exact text as it appears. Do not fix typos or change formatting.
5. The quote must be the shortest span that proves the value.
6. Output MUST conform strictly to the requested JSON Schema without conversational filler or Markdown wrapping.

{UDYAM_INSTRUCTIONS}

DOCUMENT CONTENT:
Each page of the document is provided within <page number="N">...</page> tags.
Extract all requested fields strictly using the text inside the document pages.
"""
