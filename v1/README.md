# 🔬 Research Paper Agent

An intelligent research assistant that finds related academic papers based on abstract similarity using semantic search.

## ✨ Features

- **Semantic Search**: Uses sentence transformers to find papers with similar meaning, not just keywords
- **arXiv Integration**: Searches the comprehensive arXiv database
- **Web Interface**: Clean, modern interface for easy abstract input
- **Similarity Scoring**: Shows how closely related each paper is to your input
- **Multiple Paper Sources**: Extensible architecture for adding more academic databases

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Internet connection (for downloading models and searching papers)

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd aiagentdemo
   ```

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Start the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** to: http://127.0.0.1:5000

### Manual Installation (if setup script fails)

```bash
pip install -r requirements.txt
python app.py
```

## 📖 How to Use

1. **Paste an Abstract**: Copy and paste the abstract of a paper you're researching
2. **Click Search**: The agent will find semantically similar papers
3. **Review Results**: Browse related papers with similarity scores
4. **Access Papers**: Click paper titles to view them on arXiv

## 🏗️ Architecture

### Core Components

- **`research_agent.py`**: Main search logic and semantic similarity calculation
- **`app.py`**: Flask web server with API endpoints and web interface
- **`requirements.txt`**: Python dependencies

### How It Works

1. **Text Processing**: Cleans and preprocesses the input abstract
2. **Keyword Extraction**: Identifies key terms for initial paper search
3. **Paper Retrieval**: Searches arXiv API for relevant papers
4. **Semantic Analysis**: Uses sentence transformers to encode abstracts
5. **Similarity Matching**: Calculates cosine similarity between embeddings
6. **Ranking**: Returns papers sorted by semantic similarity

## 🔧 Configuration

### Adjusting Search Parameters

Edit `research_agent.py` to modify:

- **Similarity Threshold**: Change `similarity_threshold` in `find_related_papers()`
- **Number of Results**: Modify `max_results` in `search_arxiv()`
- **Model Selection**: Change the sentence transformer model in `__init__()`

### Adding New Paper Sources

The architecture is designed to be extensible. To add new paper databases:

1. Create a new search method similar to `search_arxiv()`
2. Update `find_related_papers()` to include the new source
3. Ensure the paper format matches the expected structure

## 🧠 Model Information

- **Sentence Transformer**: `all-MiniLM-L6-v2`
  - Fast and efficient for semantic similarity
  - Good balance between speed and accuracy
  - ~80MB download on first use

## 🎯 Example Use Cases

- **Literature Review**: Find papers related to your research topic
- **Citation Discovery**: Identify relevant papers to cite
- **Research Gaps**: Discover what's been done in your field
- **Cross-Disciplinary Research**: Find related work in adjacent fields

## 🐛 Troubleshooting

### Common Issues

1. **Slow First Search**: The model downloads ~80MB on first use
2. **No Results**: Try a more technical abstract with specific terminology
3. **Connection Errors**: Check internet connection for arXiv access

### Performance Tips

- **Abstract Quality**: More technical abstracts yield better results
- **Length**: 100-500 word abstracts work best
- **Specificity**: Include domain-specific terms and methodologies

## 🛠️ Development

### Project Structure
```
aiagentdemo/
├── research_agent.py    # Core search logic
├── app.py              # Web application
├── requirements.txt    # Dependencies
├── setup.py           # Setup script
└── README.md          # This file
```

### Extending the System

- **New Embeddings**: Replace the sentence transformer model
- **Better Search**: Add more sophisticated keyword extraction
- **Paper Filtering**: Add filters by date, author, or subject
- **Caching**: Implement paper and embedding caching for performance

## 📊 API Endpoints

### `POST /api/search`
Search for related papers

**Request Body**:
```json
{
  "abstract": "Your paper abstract here..."
}
```

**Response**:
```json
{
  "success": true,
  "papers": [
    {
      "title": "Paper Title",
      "authors": "Author Names",
      "abstract": "Truncated abstract...",
      "url": "https://arxiv.org/abs/...",
      "published": "2023-01-01",
      "similarity_score": 0.85,
      "source": "arXiv"
    }
  ],
  "total_found": 10
}
```

## 📝 License

This project is open source. Feel free to modify and extend it for your research needs.

## 🤝 Contributing

Contributions are welcome! Some ideas:

- Add more paper databases (PubMed, Google Scholar, etc.)
- Improve the similarity algorithm
- Add paper filtering and sorting options
- Create a better UI/UX
- Add paper recommendation features