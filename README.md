# 🌐 Network Topology Identification System

> **AI-powered telecom fronthaul network topology identification and anomaly detection**

An intelligent system that analyzes 5G fronthaul network data to automatically identify topology groups, detect congestion anomalies, and provide actionable insights using ML and LLM-powered analysis.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![React](https://img.shields.io/badge/react-19-61DAFB)
![Status](https://img.shields.io/badge/status-active-success)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Topology Detection** | Automatically identifies fronthaul link groups using correlation analysis |
| **Anomaly Detection** | ML-based detection of throughput drops and congestion events |
| **Interactive Dashboard** | Real-time visualization with heatmaps, topology graphs, and propagation flows |
| **LLM Copilot** | AI-powered chat assistant for network insights and recommendations |
| **Configurable Thresholds** | Adjustable anomaly detection sensitivity |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                  │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────────────┐ │
│  │ Topology    │ │  Heatmap     │ │  LLM Copilot Chatbot      │ │
│  │ Graph       │ │  Viz         │ │                           │ │
│  └─────────────┘ └──────────────┘ └───────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI + Python)                  │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────────────┐ │
│  │ REST API    │ │  LLM Service │ │  ML Pipeline Integration  │ │
│  │ /v1/api/*   │ │  (Ollama)    │ │                           │ │
│  └─────────────┘ └──────────────┘ └───────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ML PIPELINE (Python)                      │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────────────┐ │
│  │Preprocessing│ │  Anomaly     │ │  Clustering               │ │
│  │             │─▶│  Detection   │─▶│  (Hierarchical)          │ │
│  └─────────────┘ └──────────────┘ └───────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **Ollama** (for LLM features) - [Install Ollama](https://ollama.ai)

### 1. Clone the Repository

```bash
git clone https://github.com/NishDs-06/Network_Toplogy_Idetificaiton.git
cd Network_Toplogy_Idetificaiton
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Ollama (LLM Backend)

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the required model
ollama pull llama3.1:8b

# Start Ollama server
ollama serve
```

### 4. Configure Backend

```bash
cd backend

# Create .env file
cat > .env << EOF
# Ollama LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.1:8b
OLLAMA_TIMEOUT=120

# App settings
DEBUG=true
LOG_LEVEL=INFO
EOF
```

### 5. Start Backend Server

```bash
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 6. Start Frontend

```bash
cd Frontend
npm install
npm run dev
```

### 7. Open Browser

Navigate to: **http://localhost:5173**

---

## ⚙️ Configuration

### LLM Configuration (Backend)

Edit `backend/.env`:

```env
# ============================================
# OLLAMA CONFIGURATION (Self-Hosted LLM)
# ============================================

# Local Ollama (default)
OLLAMA_BASE_URL=http://localhost:11434

# OR: Remote Ollama (e.g., via Tailscale)
# OLLAMA_BASE_URL=http://100.109.131.90:11434

# Available models (run: ollama list)
OLLAMA_DEFAULT_MODEL=llama3.1:8b
# Alternatives: llama3.2, qwen2.5:14b, mistral, gemma2

# Timeout for LLM requests (seconds)
OLLAMA_TIMEOUT=120
```

### Supported LLM Models

| Model | Size | Speed | Quality | VRAM Required |
|-------|------|-------|---------|---------------|
| `llama3.1:8b` | 4.7GB | Fast | Good | 8GB |
| `llama3.2:3b` | 2GB | Very Fast | Basic | 4GB |
| `qwen2.5:14b` | 9GB | Medium | Excellent | 16GB |
| `mistral:7b` | 4.1GB | Fast | Good | 8GB |

### ML Pipeline Thresholds

Edit `ML/step2_detect_anomalies.py`:

```python
WINDOW = 100       # Rolling window size for baseline
DROP_RATIO = 0.30  # 30% throughput drop = anomaly
```

Edit `visualization/plot_topology_graph.py`:

```python
ANOMALY_THRESHOLD = 0.25  # Flag cell if >25% slots anomalous
```

---

## 📖 Usage

### Running the ML Pipeline

```bash
# 1. Preprocess raw data
cd Preprocessing
python preprocess.py

# 2. Detect anomalies
cd ../ML
python step2_detect_anomalies.py

# 3. Cluster topology
cd ../Clustering
python personC_clustering.py

# 4. Generate visualizations
cd ../visualization
python plot_topology_graph.py
```

### Using the Dashboard

1. **Topology View** - See network cell groupings
2. **Heatmap** - View correlation matrix
3. **Propagation Flow** - See congestion spread patterns
4. **Chatbot** - Ask questions like:
   - "Where are the anomalies?"
   - "Why is Cell 5 flagged?"
   - "What cells share topology with Cell 10?"

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000/v1/api
```

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cells` | GET | Get all cell data with anomaly status |
| `/topology-groups` | GET | Get detected topology groups |
| `/similarity-matrix` | GET | Get cell correlation matrix |
| `/recommendations` | GET | Get AI-generated recommendations |
| `/chat` | POST | Send message to LLM copilot |
| `/recommendation-expand` | POST | Get detailed recommendation info |

### Example: Chat API

```bash
curl -X POST http://localhost:8000/v1/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Where are the anomalies?"}'
```

---

## 📁 Project Structure

```
Network_Toplogy_Idetificaiton/
├── Frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── store/           # Zustand state
│   │   └── services/        # API client
│   └── package.json
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/v1/routes/   # API endpoints
│   │   ├── services/        # Business logic
│   │   └── providers/       # Ollama integration
│   └── .env                 # Configuration
│
├── ML/                       # ML pipeline
│   ├── step2_detect_anomalies.py
│   └── outputs/             # Generated CSV files
│
├── Clustering/               # Topology clustering
│   ├── personC_clustering.py
│   └── outputs/
│
├── Preprocessing/            # Data preprocessing
│   ├── raw_data/            # Input .dat files
│   └── outputs/
│
├── visualization/            # Plot generation
│   ├── plot_topology_graph.py
│   └── plot_heatmap.py
│
├── requirements.txt          # Python dependencies
└── README.md
```

---

<div align="center">

## 👨‍💻 The Team

<table>
<tr>
<td align="center">
<a href="https://github.com/NishDs-06">
<img src="https://github.com/NishDs-06.png" width="100px;" alt="Nishanth"/><br />
<sub><b>✨ Nishanth ✨</b></sub>
</a><br />
<sub>🔧 Full Stack & ML</sub>
</td>
<td align="center">
<a href="https://github.com/">
<img src="https://avatars.githubusercontent.com/u/583231?v=4" width="100px;" alt="Teammate"/><br />
<sub><b>Team Member</b></sub>
</a><br />
<sub>📊 Data Science</sub>
</td>
<td align="center">
<a href="https://github.com/">
<img src="https://avatars.githubusercontent.com/u/583231?v=4" width="100px;" alt="Teammate"/><br />
<sub><b>Team Member</b></sub>
</a><br />
<sub>🎨 Frontend</sub>
</td>
</tr>
</table>

---

### 🌟 Star this repo if you found it helpful!

<p>
<a href="https://github.com/NishDs-06/Network_Toplogy_Idetificaiton/stargazers">
<img src="https://img.shields.io/github/stars/NishDs-06/Network_Toplogy_Idetificaiton?style=social" alt="Stars">
</a>
<a href="https://github.com/NishDs-06/Network_Toplogy_Idetificaiton/network/members">
<img src="https://img.shields.io/github/forks/NishDs-06/Network_Toplogy_Idetificaiton?style=social" alt="Forks">
</a>
</p>

**Built with ❤️ for telecom network intelligence**

*© 2026 Network Topology Team*

</div>
