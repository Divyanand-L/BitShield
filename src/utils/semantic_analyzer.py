"""
Semantic Similarity Analysis using Sentence Transformers
"""
from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class SemanticAnalyzer:
    """Analyzes semantic similarity between documents"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic analyzer.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        logger.info("Loading semantic model: %s", model_name)
        self.model = SentenceTransformer(model_name)
    
    def compute_similarity_matrix(self, texts: List[str]) -> np.ndarray:
        """
        Compute pairwise similarity between all texts.
        
        Args:
            texts: List of text documents
            
        Returns:
            Similarity matrix (NxN numpy array)
        """
        if not texts:
            return np.array([])
        
        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_tensor=True)
        
        # Compute cosine similarities
        similarity_matrix = util.cos_sim(embeddings, embeddings)
        
        return similarity_matrix.cpu().numpy()
    
    def find_similar_documents(
        self, 
        texts: Dict[str, str], 
        threshold: float = 0.7
    ) -> List[Tuple[str, str, float]]:
        """
        Find pairs of documents that are highly similar.
        
        Args:
            texts: Dictionary mapping document IDs to text content
            threshold: Similarity threshold (0 to 1)
            
        Returns:
            List of (doc1_id, doc2_id, similarity_score) tuples
        """
        doc_ids = list(texts.keys())
        doc_texts = [texts[doc_id] for doc_id in doc_ids]
        
        if len(doc_texts) < 2:
            return []
        
        # Compute similarity matrix
        sim_matrix = self.compute_similarity_matrix(doc_texts)
        
        # Find similar pairs
        similar_pairs = []
        for i in range(len(doc_ids)):
            for j in range(i + 1, len(doc_ids)):
                similarity = sim_matrix[i, j]
                if similarity >= threshold:
                    similar_pairs.append((doc_ids[i], doc_ids[j], float(similarity)))
        
        # Sort by similarity (descending)
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        
        logger.info("Found %d similar document pairs above threshold %.2f", len(similar_pairs), threshold)
        return similar_pairs
    
    def analyze_bidder_documents(
        self, 
        bidder_texts: Dict[str, Dict[str, str]]
    ) -> Dict[str, any]:
        """
        Analyze similarity across bidder submissions.
        
        Args:
            bidder_texts: Nested dict {bidder_id: {doc_id: text}}
            
        Returns:
            Analysis results with similarity scores and suspicious patterns
        """
        # Flatten all documents
        all_docs = {}
        for bidder_id, docs in bidder_texts.items():
            for doc_id, text in docs.items():
                all_docs[f"{bidder_id}:{doc_id}"] = text
        
        # Find similar documents
        similar_pairs = self.find_similar_documents(all_docs, threshold=0.7)
        
        # Group by bidder pairs
        cross_bidder_similarity = []
        for doc1, doc2, score in similar_pairs:
            bidder1 = doc1.split(":")[0]
            bidder2 = doc2.split(":")[0]
            
            if bidder1 != bidder2:
                cross_bidder_similarity.append({
                    "bidder1": bidder1,
                    "bidder2": bidder2,
                    "document1": doc1,
                    "document2": doc2,
                    "similarity": score
                })
        
        return {
            "total_comparisons": len(similar_pairs),
            "cross_bidder_similarities": cross_bidder_similarity,
            "high_risk_pairs": [p for p in cross_bidder_similarity if p["similarity"] > 0.85]
        }
