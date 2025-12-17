"""
LangGraph Agent Node Functions

Each function represents a node in the agent workflow graph.
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..state import TenderAnalysisState, RiskSignal
from ..utils import (
    process_tender_documents,
    SemanticAnalyzer,
    StylometryAnalyzer,
    PriceAnalyzer,
    RelationshipAnalyzer
)
from config import OPENAI_MODEL
import logging

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)

# Initialize analyzers (lazy loading could be added)
semantic_analyzer = SemanticAnalyzer()
stylometry_analyzer = StylometryAnalyzer()
price_analyzer = PriceAnalyzer()
relationship_analyzer = RelationshipAnalyzer()


def extract_documents_node(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Node 1: Extract text from uploaded tender documents.
    """
    logger.info(f"[Node: Extract Documents] Processing {len(state['uploaded_documents'])} documents")
    
    try:
        extracted_text = process_tender_documents(state["uploaded_documents"])
        
        return {
            "extracted_text": extracted_text,
            "current_step": "document_extraction",
            "messages": [HumanMessage(content=f"Extracted text from {len(extracted_text)} documents")]
        }
    except Exception as e:
        logger.error(f"Error in document extraction: {e}")
        return {
            "error": str(e),
            "current_step": "document_extraction_failed"
        }


def analyze_prices_node(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Node 2: Analyze bid prices for statistical anomalies and suspicious patterns.
    """
    logger.info("[Node: Price Analysis] Analyzing bid prices")
    
    try:
        # Extract prices from bidders
        bidder_prices = {
            bidder.bidder_id: bidder.bid_amount 
            for bidder in state["bidders"]
        }
        
        # Run price analysis
        price_results = price_analyzer.analyze_price_patterns(bidder_prices)
        
        # Generate risk signals
        risk_signals = []
        if price_results["risk_score"] > 0:
            risk_signals.append(RiskSignal(
                signal_type="price_anomaly",
                severity=price_results["severity"],
                score=price_results["risk_score"],
                description=f"Price analysis detected {len(price_results['risk_indicators'])} risk indicators",
                evidence=price_results,
                affected_bidders=list(bidder_prices.keys())
            ))
        
        return {
            "price_analysis": price_results,
            "risk_signals": state.get("risk_signals", []) + risk_signals,
            "current_step": "price_analysis",
            "messages": [HumanMessage(content=f"Price analysis complete. Risk score: {price_results['risk_score']:.2f}")]
        }
    
    except Exception as e:
        logger.error(f"Error in price analysis: {e}")
        return {"error": str(e)}


def analyze_similarity_node(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Node 3: Analyze semantic similarity between bidder documents.
    """
    logger.info("[Node: Similarity Analysis] Analyzing document similarity")
    
    try:
        # Organize texts by bidder
        bidder_texts = {}
        for bidder in state["bidders"]:
            bidder_texts[bidder.bidder_id] = {}
            for doc_path in bidder.documents:
                if doc_path in state["extracted_text"]:
                    bidder_texts[bidder.bidder_id][doc_path] = state["extracted_text"][doc_path]
        
        # Run semantic analysis
        similarity_results = semantic_analyzer.analyze_bidder_documents(bidder_texts)
        
        # Generate risk signals
        risk_signals = []
        high_risk_pairs = similarity_results.get("high_risk_pairs", [])
        
        if high_risk_pairs:
            for pair in high_risk_pairs:
                risk_signals.append(RiskSignal(
                    signal_type="document_similarity",
                    severity="high" if pair["similarity"] > 0.9 else "medium",
                    score=pair["similarity"],
                    description=f"High similarity detected between {pair['bidder1']} and {pair['bidder2']}",
                    evidence=pair,
                    affected_bidders=[pair["bidder1"], pair["bidder2"]]
                ))
        
        return {
            "similarity_analysis": similarity_results,
            "risk_signals": state.get("risk_signals", []) + risk_signals,
            "current_step": "similarity_analysis",
            "messages": [HumanMessage(content=f"Found {len(high_risk_pairs)} high-similarity document pairs")]
        }
    
    except Exception as e:
        logger.error(f"Error in similarity analysis: {e}")
        return {"error": str(e)}


def analyze_stylometry_node(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Node 4: Analyze writing style across bidder documents.
    """
    logger.info("[Node: Stylometry Analysis] Analyzing writing styles")
    
    try:
        # Organize texts by bidder
        bidder_texts = {}
        for bidder in state["bidders"]:
            bidder_texts[bidder.bidder_id] = {}
            for doc_path in bidder.documents:
                if doc_path in state["extracted_text"]:
                    bidder_texts[bidder.bidder_id][doc_path] = state["extracted_text"][doc_path]
        
        # Run stylometry analysis
        stylometry_results = stylometry_analyzer.analyze_bidder_styles(bidder_texts)
        
        # Generate risk signals
        risk_signals = []
        suspicious_matches = stylometry_results.get("suspicious_style_matches", [])
        
        for match in suspicious_matches:
            risk_signals.append(RiskSignal(
                signal_type="stylometry",
                severity="high" if match["similarity"] > 0.85 else "medium",
                score=match["similarity"],
                description=f"Similar writing style detected between {match['doc1']} and {match['doc2']}",
                evidence=match,
                affected_bidders=[match["doc1"], match["doc2"]]
            ))
        
        return {
            "stylometry_analysis": stylometry_results,
            "risk_signals": state.get("risk_signals", []) + risk_signals,
            "current_step": "stylometry_analysis",
            "messages": [HumanMessage(content=f"Stylometry analysis found {len(suspicious_matches)} suspicious matches")]
        }
    
    except Exception as e:
        logger.error(f"Error in stylometry analysis: {e}")
        return {"error": str(e)}


def build_relationship_graph_node(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Node 5: Build and analyze relationship graph between bidders.
    """
    logger.info("[Node: Relationship Graph] Building bidder network")
    
    try:
        # Extract bidder IDs
        bidder_ids = [bidder.bidder_id for bidder in state["bidders"]]
        
        # Extract contact information
        contact_data = {}
        for bidder in state["bidders"]:
            if bidder.contact_info:
                contact_data[bidder.bidder_id] = bidder.contact_info
        
        # Build and analyze network
        graph_results = relationship_analyzer.analyze_bidder_network(
            bidders=bidder_ids,
            similarity_data=state.get("similarity_analysis"),
            contact_data=contact_data
        )
        
        # Generate risk signals
        risk_signals = []
        high_risk_groups = graph_results.get("high_risk_groups", [])
        
        for group in high_risk_groups:
            risk_signals.append(RiskSignal(
                signal_type="relationship_network",
                severity="high" if group["size"] >= 4 else "medium",
                score=min(group["size"] / len(bidder_ids), 1.0),
                description=f"Detected {group['type']} of {group['size']} connected bidders",
                evidence=group,
                affected_bidders=group["bidders"]
            ))
        
        return {
            "relationship_graph": graph_results,
            "risk_signals": state.get("risk_signals", []) + risk_signals,
            "current_step": "relationship_graph",
            "messages": [HumanMessage(content=f"Network analysis complete. Found {len(high_risk_groups)} high-risk groups")]
        }
    
    except Exception as e:
        logger.error(f"Error in relationship graph: {e}")
        return {"error": str(e)}


def generate_report_node(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Node 6: Use LLM to generate explainable summary of findings.
    """
    logger.info("[Node: Generate Report] Generating AI summary")
    
    try:
        # Prepare context for LLM
        risk_summary = []
        for signal in state.get("risk_signals", []):
            risk_summary.append(
                f"- {signal.signal_type} ({signal.severity}): {signal.description} [Score: {signal.score:.2f}]"
            )
        
        risk_text = "\n".join(risk_summary) if risk_summary else "No significant risks detected."
        
        # Create prompt
        system_prompt = """You are an expert procurement fraud analyst. 
        Analyze the risk signals and provide a clear, actionable summary for procurement officers.
        Focus on explainability and evidence-based reasoning.
        Avoid making definitive accusations - present findings as risk indicators requiring human review."""
        
        user_prompt = f"""
Tender ID: {state['tender_id']}
Description: {state['tender_description']}
Number of Bidders: {len(state['bidders'])}

Risk Signals Detected:
{risk_text}

Provide:
1. Executive Summary (2-3 sentences)
2. Key Risk Indicators (prioritized list)
3. Recommended Actions
4. Confidence Level
"""
        
        # Generate report
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        report_text = response.content
        
        # Calculate overall risk score
        risk_scores = [signal.score for signal in state.get("risk_signals", [])]
        overall_risk = max(risk_scores) if risk_scores else 0.0
        
        return {
            "overall_risk_score": overall_risk,
            "current_step": "report_generation",
            "analysis_complete": True,
            "messages": state.get("messages", []) + [
                HumanMessage(content="AI Report Generated"),
                response
            ]
        }
    
    except Exception as e:
        logger.error(f"Error in report generation: {e}")
        return {"error": str(e)}


def should_continue(state: TenderAnalysisState) -> str:
    """
    Conditional edge function to determine next step or completion.
    """
    if state.get("error"):
        return "error"
    
    if state.get("analysis_complete"):
        return "complete"
    
    return "continue"
