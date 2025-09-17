from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import time

app = Flask(__name__)
CORS(app)

# LLM Prompt templates
GEN_QUERIES_SYSTEM = "You generate search queries for literature review."

GEN_QUERIES_USER_TEMPLATE = """Input abstract/idea:
\"\"\"
{ABSTRACT}
\"\"\"

Task: Propose 10 concise, diverse search queries (max 8–12 words each) that best describe potential related work in different aspects (methods, tasks, data, theory, applications).

Respond with ONLY a valid JSON array of strings, no other text or formatting. Example format:
["query 1", "query 2", "query 3"]"""

COMPARE_SYSTEM = """You are scoring relatedness between a source abstract and a candidate paper.
Give a score 0–100 (higher = more similar) and a brief reason."""

COMPARE_USER_TEMPLATE = """SOURCE ABSTRACT:
\"\"\"
{ABSTRACT}
\"\"\"

CANDIDATE PAPER:
Title: {TITLE}
Authors: {AUTHORS}
Venue/Year: {VENUE} / {YEAR}
Abstract:
\"\"\"
{PAPER_ABSTRACT}
\"\"\"

Task: Return ONLY valid JSON with no other text or formatting. Required format:
{{
  "score": <0-100 integer>,
  "note": "<one-sentence reason why it is relevant or irrelevant>"
}}"""

def openai_chat_complete(api_key, system_prompt, user_prompt):
    """Make a call to OpenAI Chat Completions API"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': 'gpt-5',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    }

    response = requests.post('https://api.openai.com/v1/chat/completions',
                           headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

    return response.json()['choices'][0]['message']['content']

def semantic_scholar_search(query, limit=50):
    """Search Semantic Scholar for papers"""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        'query': query,
        'limit': limit,
        'fields': 'paperId,title,authors,year,venue,url,abstract'
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Semantic Scholar API error for query '{query}': {response.status_code}")
        return []

    data = response.json()
    return data.get('data', [])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/related-work', methods=['POST'])
def find_related_work():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        abstract = data.get('abstract', '').strip()
        openai_api_key = data.get('openai_api_key', '').strip()

        if not abstract:
            return jsonify({'error': 'Abstract is required'}), 400

        if not openai_api_key:
            return jsonify({'error': 'OpenAI API key is required'}), 400

        # Step 1: Generate search queries
        try:
            queries_response = openai_chat_complete(
                api_key=openai_api_key,
                system_prompt=GEN_QUERIES_SYSTEM,
                user_prompt=GEN_QUERIES_USER_TEMPLATE.format(ABSTRACT=abstract)
            )

            # Try to extract JSON from the response if it contains extra text
            queries_response = queries_response.strip()
            if queries_response.startswith('```json'):
                queries_response = queries_response.replace('```json', '').replace('```', '').strip()
            elif queries_response.startswith('```'):
                queries_response = queries_response.replace('```', '').strip()

            queries = json.loads(queries_response)

            if not isinstance(queries, list):
                raise ValueError("Expected JSON array of queries")

            # Ensure we have reasonable queries
            queries = [q for q in queries if isinstance(q, str) and len(q.strip()) > 0][:10]

            if len(queries) == 0:
                raise ValueError("No valid queries generated")

        except (json.JSONDecodeError, ValueError) as e:
            return jsonify({'error': f'LLM output parsing error for query generation. Response was: {queries_response[:200]}...'}), 500
        except Exception as e:
            return jsonify({'error': f'Error generating queries: {str(e)}'}), 500

        final_results = []

        # Step 2: For each query, search papers and compare
        for query in queries:
            try:
                papers = semantic_scholar_search(query, limit=50)

                for paper in papers:
                    if not paper.get('abstract'):
                        continue

                    # Prepare paper data for comparison
                    authors = [author.get('name', 'Unknown') for author in paper.get('authors', [])]
                    authors_str = ', '.join(authors)
                    venue = paper.get('venue', 'Unknown venue')
                    year = paper.get('year', 'Unknown year')

                    try:
                        compare_prompt = COMPARE_USER_TEMPLATE.format(
                            ABSTRACT=abstract,
                            TITLE=paper.get('title', ''),
                            AUTHORS=authors_str,
                            VENUE=venue,
                            YEAR=year,
                            PAPER_ABSTRACT=paper.get('abstract', '')
                        )

                        compare_response = openai_chat_complete(
                            api_key=openai_api_key,
                            system_prompt=COMPARE_SYSTEM,
                            user_prompt=compare_prompt
                        )

                        # Clean up the response for JSON parsing
                        compare_response = compare_response.strip()
                        if compare_response.startswith('```json'):
                            compare_response = compare_response.replace('```json', '').replace('```', '').strip()
                        elif compare_response.startswith('```'):
                            compare_response = compare_response.replace('```', '').strip()

                        comparison = json.loads(compare_response)
                        score = comparison.get('score', 0)
                        note = comparison.get('note', '')

                        # Validate score is a number
                        if not isinstance(score, (int, float)):
                            score = 0

                        if score > 70:
                            final_results.append({
                                'query': query,
                                'paper': {
                                    'paperId': paper.get('paperId', ''),
                                    'title': paper.get('title', ''),
                                    'authors': authors,
                                    'year': year,
                                    'venue': venue,
                                    'url': paper.get('url', ''),
                                    'abstract': paper.get('abstract', '')
                                },
                                'similarity_score': score,
                                'note': note
                            })

                    except (json.JSONDecodeError, ValueError):
                        print(f"LLM parsing error for paper comparison: {paper.get('title', 'Unknown')}")
                        continue
                    except Exception as e:
                        print(f"Error comparing paper {paper.get('title', 'Unknown')}: {str(e)}")
                        continue

            except Exception as e:
                print(f"Error processing query '{query}': {str(e)}")
                continue

        return jsonify({
            'input_abstract': abstract,
            'generated_queries': queries,
            'results': final_results
        })

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)