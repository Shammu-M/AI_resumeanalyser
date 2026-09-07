import os
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

load_dotenv()

DEFAULT_MODEL = "qwen/qwen3.6-27b"
MODEL_NAME = os.getenv("GROQ_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL

st.set_page_config(
    page_title="Resume Analyser",
    page_icon="📄",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background: #f5f7fb; }
    .block-container { max-width: 1100px; padding-top: 3rem; }
    .hero { padding: 1rem 0 2rem; }
    .hero h1 { color: #182230; font-size: 2.5rem; margin-bottom: .35rem; }
    .hero p { color: #5d6978; font-size: 1.05rem; }
    .result { background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.4rem 1.6rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def extract_resume_text(uploaded_files):
    """Extract readable text from each uploaded PDF."""
    resumes = []
    for uploaded_file in uploaded_files:
        reader = PdfReader(BytesIO(uploaded_file.getvalue()))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        if text:
            resumes.append((uploaded_file.name, text))
    return resumes


def analyse_resume(resume_name, resume_text, job_role):
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Add it to your .env file.")

    client = Groq(api_key=api_key)
    system_prompt = """You are an expert resume reviewer and career coach.
Analyse the resume against the requested job role using only evidence in the resume.
Be specific, constructive, concise, and honest. Use Markdown headings and bullets.
Do not invent experience, skills, metrics, or education. Clearly label suggestions as suggestions.
Return exactly these six sections:
1. Content Clarity & Impact
2. Skills Presentation
3. Experience Descriptions
4. Specific Recommendations for the Job Role
5. Overall Rating & Checklist
6. Refined Resume
For the Refined Resume section, provide a complete rewritten resume in Markdown, preserving true facts and using [brackets] for missing details that the candidate should fill in.
"""
    user_prompt = f"""Job role: {job_role}
Resume file: {resume_name}

Resume text:
{resume_text}

Review this resume for the job role above and follow the six-section format exactly."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=7000,
    )
    return response.choices[0].message.content


st.markdown(
    """
    <div class="hero">
      <h1>Resume Analyser</h1>
      <p>Get practical, role-specific feedback and a refined resume draft powered by Groq.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("resume_analysis_form"):
    job_role = st.text_input(
        "Target job role",
        placeholder="e.g. Senior Python Backend Engineer",
    )
    uploaded_files = st.file_uploader(
        "Upload resume PDF(s)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Text-based PDFs work best. Scanned image-only PDFs may not contain extractable text.",
    )
    submitted = st.form_submit_button("Analyse resume", type="primary", use_container_width=True)

if submitted:
    if not job_role.strip():
        st.error("Enter the job role you want to target.")
    elif not uploaded_files:
        st.error("Upload at least one PDF resume.")
    else:
        with st.spinner("Extracting resume text and generating analysis..."):
            try:
                resumes = extract_resume_text(uploaded_files)
                if not resumes:
                    st.error("No readable text was found in the uploaded PDF(s).")
                else:
                    for resume_name, resume_text in resumes:
                        st.subheader(resume_name)
                        st.caption(f"{len(resume_text):,} characters extracted")
                        result = analyse_resume(resume_name, resume_text, job_role.strip())
                        with st.container(border=True):
                            st.markdown(result)
            except Exception as error:
                st.error(f"Analysis failed: {error}")

st.divider()
st.caption(f"Model: {MODEL_NAME} · Keep your API key in .env and never commit it.")
