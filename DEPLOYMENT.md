# Deployment Guide

This project is a Streamlit dashboard. For the interactive dashboard, the recommended free deployment target is **Streamlit Community Cloud**.

GitHub Pages and Vercel are useful for a static portfolio landing page, but they do not directly host a long-running Streamlit server in the same way.

## Recommended: Streamlit Community Cloud

1. Create a GitHub repository for this folder.
2. Push the project to GitHub.
3. Go to https://share.streamlit.io/
4. Choose the repository.
5. Set the app entry point to:

```text
app/app.py
```

6. In **Advanced settings**, choose a stable Python version supported by the app, preferably Python `3.11` or `3.12`.
7. Keep `requirements.txt` in the repository root.
8. Deploy.

This gives you a live interactive dashboard URL that can be used in LinkedIn posts and in the static landing page.

Official Streamlit notes:

- Community Cloud is designed for public apps and is free for community sharing.
- Dependencies are read from `requirements.txt`.
- Python version is selected in the Community Cloud deployment UI, not from `runtime.txt`.

## GitHub Pages Static Landing Page

This repo includes a static landing page in:

```text
docs/index.html
```

To publish it:

1. Push the repository to GitHub.
2. Open repository **Settings**.
3. Go to **Pages**.
4. Choose **Deploy from a branch**.
5. Select the `main` branch and `/docs` folder.
6. Save.

After Streamlit Cloud deployment, edit `docs/index.html` and replace:

```text
#interactive-dashboard
```

with the real Streamlit dashboard URL.

GitHub Pages is free for the static landing page. It cannot run the Streamlit Python app by itself.

## Vercel Static Landing Page

Vercel can host the static landing page:

1. Import the GitHub repository into Vercel.
2. Set the project root or output folder to:

```text
docs
```

3. Leave the build command empty.
4. Deploy.

Use the Vercel page as the public portfolio page and link its “Launch Dashboard” button to the Streamlit Cloud app.

Vercel is free for a static landing page. It is not the recommended host for this Streamlit app because Streamlit expects a persistent Python web process.

## Exact Free Deployment Checklist

Use this sequence:

1. Create a public GitHub repository.
2. Push this project folder to the repository.
3. Go to https://share.streamlit.io/
4. Sign in with GitHub.
5. Click **Create app**.
6. Select the repo and branch.
7. Set main file path to `app/app.py`.
8. Open **Advanced settings** and select Python `3.11` or `3.12`.
9. Click **Deploy**.
10. Copy the resulting `*.streamlit.app` URL.
11. Paste that URL into LinkedIn and optionally into `docs/index.html`.

## Contact CTA

Creator: Shireen El Sabea  
LinkedIn: https://www.linkedin.com/in/shireenalsabea/  
Email: sabeashireen@gmail.com
