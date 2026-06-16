# Free Deployment Checklist

The interactive dashboard should be deployed on **Streamlit Community Cloud**.

Why: Streamlit Community Cloud is free for public community apps, works directly from GitHub, and supports Streamlit apps without paid hosting.

## What Is Ready

- App entry point: `app/app.py`
- Dependencies: `requirements.txt`
- App config: `.streamlit/config.toml`
- Static landing page: `docs/index.html`
- Report PDF: `output/pdf/study_report.pdf`
- LinkedIn carousel: `opoenai carousel/sudan_humanitarian_ai_linkedin_carousel.pdf`

## Exact Settings

When deploying on Streamlit Community Cloud:

- Repository: your public GitHub repository
- Branch: `main`
- Main file path: `app/app.py`
- Python version: choose `3.11` or `3.12` in Advanced settings
- Secrets: none required

## Important

GitHub Pages and Vercel can host the static landing page in `docs/`, but they cannot directly run the interactive Streamlit Python app.

After deployment, copy the Streamlit app URL and add it to:

- LinkedIn post
- `docs/index.html` Launch Dashboard button
- README project links
