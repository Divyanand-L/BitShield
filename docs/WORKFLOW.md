# 🔄 BitShield Workflow - Detailed Explanation

This document provides an in-depth explanation of how the BitShield Transparent Procurement Agent processes tender data to detect fraud risks.

---

## 🎯 System Overview

BitShield is a **stateful AI agent** that orchestrates multiple analysis modules through a LangGraph workflow. The system maintains state throughout the analysis, allowing each node to build upon previous findings and enabling complex, multi-step reasoning.

### Key Principles

1. **Evidence-Based**: Every risk signal is backed by concrete evidence
2. **Explainable**: AI decisions are transparent and interpretable
3. **Human-in-the-Loop**: System assists, not replaces, procurement officers
4. **Privacy-Preserving**: All processing happens locally
5. **Configurable**: Thresholds and parameters can be tuned

---

## 🏗️ LangGraph State Machine

### State Schema

The system maintains a comprehensive state object that flows through all nodes:

```python
TenderAnalysisState:
    # Input Data
    - tender_id: str
    - tender_description: str
    - bidders: List[BidderInfo]
    - uploaded_documents: List[str]
    
    # Extracted Data
    - extracted_text: Dict[str, str]
    
    # Analysis Results
    - price_analysis: Dict
    - similarity_analysis: Dict
    - stylometry_analysis: Dict
    - relationship_graph: Dict
    
    # Risk Output
    - risk_signals: List[RiskSignal]
    - overall_risk_score: float
    
    # Agent Communication
    - messages: List[Message]
    
    # Control Flow
    - current_step: str
    - analysis_complete: bool
    - error: Optional[str]
```

### State Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     INITIAL STATE                           │
│  tender_id, bidders, documents → empty analysis fields      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              NODE 1: Extract Documents                      │
│  State Update: extracted_text = {path: text, ...}           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              NODE 2: Analyze Prices                         │
│  State Update: price_analysis = {...}                       │
│                risk_signals += [price_signal]               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              NODE 3: Analyze Similarity                     │
│  State Update: similarity_analysis = {...}                  │
│                risk_signals += [similarity_signals]         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              NODE 4: Analyze Stylometry                     │
│  State Update: stylometry_analysis = {...}                  │
│                risk_signals += [style_signals]              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              NODE 5: Build Relationship Graph               │
│  State Update: relationship_graph = {...}                   │
│                risk_signals += [network_signals]            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              NODE 6: Generate AI Report                     │
│  State Update: overall_risk_score = max(signal_scores)      │
│                analysis_complete = True                     │
│                messages += [AI_report]                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
                          [END]
```

---

## 🔍 Node-by-Node Analysis

### Node 1: Document Extraction

**Purpose**: Convert unstructured PDF documents into machine-readable text.

**Technology**: pdfplumber

**Process**:
1. Iterate through all uploaded document paths
2. For each PDF:
   - Open file using pdfplumber
   - Extract text from each page
   - Combine pages into single text block
   - Handle tables separately (optional)
3. Store in state: `extracted_text[doc_path] = text`

**Error Handling**:
- Corrupted PDFs → Skip and log warning
- Scanned images → Return empty text (OCR could be added)
- Large files → Stream processing to manage memory

**Output Example**:
```python
{
    "/uploads/bidder_1_proposal.pdf": "Our company proposes...",
    "/uploads/bidder_2_proposal.pdf": "We submit this bid...",
    ...
}
```

---

### Node 2: Price Analysis

**Purpose**: Detect statistical anomalies and suspicious pricing patterns.

**Technology**: Pandas, NumPy, SciPy

**Statistical Methods**:

1. **Outlier Detection**
   - **Z-Score Method**: Identifies bids > 2 standard deviations from mean
   - **IQR Method**: Flags bids outside [Q1-1.5×IQR, Q3+1.5×IQR]
   
2. **Cover Bidding Detection**
   - Identify lowest bid (likely winner)
   - Find bids that are:
     - Significantly higher (>15% above lowest)
     - Clustered together (within 5% of each other)
   - Pattern suggests coordinated "losing bids"

3. **Price Coordination Indicators**
   - **Low Coefficient of Variation**: CV < 0.1 suggests artificial uniformity
   - **Round Number Clustering**: > 50% bids ending in $1000 or $5000
   - **Suspiciously Even Spacing**: Equal gaps between bids

**Risk Score Calculation**:
```python
risk_score = 0.0
if CV < 0.1:
    risk_score += 0.3
