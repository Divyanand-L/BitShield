# 🛡️ BitShield - Transparent Procurement Agent

A stateful AI agent built with LangGraph that orchestrates document analysis, statistical checks, and relationship modeling to generate explainable early-warning signals for government tender risk.

## 🎯 Overview

The **Transparent Procurement Agent** is designed to support government procurement officers by identifying anomalous bidding patterns in public tenders. By analyzing tender documents, pricing behavior, and relational signals, the agent flags potential risks such as:

- 🤝 **Collusion** - Coordinated bidding between competitors
- 📝 **Cover Bidding** - Artificially high bids to make favored bidder appear competitive
- 🔗 **Undeclared Relationships** - Hidden connections between bidders
- 📄 **Document Similarity** - Suspiciously similar submissions
- ✍️ **Stylometric Patterns** - Same author across multiple bids

Rather than making automated judgments, the system provides **explainable evidence** and **risk scores** to guide human review, improving transparency and reducing fraud before contracts are awarded.

---

## 🏗️ Architecture

### Technology Stack

| Responsibility      | Technology          | Purpose                                    |
| ------------------- | ------------------- | ------------------------------------------ |
| Agent Control       | LangGraph           | Stateful workflow orchestration            |
| Reasoning           | LLM (via LangChain) | Generate explainable reports               |
| State Management    | LangGraph State     | Maintain analysis context                  |
| Text Extraction     | pdfplumber          | Extract text from PDF documents            |
| Semantic Similarity | SBERT               | Detect document content similarity         |
| Stylometry          | spaCy + sklearn     | Analyze writing style patterns             |
| Price Analysis      | Pandas + NumPy      | Statistical anomaly detection              |
| Relationship Graph  | NetworkX            | Graph-based relationship detection         |
| UI                  | Streamlit           | Interactive web interface                  |
| Environment         | Python + venv       | Isolated dependency management             |

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                       │
│           (User Input, Visualization, Reports)              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph Agent Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Extract     │→ │   Analyze    │→ │  Generate    │     │
│  │  Documents   │  │   Patterns   │  │   Report     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Analysis Utils Layer                       │
│  • Price Analyzer    • Semantic Analyzer                    │
│  • Stylometry        • Relationship Graph                   │
│  • Document Processor                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  • State Management  • Risk Signals  • Evidence             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
BitShield/
├── app.py                      # Streamlit application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
├── .gitignore                 # Git ignore rules
│
├── config/                    # Configuration settings
│   ├── __init__.py
│   └── config.py              # Application settings & thresholds
│
├── src/                       # Core application code
│   ├── __init__.py
│   │
│   ├── agents/                # LangGraph agent workflow
│   │   ├── __init__.py
│   │   ├── nodes.py           # Agent node functions
│   │   └── workflow.py        # Workflow graph definition
│   │
│   ├── state/                 # State management
│   │   ├── __init__.py
│   │   └── agent_state.py     # State schema & models
│   │
│   └── utils/                 # Analysis utilities
│       ├── __init__.py
│       ├── document_processor.py   # PDF text extraction
│       ├── semantic_analyzer.py    # SBERT similarity
│       ├── stylometry.py           # Writing style analysis
│       ├── price_analyzer.py       # Statistical price checks
│       └── relationship_graph.py   # NetworkX graph analysis
│
├── ui/                        # Streamlit UI components
│   ├── __init__.py
│   └── app.py                 # Main UI application
│
├── data/                      # Data directory
│   ├── uploads/               # Uploaded tender documents
│   ├── cache/                 # Cached analysis results
│   └── models/                # Downloaded ML models
│
└── docs/                      # Documentation
    ├── WORKFLOW.md            # Detailed workflow explanation
    └── SETUP.md               # Setup instructions
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- OpenAI API key
- 2GB+ RAM (for ML models)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd BitShield

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## 🔄 Workflow Explanation

### Agent Workflow Graph

The LangGraph agent executes a sequential workflow:

```
START
  ↓
[1] Extract Documents
  ↓
[2] Analyze Prices
  ↓
[3] Analyze Similarity
  ↓
[4] Analyze Stylometry
  ↓
[5] Build Relationship Graph
  ↓
[6] Generate AI Report
  ↓
END
```

### Detailed Node Descriptions

#### **Node 1: Extract Documents**
- **Input**: List of PDF document paths
- **Process**: Uses `pdfplumber` to extract raw text from all documents
- **Output**: Dictionary mapping document paths to extracted text
- **Purpose**: Convert unstructured PDFs into processable text

#### **Node 2: Analyze Prices**
- **Input**: Bid amounts from all bidders
- **Process**:
  - Statistical outlier detection (Z-score, IQR methods)
  - Cover bidding pattern detection
  - Price clustering analysis
  - Round number frequency check
- **Output**: Risk scores, suspicious patterns, statistical metrics
- **Risk Signals**: `price_anomaly` (high/medium/low)

#### **Node 3: Analyze Similarity**
- **Input**: Extracted text from all bidder documents
- **Process**:
  - Generate embeddings using Sentence-BERT
  - Compute pairwise cosine similarity
  - Identify cross-bidder similarities > 0.7
- **Output**: Similarity matrix, high-risk pairs
- **Risk Signals**: `document_similarity` (high if > 0.9)

