1) Goal

Given a paper abstract (or idea), the system:

- uses an LLM (OpenAI API) to generate ~10 search queries,

- for each query, calls the Semantic Scholar API to fetch the top 50 related papers,

- for each candidate paper, uses the LLM to compare it to the input and output a similarity score (0–100) plus a short note,

- keeps papers with score > 70 and returns them,

- shows everything in a simple web page where the user pastes the abstract and their OpenAI API key.

2) High-level flow

User pastes abstract/idea + OpenAI API key in the web UI → click “Find related work”.

Backend:

LLM reads the abstract → generates 10 diverse queries.

Push queries into a queue.

While queue not empty:

Pop one query → call Semantic Scholar → collect up to 50 papers.

For each paper:

LLM compares the paper (title+abstract+metadata) with the input abstract → score 0–100 and a short note why relevant/irrelevant.

If score > 70 → add to final output list (include the note).

Return the final list.

Frontend displays the results (paper metadata, similarity score, and note).

3) Interfaces (contract first)
3.1 Backend HTTP API

POST /related-work

Request JSON

{
  "abstract": "string (required)",
  "openai_api_key": "string (required)"
}


Response JSON

{
  "input_abstract": "string",
  "generated_queries": ["string", "... up to 10"],
  "results": [
    {
      "query": "string (the query that surfaced this paper)",
      "paper": {
        "paperId": "string",
        "title": "string",
        "authors": ["string", "..."],
        "year": 2023,
        "venue": "string",
        "url": "string",
        "abstract": "string"
      },
      "similarity_score": 0,
      "note": "short reason why it is (ir)relevant"
    }
  ]
}


Behavior: returns only items with similarity_score > 70.

3.2 Frontend UI elements

Textarea: “Paste idea or abstract”

Text input: “OpenAI API key” (password-type field)

Button: “Find related work”

Loading state: “Running search…”

Results area:

For each paper: Title (link), authors, venue/year, similarity score, note, and a short abstract snippet.

4) LLM prompts (exact templates)
4.1 Generate queries (10)

System:

You generate search queries for literature review.


User template:

Input abstract/idea:
"""
{ABSTRACT}
"""

Task: Propose 10 concise, diverse search queries (max 8–12 words each) that best describe potential related work in different aspects (methods, tasks, data, theory, applications). Output as a JSON array of strings only.


Expected output: JSON array of 10 strings.

4.2 Compare input vs. a candidate paper

System:

You are scoring relatedness between a source abstract and a candidate paper.
Give a score 0–100 (higher = more similar) and a brief reason.


User template:

SOURCE ABSTRACT:
"""
{ABSTRACT}
"""

CANDIDATE PAPER:
Title: {TITLE}
Authors: {AUTHORS}
Venue/Year: {VENUE} / {YEAR}
Abstract:
"""
{PAPER_ABSTRACT}
"""

Task: Return strictly JSON with fields:
{
  "score": <0-100 integer>,
  "note": "<one-sentence reason why it is relevant or irrelevant>"
}

5) Backend logic (pseudocode)
POST /related-work
  read abstract, openai_api_key

  # 1) Generate queries
  queries = openai_chat_complete(
    api_key=openai_api_key,
    system=GEN_QUERIES_SYSTEM,
    user=GEN_QUERIES_USER(abstract)
  )
  queries = parse_json_array(queries)   # expect ~10 strings

  final_results = []
  for query in queries:
    # 2) Search on Semantic Scholar
    papers = semantic_scholar_search(query, limit=50)

    for paper in papers:
      compare_json = openai_chat_complete(
        api_key=openai_api_key,
        system=COMPARE_SYSTEM,
        user=COMPARE_USER(abstract, paper)
      )
      {score, note} = parse_json(compare_json)

      if score > 70:
        final_results.append({
          "query": query,
          "paper": {
            "paperId": paper.paperId,
            "title": paper.title,
            "authors": [a.name for a in paper.authors],
            "year": paper.year,
            "venue": paper.venue,
            "url": paper.url,                 # prefer open-access / S2 URL
            "abstract": paper.abstract
          },
          "similarity_score": score,
          "note": note
        })

  return {
    "input_abstract": abstract,
    "generated_queries": queries,
    "results": final_results
  }

6) External API usage (only what you specified)
6.1 OpenAI API (LLM calls)

Use the Chat Completions (or Responses) endpoint with model set to your chosen OpenAI chat model.

Pass through the user-supplied OpenAI API key from the UI in the Authorization header for both prompts above.

6.2 Semantic Scholar (search engine)

Use the public Semantic Scholar API search endpoint to fetch top 50 papers per query (title, authors, year, venue, URL, abstract).

Extract paperId, title, authors, year, venue, url, and abstract for scoring and display.

7) Minimal frontend behavior (wireframe-level)
[ OpenAI API key ______________________ ]  (type=password)
[ Paste idea/abstract here .................................... ]
[ Find related work ]

--- Loading state: “Running search…” ---

Results:
- [Title (link)]  | Authors | Venue, Year
  Similarity: 87
  Note: “...” 
  Abstract: “... (short snippet)”
- [Title (link)]  | ...
  ...

8) Minimal validation & errors (keep simple)

If abstract or API key is empty → show inline message on the page.

If OpenAI returns a non-JSON response for queries or comparison → show “LLM output parsing error”.

If Semantic Scholar returns no results for a query → skip it silently.

If the backend returns HTTP error → show its message.