if cover_bidding_detected:
    risk_score += 0.4
if round_number_ratio > 0.5:
    risk_score += 0.2
risk_score = min(risk_score, 1.0)
```

**Example Output**:
```json
{
  "outlier_analysis": {
    "mean": 105000,
    "median": 103000,
    "std_dev": 8500,
    "coefficient_variation": 0.081,
    "z_score_outliers": [false, false, true]
  },
  "cover_bidding_analysis": {
    "suspicious_patterns": [
      {
        "bidder1": "B2",
        "bidder2": "B3",
        "price1": 120000,
        "price2": 121000,
        "difference_pct": 0.83,
        "pattern": "clustered_high_bids"
      }
    ]
  },
  "risk_score": 0.7,
  "severity": "high"
}
```

---

### Node 3: Semantic Similarity Analysis

**Purpose**: Detect document content similarity that suggests copy-paste or shared authorship.

**Technology**: Sentence-BERT (all-MiniLM-L6-v2)

**Process**:

1. **Embedding Generation**
   ```python
   text_embeddings = sbert_model.encode(documents)
   # Each document → 384-dimensional vector
   ```

2. **Similarity Computation**
   ```python
   similarity_matrix = cosine_similarity(embeddings)
   # Range: 0.0 (completely different) to 1.0 (identical)
   ```

3. **Cross-Bidder Filtering**
   - Only flag similarities between DIFFERENT bidders
   - Same bidder having similar docs is normal (e.g., cover letter + proposal)

4. **Threshold-Based Detection**
   - Similarity > 0.9: **High risk** (near-identical content)
   - Similarity 0.7-0.9: **Medium risk** (substantial overlap)
   - Similarity < 0.7: Normal competitive variance

**Why This Matters**:
- Legitimate competitors write unique proposals
- High similarity suggests:
  - One bidder wrote both documents
  - Documents were shared between bidders
  - Copy-paste from common template (requires investigation)

**Example Output**:
```json
{
  "cross_bidder_similarities": [
    {
      "bidder1": "B1",
      "bidder2": "B3",
      "document1": "B1:proposal.pdf",
      "document2": "B3:proposal.pdf",
      "similarity": 0.94
    }
  ],
  "high_risk_pairs": [...]
}
```

---

### Node 4: Stylometry Analysis

**Purpose**: Detect authorship similarities through writing style analysis.

**Technology**: spaCy (NLP), scikit-learn (feature comparison)

**Stylometric Features Extracted**:

1. **Lexical Features**
   - Average word length
   - Lexical diversity (unique words / total words)
   - Stopword frequency

2. **Syntactic Features**
   - Average sentence length
   - Punctuation frequency
   - Noun/verb/adjective ratios

3. **Style Fingerprint**
   - Each document → feature vector
   - Compare vectors across bidders

**Feature Extraction Example**:
```python
doc = spacy_nlp(text)

