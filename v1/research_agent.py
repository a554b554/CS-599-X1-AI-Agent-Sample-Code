import os
import requests
import feedparser
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import re
import time


class ResearchAgent:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.papers_cache = []
        self.embeddings_cache = []

    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'\s+', ' ', text)     # Normalize whitespace
        return text.strip()

    def search_arxiv(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search arXiv for papers"""
        base_url = 'http://export.arxiv.org/api/query?'
        query_encoded = requests.utils.quote(query)
        url = f"{base_url}search_query=all:{query_encoded}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"

        try:
            response = requests.get(url, timeout=10)
            feed = feedparser.parse(response.content)

            papers = []
            for entry in feed.entries:
                paper = {
                    'title': self.clean_text(entry.title),
                    'abstract': self.clean_text(entry.summary),
                    'authors': [author.name for author in entry.authors],
                    'url': entry.link,
                    'published': entry.published,
                    'arxiv_id': entry.id.split('/')[-1],
                    'source': 'arXiv'
                }
                papers.append(paper)

            return papers
        except Exception as e:
            print(f"Error searching arXiv: {e}")
            return []

    def extract_keywords(self, abstract: str) -> List[str]:
        """Extract potential search keywords from abstract"""
        # Remove common stopwords and extract meaningful terms
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'we', 'they', 'i', 'you', 'he', 'she', 'it'}

        # Simple keyword extraction - in practice, you might want to use more sophisticated NLP
        words = re.findall(r'\b[a-zA-Z]{3,}\b', abstract.lower())
        keywords = [word for word in words if word not in stopwords]

        # Get most frequent words (simple approach)
        from collections import Counter
        word_counts = Counter(keywords)
        top_keywords = [word for word, count in word_counts.most_common(10)]

        return top_keywords

    def find_related_papers(self, input_abstract: str, similarity_threshold: float = 0.3) -> List[Tuple[Dict, float]]:
        """Find papers related to the input abstract"""
        # Extract keywords and search for papers
        keywords = self.extract_keywords(input_abstract)
        search_query = ' '.join(keywords[:5])  # Use top 5 keywords

        print(f"Searching with keywords: {search_query}")

        # Search arXiv
        papers = self.search_arxiv(search_query, max_results=100)

        if not papers:
            return []

        # Create embeddings for all abstracts
        input_embedding = self.model.encode([input_abstract])
        paper_abstracts = [paper['abstract'] for paper in papers]
        paper_embeddings = self.model.encode(paper_abstracts)

        # Calculate similarities
        similarities = cosine_similarity(input_embedding, paper_embeddings)[0]

        # Filter by threshold and sort by similarity
        related_papers = []
        for i, similarity in enumerate(similarities):
            if similarity >= similarity_threshold:
                related_papers.append((papers[i], float(similarity)))

        # Sort by similarity score (descending)
        related_papers.sort(key=lambda x: x[1], reverse=True)

        return related_papers[:20]  # Return top 20 most similar papers

    def format_paper_info(self, paper: Dict, similarity_score: float) -> Dict:
        """Format paper information for display"""
        return {
            'title': paper['title'],
            'authors': ', '.join(paper['authors'][:3]) + ('...' if len(paper['authors']) > 3 else ''),
            'abstract': paper['abstract'][:300] + '...' if len(paper['abstract']) > 300 else paper['abstract'],
            'url': paper['url'],
            'published': paper['published'][:10],  # Just the date part
            'similarity_score': round(similarity_score, 3),
            'source': paper['source']
        }