# Free Deployment Checklist

## 1. Create The GitHub Repository

Create a public repository under:

```text
https://github.com/Shireenelsabea
```

Repository name:

```text
shireen-sudan-humanitarian-ai-insights
```

Then push:

```powershell
git remote add origin https://github.com/Shireenelsabea/shireen-sudan-humanitarian-ai-insights.git
git push -u origin main
```

## 2. Deploy The Live Dashboard On Vercel

Use Vercel for the complete public dashboard in `docs/`.

Settings:

```text
Framework Preset: Other
Build Command: leave empty
Install Command: leave empty
Output Directory: docs
```

The repository includes `vercel.json`, so Vercel should detect these settings automatically.

## 3. Deploy The Live Dashboard On GitHub Pages

The repository includes:

```text
.github/workflows/pages.yml
docs/.nojekyll
```

After pushing to GitHub:

```text
Settings > Pages > Source: GitHub Actions
```

Expected URL:

```text
https://shireenelsabea.github.io/shireen-sudan-humanitarian-ai-insights/
```

Mirrored dashboard URL:

```text
https://shireenelsabea.github.io/shireen-sudan-humanitarian-ai-insights/dashboard.html
```

## 4. Deploy The Interactive Dashboard On Streamlit

Use Streamlit Community Cloud for the Python dashboard.

Settings:

```text
Main file path: app/app.py
Python version: 3.11 or 3.12
Secrets: none
```

## 5. Add Final Links

After deployment, update:

- `README.md`
- `LINKEDIN_POST.md`
- Optional Vercel dashboard URL if you deploy it there too

## What Is Ready

- GitHub Pages/Vercel live dashboard: `docs/index.html`
- Mirrored dashboard URL: `docs/dashboard.html`
- Vercel config: `vercel.json`
- Streamlit app: `app/app.py`
- Dependencies: `requirements.txt`
- App config: `.streamlit/config.toml`
- Report PDF: `docs/downloads/sudan-humanitarian-ai-insights-report.pdf`
- LinkedIn carousel: `docs/downloads/sudan-humanitarian-ai-insights-carousel.pdf`