features = {
    "avg_word_length": 5.2,
    "avg_sentence_length": 18.5,
    "lexical_diversity": 0.65,
    "punct_frequency": 0.12,
    "noun_frequency": 0.25,
    "verb_frequency": 0.18
}
```

**Similarity Detection**:
- Compute cosine similarity between feature vectors
- High similarity (> 0.85) suggests same author

**Real-World Insight**:
- Everyone has unique writing "fingerprint"
- Professional documents have consistent style
- High cross-bidder stylometric match is suspicious

**Example Output**:
```json
{
  "bidder_features": {
    "B1": {
      "avg_word_length": 5.3,
      "lexical_diversity": 0.68,
      ...
    },
    "B2": {...}
  },
  "suspicious_style_matches": [
    {
      "doc1": "B1",
      "doc2": "B3",
      "similarity": 0.89
    }
  ]
}
```

---

### Node 5: Relationship Graph Analysis

**Purpose**: Map connections between bidders to detect coordinated behavior.

**Technology**: NetworkX (graph analysis)

**Graph Construction**:

**Nodes**: Each bidder is a node

**Edges**: Connections created based on:
1. **Shared Contact Info**
   - Same email domain → weight 0.8
   - Same phone number → weight 0.9
   - Same address → weight 1.0

2. **Document Similarity**
   - Similarity > 0.7 → edge with weight = similarity score

3. **Stylometric Match**
   - Style similarity > 0.8 → edge with weight = similarity

**Graph Analysis Techniques**:

1. **Community Detection**
   - Uses Louvain algorithm
   - Finds naturally clustered groups
   - Suspicious if 3+ bidders form isolated community

2. **Clique Detection**
   - Finds fully-connected subgraphs
   - Clique of 3+ bidders = high risk
   - Suggests tight coordination

3. **Centrality Analysis**
   - Identifies "hub" bidders with many connections
   - High centrality = potential coordinator

**Graph Density**:
```python
density = num_edges / num_possible_edges
# Low density (0.1-0.3): Normal competitive tender
# High density (0.6+): Suspicious coordination
```

**Example Output**:
```json
{
  "num_bidders": 5,
  "num_relationships": 7,
  "network_density": 0.35,
  "communities": [["B1", "B2", "B3"], ["B4", "B5"]],
  "suspicious_cliques": [["B1", "B2", "B3"]],
  "high_risk_groups": [
    {
      "bidders": ["B1", "B2", "B3"],
      "size": 3,
      "type": "clique"
    }
  ]
}
```

**Visualization**:
```
    B1 ━━━━━━━━━ B2
     ┃  ╲       ╱
     ┃    ╲   ╱
     ┃      B3
     ┃
    B4 ━━━━ B5

Clique detected: B1-B2-B3 (fully connected)
Isolated pair: B4-B5
```

---

### Node 6: AI Report Generation

**Purpose**: Synthesize all findings into human-readable, actionable report.

**Technology**: LangChain + GPT-4o-mini

**Process**:

1. **Aggregate Risk Signals**
   ```python
   all_signals = [
       price_signals,
       similarity_signals,
       stylometry_signals,
       network_signals
   ]
   ```

2. **Prepare LLM Context**
   ```python
   context = f"""
   Tender: {tender_id}
   Bidders: {num_bidders}
   
   Risk Signals:
   - Price Anomaly (high): Clustered bids detected
   - Document Similarity (high): B1 and B3 documents 94% similar
   - Relationship Network (medium): 3-bidder clique detected
   ...
   """
   ```

3. **Generate Report**
   - System prompt: "You are a fraud detection expert..."
   - User prompt: Context + "Provide executive summary, risk indicators, recommendations"
   - Temperature: 0 (deterministic output)

4. **Calculate Overall Risk**
   ```python
   overall_risk = max([signal.score for signal in all_signals])
   ```

**Report Structure**:

```markdown
## Executive Summary
This tender exhibits multiple high-risk indicators suggesting potential 
collusion between Bidders 1, 2, and 3. Immediate investigation recommended.

## Key Risk Indicators (Prioritized)
1. **CRITICAL**: Document Similarity (Score: 0.94)
   - B1 and B3 proposals are 94% identical
   - Evidence: semantic_similarity_matrix
   
2. **HIGH**: Price Coordination (Score: 0.85)
   - Bids are suspiciously clustered
   - B2 and B3 both exactly $1,000 above B1
   
3. **MEDIUM**: Relationship Network (Score: 0.67)
   - B1, B2, B3 form fully-connected group
   - Shared contact information detected

## Recommended Actions
1. Request additional documentation from B1 and B3
2. Verify bidder independence declarations
3. Interview procurement contact persons
4. Consider re-bidding if violations confirmed

