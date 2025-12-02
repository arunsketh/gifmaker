# AVI to GIF Converter (Streamlit Web App)

Password-protected Streamlit web app that converts `.avi` videos into animated GIFs with control over FPS, width, trim range, looping, and optimization.

## Features

- Password gate using `st.secrets` (no hard-coded password).
- Upload `.avi` files via Streamlit's web UI.
- Choose FPS, output width, start/end time, loop count, and optimization.
- Preview the generated GIF in the browser.
- Download the GIF file directly from the app.

## File structure

- `app.py` – main Streamlit app (entrypoint on Streamlit Cloud).
- `requirements.txt` – Python dependencies.
- `.streamlit/config.toml` – app configuration (telemetry disabled).
- `.gitignore` – ignores local secrets and environment cruft.
- **Not committed:** `.streamlit/secrets.toml` – local secrets only.

## Local setup

1. Clone the repository:

git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

text

2. Create and activate a virtual environment (optional but recommended).

3. Install dependencies:

pip install -r requirements.txt

text

4. Create a local secrets file (do **not** commit this):

mkdir -p .streamlit
cat > .streamlit/secrets.toml << 'EOF'
app_password = "CHANGE_ME_LOCAL"
EOF

text

5. Run the app locally:

streamlit run app.py

text

6. Open the local URL shown in the terminal, enter the password, upload an AVI, adjust options, and download the GIF.

## Deploying on Streamlit Community Cloud

1. Push your repo (with `app.py`, `requirements.txt`, `.gitignore`, `.streamlit/config.toml`, and this `README.md`) to GitHub.

2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud) and sign in with GitHub.

3. Click **New app** and select:
- Repository: `<your-username>/<your-repo>`
- Branch: `main` (or your default)
- Main file path: `app.py`

4. In the app’s **Settings → Secrets** panel, add:

app_password = "CHANGE_ME_FOR_WEB"

text

This value will be accessible in the app as `st.secrets["app_password"]` to gate the UI.[web:15]

5. Click **Deploy**. Streamlit Cloud will install dependencies from `requirements.txt` and start the app.

6. Share the app URL with users; they will see:
- A password prompt.
- The AVI upload widget and conversion options.
- GIF preview and download button after conversion.

## Security and privacy notes

- Password and any future secrets are stored via Streamlit’s secrets mechanism, not in the source code or Git history.[web:30]
- `.streamlit/secrets.toml` is ignored by `.gitignore` to avoid accidental commits of sensitive data.
- Telemetry is disabled for this project via `.streamlit/config.toml`.
