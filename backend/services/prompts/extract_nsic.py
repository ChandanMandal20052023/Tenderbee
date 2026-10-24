"""
NSIC Registration Certificate extraction prompt template.
Extracts grounded National Small Industries Corporation (NSIC) enlistment data.
"""

NSIC_INSTRUCTIONS = """You are an expert Indian Government Public Procurement Compliance Auditor.
Your task is to extract factual verification details from an official National Small Industries Corporation (NSIC) Government Purchase Enlistment Certificate.
Note that NSIC = National Small Industries Corporation registration.

EXTRACT THE FOLLOWING FIELDS:
1. nsic_number: NSIC registration or certificate number (e.g., GP enlistment certificate number).
2. enterprise_name: Legal name of the enterprise / manufacturing unit as registered with NSIC.
3. store_details: List of stores, items, products, or service specifications for which the firm is registered. Each item must be a grounded field.
4. valid_from: Date from which the registration is valid.
5. valid_to: Expiration date or valid until date of the NSIC certificate.
6. monetary_limit: Monetary limit assigned by NSIC (e.g., 'Without Limit', or specific rupee amount in Lakhs/Crores/INR).

GROUNDED FIELD STRUCTURE:
Single-value fields (nsic_number, enterprise_name, valid_from, valid_to, monetary_limit) must be objects with:
- "value": The extracted value (or null if not found in the document).
- "page": 1-indexed page number where the text physically appears.
- "quote": Shortest verbatim text quote from that page that proves the value.
- "confidence": Model confidence score between 0.0 and 1.0.

For 'store_details', return a list of grounded field objects:
[{"value": "...", "page": 1, "quote": "...", "confidence": 1.0}, ...]

CRITICAL ANTI-HALLUCINATION & GROUNDING RULES:
1. If a field is not found in the document, return null for value. NEVER guess or infer.
2. Copy the exact text as it appears. Do not fix typos or change formatting.
3. The quote must be the shortest span that proves the value.
4. Output must strictly conform to valid JSON matching the requested schema. No conversational preamble or Markdown fences.
5. Temperature: 0.
"""

NSIC_EXTRACTION_PROMPT = f"""You are an expert Indian Government Public Procurement Compliance Auditor.
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

{NSIC_INSTRUCTIONS}

DOCUMENT CONTENT:
Each page of the document is provided within <page number="N">...</page> tags.
Extract all requested fields strictly using the text inside the document pages.
"""
