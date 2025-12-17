"""
LangGraph Workflow Definition

This file defines the state machine workflow using LangGraph.
"""
from langgraph.graph import StateGraph, END
from ..state import TenderAnalysisState
from .nodes import (
    extract_documents_node,
    analyze_prices_node,
    analyze_similarity_node,
    analyze_stylometry_node,
    build_relationship_graph_node,
    generate_report_node,
    should_continue
)
import logging

logger = logging.getLogger(__name__)


def create_procurement_agent() -> StateGraph:
    """
    Create and configure the LangGraph workflow for procurement analysis.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize the graph with our state schema
    workflow = StateGraph(TenderAnalysisState)
    
    # Add nodes to the graph
    workflow.add_node("extract_documents", extract_documents_node)
    workflow.add_node("analyze_prices", analyze_prices_node)
    workflow.add_node("analyze_similarity", analyze_similarity_node)
    workflow.add_node("analyze_stylometry", analyze_stylometry_node)
    workflow.add_node("build_relationship_graph", build_relationship_graph_node)
    workflow.add_node("generate_report", generate_report_node)
    
    # Define the workflow edges (execution order)
    workflow.set_entry_point("extract_documents")
    
    # Sequential analysis flow
    workflow.add_edge("extract_documents", "analyze_prices")
    workflow.add_edge("analyze_prices", "analyze_similarity")
    workflow.add_edge("analyze_similarity", "analyze_stylometry")
    workflow.add_edge("analyze_stylometry", "build_relationship_graph")
    workflow.add_edge("build_relationship_graph", "generate_report")
    
    # Conditional edge from report generation
    workflow.add_conditional_edges(
        "generate_report",
        should_continue,
        {
            "complete": END,
            "error": END,
            "continue": END  # Fallback
        }
    )
    
    # Compile the graph
    app = workflow.compile()
    
    logger.info("Procurement agent workflow compiled successfully")
    return app


# Create the global agent instance
procurement_agent = create_procurement_agent()


def run_analysis(
    tender_id: str,
    tender_description: str,
    bidders: list,
    uploaded_documents: list
) -> dict:
    """
    Convenience function to run the complete analysis.
    
    Args:
        tender_id: Unique tender identifier
        tender_description: Description of the tender
        bidders: List of BidderInfo objects
        uploaded_documents: List of document paths
        
    Returns:
        Final state after analysis
    """
    # Initialize state
    initial_state = {
        "tender_id": tender_id,
        "tender_description": tender_description,
        "bidders": bidders,
        "uploaded_documents": uploaded_documents,
        "extracted_text": {},
        "price_analysis": None,
        "similarity_analysis": None,
        "stylometry_analysis": None,
        "relationship_graph": None,
        "risk_signals": [],
        "overall_risk_score": 0.0,
        "messages": [],
        "current_step": "initialized",
        "analysis_complete": False,
        "error": None
    }
    
    # Run the workflow
    logger.info(f"Starting analysis for tender: {tender_id}")
    final_state = procurement_agent.invoke(initial_state)
    
    logger.info(f"Analysis complete. Overall risk score: {final_state.get('overall_risk_score', 0):.2f}")
    return final_state
