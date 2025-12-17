# 🚀 BitShield Setup Guide

Complete installation and configuration instructions for the Transparent Procurement Agent.

---

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.10 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space (for models and dependencies)
- **Internet**: Required for initial model downloads and API calls

### Recommended Requirements
- **RAM**: 16GB (for large document sets)
- **CPU**: 4+ cores (parallel processing)
- **GPU**: Optional (speeds up semantic analysis)

---

## 🔧 Installation

### Step 1: Install Python

**Windows:**
```powershell
# Download from python.org or use Microsoft Store
winget install Python.Python.3.11
```

**macOS:**
```bash
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Verify Installation:**
```bash
python --version
# Should show Python 3.10 or higher
```

---

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/bitshield.git
cd bitshield

# Or download and extract ZIP
# https://github.com/your-org/bitshield/archive/main.zip
```

---

### Step 3: Create Virtual Environment

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate
```

**Verification:**
Your terminal prompt should now show `(venv)` prefix.

---

### Step 4: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This will install:
# - LangChain & LangGraph (agent framework)
# - Sentence-Transformers (semantic analysis)
# - spaCy (NLP)
# - NetworkX (graph analysis)
# - Streamlit (UI)
# - And ~40 other packages
```

**Expected Duration**: 5-10 minutes

---

### Step 5: Download NLP Models

```bash
# Download spaCy English model
python -m spacy download en_core_web_sm

# Sentence-BERT model will download automatically on first use
# (~90MB, happens during first analysis)
```

---

### Step 6: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Windows:
copy .env.example .env
```

**Edit `.env` file:**
```bash
# Open in your text editor
nano .env   # Linux/Mac
notepad .env   # Windows
```

**Add your OpenAI API key:**
```env
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Optional: Enable LangSmith tracing for debugging
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your_langsmith_key
```

**Get OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy and paste into `.env`

---

## ✅ Verify Installation

### Quick Test

```bash
# Test Python imports
python -c "import langchain, langgraph, streamlit, sentence_transformers, spacy, networkx; print('All imports successful!')"

# Test spaCy model
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy model loaded!')"
```

### Run Application

```bash
streamlit run app.py
```

**Expected Output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

Open http://localhost:8501 in your browser.

---

## 🎯 First Analysis

### Demo Workflow

1. **Open Application**: Navigate to http://localhost:8501

2. **Enter Tender Information:**
   - Tender ID: `DEMO-001`
   - Description: `Test tender for system validation`

3. **Add Bidders:**
   - Use the default 3 bidders
   - Adjust bid amounts if desired

4. **Upload Documents:**
   - Create 3 sample PDFs with text (any content)
   - Upload one document per bidder
   - Or use test fixtures: `tests/fixtures/clean_tender/`

5. **Run Analysis:**
   - Click "🔍 Analyze Tender"
   - Wait 15-25 seconds
   - View results in tabs

6. **Explore Results:**
   - Check overall risk score
   - Navigate through analysis tabs
   - View AI-generated report

---

## 🐛 Troubleshooting

### Issue: Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'langchain'
```

**Solution:**
```bash
# Ensure virtual environment is activated
# You should see (venv) in prompt

# Re-install dependencies
pip install -r requirements.txt
```

---

### Issue: spaCy Model Not Found

**Symptom:**
```
OSError: [E050] Can't find model 'en_core_web_sm'
```

**Solution:**
```bash
python -m spacy download en_core_web_sm

# If that fails, install directly:
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

---

### Issue: OpenAI API Key Error

**Symptom:**
```
AuthenticationError: Incorrect API key provided
```

**Solution:**
1. Verify `.env` file exists in project root
2. Check key format: `sk-proj-...` (new format) or `sk-...` (old format)
3. Ensure no extra spaces or quotes around key
4. Restart Streamlit app after editing `.env`

---

### Issue: Streamlit Port Already in Use

**Symptom:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or kill existing process
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8501 | xargs kill -9
```

---

### Issue: Slow First Analysis

**Symptom:**
First analysis takes 2-3 minutes.

