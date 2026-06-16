# Deployment Guide

This project has three free public deployment targets:

1. **Vercel** for the complete project hub in `docs/`
2. **GitHub Pages** for the same complete project hub through GitHub Actions
3. **Streamlit Community Cloud** for the live interactive dashboard in `app/app.py`

Vercel and GitHub Pages are both excellent for the full public portfolio page, report downloads, carousel preview, and project story. Streamlit Community Cloud is the right free host for the actual interactive Python dashboard.

## Recommended GitHub Repository

Create the public repository under Shireen's GitHub account:

```text
https://github.com/Shireenelsabea/shireen-sudan-humanitarian-ai-insights
```

See [GITHUB_REPO_SETUP.md](GITHUB_REPO_SETUP.md) for the exact repository description, topics, and deployment settings.

## Vercel: Complete Project Hub

The Vercel site serves:

- project overview
- dashboard explanation
- report download
- LinkedIn carousel preview and download
- methodology and ethical-use notes
- Shireen's contact links

This repository includes `vercel.json`:

```json
{
  "framework": null,
  "buildCommand": null,
  "installCommand": "",
  "outputDirectory": "docs",
  "cleanUrls": true
}
```

When importing into Vercel, use these settings if asked:

```text
Framework Preset: Other
Build Command: leave empty
Install Command: leave empty
Output Directory: docs
```

## GitHub Pages: Complete Project Hub

This repository includes:

```text
.github/workflows/pages.yml
docs/.nojekyll
```

After pushing the repository:

1. Open the GitHub repository.
2. Go to **Settings**.
3. Go to **Pages**.
4. Set **Source** to **GitHub Actions**.
5. The workflow will deploy `docs/`.

Expected URL:

```text
https://shireenelsabea.github.io/shireen-sudan-humanitarian-ai-insights/
```

## Streamlit Community Cloud: Interactive Dashboard

For the live dashboard:

1. Go to https://share.streamlit.io/
2. Sign in with GitHub.
3. Choose Shireen's repository.
4. Set the app entry point to:

```text
app/app.py
```

5. In Advanced settings, choose Python `3.11` or `3.12`.
6. Keep `requirements.txt` in the repository root.
7. Deploy.

This gives a public `*.streamlit.app` URL for the interactive dashboard.

## GitHub Push Commands

After creating the empty GitHub repository:

```powershell
git remote add origin https://github.com/Shireenelsabea/shireen-sudan-humanitarian-ai-insights.git
git push -u origin main
```

## Contact CTA

Creator: Shireen El Sabea  
LinkedIn: https://www.linkedin.com/in/shireenalsabea/  
Email: sabeashireen@gmail.com
