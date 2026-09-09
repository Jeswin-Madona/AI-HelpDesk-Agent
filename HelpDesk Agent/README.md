# 🤖 AI Helpdesk Agent

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat&logo=python)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-google--genai-orange?style=flat&logo=google)](https://ai.google.dev/)
[![NumPy](https://img.shields.io/badge/NumPy-Vector_Search-013243?style=flat&logo=numpy)](https://numpy.org/)
[![Naan Mudhalvan](https://img.shields.io/badge/Naan_Mudhalvan-Project-purple?style=flat)](https://www.naanmudhalvan.tn.gov.in/)

> An AI-powered technical troubleshooting assistant that combines an AI Agent, Retrieval-Augmented Generation (RAG), and real-time system diagnostic tools to diagnose common computer and technical problems.

Developed for the **Naan Mudhalvan** Skill Development Program.

---

## 📋 Core Concepts

1. **🧠 AI Agent (Reasoning Layer)**: Evaluates user queries, filters non-technical questions via guardrails, selects appropriate diagnostic tools, and orchestrates grounded diagnosis.
2. **📚 RAG (Retrieval-Augmented Generation)**: Chunks technical guides from `knowledge_base/`, generates vector embeddings using the Google GenAI SDK (`gemini-embedding-001`), caches indices locally (`data/vector_store.pkl`), and performs top cosine similarity search using NumPy.
3. **🔧 Real System Diagnostic Tools**: Executes live physical hardware inspection:
   - **Internet Diagnostic Tool**: Socket connectivity (8.8.8.8:53) & HTTP reachability checks.
   - **Disk Space Tool**: Real system storage inspection via `shutil.disk_usage()`.
   - **System Health Tool**: Live CPU utilization and RAM memory sampling via `psutil`.

---

## 🏗️ System Architecture

```text
                 USER
                   │
                   ▼
          ┌─────────────────┐
          │   AI AGENT      │
          │ Reasoning Layer │
          └────────┬────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
     ┌─────────┐      ┌─────────────┐
     │   RAG   │      │    TOOLS    │
     └────┬────┘      └──────┬──────┘
          │                  │
          ▼                  ▼
 Knowledge Base       System Diagnostics
          │                  │
          └────────┬─────────┘
                   ▼
            GROUNDED ANSWER
```

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.11+ |
| **AI / LLM** | Google Gemini API (`google-genai` SDK) |
| **Chat Model** | `gemini-2.5-flash` |
| **Embedding Model** | `gemini-embedding-001` |
| **RAG Engine** | NumPy + Cosine Similarity |
| **System Diagnostics** | `psutil` |
| **Disk Diagnostics** | `shutil` |
| **Network Diagnostics** | `socket` + `urllib` |
| **Configuration** | `python-dotenv` |
| **Interface** | Python Console CLI |

---

## 📁 Project Structure

```text
ai-helpdesk-agent/
│
├── main.py                    # Terminal CLI entry point
│
├── agent/                     # AI Agent Package
│   ├── __init__.py
│   └── helpdesk_agent.py      # Intent check, tool selection, LLM synthesis
│
├── rag/                       # RAG Vector Retrieval Package
│   ├── __init__.py
│   ├── knowledge_base.py      # Text file parser & semantic chunker
│   ├── embeddings.py         # Google GenAI embedding service wrapper
│   └── retriever.py           # NumPy vector similarity search engine
│
├── tools/                     # System Hardware Diagnostic Tools
│   ├── __init__.py
│   ├── internet_tool.py       # Physical socket & HTTP connection check
│   ├── disk_tool.py           # Drive storage inspection via shutil
│   └── system_tool.py         # CPU & RAM monitoring via psutil
│
├── knowledge_base/            # Categorized Technical Guides
│   ├── computer.txt
│   ├── network.txt
│   ├── operating_system.txt
│   ├── printer.txt
│   └── software.txt
│
├── data/                      # Local cached vector embeddings (vector_store.pkl)
├── .env.example               # Blueprint for environment variables
├── .gitignore                 # Git exclusion rules
├── requirements.txt           # Python package dependencies
└── README.md                  # Complete documentation
```

---

## ⚙️ Installation & Setup

1. **Clone the Repository & Navigate to Directory**:
   ```bash
   git clone <repository-url>
   cd ai-helpdesk-agent
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_CHAT_MODEL=gemini-2.5-flash
   EMBEDDING_MODEL=gemini-embedding-001
   SIMILARITY_THRESHOLD=0.25
   TOP_K_MATCHES=4
   ```

4. **Run the Application**:
   ```bash
   python main.py
   ```

---

## 🧪 Demonstration Scenarios

### Demo 1 — Network Troubleshooting
- **Input**: `"My laptop is connected to WiFi but websites are not opening."`
- **Flow**: User Input ➔ Agent ➔ RAG (Retrieves *WiFi Connected But No Internet*) ➔ Internet Diagnostic Tool (Socket & HTTP test) ➔ Grounded Answer.

### Demo 2 — Performance Monitoring
- **Input**: `"My laptop has become extremely slow."`
- **Flow**: User Input ➔ Agent ➔ RAG (Retrieves *Slow Laptop Performance*) ➔ System Health Tool (`psutil` CPU/RAM check) ➔ Grounded Answer.

### Demo 3 — Storage Space Check
- **Input**: `"My laptop is running out of storage space."`
- **Flow**: User Input ➔ Agent ➔ RAG (Retrieves *Low Disk Space*) ➔ Disk Diagnostic Tool (`shutil` storage metrics) ➔ Grounded Answer.

### Demo 4 — Printer Troubleshooting
- **Input**: `"My printer is connected but documents are stuck in the queue."`
- **Flow**: User Input ➔ Agent ➔ RAG (Retrieves *Print Spooler Reset Guide*) ➔ Grounded Step-by-Step Instructions.

### Demo 5 — Non-Technical Guardrail Test
- **Input**: `"Who won the World Cup?"`
- **Flow**: User Input ➔ Agent Guardrail ➔ Off-topic query detected ➔ Politely redirects user to technical troubleshooting topics.

---

## 🎓 Project Credits

Developed as part of the **Naan Mudhalvan** Skill Development Program.

- **Project Name**: AI Helpdesk Agent
- **Domain**: Artificial Intelligence & Technical Support Automation
- **Architecture**: AI Agent + RAG + Tools
- **Interface**: Python Console Application
