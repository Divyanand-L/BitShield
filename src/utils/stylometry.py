"""
Stylometry Analysis using spaCy and scikit-learn
"""
import logging
import numpy as np
from typing import Dict
from sklearn.metrics.pairwise import cosine_similarity

# Try to import spaCy, but handle Python 3.14 incompatibility
try:
    import spacy
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False
    spacy = None

logger = logging.getLogger(__name__)


class StylometryAnalyzer:
    """Analyzes writing style to detect potential authorship similarities"""
    
    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """
        Initialize the stylometry analyzer.
        
        Args:
            spacy_model: Name of the spaCy model to use
        """
        if not SPACY_AVAILABLE:
            logger.warning("spaCy is not available (Python 3.14 incompatibility). Using basic text analysis.")
            self.nlp = None
            return
            
        logger.info("Loading spaCy model: %s", spacy_model)
        try:
            self.nlp = spacy.load(spacy_model)
        except OSError:
            logger.warning("Model %s not found. Using basic analysis instead.", spacy_model)
            self.nlp = None
    
    def extract_stylometric_features(self, text: str) -> Dict[str, float]:
        """
        Extract stylometric features from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary of stylometric features
        """
        if self.nlp is None:
            # Fallback basic analysis without spaCy
            words = text.split()
            sentences = text.split('.')
            if not words:
                return {}
            return {
                "avg_word_length": sum(len(w) for w in words) / len(words),
                "avg_sentence_length": len(words) / max(1, len(sentences)),
                "lexical_diversity": len(set(words)) / len(words),
                "punct_frequency": sum(1 for c in text if c in '.,!?;:') / max(1, len(text)),
                "stopword_frequency": 0.0,
                "noun_frequency": 0.0,
                "verb_frequency": 0.0,
                "adj_frequency": 0.0,
            }
        
        doc = self.nlp(text)
        
        # Basic statistics
        total_tokens = len([token for token in doc if not token.is_space])
        total_sentences = len(list(doc.sents))
        
        if total_tokens == 0:
            return {}
        
        # Calculate features
        features = {
            "avg_word_length": np.mean([len(token.text) for token in doc if not token.is_punct]),
            "avg_sentence_length": total_tokens / max(total_sentences, 1),
            "lexical_diversity": len(set([token.text.lower() for token in doc])) / total_tokens,
            "punct_frequency": len([token for token in doc if token.is_punct]) / total_tokens,
            "stopword_frequency": len([token for token in doc if token.is_stop]) / total_tokens,
            "noun_frequency": len([token for token in doc if token.pos_ == "NOUN"]) / total_tokens,
            "verb_frequency": len([token for token in doc if token.pos_ == "VERB"]) / total_tokens,
            "adj_frequency": len([token for token in doc if token.pos_ == "ADJ"]) / total_tokens,
        }
        
        return features
    
    def compare_writing_styles(
        self, 
        texts: Dict[str, str]
    ) -> Dict[str, any]:
        """
        Compare writing styles across multiple documents.
        
        Args:
            texts: Dictionary mapping document IDs to text content
            
        Returns:
            Style comparison results
        """
        if len(texts) < 2:
            return {"error": "Need at least 2 documents to compare"}
        
        # Extract features for each document
        features = {}
        for doc_id, text in texts.items():
            features[doc_id] = self.extract_stylometric_features(text)
        
        # Convert to feature vectors
        doc_ids = list(features.keys())
        feature_names = list(next(iter(features.values())).keys())
        
        feature_matrix = np.array([
            [features[doc_id].get(fname, 0) for fname in feature_names]
            for doc_id in doc_ids
        ])
        
        # Compute similarity
        similarity_matrix = cosine_similarity(feature_matrix)
        
        # Find similar pairs
        similar_pairs = []
        for i in range(len(doc_ids)):
            for j in range(i + 1, len(doc_ids)):
                similarity = similarity_matrix[i, j]
                if similarity > 0.8:  # High similarity threshold
                    similar_pairs.append({
                        "doc1": doc_ids[i],
                        "doc2": doc_ids[j],
                        "similarity": float(similarity)
                    })
        
        return {
            "features": features,
            "similarity_pairs": similar_pairs,
            "feature_names": feature_names
        }
    
    def analyze_bidder_styles(
        self, 
        bidder_texts: Dict[str, Dict[str, str]]
    ) -> Dict[str, any]:
        """
        Analyze stylometric similarity across bidders.
        
        Args:
            bidder_texts: Nested dict {bidder_id: {doc_id: text}}
            
        Returns:
            Cross-bidder stylometric analysis
        """
        # Combine all documents per bidder
        bidder_combined_texts = {}
        for bidder_id, docs in bidder_texts.items():
            combined = " ".join(docs.values())
            bidder_combined_texts[bidder_id] = combined
        
        # Compare styles
        results = self.compare_writing_styles(bidder_combined_texts)
        
        return {
            "bidder_features": results.get("features", {}),
            "suspicious_style_matches": results.get("similarity_pairs", [])
        }
