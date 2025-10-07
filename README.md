# AI-Powered Contract Processing System

## Overview
The **AI-Powered Contract Processing System** automates the extraction, summarization, and analysis of legal contracts using advanced **Generative AI**.  
It helps legal teams save time by automatically identifying key clauses, summarizing lengthy documents, redacting sensitive information, and calculating risk scores.

This system supports **PDF, DOCX, PPTX, XLSX, TXT, and image formats (JPG, PNG)**.

---

## AI Architecture

### 🔹 Core Workflow
1. **Document Ingestion** – The system accepts multiple formats (PDF, DOCX, PPTX, XLSX, TXT, images).  
2. **Text Extraction** – Uses libraries like **PyMuPDF**, **python-docx**, **python-pptx**, **openpyxl**, and **EasyOCR** for OCR text extraction.  
3. **Entity & Clause Analysis** – Key clauses (e.g., parties, dates, obligations) are extracted using rule-based and LLM-powered entity recognition.  
4. **Summarization & Risk Scoring** – The **llama-3.3-70b-versatile** generates summaries and calculates a risk score.  
5. **Redaction** – Sensitive information such as PII (names, emails, contact numbers) is automatically masked.  
6. **Output Generation** – A concise report is returned to the user with key insights and risks.

### 🔹 Components Used
- **FastAPI** – REST API Framework  
- **Groq API (llama-3.3-70b-versatile)** – For AI-driven summarization & risk analysis  
- **EasyOCR** – For OCR-based image text extraction  
- **Ollama (gemma3:4b)** – For local model inference without cloud API  
- **dotenv** – To manage API keys securely  
- **NumPy, PyMuPDF, OpenPyXL, python-docx, python-pptx** – For text extraction  

## ⚙️ Setup Instructions

### 1️⃣ Create and Activate Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate      # (Windows)
# or
source venv/bin/activate   # (macOS/Linux)
``` 
### 2️⃣ Install Dependencies
```
pip install -r requirements.txt
```
### 3️⃣ Set Environment Variables

In config.py
```
GROQ_API_KEY=your_groq_api_key_here
```
### Run the Application

Start the FastAPI server:
```
uvicorn app.main:app --reload
```

Once the server starts, run the streamlit page:
```
streamlit run 
```

If you prefer local model inference:
```
ollama pull llama3:latest
```

Then in config.py, switch the model provider:
```
USE_GROQ = False  # Set to False to use Ollama
```
## Folder architecture
AI-Powered-Contract-Processing-System /
│
├── README.md
├── requirements.txt
├── .env.example
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── contract.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_client.py
│   │   ├── parser.py
│   │   ├── redactor.py
│   │   ├── summarizer.py
│   │   └── risk_calculator.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py
│   │
│   └── models/
│       ├── __init__.py
│       └── schema.py
│
└── tests/
    ├── __init__.py
    └── test_contract_agent.py
