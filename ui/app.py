"""
Streamlit UI for BitShield Procurement Agent
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.state import BidderInfo
from src.agents import run_analysis
from config import UPLOADS_DIR
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="BitShield - Procurement Risk Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .risk-high { background-color: #ff4444; color: white; padding: 10px; border-radius: 5px; }
    .risk-medium { background-color: #ffaa00; color: white; padding: 10px; border-radius: 5px; }
    .risk-low { background-color: #44ff44; color: white; padding: 10px; border-radius: 5px; }
    .metric-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🛡️ BitShield - Transparent Procurement Agent")
    st.markdown("### AI-powered fraud detection for government tenders")
    st.markdown("---")
    
    # Initialize session state
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    
    # Sidebar for input
    with st.sidebar:
        st.header("📋 Tender Information")
        
        tender_id = st.text_input("Tender ID", value="T-2025-001", help="Unique tender identifier")
        tender_description = st.text_area(
            "Tender Description",
            value="Road construction project for Highway 45",
            help="Brief description of the tender"
        )
        
        st.markdown("---")
        st.header("👥 Bidder Information")
        
        num_bidders = st.number_input("Number of Bidders", min_value=2, max_value=10, value=3)
        
        bidders_data = []
        for i in range(int(num_bidders)):
            with st.expander(f"Bidder {i+1}"):
                bidder_name = st.text_input(f"Name", value=f"Company {chr(65+i)}", key=f"name_{i}")
                bid_amount = st.number_input(
                    f"Bid Amount ($)", 
                    min_value=0.0, 
                    value=100000.0 + (i * 5000),
                    step=1000.0,
                    key=f"amount_{i}"
                )
                
                # Contact information
                email = st.text_input(f"Email", value=f"contact{i+1}@company{chr(65+i).lower()}.com", key=f"email_{i}")
                phone = st.text_input(f"Phone", value=f"+1-555-{1000+i}", key=f"phone_{i}")
                
                # Document upload
                uploaded_files = st.file_uploader(
                    f"Upload Documents",
                    type=['pdf'],
                    accept_multiple_files=True,
                    key=f"docs_{i}"
                )
                
                # Save uploaded files
                doc_paths = []
                if uploaded_files:
                    for file in uploaded_files:
                        save_path = UPLOADS_DIR / f"bidder_{i}_{file.name}"
                        with open(save_path, "wb") as f:
                            f.write(file.getbuffer())
                        doc_paths.append(str(save_path))
                
                bidders_data.append({
                    "bidder_id": f"B{i+1}",
                    "name": bidder_name,
                    "bid_amount": bid_amount,
                    "documents": doc_paths,
                    "contact_info": {
                        "email": email,
                        "phone": phone
                    }
                })
        
        st.markdown("---")
        analyze_button = st.button("🔍 Analyze Tender", type="primary", use_container_width=True)
    
    # Main content area
    if analyze_button:
        if not any(b["documents"] for b in bidders_data):
            st.warning("⚠️ Please upload at least one document to analyze.")
        else:
            with st.spinner("🔄 Running comprehensive analysis..."):
                try:
                    # Convert to BidderInfo objects
                    bidders = [
                        BidderInfo(
                            bidder_id=b["bidder_id"],
                            name=b["name"],
                            bid_amount=b["bid_amount"],
                            documents=b["documents"],
                            contact_info=b["contact_info"]
                        )
                        for b in bidders_data
                    ]
                    
                    # Collect all document paths
                    all_docs = []
                    for b in bidders:
                        all_docs.extend(b.documents)
                    
                    # Run analysis
                    result = run_analysis(
                        tender_id=tender_id,
                        tender_description=tender_description,
                        bidders=bidders,
                        uploaded_documents=all_docs
                    )
                    
                    st.session_state.analysis_result = result
                    st.success("✅ Analysis complete!")
                
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    logger.error(f"Analysis error: {e}", exc_info=True)
    
    # Display results
    if st.session_state.analysis_result:
        display_results(st.session_state.analysis_result)


def display_results(result: dict):
    """Display analysis results in a structured format"""
    
    st.markdown("## 📊 Analysis Results")
    
    # Overall risk score
    risk_score = result.get("overall_risk_score", 0)
    risk_level = "HIGH" if risk_score > 0.7 else "MEDIUM" if risk_score > 0.4 else "LOW"
    risk_color = "red" if risk_score > 0.7 else "orange" if risk_score > 0.4 else "green"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Risk Score", f"{risk_score:.2f}", delta=None)
    
    with col2:
        st.markdown(f"### Risk Level: :{risk_color}[{risk_level}]")
    
    with col3:
        num_signals = len(result.get("risk_signals", []))
        st.metric("Risk Signals Detected", num_signals)
    
    st.markdown("---")
    
    # Tabs for different analysis sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Executive Summary",
        "💰 Price Analysis",
        "📄 Document Similarity",
        "✍️ Stylometry",
        "🕸️ Relationship Network",
        "⚠️ Risk Signals"
    ])
    
    with tab1:
        display_executive_summary(result)
    
    with tab2:
        display_price_analysis(result.get("price_analysis"))
    
    with tab3:
        display_similarity_analysis(result.get("similarity_analysis"))
    
    with tab4:
        display_stylometry_analysis(result.get("stylometry_analysis"))
    
    with tab5:
        display_relationship_graph(result.get("relationship_graph"))
    
    with tab6:
        display_risk_signals(result.get("risk_signals", []))


def display_executive_summary(result: dict):
    """Display AI-generated executive summary"""
    st.subheader("AI-Generated Report")
    
    messages = result.get("messages", [])
    
    # Find AI response
    for msg in reversed(messages):
        if hasattr(msg, 'content') and len(msg.content) > 100:
            st.markdown(msg.content)
            break
    else:
        st.info("No executive summary generated.")


def display_price_analysis(price_data: dict):
    """Display price analysis results"""
    if not price_data:
        st.info("No price analysis available.")
        return
    
    st.subheader("Statistical Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    outlier_analysis = price_data.get("outlier_analysis", {})
    
    with col1:
        st.metric("Mean Bid", f"${outlier_analysis.get('mean', 0):,.2f}")
        st.metric("Median Bid", f"${outlier_analysis.get('median', 0):,.2f}")
    
    with col2:
        st.metric("Std Deviation", f"${outlier_analysis.get('std_dev', 0):,.2f}")
        st.metric("Coefficient of Variation", f"{outlier_analysis.get('coefficient_variation', 0):.2%}")
    
    with col3:
        price_range = outlier_analysis.get('price_range', {})
        st.metric("Min Bid", f"${price_range.get('min', 0):,.2f}")
        st.metric("Max Bid", f"${price_range.get('max', 0):,.2f}")
    
    # Risk indicators
    if price_data.get("risk_indicators"):
        st.markdown("### ⚠️ Risk Indicators")
        for indicator in price_data["risk_indicators"]:
            st.warning(indicator)
    
    # Cover bidding patterns
    cover_bidding = price_data.get("cover_bidding_analysis", {})
    if cover_bidding.get("suspicious_patterns"):
        st.markdown("### 🚨 Suspicious Bidding Patterns")
        for pattern in cover_bidding["suspicious_patterns"]:
            st.error(
                f"**{pattern['bidder1']}** and **{pattern['bidder2']}**: "
                f"${pattern['price1']:,.2f} vs ${pattern['price2']:,.2f} "
                f"(difference: {pattern['difference_pct']:.2f}%)"
            )


def display_similarity_analysis(sim_data: dict):
    """Display document similarity analysis"""
    if not sim_data:
        st.info("No similarity analysis available.")
        return
    
    st.subheader("Cross-Bidder Document Similarity")
    
    high_risk = sim_data.get("high_risk_pairs", [])
    
    if high_risk:
        st.error(f"Found {len(high_risk)} high-risk similarity matches")
        
        for pair in high_risk:
            with st.expander(f"⚠️ {pair['bidder1']} ↔️ {pair['bidder2']} ({pair['similarity']:.1%} similar)"):
                st.json(pair)
    else:
        st.success("No high-risk document similarities detected.")
    
    # All similarities
    all_sims = sim_data.get("cross_bidder_similarities", [])
    if all_sims:
        st.markdown("### All Cross-Bidder Similarities")
        df = pd.DataFrame(all_sims)
        st.dataframe(df, use_container_width=True)


def display_stylometry_analysis(style_data: dict):
    """Display stylometry analysis"""
    if not style_data:
        st.info("No stylometry analysis available.")
        return
    
    st.subheader("Writing Style Analysis")
    
    suspicious = style_data.get("suspicious_style_matches", [])
    
    if suspicious:
        st.warning(f"Found {len(suspicious)} suspicious style matches")
        
        for match in suspicious:
            st.error(
                f"**{match['doc1']}** and **{match['doc2']}** have {match['similarity']:.1%} style similarity"
            )
    else:
        st.success("No suspicious writing style patterns detected.")
    
    # Feature comparison
    features = style_data.get("bidder_features", {})
    if features:
        st.markdown("### Stylometric Features by Bidder")
        df = pd.DataFrame(features).T
        st.dataframe(df.round(3), use_container_width=True)


def display_relationship_graph(graph_data: dict):
    """Display relationship network visualization"""
    if not graph_data:
        st.info("No relationship graph available.")
        return
    
    st.subheader("Bidder Relationship Network")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Bidders", graph_data.get("num_bidders", 0))
    
    with col2:
        st.metric("Relationships Detected", graph_data.get("num_relationships", 0))
    
    with col3:
        density = graph_data.get("network_density", 0)
        st.metric("Network Density", f"{density:.2%}")
    
    # High-risk groups
    high_risk_groups = graph_data.get("high_risk_groups", [])
    if high_risk_groups:
        st.markdown("### 🚨 High-Risk Groups")
        for group in high_risk_groups:
            st.error(
                f"**{group['type'].title()}** of {group['size']} bidders: "
                f"{', '.join(group['bidders'])}"
            )
    
    # Network visualization (simplified)
    st.markdown("### Network Graph")
    
    # Use graph data to create a simple visualization
    try:
        import networkx as nx
        from networkx.readwrite import json_graph
        
        graph_json = graph_data.get("graph_data", {})
        if graph_json:
            G = json_graph.node_link_graph(graph_json)
            
            # Create plotly figure
            pos = nx.spring_layout(G)
            
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                mode='lines')
            
            node_x = []
            node_y = []
            node_text = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                text=node_text,
                textposition="top center",
                hoverinfo='text',
                marker=dict(
                    size=20,
                    color='lightblue',
                    line=dict(width=2, color='darkblue')))
            
            fig = go.Figure(data=[edge_trace, node_trace],
                          layout=go.Layout(
                              showlegend=False,
                              hovermode='closest',
                              margin=dict(b=0, l=0, r=0, t=0),
                              xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                          )
            
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not render network graph: {e}")


def display_risk_signals(risk_signals: list):
    """Display all risk signals"""
    if not risk_signals:
        st.success("✅ No risk signals detected. Tender appears clean.")
        return
    
    st.subheader(f"Total Risk Signals: {len(risk_signals)}")
    
    # Group by severity
    high = [s for s in risk_signals if s.severity == "high"]
    medium = [s for s in risk_signals if s.severity == "medium"]
    low = [s for s in risk_signals if s.severity == "low"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("High Severity", len(high), delta=None, delta_color="inverse")
    with col2:
        st.metric("Medium Severity", len(medium))
    with col3:
        st.metric("Low Severity", len(low))
    
    # Display each signal
    for signal in risk_signals:
        severity_class = f"risk-{signal.severity}"
        
        with st.expander(f"{'🔴' if signal.severity == 'high' else '🟡' if signal.severity == 'medium' else '🟢'} {signal.signal_type.upper()} - {signal.description}"):
            st.markdown(f"**Severity:** {signal.severity.upper()}")
            st.markdown(f"**Score:** {signal.score:.2f}")
            st.markdown(f"**Affected Bidders:** {', '.join(signal.affected_bidders)}")
            st.markdown("**Evidence:**")
            st.json(signal.evidence)


if __name__ == "__main__":
    main()
