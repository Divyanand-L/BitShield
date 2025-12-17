"""
Relationship Graph Analysis using NetworkX
"""
import networkx as nx
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)


class RelationshipAnalyzer:
    """Analyzes relationships between bidders using graph analysis"""
    
    def __init__(self):
        """Initialize the relationship analyzer"""
        self.graph = nx.Graph()
    
    def add_bidder(self, bidder_id: str, metadata: Dict = None):
        """
        Add a bidder node to the graph.
        
        Args:
            bidder_id: Unique bidder identifier
            metadata: Additional bidder information
        """
        self.graph.add_node(bidder_id, **(metadata or {}))
    
    def add_relationship(
        self, 
        bidder1: str, 
        bidder2: str, 
        relationship_type: str,
        weight: float = 1.0,
        evidence: Dict = None
    ):
        """
        Add a relationship edge between two bidders.
        
        Args:
            bidder1: First bidder ID
            bidder2: Second bidder ID
            relationship_type: Type of relationship (e.g., "shared_address", "document_similarity")
            weight: Strength of the relationship (0-1)
            evidence: Supporting evidence for the relationship
        """
        if self.graph.has_edge(bidder1, bidder2):
            # Update existing edge
            edge_data = self.graph[bidder1][bidder2]
            edge_data['weight'] = max(edge_data.get('weight', 0), weight)
            edge_data['relationships'] = edge_data.get('relationships', [])
            edge_data['relationships'].append(relationship_type)
        else:
            # Create new edge
            self.graph.add_edge(
                bidder1, 
                bidder2, 
                weight=weight,
                relationships=[relationship_type],
                evidence=evidence or {}
            )
    
    def detect_communities(self) -> List[Set[str]]:
        """
        Detect communities (clusters) of connected bidders.
        
        Returns:
            List of bidder communities
        """
        if len(self.graph.nodes) < 2:
            return []
        
        # Use Louvain community detection
        from networkx.algorithms import community
        
        communities = community.greedy_modularity_communities(self.graph)
        return [set(c) for c in communities if len(c) > 1]
    
    def find_suspicious_cliques(self, min_size: int = 3) -> List[List[str]]:
        """
        Find cliques (fully connected groups) of bidders.
        
        Args:
            min_size: Minimum clique size to consider suspicious
            
        Returns:
            List of suspicious cliques
        """
        cliques = list(nx.find_cliques(self.graph))
        suspicious = [clique for clique in cliques if len(clique) >= min_size]
        
        logger.info("Found %d cliques of size >= %d", len(suspicious), min_size)
        return suspicious
    
    def calculate_centrality_scores(self) -> Dict[str, float]:
        """
        Calculate centrality scores for each bidder.
        High centrality indicates bidders with many connections.
        
        Returns:
            Dictionary mapping bidder IDs to centrality scores
        """
        if len(self.graph.nodes) == 0:
            return {}
        
        # Degree centrality (number of connections)
        centrality = nx.degree_centrality(self.graph)
        return centrality
    
    def analyze_bidder_network(
        self, 
        bidders: List[str],
        similarity_data: Dict = None,
        contact_data: Dict = None
    ) -> Dict[str, any]:
        """
        Build and analyze the complete bidder relationship network.
        
        Args:
            bidders: List of bidder IDs
            similarity_data: Document similarity information
            contact_data: Contact information for detecting shared addresses/phones
            
        Returns:
            Network analysis results
        """
        # Clear previous graph
        self.graph.clear()
        
        # Add all bidders
        for bidder in bidders:
            self.add_bidder(bidder)
        
        # Add relationships based on similarity
        if similarity_data:
            for pair in similarity_data.get("cross_bidder_similarities", []):
                self.add_relationship(
                    pair["bidder1"],
                    pair["bidder2"],
                    "document_similarity",
                    weight=pair["similarity"],
                    evidence={"similarity_score": pair["similarity"]}
                )
        
        # Add relationships based on shared contact info
        if contact_data:
            # Group by email, phone, address
            for field in ["email", "phone", "address"]:
                field_groups = {}
                for bidder_id, info in contact_data.items():
                    value = info.get(field)
                    if value:
                        field_groups.setdefault(value, []).append(bidder_id)
                
                # Create edges for shared values
                for value, bidder_list in field_groups.items():
                    if len(bidder_list) > 1:
                        for i in range(len(bidder_list)):
                            for j in range(i + 1, len(bidder_list)):
                                self.add_relationship(
                                    bidder_list[i],
                                    bidder_list[j],
                                    f"shared_{field}",
                                    weight=0.8,
                                    evidence={field: value}
                                )
        
        # Analyze the network
        communities = self.detect_communities()
        cliques = self.find_suspicious_cliques()
        centrality = self.calculate_centrality_scores()
        
        # Calculate overall network metrics
        num_edges = self.graph.number_of_edges()
        num_nodes = self.graph.number_of_nodes()
        density = nx.density(self.graph) if num_nodes > 1 else 0
        
        # Identify high-risk groups
        high_risk_groups = []
        for community in communities:
            if len(community) >= 3:
                high_risk_groups.append({
                    "bidders": list(community),
                    "size": len(community),
                    "type": "community"
                })
        
        for clique in cliques:
            high_risk_groups.append({
                "bidders": clique,
                "size": len(clique),
                "type": "clique"
            })
        
        return {
            "num_bidders": num_nodes,
            "num_relationships": num_edges,
            "network_density": density,
            "communities": [list(c) for c in communities],
            "suspicious_cliques": cliques,
            "centrality_scores": centrality,
            "high_risk_groups": high_risk_groups,
            "graph_data": nx.node_link_data(self.graph)  # For visualization
        }
    
    def get_graph_for_visualization(self) -> Dict:
        """
        Export graph data in a format suitable for visualization.
        
        Returns:
            Graph data in node-link format
        """
        return nx.node_link_data(self.graph)
