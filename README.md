# 🤖 AI Career Copilot

AI Career Copilot is an intelligent resume analysis and career guidance platform built with Streamlit, LangChain, Groq LLMs, Gemini Embeddings, and ChromaDB.

The application helps job seekers evaluate their resumes against specific job descriptions, understand their strengths and weaknesses, identify skill gaps, and receive personalized career recommendations.

---

## ✨ Features

### 📄 Resume Analysis

* Upload resumes in PDF, DOC, or DOCX format.
* Extracts and processes resume content automatically.
* Generates a detailed candidate profile.

### 🎯 Job Match Analysis

* Compare resumes against a target job role and job description.
* Calculates:

  * ATS Score
  * Overall Match Score
  * Skills Match Percentage
  * ATS Pass Probability
  * Interview Selection Probability

### 📊 Candidate Insights

* Strengths Analysis
* Weaknesses Analysis
* Missing Skills Detection
* Resume Improvement Suggestions

### 🚀 Career Guidance

* Recommended Certifications
* Suggested Projects
* Personalized Learning Roadmap

### 💬 AI Resume Chat Assistant

* Ask questions about your resume.
* Receive personalized career advice.
* Explore strengths, skill gaps, projects, and job readiness.
* Powered by Retrieval-Augmented Generation (RAG).

---

## 🏗️ Tech Stack

### Frontend

* Streamlit

### LLM & AI

* LangChain
* Groq (Llama Models)
* Google Gemini Embeddings

### Vector Database

* ChromaDB

### Document Processing

* PyPDF
* Docx2Txt

---

## ⚙️ Architecture

```text
Resume Upload
      │
      ▼
Text Extraction
      │
      ▼
Document Chunking
      │
      ▼
Gemini Embeddings
      │
      ▼
Chroma Vector Store
      │
      ▼
Resume Analysis (Groq LLM)
      │
      ▼
Interactive Dashboard
      │
      ▼
AI Resume Chat Assistant
```

---

## 📂 Project Structure

```text
AI-Career-Copilot/
│
├── app.py
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

---

## 🔑 Environment Variables

Create a `.env` file locally:

```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
```

For Streamlit Cloud deployment, add these keys in the Secrets Manager.

---

## 🚀 Local Setup

### Clone Repository

```bash
git clone <repository-url>
cd AI-Career-Copilot
```

### Install Dependencies

Using uv:

```bash
uv sync
```

### Run Application

```bash
uv run streamlit run app.py
```

The application will launch in your browser.

---

## 📝 Usage

1. Upload your resume.
2. Enter the target job title.
3. Paste the job description.
4. Click **Analyze My Resume**.
5. Review:

   * ATS Score
   * Match Analysis
   * Skill Gaps
   * Career Recommendations
6. Chat with the AI Assistant for personalized guidance.

---

## 🔒 Privacy

* Resumes are processed only during the active session.
* No resume data is permanently stored.
* Temporary vector databases are created in memory and discarded after the session ends.

---

## 🎯 Future Enhancements

* Job Search Integration
* Resume Optimization Suggestions
* Resume Rewriting Assistant
* Cover Letter Generation
* Interview Preparation Module
* Skill Gap Learning Resources
* Job Recommendation Engine

---

## 👨‍💻 Author

Developed as an AI-powered career guidance and resume intelligence platform to help candidates improve their job readiness and career growth.
