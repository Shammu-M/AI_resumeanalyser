# Resume Analyser

A small Streamlit application that extracts text from resume PDFs and uses the free Groq tier to review each resume for a target job role. The app uses the `qwen/qwen3.6-27b` model by default and keeps the implementation in one file: `main.py`.

## Features

The analyser produces six sections:

1. Content Clarity & Impact
2. Skills Presentation
3. Experience Descriptions
4. Specific Recommendations for the Job Role
5. Overall Rating & Checklist
6. Refined Resume

Multiple text-based PDFs can be uploaded and analysed in one submission.

## Architecture

```text
Streamlit UI (main.py)
        |
        v
PDF upload -> pypdf text extraction
        |
        v
Prompt builder with target job role and resume text
        |
        v
Groq Chat Completions API
        |
        v
Markdown analysis rendered in Streamlit
```

All UI, PDF extraction, prompting, and Groq integration live in `main.py` to keep the project easy to understand and run.

## Workflow

1. Enter the target job role.
2. Upload one or more PDF resumes.
3. Select **Analyse resume**.
4. The app extracts text from each PDF using `pypdf`.
5. The text and job role are sent to Groq using the configured model.
6. The six-part review and refined resume are displayed in the browser.

Text-based PDFs work best. Image-only scanned PDFs require OCR and are not included in this simple version.

## Setup

Open PowerShell in the project directory and create or activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=qwen/qwen3.6-27b
```

Keep `.env` private. Never commit the API key.

## Start the app

```powershell
streamlit run main.py
```

Streamlit will print a local URL, normally `http://localhost:8501`.

## Notes

- Groq model availability and free-tier limits are controlled by Groq and may change.
- The app sends extracted resume text to the Groq API for analysis. Avoid uploading confidential information unless you are comfortable with that processing.
- If the configured model is unavailable for your account, set `GROQ_MODEL` in `.env` to a model available in your Groq console.
