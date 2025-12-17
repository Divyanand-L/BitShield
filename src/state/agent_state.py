"""
LangGraph State Definition for Procurement Risk Agent
"""
from typing import List, Dict, Any, Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class BidderInfo(BaseModel):
    """Information about a single bidder"""
    bidder_id: str
    name: str
    bid_amount: float
    documents: List[str] = Field(default_factory=list)
    contact_info: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RiskSignal(BaseModel):
    """Individual risk signal detected by the system"""
    signal_type: str
    severity: str  # "high", "medium", "low"
    score: float
    description: str
    evidence: Dict[str, Any]
    affected_bidders: List[str] = Field(default_factory=list)


class TenderAnalysisState(TypedDict):
    """
    State object that flows through the LangGraph agent.
    This maintains all information about the tender analysis process.
    """
    # Input data
    tender_id: str
    tender_description: str
    bidders: List[BidderInfo]
    uploaded_documents: List[str]
    
    # Extracted data
    extracted_text: Dict[str, str]  # document_path -> text
    
    # Analysis results
    price_analysis: Optional[Dict[str, Any]]
    similarity_analysis: Optional[Dict[str, Any]]
    stylometry_analysis: Optional[Dict[str, Any]]
    relationship_graph: Optional[Dict[str, Any]]
    
    # Risk signals
    risk_signals: List[RiskSignal]
    overall_risk_score: float
    
    # Agent messages and reasoning
    messages: Annotated[List, add_messages]
    
    # Workflow control
    current_step: str
    analysis_complete: bool
    error: Optional[str]
