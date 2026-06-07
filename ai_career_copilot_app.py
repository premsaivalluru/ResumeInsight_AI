# -*- coding: utf-8 -*-
"""
AI Career Copilot - Streamlit Application
Two-page app: Home (upload) → Dashboard (analysis results)
"""
import streamlit as st
import json
import os
import shutil
import tempfile
from operator import itemgetter
from dotenv import load_dotenv

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="AI Career Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_dotenv()

# ── Lazy imports so missing packages don't crash on import ────────────────────
def get_llm():
    from langchain_groq import ChatGroq
    api_key = os.getenv("GROQ_API_KEY")
    return ChatGroq(groq_api_key=api_key, temperature=0.3, model="llama-3.3-70b-versatile")

def get_chat_llm():
    from langchain_groq import ChatGroq
    api_key = os.getenv("GROQ_API_KEY")
    return ChatGroq(groq_api_key=api_key, temperature=0.3, model="llama-3.1-8b-instant")

# ── Global CSS ─────────────────────────────────────────────────────────────────
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #0d0f1a;
    --bg-secondary: #131627;
    --bg-card: #1a1d2e;
    --bg-card-hover: #1e2236;
    --border: #2a2d45;
    --border-accent: #4f46e5;
    --text-primary: #e8eaf0;
    --text-secondary: #8b8fa8;
    --accent-purple: #6366f1;
    --accent-blue: #3b82f6;
    --accent-green: #22c55e;
    --accent-red: #ef4444;
    --accent-yellow: #eab308;
    --accent-cyan: #06b6d4;
    --grad-purple: linear-gradient(135deg, #6366f1, #8b5cf6);
    --grad-btn: linear-gradient(135deg, #4f46e5, #7c3aed);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

[data-testid="stSidebar"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
header { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

[data-testid="stAppViewContainer"] > [data-testid="stVerticalBlock"] {
    padding: 0 !important;
}

/* ── Upload widget ───────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 2px dashed var(--border-accent) !important;
    border-radius: 12px !important;
    padding: 24px !important;
}

[data-testid="stFileUploader"] label { color: var(--text-primary) !important; }

/* ── Text inputs ─────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 15px !important;
    padding: 14px 16px !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent-purple) !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
[data-testid="stButton"] > button {
    background: var(--grad-btn) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 14px 32px !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}

[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4) !important;
}

/* ── Chat input ──────────────────────────────────────────────────────────── */
[data-testid="stChatInput"] textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 24px !important;
    color: var(--text-primary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Chat messages ───────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-accent); border-radius: 3px; }

/* ── Spinner / progress ──────────────────────────────────────────────────── */
[data-testid="stSpinner"] { color: var(--accent-purple) !important; }

/* ── Metric cards ────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}

/* ── Divider ─────────────────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ── Helper: load resume text from uploaded file ────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
def extract_resume_text(uploaded_file) -> str:
    """Save upload to temp file and extract text via LangChain loaders."""
    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(tmp_path)
        elif suffix in (".doc", ".docx"):
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(tmp_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        docs = loader.load()
        return "\n".join([d.page_content for d in docs]), docs
    finally:
        os.unlink(tmp_path)


# ══════════════════════════════════════════════════════════════════════════════
# ── Helper: run LLM analysis ──────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
def run_analysis(resume_text: str, job_title: str, job_description: str) -> dict:
    from langchain_core.output_parsers import JsonOutputParser
    llm = get_llm()
    parser = JsonOutputParser()

    prompt = f"""
You are an expert ATS and Recruitment Analyst.

Analyze how well the candidate's resume matches the target job role.

RESUME:
{resume_text}

TARGET JOB TITLE: {job_title}

TARGET JOB DESCRIPTION:
{job_description}

Instructions:
1. Analyze resume vs job description deeply.
2. Evaluate technical skills, experience, projects, education, and keywords.
3. Estimate ATS compatibility accurately.
4. Identify strengths and skill gaps specifically.
5. Return ONLY valid JSON, no markdown, no explanations.

Return this exact JSON structure:
{{
    "candidate_summary": {{
        "name": "",
        "current_role": "",
        "experience_level": "",
        "total_experience": "",
        "top_skills": [],
        "overall_summary": ""
    }},
    "resume_analysis": {{
        "ats_score": 0,
        "strengths": [],
        "weaknesses": [],
        "improvement_suggestions": []
    }},
    "job_match_analysis": {{
        "job_title": "{job_title}",
        "overall_match_score": 0,
        "skills_match_percentage": 0,
        "ats_pass_probability": 0,
        "interview_selection_probability": 0,
        "matching_skills": [],
        "missing_skills": [],
        "suitable_strengths": [],
        "suitability_gaps": []
    }},
    "career_guidance": {{
        "recommended_certifications": [],
        "recommended_projects": [],
        "learning_roadmap": []
    }}
}}

Rules:
- All scores: integers 0-100.
- At least 4 strengths, 4 weaknesses, 3 missing skills.
- overall_summary: 3-4 concise sentences.
- learning_roadmap: 4-5 actionable steps.
- Return ONLY the JSON object.
"""
    chain = llm | parser
    return chain.invoke(prompt)

def create_retriever(docs):
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_chroma import Chroma
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    return vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 10
    }
)


# ══════════════════════════════════════════════════════════════════════════════
# ── Helper: build RAG chain for chat ─────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
def build_rag_chain(retriever, dynamic_summary):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    prompt = ChatPromptTemplate.from_template("""
You are an AI Resume Advisor.

Use the resume content and analysis below to answer the user's question.

Resume Content:
{context}

Analysis Context:
{global_context}

Conversation:
{history}

User Question:
{input}

Instructions:
- Answer directly.
- Do not say "based on the candidate summary" or "according to the analysis".
- Speak naturally as if you have reviewed the resume yourself.
- If the question is about skills, projects, strengths, weaknesses, career growth, or job readiness, use both the resume and analysis.
- Keep answers concise and actionable.
- Use bullet points when useful.
""")

    chat_llm = get_chat_llm()

    rag_chain = (
        {
            "context": itemgetter("input")
            | retriever
            | (lambda docs: "\n\n".join([d.page_content for d in docs])),

            "input": itemgetter("input"),
            "history": itemgetter("history"),
            "global_context": lambda x: dynamic_summary,
        }
        | prompt
        | chat_llm
        | StrOutputParser()
    )

    return rag_chain
# ══════════════════════════════════════════════════════════════════════════════
# ── UI helpers ────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
def score_color(score: int) -> str:
    if score >= 80: return "#22c55e"
    if score >= 60: return "#eab308"
    return "#ef4444"

def score_label(score: int) -> str:
    if score >= 80: return "Excellent"
    if score >= 60: return "Good"
    return "Needs Work"

def circular_gauge(value: int, label: str, subtitle: str, icon: str) -> str:
    color = score_color(value)
    pct = value / 100
    # SVG circle: r=40, circumference≈251.2
    circ = 251.2
    offset = circ * (1 - pct)
    return f"""
<div style="background:#1a1d2e;border:1px solid #2a2d45;border-radius:16px;
            padding:24px 16px;text-align:center;min-width:160px;flex:1;">
  <svg width="100" height="100" viewBox="0 0 100 100" style="margin:0 auto;display:block;">
    <circle cx="50" cy="50" r="40" fill="none" stroke="#2a2d45" stroke-width="8"/>
    <circle cx="50" cy="50" r="40" fill="none" stroke="{color}" stroke-width="8"
            stroke-dasharray="{circ}" stroke-dashoffset="{offset:.1f}"
            stroke-linecap="round" transform="rotate(-90 50 50)"/>
    <text x="50" y="42" text-anchor="middle" fill="{color}"
          font-size="11" font-family="Space Grotesk" font-weight="700">{icon}</text>
    <text x="50" y="58" text-anchor="middle" fill="{color}"
          font-size="18" font-family="Space Grotesk" font-weight="700">{value}%</text>
  </svg>
  <div style="color:#e8eaf0;font-weight:700;font-size:13px;margin-top:8px;">{label}</div>
  <div style="color:#8b8fa8;font-size:11px;margin-top:4px;line-height:1.4;">{subtitle}</div>
</div>"""

def pill(text: str, color: str, icon: str = "") -> str:
    return f"""<span style="display:inline-flex;align-items:center;gap:4px;
        background:{color}22;border:1px solid {color}44;border-radius:20px;
        padding:4px 12px;margin:3px;font-size:13px;color:{color};">
        {icon} {text}</span>"""


# ══════════════════════════════════════════════════════════════════════════════
# ── PAGE 1: Home ──────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
def render_home():
    st.markdown("""
    <div style="text-align:center;padding:48px 24px 32px;">
      <div style="font-size:56px;margin-bottom:8px;">🤖</div>
      <h1 style="font-size:42px;font-weight:800;margin-bottom:12px;">
        <span style="color:#6366f1;">AI</span> Career Copilot
      </h1>
      <p style="color:#8b8fa8;font-size:17px;max-width:520px;margin:0 auto;line-height:1.6;">
        Your AI-powered career partner to analyze your resume,<br>
        match job roles, and accelerate your career growth.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Main card ────────────────────────────────────────────────────────────
    with st.container():
        st.markdown('<div style="max-width:760px;margin:0 auto;padding:0 16px;">', unsafe_allow_html=True)

        # File upload
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
          <span style="font-size:20px;">📄</span>
          <span style="font-weight:700;font-size:17px;">Upload Your Resume</span>
          <span style="color:#8b8fa8;font-size:13px;">Supported: PDF, DOC, DOCX (Max 10MB)</span>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            label="Resume",
            type=["pdf", "doc", "docx"],
            label_visibility="collapsed",
            key="resume_file",
        )

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # Job Title
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
          <span style="font-size:20px;">💼</span>
          <span style="font-weight:700;font-size:17px;">Job Title / Target Role</span>
        </div>
        """, unsafe_allow_html=True)

        job_title = st.text_input(
            label="Job Title",
            placeholder="e.g., Python Developer, Full Stack Developer, Data Scientist",
            label_visibility="collapsed",
            key="job_title",
        )

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # Job Description
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
          <span style="font-size:20px;">📋</span>
          <span style="font-weight:700;font-size:17px;">Job Description</span>
        </div>
        <p style="color:#8b8fa8;font-size:13px;margin-bottom:8px;">
          Paste the job description to get a more accurate analysis
        </p>
        """, unsafe_allow_html=True)

        job_desc = st.text_area(
            label="Job Description",
            placeholder="Paste the job description here...",
            height=180,
            max_chars=5000,
            label_visibility="collapsed",
            key="job_desc",
        )

        char_count = len(job_desc) if job_desc else 0
        st.markdown(f'<div style="text-align:right;color:#8b8fa8;font-size:12px;">{char_count} / 5000</div>',
                    unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # Analyze button
        if st.button("✨  Analyze My Resume", key="analyze_btn"):
            if not uploaded_file:
                st.error("⚠️ Please upload your resume (PDF or DOCX).")
            elif not job_title.strip():
                st.error("⚠️ Please enter the job title.")
            elif not job_desc.strip():
                st.error("⚠️ Please paste the job description.")
            else:
                with st.spinner("🔍 Analyzing your resume... This may take 20–30 seconds."):
                    try:
                        resume_text, docs = extract_resume_text(uploaded_file)
                        retriever = create_retriever(docs)

                        result = run_analysis(
                            resume_text,
                            job_title.strip(),
                            job_desc.strip()
                        )
                        # Store in session state
                        st.session_state["retriever"] = retriever
                        st.session_state["analysis"] = result
                        st.session_state["docs"] = docs
                        st.session_state["resume_text"] = resume_text
                        st.session_state["page"] = "dashboard"
                        st.session_state["chat_history"] = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")

        # Feature pills
        st.markdown("""
        <div style="display:flex;justify-content:center;gap:24px;flex-wrap:wrap;
                    padding:24px 0 8px;border-top:1px solid #2a2d45;margin-top:16px;">
          <span style="color:#8b8fa8;font-size:13px;">✨ AI-Powered Analysis</span>
          <span style="color:#8b8fa8;">|</span>
          <span style="color:#8b8fa8;font-size:13px;">📊 Detailed Insights</span>
          <span style="color:#8b8fa8;">|</span>
          <span style="color:#8b8fa8;font-size:13px;">🎯 Personalized Guidance</span>
          <span style="color:#8b8fa8;">|</span>
          <span style="color:#8b8fa8;font-size:13px;">📈 Career Growth</span>
        </div>
        <div style="background:#1a1d2e;border:1px solid #2a2d45;border-radius:12px;
                    padding:16px;margin-top:12px;display:flex;align-items:center;gap:12px;">
          <span style="font-size:24px;">🛡️</span>
          <div>
            <div style="font-weight:600;font-size:14px;">Your Data is Secure</div>
            <div style="color:#8b8fa8;font-size:13px;">
              Your resume and data are processed securely and are not stored permanently.
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ── PAGE 2: Dashboard ─────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
def render_dashboard():
    analysis = st.session_state.get("analysis", {})
    cs = analysis.get("candidate_summary", {})
    ra = analysis.get("resume_analysis", {})
    jm = analysis.get("job_match_analysis", {})
    cg = analysis.get("career_guidance", {})

    # ── Top bar ──────────────────────────────────────────────────────────────
    col_name, col_btn = st.columns([5, 1])
    with col_name:
        name = cs.get("name", "Candidate")
        role = cs.get("current_role", st.session_state.get("job_title", ""))
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;padding:20px 0 8px;">
          <div style="width:56px;height:56px;background:linear-gradient(135deg,#6366f1,#8b5cf6);
                      border-radius:50%;display:flex;align-items:center;justify-content:center;
                      font-size:22px;font-weight:700;color:white;flex-shrink:0;">
            {name[0].upper() if name else "C"}
          </div>
          <div>
            <div style="font-size:22px;font-weight:800;">{name}</div>
            <div style="color:#8b8fa8;font-size:15px;">{role}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_btn:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        if st.button("← New Analysis", key="back_btn"):
            st.session_state["page"] = "home"
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Score gauges ─────────────────────────────────────────────────────────
    st.markdown("### CANDIDATE ANALYSIS OVERVIEW")
    ats = ra.get("ats_score", 0)
    match = jm.get("overall_match_score", 0)
    skills_pct = jm.get("skills_match_percentage", 0)
    ats_prob = jm.get("ats_pass_probability", 0)
    interview_prob = jm.get("interview_selection_probability", 0)

    gauges_html = f"""
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 24px;">
      {circular_gauge(ats, "ATS Score", "Good chance of passing ATS screening.", "📄")}
      {circular_gauge(match, "Overall Match Score", "Match strength for the specified role.", "🎯")}
      {circular_gauge(skills_pct, "Skills Match", "Alignment between your skills and job requirements.", "🧩")}
      {circular_gauge(ats_prob, "ATS Pass Probability", "Probability of clearing ATS filters.", "🛡️")}
      {circular_gauge(interview_prob, "Interview Probability", "Chance of getting interview calls.", "👥")}
    </div>
    """
    st.markdown(gauges_html, unsafe_allow_html=True)

    # ── Summary row ───────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1.8, 1.8])

    with c1:
        st.markdown(f"""
        <div style="background:#1a1d2e;border:1px solid #2a2d45;border-radius:12px;padding:20px;height:auto;min-height:220px;overflow:hidden;">
          <div style="color:#6366f1;font-weight:700;font-size:13px;letter-spacing:1px;margin-bottom:10px;">
            👤 CANDIDATE SUMMARY
          </div>
          <p style="color:#c8cad8;font-size:13px;line-height:1.6;margin-bottom:12px;">
            {cs.get("overall_summary", "")[:220]}{"..." if len(cs.get("overall_summary",""))>220 else ""}
          </p>
          <span style="background:#6366f122;border:1px solid #6366f144;border-radius:20px;
                       padding:4px 12px;font-size:12px;color:#6366f1;">
            {cs.get("experience_level","")}</span>
          <span style="background:#3b82f622;border:1px solid #3b82f644;border-radius:20px;
                       padding:4px 12px;font-size:12px;color:#3b82f6;margin-left:6px;">
            {cs.get("total_experience","")}</span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        strengths = ra.get("strengths", [])
        s_html = "".join([f'<div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:6px;"><span style="color:#22c55e;">✓</span><span style="font-size:13px;">{s}</span></div>' for s in strengths[:5]])
        st.markdown(f"""
        <div style="background:#1a1d2e;border:1px solid #2a2d45;border-radius:12px;padding:20px;height:auto;min-height:220px;overflow:hidden;">
          <div style="color:#22c55e;font-weight:700;font-size:13px;letter-spacing:1px;margin-bottom:10px;">
            👍 STRENGTHS
          </div>
          {s_html}
        </div>
        """, unsafe_allow_html=True)

    with c3:
        weaknesses = ra.get("weaknesses", [])
        w_html = "".join([f'<div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:6px;"><span style="color:#ef4444;">✗</span><span style="font-size:13px;">{w}</span></div>' for w in weaknesses[:5]])
        st.markdown(f"""
        <div style="background:#1a1d2e;border:1px solid #2a2d45;border-radius:12px;padding:20px;height:auto; min-height:220px;overflow:hidden;">
          <div style="color:#ef4444;font-weight:700;font-size:13px;letter-spacing:1px;margin-bottom:10px;">
            👎 WEAKNESSES
          </div>
          {w_html}
        </div>
        """, unsafe_allow_html=True)

    with c4:
        matched = jm.get("matching_skills", [])
        m_html = "".join([pill(s, "#22c55e", "✓") for s in matched])
        st.markdown(f"""
        <div style="background:#1a1d2e;border:1px solid #2a2d45;border-radius:12px;padding:20px;height:auto;min-height:220px;overflow:hidden;">
          <div style="color:#22c55e;font-weight:700;font-size:13px;letter-spacing:1px;margin-bottom:10px;">
            ✅ MATCHED SKILLS
          </div>
          <div style="line-height:2;">{m_html}</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        missing = jm.get("missing_skills", [])
        ms_html = "".join([pill(s, "#ef4444", "✗") for s in missing])
        st.markdown(f"""
        <div style="background:#1a1d2e;border:1px solid #2a2d45;border-radius:12px;padding:20px;height:auto;min-height:220px;overflow:hidden;">
          <div style="color:#ef4444;font-weight:700;font-size:13px;letter-spacing:1px;margin-bottom:10px;">
            ❌ MISSING SKILLS
          </div>
          <div style="line-height:2;">{ms_html}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Career Guidance ──────────────────────────────────────────────────────
    st.markdown("### 📈 CAREER GUIDANCE")
    g1, g2, g3 = st.columns(3)

    with g1:
        certs = cg.get("recommended_certifications", [])
        certs_html = "".join([f'<li style="margin-bottom:8px;font-size:13px;">{c}</li>' for c in certs])
        st.markdown(f"""
        <div style="background:#1a1d2e;border:1px solid #2a2d45;border-radius:12px;padding:20px;min-height:180px;">
          <div style="color:#6366f1;font-weight:700;font-size:14px;margin-bottom:12px;">🏆 Recommended Certifications</div>
          <ul style="color:#c8cad8;padding-left:16px;">{certs_html}</ul>
        </div>
        """, unsafe_allow_html=True)

    with g2:
        projects = cg.get("recommended_projects", [])
        proj_html = "".join([f'<li style="margin-bottom:8px;font-size:13px;">{p}</li>' for p in projects])
        st.markdown(f"""
        <div style="background:#1a1d2e;border:1px solid #2a2d45;border-radius:12px;padding:20px;min-height:180px;">
          <div style="color:#3b82f6;font-weight:700;font-size:14px;margin-bottom:12px;">📁 Recommended Projects</div>
          <ul style="color:#c8cad8;padding-left:16px;">{proj_html}</ul>
        </div>
        """, unsafe_allow_html=True)

    with g3:
        roadmap = cg.get("learning_roadmap", [])
        steps_html = "".join([f"""
        <div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;">
          <div style="width:24px;height:24px;border-radius:50%;background:#eab30822;border:2px solid #eab308;
                      color:#eab308;font-size:11px;font-weight:700;display:flex;align-items:center;
                      justify-content:center;flex-shrink:0;">{i+1}</div>
          <span style="font-size:13px;color:#c8cad8;">{step}</span>
        </div>""" for i, step in enumerate(roadmap)])

        st.markdown(f"""
        <div style="background:#1a1d2e;border:1px solid #2a2d45;border-radius:12px;padding:20px;min-height:180px;">
          <div style="color:#eab308;font-weight:700;font-size:14px;margin-bottom:12px;">🗺️ Learning Roadmap</div>
          {steps_html}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Improvement Suggestions ───────────────────────────────────────────────
    suggestions = ra.get("improvement_suggestions", [])
    if suggestions:
        sug_html = "".join([f'<div style="background:#1a1d2e;border:1px solid #2a2d45;border-radius:8px;padding:12px 16px;margin-bottom:8px;font-size:13px;color:#c8cad8;display:flex;gap:10px;"><span style="color:#06b6d4;">💡</span>{s}</div>' for s in suggestions])
        st.markdown(f"""
        <div style="background:#131627;border:1px solid #2a2d45;border-radius:12px;padding:20px;margin-bottom:16px;">
          <div style="color:#06b6d4;font-weight:700;font-size:14px;margin-bottom:12px;">💡 Improvement Suggestions</div>
          {sug_html}
        </div>
        """, unsafe_allow_html=True)

    # ── Chat section ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#131627;border:1px solid #2a2d45;border-radius:12px;padding:20px;margin-bottom:8px;">
      <div style="color:#6366f1;font-weight:700;font-size:15px;margin-bottom:4px;">✨ CHAT WITH ASSISTANT</div>
      <div style="color:#8b8fa8;font-size:13px;">Ask anything about your resume, skills, career growth, or job opportunities.</div>
    </div>
    """, unsafe_allow_html=True)

    # Init chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Build dynamic summary for RAG
    dynamic_summary = f"""
Candidate Summary: {analysis.get('candidate_summary', {}).get('overall_summary', '')}
ATS Score: {ra.get('ats_score', 0)}
Strengths: {', '.join(ra.get('strengths', []))}
Weaknesses: {', '.join(ra.get('weaknesses', []))}
Match Score: {jm.get('overall_match_score', 0)}
Missing Skills: {', '.join(jm.get('missing_skills', []))}
Learning Roadmap: {' | '.join(cg.get('learning_roadmap', []))}
"""

    # Display existing messages
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input
    if user_input := st.chat_input("Type your question here..."):
        st.session_state["chat_history"].append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()

            with st.spinner("Thinking..."):
                try:
                    retriever = st.session_state.get("retriever")

                    if retriever:
                        rag_chain = build_rag_chain(retriever, dynamic_summary)

                        history_text = "\n".join([
                            f"{m['role']}: {m['content']}"
                            for m in st.session_state["chat_history"][-6:]
                        ])

                        answer = rag_chain.invoke({
                            "input": user_input,
                            "history": history_text
                        })
                    else:
                        chat_llm = get_chat_llm()
                        answer = chat_llm.invoke(
                            f"{dynamic_summary}\n\nUser: {user_input}"
                        ).content

                    response_placeholder.markdown(answer)

                    st.session_state["chat_history"].append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:
                    err = f"❌ Chat error: {str(e)}"
                    response_placeholder.error(err)

                    st.session_state["chat_history"].append({
                        "role": "assistant",
                        "content": err
                    })


# ══════════════════════════════════════════════════════════════════════════════
# ── Router ────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "home"

    if st.session_state["page"] == "home":
        render_home()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