**Solution:**
This is normal! The system is:
- Downloading Sentence-BERT model (~90MB)
- Loading spaCy model into memory
- Initializing LLM connection

Subsequent analyses will be much faster (15-25 seconds).

---

### Issue: Memory Errors with Large Documents

**Symptom:**
```
MemoryError: Unable to allocate array
```

**Solution:**
```python
# Edit config/config.py
MAX_TENDER_FILE_SIZE_MB = 10  # Reduce from 50

# Or process documents in batches
# Edit src/utils/semantic_analyzer.py to use batch processing
```

---

## 🔐 Security Best Practices

### Protect API Keys

```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use environment variables in production
export OPENAI_API_KEY="sk-..."

# Rotate keys regularly
# Set usage limits in OpenAI dashboard
```

### Secure File Uploads

```python
# Configure in config/config.py
ALLOWED_EXTENSIONS = ['.pdf']
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
UPLOAD_FOLDER = "data/uploads"  # Restrict to specific directory
```

### Production Deployment

```bash
# Use HTTPS
streamlit run app.py --server.enableCORS false --server.enableXsrfProtection true

# Add authentication (example with streamlit-authenticator)
pip install streamlit-authenticator

# Configure firewall
# Only allow access from internal network
```

---

## 📦 Optional Components

### GPU Acceleration (CUDA)

For faster semantic analysis on NVIDIA GPUs:

```bash
# Check CUDA availability
nvidia-smi

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

### Database Integration

For persistent storage:

```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Configure database
# Edit config/config.py
DATABASE_URL = "postgresql://user:pass@localhost/bitshield"
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

```bash
# Build and run
docker build -t bitshield .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... bitshield
```

---

## 🧪 Development Setup

### Install Dev Dependencies

```bash
# Create dev requirements
cat > requirements-dev.txt << EOF
pytest==7.4.3
pytest-cov==4.1.0
black==23.12.1
flake8==6.1.0
mypy==1.7.1
pre-commit==3.6.0
EOF

# Install
pip install -r requirements-dev.txt
```

### Pre-commit Hooks

```bash
# Setup
pre-commit install

# Run manually
pre-commit run --all-files
```

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src tests/

# Specific test
pytest tests/test_price_analyzer.py -v
```

---

## 📊 Monitoring & Logging

### Enable LangSmith Tracing

```env
# .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls_...
LANGCHAIN_PROJECT=bitshield-prod
```

View traces at: https://smith.langchain.com

### Application Logs

```bash
# View logs
tail -f logs/app.log

# Configure logging level
# Edit config/config.py
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

---

## 🆘 Getting Help

### Resources

- **Documentation**: `/docs` folder
- **GitHub Issues**: Report bugs and request features
- **Community Forum**: [link]
- **Email Support**: support@bitshield.dev

### Common Questions

**Q: Can I use Claude or other LLMs instead of OpenAI?**
A: Yes! Edit `src/agents/nodes.py`:
```python
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-sonnet-20240229")
```

**Q: How much does OpenAI API cost per analysis?**
A: Approximately $0.01-0.05 per tender analysis with GPT-4o-mini. Using GPT-4 costs ~10x more but provides better reports.

**Q: Can I run this offline?**
A: Partially. You need internet for:
- Initial model downloads
- LLM report generation

Everything else (price analysis, similarity, graph) works offline.

**Q: Is this GDPR compliant?**
A: The system processes data locally. However:
- OpenAI API sends data to their servers
- Consider using local LLMs (Ollama, LLaMA) for sensitive data
- Implement data anonymization before LLM calls

---

## ✅ Installation Checklist

- [ ] Python 3.10+ installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] spaCy model downloaded (`python -m spacy download en_core_web_sm`)
- [ ] `.env` file created with OpenAI API key
- [ ] Test imports successful
- [ ] Streamlit app launches
- [ ] First analysis completes successfully

---

**Congratulations!** 🎉 Your BitShield installation is complete.

Next: Read [WORKFLOW.md](WORKFLOW.md) to understand how the system works.
