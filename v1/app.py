from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from research_agent import ResearchAgent
import os

app = Flask(__name__)
CORS(app)

# Initialize the research agent
agent = ResearchAgent()

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Paper Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .input-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .input-section h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }

        textarea {
            width: 100%;
            min-height: 150px;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 14px;
            font-family: inherit;
            resize: vertical;
            transition: border-color 0.3s ease;
        }

        textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .search-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 15px;
            transition: transform 0.3s ease;
        }

        .search-btn:hover {
            transform: translateY(-2px);
        }

        .search-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }

        .loading {
            text-align: center;
            padding: 40px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .results {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .results-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            font-size: 1.2rem;
            font-weight: 600;
        }

        .paper-card {
            border-bottom: 1px solid #e1e5e9;
            padding: 25px 30px;
            transition: background-color 0.3s ease;
        }

        .paper-card:hover {
            background-color: #f8f9fa;
        }

        .paper-card:last-child {
            border-bottom: none;
        }

        .paper-title {
            color: #2c3e50;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 10px;
            line-height: 1.4;
        }

        .paper-title a {
            color: inherit;
            text-decoration: none;
        }

        .paper-title a:hover {
            color: #667eea;
        }

        .paper-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 15px;
            font-size: 0.9rem;
            color: #666;
        }

        .meta-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .similarity-score {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .paper-abstract {
            color: #555;
            line-height: 1.6;
            margin-top: 15px;
        }

        .error {
            background: #fee;
            border: 1px solid #fcc;
            color: #c66;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }

            .input-section, .paper-card {
                padding: 20px;
            }

            .paper-meta {
                flex-direction: column;
                gap: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Research Paper Agent</h1>
            <p>Find related papers by pasting an abstract below</p>
        </div>

        <div class="input-section">
            <h2>📄 Enter Paper Abstract</h2>
            <textarea
                id="abstractInput"
                placeholder="Paste the abstract of your paper here. The agent will find related work by analyzing semantic similarity..."
            ></textarea>
            <button class="search-btn" onclick="searchRelatedPapers()" id="searchBtn">
                🔍 Find Related Papers
            </button>
        </div>

        <div id="loading" class="loading" style="display: none;">
            <div class="loading-spinner"></div>
            <p>Searching for related papers...</p>
        </div>

        <div id="results" style="display: none;"></div>
    </div>

    <script>
        async function searchRelatedPapers() {
            const abstract = document.getElementById('abstractInput').value.trim();

            if (!abstract) {
                alert('Please enter an abstract first!');
                return;
            }

            const searchBtn = document.getElementById('searchBtn');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');

            // Show loading state
            searchBtn.disabled = true;
            searchBtn.textContent = 'Searching...';
            loading.style.display = 'block';
            results.style.display = 'none';

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ abstract: abstract })
                });

                const data = await response.json();

                if (data.success) {
                    displayResults(data.papers);
                } else {
                    displayError(data.error || 'An error occurred while searching for papers.');
                }

            } catch (error) {
                console.error('Error:', error);
                displayError('Failed to connect to the server. Please try again.');
            } finally {
                // Reset UI state
                searchBtn.disabled = false;
                searchBtn.textContent = '🔍 Find Related Papers';
                loading.style.display = 'none';
            }
        }

        function displayResults(papers) {
            const results = document.getElementById('results');

            if (!papers || papers.length === 0) {
                results.innerHTML = `
                    <div class="results-header">No Related Papers Found</div>
                    <div class="paper-card">
                        <p>No related papers were found. Try using a different abstract or check if the abstract contains enough technical terms.</p>
                    </div>
                `;
            } else {
                let html = `<div class="results-header">Found ${papers.length} Related Papers</div>`;

                papers.forEach(paper => {
                    html += `
                        <div class="paper-card">
                            <div class="paper-title">
                                <a href="${paper.url}" target="_blank">${paper.title}</a>
                            </div>
                            <div class="paper-meta">
                                <div class="meta-item">
                                    <span>👥 ${paper.authors}</span>
                                </div>
                                <div class="meta-item">
                                    <span>📅 ${paper.published}</span>
                                </div>
                                <div class="meta-item">
                                    <span>🏷️ ${paper.source}</span>
                                </div>
                                <div class="similarity-score">
                                    ${Math.round(paper.similarity_score * 100)}% match
                                </div>
                            </div>
                            <div class="paper-abstract">${paper.abstract}</div>
                        </div>
                    `;
                });

                results.innerHTML = html;
            }

            results.style.display = 'block';
        }

        function displayError(message) {
            const results = document.getElementById('results');
            results.innerHTML = `
                <div class="results-header">Error</div>
                <div class="paper-card">
                    <div class="error">${message}</div>
                </div>
            `;
            results.style.display = 'block';
        }

        // Allow Enter key to trigger search
        document.getElementById('abstractInput').addEventListener('keydown', function(event) {
            if (event.ctrlKey && event.key === 'Enter') {
                searchRelatedPapers();
            }
        });
    </script>
</body>
</html>
    """)

@app.route('/api/search', methods=['POST'])
def search_papers():
    try:
        data = request.json
        abstract = data.get('abstract', '').strip()

        if not abstract:
            return jsonify({'success': False, 'error': 'Abstract is required'})

        # Find related papers
        related_papers = agent.find_related_papers(abstract)

        # Format the results
        formatted_papers = []
        for paper, similarity in related_papers:
            formatted_paper = agent.format_paper_info(paper, similarity)
            formatted_papers.append(formatted_paper)

        return jsonify({
            'success': True,
            'papers': formatted_papers,
            'total_found': len(formatted_papers)
        })

    except Exception as e:
        print(f"Error in search_papers: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("Starting Research Paper Agent...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)