# Sudan Humanitarian AI Insights Dashboard

A first-phase, LinkedIn-ready demo showing how AI-assisted analysis can support humanitarian prioritization without paid APIs, private data, or a full production system.

Created by **Shireen El Sabea**.

- LinkedIn: https://www.linkedin.com/in/shireenalsabea/
- Collaboration email: sabeashireen@gmail.com

The dashboard turns a small public-data-informed humanitarian scenario into:

- State-level displacement and needs visuals
- A transparent AI-style priority score
- Local NLP classification of synthetic community feedback
- A simple displacement scenario forecast
- An intervention queue for NGO decision-makers
- A selected-hotspot AI Action Brief with recommended next steps
- Branded logo and clean in-app logo reveal animation

## Why This Demo Works

This is intentionally lightweight. It is not trying to be a finished NGO platform. It is designed to show the potential of AI in a credible way: data comes in, feedback is classified, hotspots are ranked, and the output becomes something a program manager could discuss.

No paid services are required. The app runs locally with Streamlit, Pandas, NumPy, and Plotly.

## Deployment

For the interactive dashboard, use Streamlit Community Cloud. See [DEPLOYMENT.md](DEPLOYMENT.md).

For GitHub Pages or Vercel, use the static landing page in:

```text
docs/index.html
```

GitHub Pages and Vercel are suitable for the landing page, while Streamlit Community Cloud is the suitable host for the interactive app.

## Suggested Demo Flow

1. Start on **Operations View** to show the map and ranked hotspots.
2. Open **Feedback Intelligence** to show local NLP classification.
3. Open **Hotspot Brief** and select South Darfur or North Darfur.
4. Download the selected action brief to show how the dashboard turns analysis into a usable decision note.
5. End with the CTA: connect with NGOs, humanitarian data teams, and social-impact employers.

## Run It

```powershell
pip install -r requirements.txt
streamlit run app/app.py
```

Then open:

```text
http://localhost:8501
```

## Data Transparency

The included state-level rows and feedback samples are synthetic demonstration data. They are calibrated around public humanitarian themes and public context sources, but they are not operational field data.

No personally identifiable information is included.

Useful public context sources:

- IOM DTM Sudan Mobility Tracking: https://dtm.iom.int/sudan
- HDX Sudan IOM DTM dataset page: https://data.humdata.org/dataset/sdn-iom-dtm-from-api
- OCHA Sudan HDX organization page: https://data.humdata.org/organization/ocha-sudan
- ReliefWeb Sudan response updates: https://response.reliefweb.int/sudan

## Suggested Positioning

Use this as a proof-of-concept for a public post:

> What if humanitarian teams could turn community feedback and displacement data into rapid operational insight, without exposing private data or depending on expensive tools?

That is the story this prototype demonstrates.

CTA:

> I am open to collaboration with NGOs, humanitarian data teams, and social-impact employers interested in responsible AI for community feedback, needs analysis, and decision-support dashboards.