#### **Node 4: Analyze Stylometry**
- **Input**: Extracted text from all bidder documents
- **Process**:
  - Extract linguistic features (word length, sentence length, lexical diversity)
  - POS tagging for syntax patterns
  - Compare stylometric fingerprints
- **Output**: Feature vectors, suspicious style matches
- **Risk Signals**: `stylometry` (high if > 0.85)

#### **Node 5: Build Relationship Graph**
- **Input**: Bidder IDs, contact info, previous analysis results
- **Process**:
  - Create NetworkX graph with bidders as nodes
  - Add edges for shared contacts, document similarity
  - Detect communities (clusters of connected bidders)
  - Find cliques (fully connected subgroups)
  - Calculate centrality scores
- **Output**: Graph structure, communities, suspicious groups
- **Risk Signals**: `relationship_network` (based on group size)

#### **Node 6: Generate AI Report**
- **Input**: All risk signals from previous nodes
- **Process**:
  - Aggregate evidence from all analysis modules
  - Use LLM (GPT-4) to generate human-readable summary
  - Provide actionable recommendations
  - Calculate overall risk score (max of individual signals)
- **Output**: Executive summary, prioritized risk list, confidence level

---

## 🎯 Use Cases

### Example 1: Detecting Cover Bidding
```
Scenario: Company A submits a $100,000 bid. Companies B and C submit 
         $120,000 bids (20% higher and nearly identical).

Detection:
  ✓ Price Analysis: Flags clustered high bids
  ✓ Relationship Graph: Checks for connections between B and C
  ✓ AI Report: "Companies B and C may be submitting cover bids"
```

### Example 2: Document Copy-Paste
```
Scenario: Two bidders submit proposals with 95% identical text.

Detection:
  ✓ Similarity Analysis: 0.95 semantic similarity score
  ✓ Stylometry: Identical writing style features
  ✓ AI Report: "High likelihood of document sharing between bidders"
```

### Example 3: Hidden Relationships
```
Scenario: Three bidders share the same phone number and email domain.

Detection:
  ✓ Relationship Graph: Forms a clique in the network
  ✓ Centrality: High connection density
  ✓ AI Report: "Detected undeclared relationships requiring investigation"
```

---

## ⚙️ Configuration

### Risk Thresholds (config/config.py)

```python
RISK_THRESHOLDS = {
    "price_anomaly": {
        "high": 0.8,    # Score > 0.8 = high risk
        "medium": 0.5,   # Score 0.5-0.8 = medium risk
        "low": 0.3       # Score < 0.3 = low risk
    },
    "document_similarity": {
        "high": 0.9,     # Similarity > 90%
        "medium": 0.7,
        "low": 0.5
    },
    # ... other thresholds
}
```

### Analysis Parameters

- `MIN_BIDDERS_FOR_COLLUSION = 2` - Minimum bidders needed for collusion analysis
- `STATISTICAL_SIGNIFICANCE_LEVEL = 0.05` - P-value threshold for statistical tests
- `PRICE_OUTLIER_STD_THRESHOLD = 2.0` - Standard deviations for outlier detection

---

## 📊 Output & Reports

### Risk Signal Structure

Each detected risk is represented as:

```python
RiskSignal(
    signal_type="document_similarity",
    severity="high",  # high/medium/low
    score=0.92,       # 0.0 to 1.0
    description="High similarity detected between B1 and B2",
    evidence={
        "bidder1": "B1",
        "bidder2": "B2",
        "similarity_score": 0.92,
        "document1": "proposal_B1.pdf",
        "document2": "proposal_B2.pdf"
    },
    affected_bidders=["B1", "B2"]
)
```

### AI-Generated Report

The LLM produces a structured report:

1. **Executive Summary**: 2-3 sentence overview
2. **Key Risk Indicators**: Prioritized list with evidence
3. **Recommended Actions**: Specific steps for procurement officers
4. **Confidence Level**: System's confidence in findings

---

## 🧪 Testing

### Running Tests

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=src tests/
```

### Test Data

Sample tender documents are provided in `tests/fixtures/`:
- `clean_tender/` - Normal competitive bidding
- `collusion_tender/` - Known collusion case
- `cover_bidding_tender/` - Cover bidding pattern

---

## 🔒 Security & Privacy

- **Data Privacy**: All uploaded documents are stored locally
- **API Keys**: Never commit `.env` file to version control
- **Anonymization**: System can anonymize bidder names in reports
- **Audit Logs**: All analyses are logged with timestamps

---

## 📈 Performance

### Expected Processing Times

- Document extraction: ~1-2 seconds per PDF
- Semantic analysis: ~3-5 seconds for 10 documents
- Stylometry: ~2-4 seconds for 10 documents
- Price analysis: < 1 second
- Relationship graph: < 1 second
- AI report generation: ~5-10 seconds

**Total**: ~15-25 seconds for typical tender (3 bidders, 10 documents)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- LangChain & LangGraph for agent orchestration framework
- Sentence-Transformers for semantic similarity
- spaCy for NLP capabilities
- NetworkX for graph analysis
- Streamlit for rapid UI development

---

## 📞 Support

For questions or issues:
- Open a GitHub issue
- Contact: support@bitshield.dev
- Documentation: [docs/](docs/)

---

**Built with ❤️ for transparent and fair government procurement**