## Confidence Level
**HIGH** (85%) - Multiple independent signals converge
```

---

## 🎨 UI Workflow

### User Journey

1. **Input Phase**
   - User enters tender ID and description
   - Adds bidder information (name, price, contact)
   - Uploads PDF documents (proposals, quotes)

2. **Processing Phase**
   - Click "Analyze Tender"
   - Progress indicator shows current node
   - Estimated time: 15-25 seconds

3. **Results Phase**
   - Overall risk score displayed prominently
   - Interactive tabs for each analysis type
   - Network graph visualization
   - Detailed risk signal list
   - Downloadable report

### Streamlit Features

- **Real-time Feedback**: Progress updates during analysis
- **Interactive Visualizations**: Network graphs, price distributions
- **Drill-Down**: Click signals to see detailed evidence
- **Export**: Download PDF report for documentation
- **History**: View past analyses (session-based)

---

## 🔧 Customization & Tuning

### Adjusting Risk Thresholds

Edit `config/config.py`:

```python
# More conservative (fewer false positives)
RISK_THRESHOLDS = {
    "document_similarity": {
        "high": 0.95,  # Only flag near-perfect matches
        "medium": 0.85,
        "low": 0.70
    }
}

# More aggressive (catch more potential risks)
RISK_THRESHOLDS = {
    "document_similarity": {
        "high": 0.85,
        "medium": 0.65,
        "low": 0.45
    }
}
```

### Adding Custom Analysis Nodes

1. **Create Node Function** (src/agents/nodes.py)
   ```python
   def analyze_timing_node(state: TenderAnalysisState) -> Dict:
       # Analyze bid submission timestamps
       ...
       return {"timing_analysis": results}
   ```

2. **Update Workflow** (src/agents/workflow.py)
   ```python
   workflow.add_node("analyze_timing", analyze_timing_node)
   workflow.add_edge("build_relationship_graph", "analyze_timing")
   workflow.add_edge("analyze_timing", "generate_report")
   ```

3. **Update State Schema** (src/state/agent_state.py)
   ```python
   class TenderAnalysisState(TypedDict):
       ...
       timing_analysis: Optional[Dict[str, Any]]
   ```

---

## 📊 Performance Optimization

### Caching Strategies

1. **Model Loading**: Load ML models once at startup
2. **Embedding Cache**: Cache document embeddings
3. **Graph Reuse**: Persist relationship graphs for similar tenders

### Parallel Processing

Consider parallelizing independent nodes:
```python
# Price and document extraction are independent
with ThreadPoolExecutor() as executor:
    future1 = executor.submit(analyze_prices_node, state)
    future2 = executor.submit(analyze_similarity_node, state)
    results = [f.result() for f in [future1, future2]]
```

---

## 🧪 Testing Strategy

### Unit Tests
- Test each analyzer independently
- Mock LLM calls for deterministic tests
- Validate state transitions

### Integration Tests
- End-to-end workflow execution
- Test with known fraud cases
- Verify risk scores match expectations

### Test Fixtures
```
tests/fixtures/
├── clean_tender/       # Normal competitive bidding
├── collusion_case/     # Known collusion example
└── cover_bidding/      # Cover bidding pattern
```

---

## 🚀 Deployment Considerations

### Production Checklist
- [ ] Set up proper logging (ELK stack, CloudWatch)
- [ ] Implement authentication (OAuth, SAML)
- [ ] Add database for persistent storage
- [ ] Configure horizontal scaling (multiple workers)
- [ ] Set up monitoring and alerting
- [ ] Implement audit trail
- [ ] Add data encryption at rest
- [ ] Configure API rate limiting
- [ ] Set up backup and disaster recovery

### Scalability
- Use Celery for background task processing
- Redis for caching and session management
- PostgreSQL for persistent storage
- S3/MinIO for document storage

---

## 📚 References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Sentence-BERT Paper](https://arxiv.org/abs/1908.10084)
- [NetworkX Documentation](https://networkx.org/)
- [Stylometry in Authorship Attribution](https://en.wikipedia.org/wiki/Stylometry)

---

**Next Steps**: See [SETUP.md](SETUP.md) for detailed installation instructions.
