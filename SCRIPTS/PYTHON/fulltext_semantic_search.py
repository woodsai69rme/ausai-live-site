import numpy as np
import sqlite3
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import faiss
import re
import logging
from datetime import datetime


class FullTextSemanticSearch:
    """
    Implements both full-text and semantic search functionality for documents,
    prompts, and code snippets using TF-IDF and sentence embeddings.
    """
    
    def __init__(self, db_path: str = "./prompts_solutions.db", embeddings_model: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.embeddings_model_name = embeddings_model
        self.model = SentenceTransformer(embeddings_model)
        
        # Initialize database connection
        self.conn = sqlite3.connect(db_path)
        
        # Initialize components
        self.tfidf_vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
        self.document_embeddings = None
        self.document_ids = []
        self.documents = []
        
        # FAISS index for efficient similarity search
        self.index = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_documents_from_db(self):
        """Load documents from the database for indexing."""
        cursor = self.conn.cursor()
        
        # Load prompts
        cursor.execute("SELECT id, prompt_text FROM prompts")
        for row in cursor.fetchall():
            self.document_ids.append(f"prompt_{row[0]}")
            self.documents.append({
                'id': f"prompt_{row[0]}",
                'type': 'prompt',
                'content': row[1],
                'title': f"Prompt {row[0]}"
            })
        
        # Load solutions
        cursor.execute("SELECT id, solution_code, language FROM solutions")
        for row in cursor.fetchall():
            self.document_ids.append(f"solution_{row[0]}")
            self.documents.append({
                'id': f"solution_{row[0]}",
                'type': 'solution',
                'content': row[1],
                'title': f"Solution {row[0]} in {row[2]}"
            })
        
        # Load documents from RAG chunks if available
        try:
            with open("./rag_chunks.json", 'r', encoding='utf-8') as f:
                rag_chunks = json.load(f)
            
            for chunk in rag_chunks:
                doc_id = f"rag_{chunk['chunk_id'][:12]}"
                self.document_ids.append(doc_id)
                self.documents.append({
                    'id': doc_id,
                    'type': 'document_chunk',
                    'content': chunk['content'],
                    'title': f"Document: {Path(chunk['source']).name}"
                })
        except FileNotFoundError:
            self.logger.info("RAG chunks file not found, skipping document chunks")
        except Exception as e:
            self.logger.warning(f"Error loading RAG chunks: {e}")
    
    def build_tfidf_index(self):
        """Build TF-IDF index for full-text search."""
        if not self.documents:
            self.logger.warning("No documents loaded for indexing")
            return
        
        # Extract content texts
        texts = [doc['content'] for doc in self.documents]
        
        # Fit TF-IDF vectorizer
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
        self.logger.info(f"Built TF-IDF index with {self.tfidf_matrix.shape[0]} documents")
    
    def build_semantic_index(self):
        """Build semantic index using sentence embeddings and FAISS."""
        if not self.documents:
            self.logger.warning("No documents loaded for indexing")
            return
        
        # Extract content texts
        texts = [doc['content'] for doc in self.documents]
        
        # Generate embeddings
        self.logger.info(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings.astype('float32')
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Add embeddings to index
        self.index.add(embeddings)
        
        self.logger.info(f"Built semantic index with {embeddings.shape[0]} documents")
    
    def initialize_search_engine(self):
        """Initialize both full-text and semantic search indexes."""
        self.logger.info("Loading documents from database...")
        self.load_documents_from_db()
        
        self.logger.info("Building TF-IDF index...")
        self.build_tfidf_index()
        
        self.logger.info("Building semantic index...")
        self.build_semantic_index()
        
        self.logger.info("Search engine initialized successfully!")
    
    def full_text_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform full-text search using TF-IDF."""
        if not hasattr(self, 'tfidf_matrix'):
            self.logger.error("TF-IDF index not built")
            return []
        
        # Transform query using the same vectorizer
        query_vec = self.tfidf_vectorizer.transform([query])
        
        # Compute similarities
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top-k results
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include results with positive similarity
                results.append({
                    'id': self.documents[idx]['id'],
                    'type': self.documents[idx]['type'],
                    'title': self.documents[idx]['title'],
                    'content': self.documents[idx]['content'][:200] + "..." if len(self.documents[idx]['content']) > 200 else self.documents[idx]['content'],
                    'similarity_score': float(similarities[idx]),
                    'search_type': 'full_text'
                })
        
        return results
    
    def semantic_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search using sentence embeddings."""
        if self.index is None:
            self.logger.error("Semantic index not built")
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])
        query_embedding = query_embedding.astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search in FAISS index
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and score > 0:  # Valid result with positive similarity
                results.append({
                    'id': self.documents[idx]['id'],
                    'type': self.documents[idx]['type'],
                    'title': self.documents[idx]['title'],
                    'content': self.documents[idx]['content'][:200] + "..." if len(self.documents[idx]['content']) > 200 else self.documents[idx]['content'],
                    'similarity_score': float(score),
                    'search_type': 'semantic'
                })
        
        return results
    
    def hybrid_search(self, query: str, top_k: int = 10, semantic_weight: float = 0.7) -> List[Dict[str, Any]]:
        """Combine full-text and semantic search results."""
        ft_results = self.full_text_search(query, top_k * 2)  # Get more results for combination
        sem_results = self.semantic_search(query, top_k * 2)
        
        # Create dictionaries for easy lookup and scoring
        ft_scores = {res['id']: res['similarity_score'] for res in ft_results}
        sem_scores = {res['id']: res['similarity_score'] for res in sem_results}
        
        # Combine all unique document IDs
        all_ids = set(ft_scores.keys()) | set(sem_scores.keys())
        
        combined_results = []
        for doc_id in all_ids:
            ft_score = ft_scores.get(doc_id, 0.0)
            sem_score = sem_scores.get(doc_id, 0.0)
            
            # Normalize scores to 0-1 range if they exist
            if ft_results:
                max_ft_score = max(ft_scores.values()) if ft_scores else 1.0
                ft_score = ft_score / max_ft_score if max_ft_score > 0 else 0.0
            
            if sem_results:
                max_sem_score = max(sem_scores.values()) if sem_scores else 1.0
                sem_score = sem_score / max_sem_score if max_sem_score > 0 else 0.0
            
            # Calculate weighted combined score
            combined_score = (1 - semantic_weight) * ft_score + semantic_weight * sem_score
            
            # Find the document details
            doc_details = None
            for doc in self.documents:
                if doc['id'] == doc_id:
                    doc_details = doc
                    break
            
            if doc_details:
                combined_results.append({
                    'id': doc_id,
                    'type': doc_details['type'],
                    'title': doc_details['title'],
                    'content': doc_details['content'][:200] + "..." if len(doc_details['content']) > 200 else doc_details['content'],
                    'ft_score': ft_score,
                    'sem_score': sem_score,
                    'combined_score': combined_score,
                    'search_type': 'hybrid'
                })
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return combined_results[:top_k]
    
    def search_by_type(self, query: str, doc_type: str, search_method: str = 'hybrid', top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for documents of a specific type."""
        all_results = []
        
        if search_method == 'full_text':
            all_results = self.full_text_search(query, top_k * 3)  # Get more results to filter
        elif search_method == 'semantic':
            all_results = self.semantic_search(query, top_k * 3)
        elif search_method == 'hybrid':
            all_results = self.hybrid_search(query, top_k * 3)
        
        # Filter by document type
        filtered_results = [res for res in all_results if res['type'] == doc_type]
        
        return filtered_results[:top_k]
    
    def save_index(self, index_path: str = "./search_index.pkl"):
        """Save the search index to disk."""
        index_data = {
            'document_ids': self.document_ids,
            'documents': self.documents,
            'index': self.index,
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'tfidf_matrix': self.tfidf_matrix
        }
        
        with open(index_path, 'wb') as f:
            pickle.dump(index_data, f)
        
        self.logger.info(f"Search index saved to {index_path}")
    
    def load_index(self, index_path: str = "./search_index.pkl"):
        """Load the search index from disk."""
        try:
            with open(index_path, 'rb') as f:
                index_data = pickle.load(f)
            
            self.document_ids = index_data['document_ids']
            self.documents = index_data['documents']
            self.index = index_data['index']
            self.tfidf_vectorizer = index_data['tfidf_vectorizer']
            self.tfidf_matrix = index_data['tfidf_matrix']
            
            self.logger.info(f"Search index loaded from {index_path}")
            return True
        except FileNotFoundError:
            self.logger.warning(f"Index file {index_path} not found")
            return False
        except Exception as e:
            self.logger.error(f"Error loading index: {e}")
            return False


class SearchInterface:
    """User-friendly interface for the search functionality."""
    
    def __init__(self, db_path: str = "./prompts_solutions.db"):
        self.search_engine = FullTextSemanticSearch(db_path)
    
    def initialize(self, rebuild_index: bool = False, index_path: str = "./search_index.pkl"):
        """Initialize the search engine, optionally loading from saved index."""
        if not rebuild_index:
            if self.search_engine.load_index(index_path):
                return  # Successfully loaded from saved index
        
        # Build new index
        self.search_engine.initialize_search_engine()
        
        # Save the new index
        self.search_engine.save_index(index_path)
    
    def search(self, query: str, search_type: str = 'hybrid', top_k: int = 10, doc_type: str = None) -> List[Dict[str, Any]]:
        """Perform a search with the specified parameters."""
        if doc_type:
            return self.search_engine.search_by_type(query, doc_type, search_type, top_k)
        
        if search_type == 'full_text':
            return self.search_engine.full_text_search(query, top_k)
        elif search_type == 'semantic':
            return self.search_engine.semantic_search(query, top_k)
        elif search_type == 'hybrid':
            return self.search_engine.hybrid_search(query, top_k)
        else:
            raise ValueError("search_type must be 'full_text', 'semantic', or 'hybrid'")
    
    def get_available_types(self) -> List[str]:
        """Get list of available document types."""
        return list(set(doc['type'] for doc in self.search_engine.documents))
    
    def close(self):
        """Close resources."""
        if self.search_engine.conn:
            self.search_engine.conn.close()


def main():
    """Main function to demonstrate the search functionality."""
    print("Full-Text and Semantic Search Engine")
    print("=" * 40)
    
    db_path = input("Enter database path (default: ./prompts_solutions.db): ").strip()
    if not db_path:
        db_path = "./prompts_solutions.db"
    
    index_path = input("Enter index file path (default: ./search_index.pkl): ").strip()
    if not index_path:
        index_path = "./search_index.pkl"
    
    rebuild = input("Rebuild index? (y/N): ").strip().lower() == 'y'
    
    # Initialize search interface
    search_interface = SearchInterface(db_path)
    print("Initializing search engine...")
    search_interface.initialize(rebuild_index=rebuild, index_path=index_path)
    
    # Show available document types
    types = search_interface.get_available_types()
    print(f"\nAvailable document types: {', '.join(types)}")
    
    # Interactive search
    print("\nInteractive Search (type 'quit' to exit):")
    while True:
        query = input("\nEnter search query: ").strip()
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        search_type = input("Search type (full_text/semantic/hybrid - default: hybrid): ").strip().lower()
        if not search_type:
            search_type = 'hybrid'
        
        doc_type = input("Filter by document type (press Enter for all types): ").strip()
        if not doc_type:
            doc_type = None
        
        try:
            results = search_interface.search(query, search_type=search_type, top_k=5, doc_type=doc_type)
            
            print(f"\nSearch results ({search_type}):")
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. [{result['type']}] {result['title']}")
                    print(f"     Score: {result.get('combined_score', result.get('similarity_score', 0)):.3f}")
                    print(f"     Preview: {result['content'][:150]}...")
                    print()
            else:
                print("  No results found.")
        
        except Exception as e:
            print(f"Search error: {e}")
    
    search_interface.close()
    print("\nSearch engine closed. Full-text and semantic search functionality implemented!")


if __name__ == "__main__":
    main()