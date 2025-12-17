"""
Price Analysis and Statistical Anomaly Detection
"""
import numpy as np
from scipy import stats
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class PriceAnalyzer:
    """Analyzes bid prices for anomalies and suspicious patterns"""
    
    def __init__(self, outlier_threshold: float = 2.0):
        """
        Initialize price analyzer.
        
        Args:
            outlier_threshold: Number of standard deviations for outlier detection
        """
        self.outlier_threshold = outlier_threshold
    
    def detect_outliers(self, prices: List[float]) -> Dict[str, any]:
        """
        Detect price outliers using statistical methods.
        
        Args:
            prices: List of bid prices
            
        Returns:
            Outlier analysis results
        """
        if len(prices) < 3:
            return {"error": "Need at least 3 bids for statistical analysis"}
        
        prices_array = np.array(prices)
        mean_price = np.mean(prices_array)
        std_price = np.std(prices_array)
        median_price = np.median(prices_array)
        
        # Z-score outliers
        z_scores = np.abs(stats.zscore(prices_array))
        outliers = z_scores > self.outlier_threshold
        
        # IQR method
        q1 = np.percentile(prices_array, 25)
        q3 = np.percentile(prices_array, 75)
        iqr = q3 - q1
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        
        iqr_outliers = (prices_array < lower_bound) | (prices_array > upper_bound)
        
        return {
            "mean": float(mean_price),
            "median": float(median_price),
            "std_dev": float(std_price),
            "coefficient_variation": float(std_price / mean_price) if mean_price > 0 else 0,
            "z_score_outliers": outliers.tolist(),
            "iqr_outliers": iqr_outliers.tolist(),
            "price_range": {
                "min": float(np.min(prices_array)),
                "max": float(np.max(prices_array)),
                "range": float(np.max(prices_array) - np.min(prices_array))
            }
        }
    
    def detect_cover_bidding(
        self, 
        bidder_prices: Dict[str, float],
        margin_threshold: float = 0.05
    ) -> Dict[str, any]:
        """
        Detect potential cover bidding (artificially high bids).
        
        Args:
            bidder_prices: Dictionary mapping bidder IDs to bid amounts
            margin_threshold: Threshold for detecting clustered pricing
            
        Returns:
            Cover bidding analysis results
        """
        prices = list(bidder_prices.values())
        bidder_ids = list(bidder_prices.keys())
        
        if len(prices) < 2:
            return {"suspicious_patterns": []}
        
        # Sort prices
        sorted_indices = np.argsort(prices)
        sorted_prices = [prices[i] for i in sorted_indices]
        sorted_bidders = [bidder_ids[i] for i in sorted_indices]
        
        # Look for suspiciously high bids (far from winning bid)
        lowest_bid = sorted_prices[0]
        suspicious_bids = []
        
        for i in range(1, len(sorted_prices)):
            price_gap = (sorted_prices[i] - lowest_bid) / lowest_bid
            
            # If a bid is significantly higher but close to another bid, it's suspicious
            if price_gap > 0.15:  # More than 15% higher than lowest
                # Check if it's close to another bid (potential coordination)
                for j in range(i + 1, len(sorted_prices)):
                    relative_diff = abs(sorted_prices[j] - sorted_prices[i]) / sorted_prices[i]
                    
                    if relative_diff < margin_threshold:
                        suspicious_bids.append({
                            "bidder1": sorted_bidders[i],
                            "bidder2": sorted_bidders[j],
                            "price1": sorted_prices[i],
                            "price2": sorted_prices[j],
                            "difference_pct": relative_diff * 100,
                            "pattern": "clustered_high_bids"
                        })
        
        return {
            "lowest_bid": lowest_bid,
            "highest_bid": sorted_prices[-1],
            "suspicious_patterns": suspicious_bids
        }
    
    def analyze_price_patterns(
        self, 
        bidder_prices: Dict[str, float]
    ) -> Dict[str, any]:
        """
        Comprehensive price pattern analysis.
        
        Args:
            bidder_prices: Dictionary mapping bidder IDs to bid amounts
            
        Returns:
            Complete price analysis
        """
        prices = list(bidder_prices.values())
        
        # Run all analyses
        outlier_results = self.detect_outliers(prices)
        cover_bid_results = self.detect_cover_bidding(bidder_prices)
        
        # Check for round number clustering (sign of price coordination)
        round_numbers = sum(1 for p in prices if p % 1000 == 0 or p % 500 == 0)
        round_number_ratio = round_numbers / len(prices) if prices else 0
        
        # Calculate risk score
        risk_indicators = []
        risk_score = 0.0
        
        if outlier_results.get("coefficient_variation", 0) < 0.1:
            risk_indicators.append("Low price variation (potential coordination)")
            risk_score += 0.3
        
        if cover_bid_results.get("suspicious_patterns"):
            risk_indicators.append("Clustered high bids detected")
            risk_score += 0.4
        
        if round_number_ratio > 0.5:
            risk_indicators.append("High proportion of round number bids")
            risk_score += 0.2
        
        risk_score = min(risk_score, 1.0)
        
        return {
            "outlier_analysis": outlier_results,
            "cover_bidding_analysis": cover_bid_results,
            "round_number_ratio": round_number_ratio,
            "risk_score": risk_score,
            "risk_indicators": risk_indicators,
            "severity": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low"
        }
