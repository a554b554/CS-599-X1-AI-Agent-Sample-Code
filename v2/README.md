# Academic Paper Related Work Finder

A web application that uses AI to find related academic papers based on your research abstract or idea.

## Features

- Generate diverse search queries using OpenAI's GPT models
- Search academic papers using Semantic Scholar API
- AI-powered similarity scoring between your abstract and candidate papers
- Clean web interface for easy use
- Only shows papers with similarity score > 70

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and go to `http://localhost:5000`

## Usage

1. Enter your OpenAI API key (this is not stored and only used for the current session)
2. Paste your research abstract or idea in the text area
3. Click "Find Related Work"
4. Review the results with similarity scores and relevance notes

## How it works

1. **Query Generation**: The system uses OpenAI to generate ~10 diverse search queries based on your abstract
2. **Paper Search**: Each query is used to search Semantic Scholar for up to 50 related papers
3. **Similarity Scoring**: OpenAI compares each paper to your abstract and provides a 0-100 similarity score with a note
4. **Filtering**: Only papers with similarity score > 70 are shown in the results

## API Endpoint

The system also provides a REST API endpoint:

**POST /related-work**

Request:
```json
{
  "abstract": "Your research abstract or idea",
  "openai_api_key": "Your OpenAI API key"
}
```

Response:
```json
{
  "input_abstract": "...",
  "generated_queries": ["query1", "query2", ...],
  "results": [
    {
      "query": "query that found this paper",
      "paper": {
        "paperId": "...",
        "title": "...",
        "authors": ["..."],
        "year": 2023,
        "venue": "...",
        "url": "...",
        "abstract": "..."
      },
      "similarity_score": 85,
      "note": "Why this paper is relevant..."
    }
  ]
}
```